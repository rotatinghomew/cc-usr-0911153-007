from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from corridor_twin.events.logistics_event import ContractError, Decision, DomainRecord, records_from_fixture, stable_hash
from corridor_twin.state.twin_repository import Repository
from corridor_twin.dispatch.decision_flow import advance_for_outcome, decide
from corridor_twin.visibility.control_tower import export_bundle, verify_bundle
from corridor_twin.network.capacity_replay import derive_context
from corridor_twin.dispatch.transport_book import TransportBook
from corridor_twin.dispatch.reroute_scenario import compare_plans, control_tower_view


class Application:
    def __init__(self, database: str | Path, context: Mapping[str, Any] | None = None):
        self.repository = Repository(database)
        self.transport_book = TransportBook(self.repository)
        self.context = dict(context or {})

    def ingest(self, record: DomainRecord) -> DomainRecord:
        current = self.repository.get_record(record.record_id)
        if current is None:
            self.repository.save_record(record)
            return record
        if current.fingerprint == record.fingerprint:
            return current
        replacement = DomainRecord(record.record_id, record.payload, current.state,
                                   current.version + 1, record.occurred_at, record.source)
        self.repository.save_record(replacement, expected_version=current.version)
        return replacement

    def process(self, record: DomainRecord) -> tuple[DomainRecord, Decision]:
        stored = self.ingest(record)
        context = dict(self.context)
        context.update(derive_context(stored, self.repository))
        decision = decide(stored, context)
        self.repository.save_decision(decision)
        advanced = advance_for_outcome(stored, decision)
        if advanced.fingerprint != stored.fingerprint:
            self.repository.save_record(advanced, expected_version=stored.version)
        return advanced, decision

    def run_fixture(self, fixture: Mapping[str, Any], output: str | Path) -> dict[str, Any]:
        records = records_from_fixture(fixture)
        fixture_hash = stable_hash(fixture)
        run_id = self.repository.begin_run(fixture_hash, len(records))
        completed = self.repository.completed_run(run_id)
        if completed is not None:
            return completed
        decisions: dict[str, Decision] = {}
        final_records: list[DomainRecord] = []
        for record in records:
            final_record, decision = self.process(record)
            final_records.append(final_record)
            decisions[record.record_id] = decision
        snapshot = self.repository.snapshot()
        if snapshot["chain_errors"]:
            raise ContractError("audit chain verification failed")
        manifest = export_bundle(output, final_records, decisions, snapshot, self.repository.event_rows(),
                                 self._transport_report())
        result = {"run_id": run_id, "fixture_hash": fixture_hash, "records": len(final_records),
                  "decisions": len(decisions), "manifest": manifest, "snapshot": snapshot}
        self.repository.finish_run(run_id, result)
        return result

    def compare_reroute(self, plans: list[Mapping[str, Any]]) -> dict[str, Any]:
        """晨会场景比较：多票共享路段及口岸能力的假设性分析，不写入台账。"""
        return compare_plans(self.transport_book, plans)

    def commit_reroute(self, plan: Mapping[str, Any]) -> dict[str, Any]:
        """落实选定方案：按实时台账复核比较依据后原子生效。"""
        if not isinstance(plan, Mapping):
            raise ContractError("方案格式无效")
        basis = plan.get("basis_hash")
        if not basis:
            raise ContractError("方案缺少比较依据，需先比较再落实")
        return self.transport_book.apply_plan(list(plan.get("moves") or []), basis)

    def _transport_report(self) -> dict[str, Any]:
        report = self.transport_book.inspect()
        report["view"] = control_tower_view(self.transport_book)
        return report

    def inspect(self) -> dict[str, Any]:
        return {"snapshot": self.repository.snapshot(), "records": [record.__dict__ for record in self.repository.list_records()],
                "decisions": self.repository.decision_rows(), "transport": self._transport_report()}


def load_fixture(path: str | Path) -> dict[str, Any]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read fixture: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError("fixture root must be an object")
    return value


def run(fixture_path: str | Path, database: str | Path, output: str | Path,
        context: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return Application(database, context).run_fixture(load_fixture(fixture_path), output)


def verify(database: str | Path, output: str | Path) -> dict[str, Any]:
    repository = Repository(database)
    chain_errors = repository.verify_chain()
    bundle_errors = verify_bundle(output)
    return {"ok": not chain_errors and not bundle_errors, "chain_errors": chain_errors,
            "bundle_errors": bundle_errors, "snapshot": repository.snapshot()}
