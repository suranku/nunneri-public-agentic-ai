#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def index_by_id(items: list[dict]) -> dict[str, dict]:
    return {item["id"]: item for item in items}


def run_contract(repo_root: Path, workflow_name: str, auto_approve: bool, reject_gate: str | None) -> dict:
    neutral = load_json(repo_root / "dist/nunneri-runtime/workflows" / f"{workflow_name}.json")
    crewai = load_json(repo_root / "dist/crewai/flows" / f"{workflow_name}.json")
    flow = crewai["flow"]
    steps = flow["steps"]
    neutral_nodes = index_by_id(neutral["nodes"])

    completed: list[str] = []
    gate_decisions: dict[str, dict] = {}
    status = "completed"
    cancelled_at = None

    for step in steps:
        step_id = step["id"]
        node = neutral_nodes.get(step_id, {})
        if step.get("kind") == "human_input" or node.get("type") == "human_approval":
            if reject_gate == step_id:
                gate_decisions[step_id] = {"approved": False, "action": "reject", "on_reject": "cancel"}
                status = "cancelled"
                cancelled_at = step_id
                break
            if not auto_approve:
                gate_decisions[step_id] = {"approved": None, "action": "waiting"}
                status = "waiting_approval"
                cancelled_at = step_id
                break
            gate_decisions[step_id] = {"approved": True, "action": "approve"}
        completed.append(step_id)

    return {
        "runtime": "crewai",
        "mode": "contract_runner",
        "workflow_name": neutral["name"],
        "contract_source": crewai["contract_source"],
        "status": status,
        "completed_steps": completed,
        "cancelled_at": cancelled_at,
        "gate_decisions": gate_decisions,
        "human_in_loop": flow.get("human_in_loop", []),
        "step_count": len(steps),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a generated CrewAI flow manifest from the Nunneri neutral runtime contract.")
    parser.add_argument("--repo-root", default=Path(__file__).resolve().parents[2], type=Path)
    parser.add_argument("--workflow", default="triage-nine-phase")
    parser.add_argument("--auto-approve", action="store_true", help="Approve all human_input gates and complete the flow.")
    parser.add_argument("--reject-gate", help="Reject a specific gate id and cancel downstream execution.")
    args = parser.parse_args()

    payload = run_contract(args.repo_root.resolve(), args.workflow, args.auto_approve, args.reject_gate)
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
