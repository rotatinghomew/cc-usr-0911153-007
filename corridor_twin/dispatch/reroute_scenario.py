"""改道场景比较：多票共享路段及口岸能力的假设性分析。

compare_plans 只读取台账快照做推演，不写入任何承诺，比较中的假设不会提前变成
已发生事件；选定方案后由 TransportBook.apply_plan 按实时剩余能力和货票当前状态
复核并原子落实。control_tower_view 供控制塔展示当前占用下各货票的排队、
预计到达与风险，撤销释放的容量会即时反映到结论中。
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from statistics import fmean
from typing import Any

from corridor_twin.events.logistics_event import ContractError, bounded, finite_number, utc_now
from corridor_twin.network.capacity_replay import journey_pressure
from corridor_twin.dispatch.transport_book import validate_route

# 占用超过登记容量时的拥堵上限（倍），避免推演数值发散
CONGESTION_CAP = 10.0


def _route_of(order: dict) -> list:
    return list(json.loads(order["edges_json"]))


def _loads(usage_rows: list) -> dict:
    loads: dict = {}
    for row in usage_rows:
        key = (row["edge_id"], row["window"])
        loads[key] = loads.get(key, 0) + row["units"]
    return loads


def _projection(record, route, window, loads, capacities) -> dict:
    """单票在指定路径与占用水平下的排队、预计到达与风险。"""
    pressure = journey_pressure(record)
    base_queue = max(0.0, finite_number(record.payload.get("border_queue", 0.0)))
    eta0 = max(0.0, finite_number(record.payload.get("eta_min", 0.0)))
    utils = []
    for edge_id in route:
        capacity = capacities.get((edge_id, window), 0)
        load = loads.get((edge_id, window), 0)
        if capacity > 0:
            utils.append(min(load / capacity, CONGESTION_CAP))
        else:
            utils.append(CONGESTION_CAP if load > 0 else 0.0)
    mean_util = fmean(utils) if utils else 0.0
    queue = base_queue * mean_util
    eta = eta0 + queue
    risk = bounded(pressure["total"] * (1.0 + queue / max(1.0, eta0)))
    return {"queue_min": round(queue, 3), "eta_min": round(eta, 3), "risk": round(risk, 6),
            "max_utilization": round(max(utils), 6) if utils else 0.0}


@dataclass
class _Board:
    edges: list
    orders: list
    usage: list
    capacities: dict
    edge_metas: dict
    base_loads: dict
    records: dict
    basis: str


def _normalize_moves(plan: dict) -> list:
    moves = []
    for move in plan.get("moves") or []:
        shipment_id = move.get("shipment_id")
        if not shipment_id:
            raise ContractError("方案步骤缺少货票标识")
        if move.get("cancel") is None and move.get("order_id") is None:
            raise ContractError("方案步骤缺少撤销或新建承诺")
        moves.append({"cancel": move.get("cancel"), "order_id": move.get("order_id"),
                      "shipment_id": shipment_id, "window": move.get("window"),
                      "edges": move.get("edges"), "units": move.get("units")})
    return moves


def _load_board(book, moved_ids) -> _Board:
    repository = book.repository
    with repository.connect() as c:
        edges = [dict(r) for r in c.execute("SELECT * FROM transport_edges")]
        orders = [dict(r) for r in c.execute(
            "SELECT * FROM transport_orders WHERE status IN ('reserved','dispatched') ORDER BY order_id")]
        usage = [dict(r) for r in c.execute("SELECT * FROM transport_usage")]
        basis = book.basis_hash(moved_ids, connection=c)
    shipment_ids = set(moved_ids) | {order["shipment_id"] for order in orders}
    records = {sid: repository.get_record(sid) for sid in sorted(shipment_ids)}
    return _Board(edges=edges, orders=orders, usage=usage,
                  capacities={(e["edge_id"], e["window"]): e["capacity"] for e in edges},
                  edge_metas={(e["edge_id"], e["window"]): (e["origin"], e["destination"]) for e in edges},
                  base_loads=_loads(usage), records=records, basis=basis)


def _compare_one(plan, board: _Board) -> dict:
    violations: list[str] = []
    after_orders = {order["order_id"]: dict(order) for order in board.orders}
    cancelled: dict = {}
    touched: set = set()
    for move in plan["moves"]:
        if move["cancel"] is None:
            continue
        old = after_orders.get(move["cancel"])
        if old is None:
            violations.append(f"运输承诺 {move['cancel']} 不存在或已取消，方案假设不成立")
            continue
        if old["status"] != "reserved":
            violations.append(f"运输承诺 {move['cancel']} 已发运，不可撤销或改写")
            continue
        cancelled[move["cancel"]] = old
        touched.update((edge_id, old["window"]) for edge_id in _route_of(old))
        del after_orders[move["cancel"]]
    created: list = []
    for move in plan["moves"]:
        if move["order_id"] is None:
            continue
        order_id, shipment_id, window = move["order_id"], move["shipment_id"], move["window"]
        edges, units = move["edges"], move["units"]
        if order_id in after_orders or order_id in cancelled:
            violations.append(f"运输承诺 {order_id} 标识冲突")
            continue
        if (not isinstance(edges, (list, tuple)) or not edges or len(set(edges)) != len(edges)
                or type(units) is not int or units <= 0 or not window):
            violations.append(f"运输承诺 {order_id} 的路径或占用无效")
            continue
        edges = list(edges)
        record = board.records.get(shipment_id)
        if record is None:
            violations.append(f"货票 {shipment_id} 不存在，不能分配新承诺")
            continue
        if record.state != "booked":
            violations.append(f"货票 {shipment_id} 当前状态为 {record.state}，只有尚未发运的货票可以分配新承诺")
            continue
        if any(order["shipment_id"] == shipment_id for order in after_orders.values()):
            violations.append(f"货票 {shipment_id} 在方案后仍有多条有效承诺")
            continue
        metas = {edge_id: board.edge_metas[(edge_id, window)] for edge_id in edges
                 if (edge_id, window) in board.edge_metas}
        try:
            validate_route(record.payload.get("route_code", ""), metas, edges)
        except ContractError as exc:
            violations.append(f"运输承诺 {order_id}：{exc}")
            continue
        order = {"order_id": order_id, "shipment_id": shipment_id, "window": window,
                 "units": units, "edges_json": json.dumps(edges), "status": "reserved"}
        after_orders[order_id] = order
        created.append(order)
        touched.update((edge_id, window) for edge_id in edges)
    after_usage = [{"order_id": order["order_id"], "edge_id": edge_id,
                    "window": order["window"], "units": order["units"]}
                   for order in after_orders.values() for edge_id in _route_of(order)]
    after_loads = _loads(after_usage)
    for (edge_id, window), load in sorted(after_loads.items()):
        capacity = board.capacities.get((edge_id, window), 0)
        if load > capacity:
            violations.append(
                f"共享路段 {edge_id}@{window} 需求 {load} 超出容量 {capacity}，同一容量不能被多票独立重复占用")
    before_by_sid = {order["shipment_id"]: order for order in board.orders}
    after_by_sid: dict = {}
    for order in after_orders.values():
        after_by_sid.setdefault(order["shipment_id"], order)
    moved_sids = {move["shipment_id"] for move in plan["moves"]}
    affected = []
    for sid in sorted(board.records):
        record = board.records.get(sid)
        if record is None:
            continue
        before_order = before_by_sid.get(sid)
        after_order = after_by_sid.get(sid)
        before_edges = {(e, before_order["window"]) for e in _route_of(before_order)} if before_order else set()
        after_edges = {(e, after_order["window"]) for e in _route_of(after_order)} if after_order else set()
        moved = sid in moved_sids
        if not moved and not (before_edges & touched) and not (after_edges & touched):
            continue
        before = _projection(record, _route_of(before_order) if before_order else [],
                             before_order["window"] if before_order else None,
                             board.base_loads, board.capacities)
        after = _projection(record, _route_of(after_order) if after_order else [],
                            after_order["window"] if after_order else None,
                            after_loads, board.capacities)
        delta = {"queue_min": round(after["queue_min"] - before["queue_min"], 3),
                 "eta_min": round(after["eta_min"] - before["eta_min"], 3),
                 "risk": round(after["risk"] - before["risk"], 6)}
        kind = "改道" if moved else "受共享路段影响"
        explanation = (f"货票 {sid}（{kind}）：排队 {before['queue_min']}→{after['queue_min']} 分钟，"
                       f"预计到达 {before['eta_min']}→{after['eta_min']} 分钟，"
                       f"风险 {before['risk']}→{after['risk']}")
        affected.append({"shipment_id": sid, "moved": moved,
                         "order_before": before_order["order_id"] if before_order else None,
                         "order_after": after_order["order_id"] if after_order else None,
                         "before": before, "after": after, "delta": delta, "explanation": explanation})
    edge_orders: dict = {}
    for order in after_orders.values():
        for edge_id in _route_of(order):
            edge_orders.setdefault((edge_id, order["window"]), []).append(order["order_id"])
    shared = []
    for (edge_id, window), order_ids in sorted(edge_orders.items()):
        if len(order_ids) < 2:
            continue
        capacity = board.capacities.get((edge_id, window), 0)
        shared.append({"edge_id": edge_id, "window": window, "orders": sorted(order_ids),
                       "capacity": capacity, "load_after": after_loads.get((edge_id, window), 0),
                       "utilization_before": round(board.base_loads.get((edge_id, window), 0) / capacity, 6) if capacity else None,
                       "utilization_after": round(after_loads.get((edge_id, window), 0) / capacity, 6) if capacity else None})
    summary = {"feasible": not violations, "affected_shipments": len(affected),
               "total_queue_before": round(sum(row["before"]["queue_min"] for row in affected), 3),
               "total_queue_after": round(sum(row["after"]["queue_min"] for row in affected), 3),
               "cancelled": [move["cancel"] for move in plan["moves"] if move["cancel"]],
               "created": [order["order_id"] for order in created]}
    return {"plan_id": plan["plan_id"], "feasible": not violations, "violations": violations,
            "shipments": affected, "shared_edges": shared, "summary": summary,
            "moves": plan["moves"], "basis_hash": board.basis}


def compare_plans(book, plans: list) -> dict:
    """比较多个候选方案；结果仅为假设，落实前须以 basis_hash 复核。"""
    if not plans:
        raise ContractError("至少需要一个候选方案")
    prepared = []
    moved_ids: set = set()
    for index, plan in enumerate(plans):
        moves = _normalize_moves(plan)
        moved_ids.update(move["shipment_id"] for move in moves)
        prepared.append({"plan_id": str(plan.get("plan_id") or f"plan-{index + 1}"), "moves": moves})
    board = _load_board(book, sorted(moved_ids))
    return {"basis_hash": board.basis, "compared_at": utc_now(),
            "note": "场景比较仅为假设，未写入台账；落实时按实时剩余能力与货票当前状态复核",
            "plans": [_compare_one(plan, board) for plan in prepared]}


def control_tower_view(book) -> dict:
    """控制塔当前结论：各路段占用与在册货票的排队、预计到达、风险。"""
    snapshot = book.snapshot()
    capacities = {(edge["edge_id"], edge["window"]): edge["capacity"] for edge in snapshot["edges"]}
    loads = _loads(snapshot["usage"])
    edge_orders: dict = {}
    for order in snapshot["orders"]:
        for edge_id in _route_of(order):
            edge_orders.setdefault((edge_id, order["window"]), []).append(order["order_id"])
    edges_view = []
    for edge in snapshot["edges"]:
        key = (edge["edge_id"], edge["window"])
        used = loads.get(key, 0)
        edges_view.append({"edge_id": edge["edge_id"], "window": edge["window"],
                           "capacity": edge["capacity"], "used": used,
                           "available": edge["capacity"] - used,
                           "utilization": round(used / edge["capacity"], 6) if edge["capacity"] else (1.0 if used else 0.0),
                           "orders": sorted(edge_orders.get(key, []))})
    shipments_view = []
    for order in snapshot["orders"]:
        record = book.repository.get_record(order["shipment_id"])
        if record is None:
            continue
        projection = _projection(record, _route_of(order), order["window"], loads, capacities)
        shipments_view.append({"shipment_id": order["shipment_id"], "order_id": order["order_id"],
                               "status": order["status"], "window": order["window"],
                               "route": _route_of(order), **projection})
    return {"generated_at": utc_now(), "edges": edges_view,
            "shared_edges": [row for row in edges_view if len(row["orders"]) >= 2],
            "shipments": shipments_view}
