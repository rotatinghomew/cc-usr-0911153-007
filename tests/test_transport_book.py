import tempfile
import unittest
from pathlib import Path
from corridor_twin.twin_service import Application
from corridor_twin.events.logistics_event import DomainRecord, ContractError


class TransportBookTests(unittest.TestCase):
    def test_shared_edges_reserve_atomically_and_release_on_cancellation(self):
        with tempfile.TemporaryDirectory() as d:
            app = Application(Path(d) / "db")
            for name in ("a", "b"):
                app.ingest(DomainRecord(name, {}))
            book = app.transport_book
            book.capacity("ab", "morning", "a", "b", 1)
            book.capacity("bc", "morning", "b", "c", 1)
            book.reserve("one", "a", "morning", ["ab", "bc"], 1, {"ab": 1, "bc": 1})
            with self.assertRaises(ContractError):
                book.reserve("two", "b", "morning", ["ab", "bc"], 1, {"ab": 1, "bc": 1})
            self.assertEqual(len(book.inspect()["orders"]), 1)
            book.transition("one", "cancelled")
            book.reserve("two", "b", "morning", ["ab", "bc"], 1, {"ab": 1, "bc": 1})
            book.transition("two", "dispatched")
            with self.assertRaises(ContractError):
                book.transition("two", "cancelled")
            book.transition("two", "completed")
            rows = Application(Path(d) / "db").inspect()["transport"]
            self.assertEqual([r["status"] for r in rows["orders"]], ["cancelled", "completed"])
            self.assertTrue(all(r["available"] == 1 for r in rows["edges"]))

    def test_changed_capacity_and_disconnected_route_leave_no_partial_booking(self):
        with tempfile.TemporaryDirectory() as d:
            app = Application(Path(d) / "db")
            app.ingest(DomainRecord("a", {}))
            book = app.transport_book
            book.capacity("ab", "morning", "a", "b", 2)
            book.capacity("xy", "morning", "x", "y", 2)
            with self.assertRaises(ContractError):
                book.reserve("one", "a", "morning", ["ab", "xy"], 1, {"ab": 1, "xy": 1})
            book.capacity("ab", "morning", "a", "b", 3, 1)
            with self.assertRaises(ContractError):
                book.reserve("two", "a", "morning", ["ab"], 1, {"ab": 1})
            self.assertEqual(book.inspect()["orders"], [])
