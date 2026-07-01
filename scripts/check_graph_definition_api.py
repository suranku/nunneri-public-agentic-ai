#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def main() -> int:
    failures: list[str] = []
    api_path = ROOT / "api/main.py"
    graph_path = ROOT / "dist/langgraph/graphs/triage-nine-phase.json"
    contract_path = ROOT / "dist/nunneri-runtime/workflows/triage-nine-phase.json"

    api = api_path.read_text(encoding="utf-8")
    graph = json.loads(graph_path.read_text(encoding="utf-8"))
    contract = json.loads(contract_path.read_text(encoding="utf-8"))

    require('@app.get("/agents/{agent_name}/graph-definition"' in api, "graph-definition GET route is missing", failures)
    require("def get_agent_graph_definition" in api, "graph-definition handler is missing", failures)
    require("resolve_manifest(agent_name)" in api, "graph-definition handler must resolve agents and commands", failures)
    require("load_graph_definition(manifest, is_command)" in api, "graph-definition handler must use load_graph_definition", failures)
    require('"nodes": nodes' in api, "load_graph_definition must return nodes", failures)
    require('"edges": graph.get("edges", linear_edges(nodes))' in api, "load_graph_definition must return graph edges", failures)
    require('"terminology"' in api, "graph-definition response must include terminology", failures)

    require(graph.get("runtime") == "langgraph", "triage graph-definition source must be LangGraph", failures)
    require(graph.get("contract_source") == "dist/nunneri-runtime/workflows/triage-nine-phase.json", "triage graph must reference the neutral contract", failures)
    require(len(graph.get("nodes", [])) == 9, "triage graph must expose exactly 9 nodes", failures)
    require(len(graph.get("edges", [])) == 8, "triage graph must expose exactly 8 edges", failures)

    by_id = {node.get("id"): node for node in graph.get("nodes", [])}
    require(by_id.get("classification", {}).get("classification_options"), "classification options must be API-visible in graph nodes", failures)
    for gate_id in ("gate_1", "gate_2"):
        gate = by_id.get(gate_id, {})
        approval = gate.get("approval", {})
        require(gate.get("type") == "human_approval", f"{gate_id} must be a human_approval node", failures)
        require(gate.get("approval_checkpoint") is True, f"{gate_id} must be marked as an approval checkpoint", failures)
        require(approval.get("question"), f"{gate_id} must expose an approval question", failures)
        require(approval.get("required_context"), f"{gate_id} must expose required approval context", failures)

    approved_edges = [
        edge for edge in graph.get("edges", [])
        if edge.get("from") == "gate_1" and edge.get("to") == "test_first_fix"
    ]
    require(approved_edges and approved_edges[0].get("condition") == "approved", "gate_1 edge must expose approved condition", failures)
    contract_ids = [node.get("id") for node in contract.get("nodes", [])]
    graph_ids = [node.get("id") for node in graph.get("nodes", [])]
    require(contract_ids == graph_ids, "LangGraph graph-definition nodes must preserve neutral contract order", failures)
    contract_classification = next((node for node in contract.get("nodes", []) if node.get("id") == "classification"), {})
    require(
        by_id.get("classification", {}).get("classification_options") == contract_classification.get("classification_options"),
        "graph-definition classification options must match the neutral contract",
        failures,
    )

    if failures:
        for failure in failures:
            print(failure)
        return 1
    print("Graph-definition API contract checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
