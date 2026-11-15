from __future__ import annotations

import heapq
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from corridor_twin.events.logistics_event import DomainRecord, bounded, finite_number, normalized_text


@dataclass(frozen=True)
class RouteOption:
    route: tuple[str, ...]
    minutes: float
    cost: float
    capacity_left: float
    cold_chain_risk: float


def route_graph(records: Iterable[DomainRecord]) -> dict[str, list[tuple[str, float, float]]]:
    graph: dict[str, list[tuple[str, float, float]]] = defaultdict(list)
    for record in records:
        route = normalized_text(record.payload.get("route_code", "origin-destination")).replace("_", "-")
        parts = [part for part in route.split("-") if part]
        if len(parts) < 2:
            parts = ["origin", parts[0] if parts else "destination"]
        eta = max(1.0, finite_number(record.payload.get("eta_min", 60.0)))
        capacity = max(0.0, finite_number(record.payload.get("capacity_units", 0.0)))
        for left, right in zip(parts, parts[1:]):
            graph[left].append((right, eta / (len(parts) - 1), capacity))
    return graph


def shortest_capacity_path(graph: Mapping[str, list[tuple[str, float, float]]], start: str, end: str,
                           demand: float) -> RouteOption | None:
    queue = [(0.0, start, (start,), float("inf"))]
    seen: dict[str, float] = {}
    while queue:
        minutes, node, route, capacity = heapq.heappop(queue)
        if node == end:
            left = max(0.0, capacity - demand)
            return RouteOption(route, minutes, minutes * 0.7 + demand * 1.3, left, 0.0)
        if minutes >= seen.get(node, float("inf")):
            continue
        seen[node] = minutes
        for target, edge_minutes, edge_capacity in graph.get(node, []):
            if edge_capacity < demand:
                continue
            heapq.heappush(queue, (minutes + edge_minutes, target, route + (target,), min(capacity, edge_capacity)))
    return None


def journey_pressure(record: DomainRecord) -> dict[str, float]:
    border = bounded(finite_number(record.payload.get("border_queue", 0.0)) / 300.0)
    warehouse = bounded(finite_number(record.payload.get("warehouse_load", 0.0)))
    customs = normalized_text(record.payload.get("customs_status", "clear"))
    customs_risk = 0.8 if customs not in {"clear", "released", "approved"} else 0.1
    temperature = finite_number(record.payload.get("temperature", 20.0))
    cold_risk = bounded(abs(temperature - 4.0) / 30.0) if normalized_text(record.payload.get("cargo_class")) in {"cold", "fresh", "medical"} else 0.0
    return {"border": border, "warehouse": warehouse, "customs": customs_risk, "cold": cold_risk,
            "total": bounded(border * .3 + warehouse * .25 + customs_risk * .25 + cold_risk * .2)}


def network_balance(records: Iterable[DomainRecord]) -> dict[str, float]:
    rows = list(records)
    capacities = [max(0.0, finite_number(row.payload.get("capacity_units", 0.0))) for row in rows]
    demands = [1.0 + max(0.0, finite_number(row.payload.get("priority", 0.0))) for row in rows]
    capacity = sum(capacities)
    demand = sum(demands)
    return {"capacity": capacity, "demand": demand, "utilization": bounded(demand / max(1.0, capacity)),
            "slack": max(0.0, capacity - demand)}


def derive_context(record: DomainRecord, repository: Any) -> dict[str, float]:
    rows = repository.list_records() or [record]
    pressure = journey_pressure(record)
    balance = network_balance(rows)
    return {"route_pressure_weight": 0.7 + pressure["total"] * 0.7,
            "eta_reliability_weight": 1.1 - pressure["border"] * 0.4,
            "capacity_balance_weight": 1.1 - balance["utilization"] * 0.3,
            "cold_chain_risk_weight": 0.7 + pressure["cold"] * 0.7,
            "network_resilience_weight": 0.6 + bounded(balance["slack"] / max(1.0, balance["capacity"])) * 0.6}
