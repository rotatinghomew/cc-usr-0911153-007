import json
import tempfile
import unittest
from pathlib import Path

from corridor_twin.events.logistics_event import ContractError, DomainRecord
from corridor_twin.twin_service import Application


def shipment(sid, route="a-b-c", eta=100.0, queue=40.0):
    return DomainRecord(sid, {"shipment_id": sid, "route_code": route, "vehicle_class": "reefer",
        "cargo_class": "cold", "eta_min": eta, "border_queue": queue, "warehouse_load": 0.4,
        "temperature": 4.0, "customs_status": "clear", "capacity_units": 10, "priority": 1,
        "event_sequence": 1})


class RerouteScenarioTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.app = Application(Path(self.temp.name) / "db")
        self.book = self.app.transport_book

    def boot(self, *records):
        for record in records:
            self.app.ingest(record)

    def corridor(self, capacity=2):
        for edge, origin, destination in (("ab", "a", "b"), ("bc", "b", "c"),
                                          ("ad", "a", "d"), ("dc", "d", "c")):
            self.book.capacity(edge, "morning", origin, destination, capacity)

    def test_shared_capacity_is_counted_once_across_tickets(self):
        self.boot(shipment("s1"), shipment("s2"))
        self.book.capacity("ab", "morning", "a", "b", 3)
        self.book.capacity("bc", "morning", "b", "c", 5)
        moves = [{"order_id": "o1", "shipment_id": "s1", "window": "morning", "edges": ["ab", "bc"], "units": 2},
                 {"order_id": "o2", "shipment_id": "s2", "window": "morning", "edges": ["ab", "bc"], "units": 2}]
        plan = self.app.compare_reroute([{"plan_id": "both", "moves": moves}])["plans"][0]
        self.assertFalse(plan["feasible"])
        self.assertTrue(any("共享路段 ab@morning" in text and "重复占用" in text for text in plan["violations"]))
        shared = {row["edge_id"]: row for row in plan["shared_edges"]}
        self.assertEqual(shared["ab"]["orders"], ["o1", "o2"])
        self.assertGreater(shared["ab"]["utilization_after"], 1.0)
        solo = self.app.compare_reroute([{"plan_id": "solo", "moves": moves[:1]}])["plans"][0]
        self.assertTrue(solo["feasible"])
        self.assertEqual(self.book.inspect()["orders"], [])

    def test_comparison_is_hypothetical_and_does_not_touch_the_book(self):
        self.boot(shipment("s1"))
        self.corridor()
        self.book.reserve("o1", "s1", "morning", ["ab", "bc"], 1, {"ab": 1, "bc": 1})
        before = self.book.inspect()
        counts = self.app.repository.snapshot()["counts"]
        result = self.app.compare_reroute([{"plan_id": "p", "moves": [
            {"cancel": "o1", "order_id": "o2", "shipment_id": "s1", "window": "morning",
             "edges": ["ad", "dc"], "units": 2}]}])
        self.assertIn("假设", result["note"])
        self.assertEqual(self.book.inspect(), before)
        self.assertEqual(self.app.repository.snapshot()["counts"], counts)

    def test_reroute_changes_queue_eta_and_risk_for_shared_shipments(self):
        self.boot(shipment("s1"), shipment("s2"))
        self.corridor()
        self.book.reserve("o1", "s1", "morning", ["ab", "bc"], 1, {"ab": 1, "bc": 1})
        self.book.reserve("o2", "s2", "morning", ["ab", "bc"], 1, {"ab": 1, "bc": 1})
        plan = self.app.compare_reroute([{"plan_id": "reroute-s1", "moves": [
            {"cancel": "o1", "order_id": "o3", "shipment_id": "s1", "window": "morning",
             "edges": ["ad", "dc"], "units": 1}]}])["plans"][0]
        self.assertTrue(plan["feasible"], plan["violations"])
        by_id = {row["shipment_id"]: row for row in plan["shipments"]}
        other = by_id["s2"]
        self.assertFalse(other["moved"])
        self.assertLess(other["after"]["queue_min"], other["before"]["queue_min"])
        self.assertLess(other["after"]["eta_min"], other["before"]["eta_min"])
        self.assertLessEqual(other["after"]["risk"], other["before"]["risk"])
        moved = by_id["s1"]
        self.assertTrue(moved["moved"])
        self.assertEqual((moved["order_before"], moved["order_after"]), ("o1", "o3"))
        self.assertIn("排队", moved["explanation"])
        self.assertIn("预计到达", moved["explanation"])
        self.assertIn("风险", moved["explanation"])

    def test_commit_applies_plan_and_releases_old_capacity(self):
        self.boot(shipment("s1"), shipment("s2"))
        self.corridor(capacity=1)
        self.book.reserve("o1", "s1", "morning", ["ab", "bc"], 1, {"ab": 1, "bc": 1})
        plan = self.app.compare_reroute([{"plan_id": "p", "moves": [
            {"cancel": "o1", "order_id": "o2", "shipment_id": "s1", "window": "morning",
             "edges": ["ad", "dc"], "units": 1}]}])["plans"][0]
        applied = self.app.commit_reroute(plan)
        self.assertEqual(applied["cancelled"], ["o1"])
        self.assertEqual(applied["created"], ["o2"])
        orders = {row["order_id"]: row["status"] for row in self.book.inspect()["orders"]}
        self.assertEqual(orders, {"o1": "cancelled", "o2": "reserved"})
        edges = {row["edge_id"]: row["available"] for row in self.book.inspect()["edges"]}
        self.assertEqual(edges["ab"], 1)
        self.assertEqual(edges["ad"], 0)
        view = self.app.inspect()["transport"]["view"]
        self.assertEqual({row["shipment_id"] for row in view["shipments"]}, {"s1"})
        with self.assertRaises(ContractError):
            self.app.commit_reroute(plan)

    def test_commit_is_rejected_when_commitments_change_after_comparison(self):
        self.boot(shipment("s1"), shipment("s2"))
        self.corridor()
        self.book.reserve("o1", "s1", "morning", ["ab", "bc"], 1, {"ab": 1, "bc": 1})
        moves = [{"cancel": "o1", "order_id": "o2", "shipment_id": "s1", "window": "morning",
                  "edges": ["ad", "dc"], "units": 1}]
        plan = self.app.compare_reroute([{"plan_id": "p", "moves": moves}])["plans"][0]
        self.book.reserve("o9", "s2", "morning", ["ab", "bc"], 1, {"ab": 1, "bc": 1})
        self.book.transition("o9", "cancelled")
        with self.assertRaisesRegex(ContractError, "重新判断"):
            self.app.commit_reroute(plan)
        reserved = [row["order_id"] for row in self.book.inspect()["orders"] if row["status"] == "reserved"]
        self.assertEqual(reserved, ["o1"])
        plan2 = self.app.compare_reroute([{"plan_id": "p2", "moves": moves}])["plans"][0]
        self.book.capacity("ad", "morning", "a", "d", 3, 1)
        with self.assertRaisesRegex(ContractError, "重新判断"):
            self.app.commit_reroute(plan2)

    def test_dispatched_commitment_keeps_history_and_cannot_be_rerouted(self):
        self.boot(shipment("s1"))
        self.corridor()
        self.book.reserve("o1", "s1", "morning", ["ab", "bc"], 1, {"ab": 1, "bc": 1})
        self.book.transition("o1", "dispatched")
        plan = self.app.compare_reroute([{"plan_id": "p", "moves": [
            {"cancel": "o1", "order_id": "o2", "shipment_id": "s1", "window": "morning",
             "edges": ["ad", "dc"], "units": 1}]}])["plans"][0]
        self.assertFalse(plan["feasible"])
        self.assertTrue(any("已发运" in text for text in plan["violations"]))
        with self.assertRaisesRegex(ContractError, "已发运"):
            self.app.commit_reroute(plan)
        order = {row["order_id"]: row for row in self.book.inspect()["orders"]}["o1"]
        self.assertEqual(order["status"], "dispatched")
        self.assertEqual(json.loads(order["edges_json"]), ["ab", "bc"])

    def test_released_capacity_is_reflected_in_comparison_and_control_tower(self):
        self.boot(shipment("s1"), shipment("s2"))
        self.book.capacity("ab", "morning", "a", "b", 1)
        self.book.capacity("bc", "morning", "b", "c", 1)
        self.book.reserve("o1", "s1", "morning", ["ab", "bc"], 1, {"ab": 1, "bc": 1})
        moves = [{"order_id": "o2", "shipment_id": "s2", "window": "morning", "edges": ["ab", "bc"], "units": 1}]
        blocked = self.app.compare_reroute([{"plan_id": "p", "moves": moves}])["plans"][0]
        self.assertFalse(blocked["feasible"])
        self.book.transition("o1", "cancelled")
        view = self.app.inspect()["transport"]["view"]
        self.assertEqual({row["edge_id"]: row["available"] for row in view["edges"]}, {"ab": 1, "bc": 1})
        freed = self.app.compare_reroute([{"plan_id": "p", "moves": moves}])["plans"][0]
        self.assertTrue(freed["feasible"], freed["violations"])
        self.assertNotEqual(blocked["basis_hash"], freed["basis_hash"])

    def test_commit_rechecks_current_shipment_state(self):
        self.boot(shipment("s1"))
        self.book.capacity("ab", "morning", "a", "b", 1)
        self.book.capacity("bc", "morning", "b", "c", 1)
        moves = [{"order_id": "o1", "shipment_id": "s1", "window": "morning", "edges": ["ab", "bc"], "units": 1}]
        plan = self.app.compare_reroute([{"plan_id": "p", "moves": moves}])["plans"][0]
        self.assertTrue(plan["feasible"], plan["violations"])
        record = self.app.repository.get_record("s1")
        self.app.repository.save_record(record.with_state("in_transit"), expected_version=record.version)
        with self.assertRaisesRegex(ContractError, "重新判断"):
            self.app.commit_reroute(plan)
        again = self.app.compare_reroute([{"plan_id": "p", "moves": moves}])["plans"][0]
        self.assertFalse(again["feasible"])
        self.assertTrue(any("in_transit" in text for text in again["violations"]))

    def test_morning_meeting_end_to_end(self):
        self.boot(shipment("s1"), shipment("s2"), shipment("s3"))
        self.corridor()
        self.book.capacity("ad", "morning", "a", "d", 1, 1)
        self.book.capacity("dc", "morning", "d", "c", 1, 1)
        self.book.reserve("o1", "s1", "morning", ["ab", "bc"], 1, {"ab": 1, "bc": 1})
        self.book.reserve("o2", "s2", "morning", ["ab", "bc"], 1, {"ab": 1, "bc": 1})
        result = self.app.compare_reroute([
            {"plan_id": "keep", "moves": []},
            {"plan_id": "reroute-s2", "moves": [
                {"cancel": "o2", "order_id": "o3", "shipment_id": "s2", "window": "morning",
                 "edges": ["ad", "dc"], "units": 1}]}])
        keep, reroute = result["plans"]
        self.assertTrue(keep["feasible"], keep["violations"])
        self.assertEqual(keep["summary"]["total_queue_before"], keep["summary"]["total_queue_after"])
        shared = {row["edge_id"]: row for row in keep["shared_edges"]}
        self.assertEqual(set(shared), {"ab", "bc"})
        self.assertEqual(shared["ab"]["orders"], ["o1", "o2"])
        self.assertEqual(shared["ab"]["utilization_after"], 1.0)
        self.assertTrue(reroute["feasible"], reroute["violations"])
        s1 = {row["shipment_id"]: row for row in reroute["shipments"]}["s1"]
        self.assertLess(s1["after"]["eta_min"], s1["before"]["eta_min"])
        applied = self.app.commit_reroute(reroute)
        self.assertEqual(applied["created"], ["o3"])
        with self.assertRaises(ContractError):
            self.app.commit_reroute(keep)


if __name__ == "__main__":
    unittest.main()
