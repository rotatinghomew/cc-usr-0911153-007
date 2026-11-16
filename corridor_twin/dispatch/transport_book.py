"""分时窗路段容量与人工运输承诺；实际发运保留历史。"""
import json

from corridor_twin.events.logistics_event import ContractError, stable_hash


def validate_route(route_code, edge_metas, edges):
    """校验路径连续性与起终点；edge_metas 为 {edge_id: (origin, destination)}。"""
    route = [part.strip().casefold() for part in str(route_code or "").replace("_", "-").split("-") if part.strip()]
    previous = None
    first_origin = None
    for edge_id in edges:
        meta = edge_metas.get(edge_id)
        if meta is None:
            raise ContractError("路径包含未知或已更新路段")
        origin, destination = meta
        if previous is not None and previous != origin:
            raise ContractError("运输路径不连续")
        if first_origin is None:
            first_origin = origin
        previous = destination
    if len(route) >= 2 and (first_origin.casefold(), previous.casefold()) != (route[0], route[-1]):
        raise ContractError("运输路径起终点与货票不符")


class TransportBook:
    def __init__(self, repository):
        self.repository = repository
        with repository.connect() as c:
            c.executescript("""
                CREATE TABLE IF NOT EXISTS transport_edges(
                    edge_id TEXT NOT NULL, window TEXT NOT NULL, origin TEXT NOT NULL,
                    destination TEXT NOT NULL, capacity INTEGER NOT NULL CHECK(capacity>=0),
                    revision INTEGER NOT NULL, PRIMARY KEY(edge_id,window));
                CREATE TABLE IF NOT EXISTS transport_orders(
                    order_id TEXT PRIMARY KEY, shipment_id TEXT NOT NULL, fingerprint TEXT NOT NULL,
                    window TEXT NOT NULL, units INTEGER NOT NULL CHECK(units>0),
                    edges_json TEXT NOT NULL, status TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS transport_usage(
                    order_id TEXT NOT NULL, edge_id TEXT NOT NULL, window TEXT NOT NULL,
                    units INTEGER NOT NULL, PRIMARY KEY(order_id,edge_id,window));
            """)

    def capacity(self, edge_id, window, origin, destination, units, expected_revision=0):
        if not all(isinstance(x, str) and x for x in (edge_id, window, origin, destination)) or origin == destination:
            raise ContractError("路段及时间窗无效")
        if type(units) is not int or units < 0:
            raise ContractError("容量须为非负整数")
        with self.repository.transaction() as c:
            old = c.execute("SELECT * FROM transport_edges WHERE edge_id=? AND window=?", (edge_id, window)).fetchone()
            if (old["revision"] if old else 0) != expected_revision:
                raise ContractError("路段容量版本已改变")
            occupied = c.execute("SELECT COALESCE(SUM(units),0) FROM transport_usage WHERE edge_id=? AND window=?",
                                 (edge_id, window)).fetchone()[0]
            if occupied > units or (old and (old["origin"], old["destination"]) != (origin, destination)):
                raise ContractError("已有承诺不能被容量或路段更改破坏")
            c.execute("INSERT INTO transport_edges VALUES(?,?,?,?,?,?) ON CONFLICT(edge_id,window) DO UPDATE "
                      "SET capacity=excluded.capacity,revision=excluded.revision",
                      (edge_id, window, origin, destination, units, expected_revision + 1))
        return expected_revision + 1

    def _validate_move(self, order_id, edges, units):
        if (not order_id or not isinstance(edges, (list, tuple)) or not edges
                or len(set(edges)) != len(edges) or type(units) is not int or units <= 0):
            raise ContractError("运输承诺、路径或占用无效")

    def _insert_order(self, c, order_id, shipment_id, window, edges, units):
        if c.execute("SELECT 1 FROM transport_orders WHERE order_id=?", (order_id,)).fetchone():
            raise ContractError("运输承诺标识冲突")
        shipment = c.execute("SELECT * FROM records WHERE record_id=?", (shipment_id,)).fetchone()
        if shipment is None or shipment["state"] != "booked":
            raise ContractError("只有尚未发运的货票可以分配新承诺")
        if c.execute("SELECT 1 FROM transport_orders WHERE shipment_id=? AND status IN ('reserved','dispatched')",
                     (shipment_id,)).fetchone():
            raise ContractError("货票已有运输承诺")
        edge_rows = {}
        for edge_id in edges:
            edge = c.execute("SELECT * FROM transport_edges WHERE edge_id=? AND window=?", (edge_id, window)).fetchone()
            if edge is not None:
                edge_rows[edge_id] = edge
        validate_route(json.loads(shipment["payload_json"]).get("route_code", ""),
                       {edge_id: (row["origin"], row["destination"]) for edge_id, row in edge_rows.items()}, edges)
        for edge_id in edges:
            used = c.execute("SELECT COALESCE(SUM(units),0) FROM transport_usage WHERE edge_id=? AND window=?",
                             (edge_id, window)).fetchone()[0]
            if used + units > edge_rows[edge_id]["capacity"]:
                raise ContractError("共享路段容量不足")
        c.execute("INSERT INTO transport_orders VALUES(?,?,?,?,?,?,'reserved')",
                  (order_id, shipment_id, shipment["fingerprint"], window, units, json.dumps(list(edges))))
        for edge_id in edges:
            c.execute("INSERT INTO transport_usage VALUES(?,?,?,?)", (order_id, edge_id, window, units))

    def reserve(self, order_id, shipment_id, window, edges, units, revisions):
        self._validate_move(order_id, edges, units)
        with self.repository.transaction() as c:
            old = c.execute("SELECT * FROM transport_orders WHERE order_id=?", (order_id,)).fetchone()
            if old:
                if (old["shipment_id"], old["window"], old["units"], json.loads(old["edges_json"])) != (shipment_id, window, units, edges):
                    raise ContractError("运输承诺标识冲突")
                return dict(old)
            for edge_id in edges:
                edge = c.execute("SELECT revision FROM transport_edges WHERE edge_id=? AND window=?", (edge_id, window)).fetchone()
                if edge is None or revisions.get(edge_id) != edge["revision"]:
                    raise ContractError("路径包含未知或已更新路段")
            self._insert_order(c, order_id, shipment_id, window, edges, units)
            return dict(c.execute("SELECT * FROM transport_orders WHERE order_id=?", (order_id,)).fetchone())

    def transition(self, order_id, status):
        allowed = {"reserved": {"dispatched", "cancelled"}, "dispatched": {"completed"}, "cancelled": set(), "completed": set()}
        with self.repository.transaction() as c:
            old = c.execute("SELECT * FROM transport_orders WHERE order_id=?", (order_id,)).fetchone()
            if old is None:
                raise ContractError("运输承诺不存在")
            if old["status"] == status:
                return
            if status not in allowed[old["status"]]:
                raise ContractError("已发运承诺不可撤销或改写")
            if status == "dispatched":
                current = c.execute("SELECT fingerprint FROM records WHERE record_id=?", (old["shipment_id"],)).fetchone()
                if current is None or current[0] != old["fingerprint"]:
                    raise ContractError("货票资料已改变，须重新确认运输安排")
            c.execute("UPDATE transport_orders SET status=? WHERE order_id=?", (status, order_id))
            if status in {"completed", "cancelled"}:
                c.execute("DELETE FROM transport_usage WHERE order_id=?", (order_id,))

    def _basis(self, c, shipment_ids):
        edges = [tuple(r) for r in c.execute(
            "SELECT edge_id,window,origin,destination,capacity,revision FROM transport_edges ORDER BY edge_id,window")]
        orders = [tuple(r) for r in c.execute(
            "SELECT order_id,shipment_id,fingerprint,window,units,edges_json,status FROM transport_orders ORDER BY order_id")]
        usage = [tuple(r) for r in c.execute(
            "SELECT order_id,edge_id,window,units FROM transport_usage ORDER BY order_id,edge_id,window")]
        shipments = {}
        for shipment_id in sorted(set(shipment_ids)):
            row = c.execute("SELECT state,fingerprint FROM records WHERE record_id=?", (shipment_id,)).fetchone()
            shipments[shipment_id] = tuple(row) if row else None
        return stable_hash({"edges": edges, "orders": orders, "usage": usage, "shipments": shipments})

    def basis_hash(self, shipment_ids, connection=None):
        """比较依据：路段容量版本、全部承诺与占用、相关货票状态指纹的哈希。"""
        if connection is not None:
            return self._basis(connection, shipment_ids)
        with self.repository.connect() as c:
            return self._basis(c, shipment_ids)

    def apply_plan(self, moves, expected_basis):
        """在一个事务内落实选定方案：复核比较依据，撤销未发运承诺并写入新承诺。"""
        if not expected_basis:
            raise ContractError("方案缺少比较依据，需先比较再落实")
        if not moves:
            raise ContractError("方案为空，没有可落实的调度")
        normalized = []
        for move in moves:
            cancel = move.get("cancel")
            order_id = move.get("order_id")
            shipment_id = move.get("shipment_id")
            window = move.get("window")
            edges = move.get("edges")
            units = move.get("units")
            if not shipment_id or not isinstance(shipment_id, str):
                raise ContractError("运输承诺、路径或占用无效")
            if cancel is None and order_id is None:
                raise ContractError("方案步骤缺少撤销或新建承诺")
            if cancel is not None and (not isinstance(cancel, str) or not cancel):
                raise ContractError("运输承诺、路径或占用无效")
            if order_id is not None:
                self._validate_move(order_id, edges, units)
                if not isinstance(window, str) or not window:
                    raise ContractError("运输承诺、路径或占用无效")
            normalized.append({"cancel": cancel, "order_id": order_id, "shipment_id": shipment_id,
                               "window": window, "edges": list(edges) if order_id is not None else [],
                               "units": units})
        shipment_ids = [move["shipment_id"] for move in normalized]
        with self.repository.transaction() as c:
            if self._basis(c, shipment_ids) != expected_basis:
                raise ContractError("运输承诺或路段容量在比较后已变化，需重新判断后再落实")
            cancelled, created = [], []
            for move in normalized:
                if move["cancel"] is None:
                    continue
                row = c.execute("SELECT status FROM transport_orders WHERE order_id=?", (move["cancel"],)).fetchone()
                if row is None:
                    raise ContractError("运输承诺不存在")
                if row["status"] == "dispatched":
                    raise ContractError("已发运承诺不可撤销或改写")
                if row["status"] != "reserved":
                    raise ContractError("运输承诺状态已变化，需重新判断")
                c.execute("UPDATE transport_orders SET status='cancelled' WHERE order_id=?", (move["cancel"],))
                c.execute("DELETE FROM transport_usage WHERE order_id=?", (move["cancel"],))
                cancelled.append(move["cancel"])
            for move in normalized:
                if move["order_id"] is None:
                    continue
                self._insert_order(c, move["order_id"], move["shipment_id"], move["window"], move["edges"], move["units"])
                created.append(move["order_id"])
        return {"cancelled": cancelled, "created": created, "snapshot": self.snapshot()}

    def snapshot(self):
        with self.repository.connect() as c:
            return {"edges": [dict(r) for r in c.execute("SELECT * FROM transport_edges ORDER BY window,edge_id")],
                    "orders": [dict(r) for r in c.execute(
                        "SELECT * FROM transport_orders WHERE status IN ('reserved','dispatched') ORDER BY order_id")],
                    "usage": [dict(r) for r in c.execute(
                        "SELECT * FROM transport_usage ORDER BY order_id,edge_id,window")]}

    def inspect(self):
        with self.repository.connect() as c:
            edges = [dict(r) for r in c.execute("SELECT e.*,e.capacity-COALESCE(SUM(u.units),0) AS available "
                "FROM transport_edges e LEFT JOIN transport_usage u ON e.edge_id=u.edge_id AND e.window=u.window "
                "GROUP BY e.edge_id,e.window ORDER BY e.window,e.edge_id")]
            return {"edges": edges, "orders": [dict(r) for r in c.execute("SELECT * FROM transport_orders ORDER BY order_id")]}
