from __future__ import annotations

import unittest
from corridor_twin.events.logistics_event import DomainRecord
from corridor_twin.network.capacity_replay import journey_pressure, network_balance, route_graph, shortest_capacity_path


class CapacityReplayTests(unittest.TestCase):
    def record(self, key, route="a-b-c"):
        return DomainRecord(key, {"shipment_id": key, "route_code": route, "vehicle_class": "truck", "cargo_class": "cold",
            "eta_min": 120, "border_queue": 20, "warehouse_load": .6, "temperature": 7,
            "customs_status": "clear", "capacity_units": 10, "priority": 2, "event_sequence": 1})

    def test_graph_path_respects_capacity(self):
        graph = route_graph([self.record("s1")])
        self.assertIsNotNone(shortest_capacity_path(graph, "a", "c", 5))
        self.assertIsNone(shortest_capacity_path(graph, "a", "c", 50))

    def test_pressure_and_balance(self):
        rows = [self.record("a"), self.record("b")]
        self.assertGreater(journey_pressure(rows[0])["total"], 0.0)
        self.assertGreater(network_balance(rows)["capacity"], network_balance(rows)["demand"])
