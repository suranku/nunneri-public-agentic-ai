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
    api = (ROOT / "api/main.py").read_text(encoding="utf-8")
    ui = (ROOT / "api/ui.html").read_text(encoding="utf-8")
    triage = json.loads((ROOT / "dist/nunneri-runtime/workflows/triage-nine-phase.json").read_text(encoding="utf-8"))

    require("/agents/{agent_name}/graph-definition" in api, "api/main.py must expose graph-definition endpoint", failures)
    require("load_graph_definition" in api, "api/main.py must load graph definitions from runtime exports", failures)
    require("graph-definition" in ui, "api/ui.html must fetch graph-definition", failures)
    require("Phase Config" in ui, "api/ui.html must label the right panel as Phase Config", failures)
    require("renderContractDefaults" in ui, "api/ui.html must render contract defaults in the phase panel", failures)
    require("edge-label" in ui, "api/ui.html must render edge condition labels", failures)
    require("loadGraphDefinition" in ui, "api/ui.html must use loadGraphDefinition for selected assets", failures)

    nodes = {node["id"]: node for node in triage.get("nodes", [])}
    require(bool(nodes.get("classification", {}).get("classification_options")), "classification phase needs contract options", failures)
    for gate_id in ("gate_1", "gate_2"):
        approval = nodes.get(gate_id, {}).get("approval", {})
        require(bool(approval.get("question")), f"{gate_id} needs an approval question", failures)
        require(bool(approval.get("required_context")), f"{gate_id} needs required approval context", failures)

    if failures:
        for failure in failures:
            print(failure)
        return 1
    print("Graph Studio contract checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
