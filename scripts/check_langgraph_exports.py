#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRIAGE_GRAPH = ROOT / "dist/langgraph/graphs/triage-nine-phase.json"


def main() -> int:
    failures: list[str] = []

    if not (ROOT / "dist/langgraph").is_dir():
        failures.append("dist/langgraph is missing")

    if not TRIAGE_GRAPH.exists():
        failures.append("dist/langgraph/graphs/triage-nine-phase.json is missing")
    else:
        graph = json.loads(TRIAGE_GRAPH.read_text(encoding="utf-8"))
        nodes = graph.get("nodes", [])
        edges = graph.get("edges", [])
        approval_nodes = [node for node in nodes if node.get("approval_checkpoint") is True]

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

        approval_ids = sorted(node.get("id") for node in approval_nodes)
        if approval_ids != ["gate_1", "gate_2"]:
            failures.append(f"approval checkpoints must be gate_1 and gate_2, found {approval_ids}")

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

    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("LangGraph export checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
