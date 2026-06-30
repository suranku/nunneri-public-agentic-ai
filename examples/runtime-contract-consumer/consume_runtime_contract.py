#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def crewai_flow_from_workflow(workflow: dict) -> dict:
    approval_nodes = [node["id"] for node in workflow["nodes"] if node.get("type") == "human_approval"]
    return {
        "name": workflow["name"],
        "description": workflow["description"],
        "steps": [
            {
                "id": node["id"],
                "label": node.get("label", node["id"]),
                "kind": "human_input" if node.get("type") == "human_approval" else "task",
                "approval": node.get("approval"),
            }
            for node in workflow["nodes"]
        ],
        "edges": workflow["edges"],
        "human_in_loop": approval_nodes,
    }


def summarize_contract(repo_root: Path, workflow_name: str) -> dict:
    contract_root = repo_root / "dist/nunneri-runtime"
    index = load_json(contract_root / "contract.json")
    workflow = load_json(contract_root / "workflows" / f"{workflow_name}.json")
    approval_gates = [node["id"] for node in workflow["nodes"] if node.get("type") == "human_approval"]
    return {
        "contract_version": index["contract_version"],
        "workflow_name": workflow["name"],
        "workflow_source": workflow["source"],
        "node_count": len(workflow["nodes"]),
        "edge_count": len(workflow["edges"]),
        "approval_gates": approval_gates,
        "runtime_hints": workflow.get("runtime_hints", {}),
        "crewai_flow": crewai_flow_from_workflow(workflow),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Read a Nunneri neutral runtime contract and project it into a CrewAI-style flow.")
    parser.add_argument("--repo-root", default=Path(__file__).resolve().parents[2], type=Path)
    parser.add_argument("--workflow", default="triage-nine-phase")
    args = parser.parse_args()
    payload = summarize_contract(args.repo_root.resolve(), args.workflow)
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
