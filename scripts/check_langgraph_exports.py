#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRIAGE_GRAPH = ROOT / "dist/langgraph/graphs/triage-nine-phase.json"
TRIAGE_CONTRACT = ROOT / "dist/nunneri-runtime/workflows/triage-nine-phase.json"


def main() -> int:
    failures: list[str] = []

    if not (ROOT / "dist/langgraph").is_dir():
        failures.append("dist/langgraph is missing")

    if not TRIAGE_CONTRACT.exists():
        failures.append("dist/nunneri-runtime/workflows/triage-nine-phase.json is missing")

    contract = {}
    if TRIAGE_CONTRACT.exists():
        contract = json.loads(TRIAGE_CONTRACT.read_text(encoding="utf-8"))

    if not TRIAGE_GRAPH.exists():
        failures.append("dist/langgraph/graphs/triage-nine-phase.json is missing")
    else:
        graph = json.loads(TRIAGE_GRAPH.read_text(encoding="utf-8"))
        nodes = graph.get("nodes", [])
        edges = graph.get("edges", [])
        approval_nodes = [node for node in nodes if node.get("approval_checkpoint") is True]
        contract_nodes = contract.get("nodes", [])
        contract_edges = contract.get("edges", [])

        if graph.get("contract_source") != "dist/nunneri-runtime/workflows/triage-nine-phase.json":
            failures.append("triage-nine-phase LangGraph export must point to the neutral contract source")

        if len(nodes) != 9:
            failures.append(f"triage-nine-phase must export exactly 9 nodes, found {len(nodes)}")

        expected_ids = [
            "intake",
            "context_load",
            "classification",
            "evidence_collection",
            "root_cause_analysis",
            "gate_1",
            "test_first_fix",
            "validation",
            "gate_2",
        ]
        actual_ids = [node.get("id") for node in nodes]
        if actual_ids != expected_ids:
            failures.append(f"triage-nine-phase node order mismatch: {actual_ids}")
        if contract_nodes and actual_ids != [node.get("id") for node in contract_nodes]:
            failures.append("triage-nine-phase LangGraph node order does not match neutral contract")

        approval_ids = sorted(node.get("id") for node in approval_nodes)
        if approval_ids != ["gate_1", "gate_2"]:
            failures.append(f"approval checkpoints must be gate_1 and gate_2, found {approval_ids}")
        for node in approval_nodes:
            approval = node.get("approval", {})
            if approval.get("on_reject") != "cancel":
                failures.append(f"{node.get('id')} approval rejection policy must be cancel")

        expected_edges = [
            ("intake", "context_load"),
            ("context_load", "classification"),
            ("classification", "evidence_collection"),
            ("evidence_collection", "root_cause_analysis"),
            ("root_cause_analysis", "gate_1"),
            ("gate_1", "test_first_fix"),
            ("test_first_fix", "validation"),
            ("validation", "gate_2"),
        ]
        actual_edges = [(edge.get("from"), edge.get("to")) for edge in edges]
        if actual_edges != expected_edges:
            failures.append(f"triage-nine-phase edge order mismatch: {actual_edges}")
        if contract_edges and actual_edges != [(edge.get("from"), edge.get("to")) for edge in contract_edges]:
            failures.append("triage-nine-phase LangGraph edges do not match neutral contract")

    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("LangGraph export checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
