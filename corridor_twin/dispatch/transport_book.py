"""分时窗路段容量与人工运输承诺；实际发运保留历史。"""
import json

from corridor_twin.events.logistics_event import ContractError


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

    def reserve(self, order_id, shipment_id, window, edges, units, revisions):
        if not order_id or not edges or len(set(edges)) != len(edges) or type(units) is not int or units <= 0:
            raise ContractError("运输承诺、路径或占用无效")
        with self.repository.transaction() as c:
            old = c.execute("SELECT * FROM transport_orders WHERE order_id=?", (order_id,)).fetchone()
            if old:
                if (old["shipment_id"], old["window"], old["units"], json.loads(old["edges_json"])) != (shipment_id, window, units, edges):
                    raise ContractError("运输承诺标识冲突")
                return dict(old)
            shipment = c.execute("SELECT * FROM records WHERE record_id=?", (shipment_id,)).fetchone()
            if shipment is None or shipment["state"] != "booked":
                raise ContractError("只有尚未发运的货票可以分配新承诺")
            if c.execute("SELECT 1 FROM transport_orders WHERE shipment_id=? AND status IN ('reserved','dispatched')",
                         (shipment_id,)).fetchone():
                raise ContractError("货票已有运输承诺")
            previous = None
            for edge_id in edges:
                edge = c.execute("SELECT * FROM transport_edges WHERE edge_id=? AND window=?", (edge_id, window)).fetchone()
                if edge is None or revisions.get(edge_id) != edge["revision"]:
                    raise ContractError("路径包含未知或已更新路段")
                if previous is not None and previous != edge["origin"]:
                    raise ContractError("运输路径不连续")
                previous = edge["destination"]
                used = c.execute("SELECT COALESCE(SUM(units),0) FROM transport_usage WHERE edge_id=? AND window=?",
                                 (edge_id, window)).fetchone()[0]
                if used + units > edge["capacity"]:
                    raise ContractError("共享路段容量不足")
            c.execute("INSERT INTO transport_orders VALUES(?,?,?,?,?,?,'reserved')",
                      (order_id, shipment_id, shipment["fingerprint"], window, units, json.dumps(edges)))
            for edge_id in edges:
                c.execute("INSERT INTO transport_usage VALUES(?,?,?,?)", (order_id, edge_id, window, units))
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

    def inspect(self):
        with self.repository.connect() as c:
            edges = [dict(r) for r in c.execute("SELECT e.*,e.capacity-COALESCE(SUM(u.units),0) AS available "
                "FROM transport_edges e LEFT JOIN transport_usage u ON e.edge_id=u.edge_id AND e.window=u.window "
                "GROUP BY e.edge_id,e.window ORDER BY e.window,e.edge_id")]
            return {"edges": edges, "orders": [dict(r) for r in c.execute("SELECT * FROM transport_orders ORDER BY order_id")]}
