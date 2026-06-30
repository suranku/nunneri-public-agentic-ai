#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples/runtime-contract-consumer/consume_runtime_contract.py"


def main() -> int:
    failures: list[str] = []

    if not EXAMPLE.exists():
        failures.append("examples/runtime-contract-consumer/consume_runtime_contract.py is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(EXAMPLE), "--repo-root", str(ROOT)],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        if completed.returncode != 0:
            failures.append(f"runtime contract consumer example failed:\n{completed.stdout}")
        else:
            try:
                payload = json.loads(completed.stdout)
            except json.JSONDecodeError as exc:
                failures.append(f"runtime contract consumer output is not JSON: {exc}")
                payload = {}
            if payload:
                if payload.get("contract_version") != "1.0":
                    failures.append("example must report contract_version 1.0")
                if payload.get("workflow_name") != "triage-nine-phase":
                    failures.append("example must load triage-nine-phase by default")
                if payload.get("node_count") != 9:
                    failures.append(f"example must report 9 workflow nodes, found {payload.get('node_count')}")
                if payload.get("approval_gates") != ["gate_1", "gate_2"]:
                    failures.append(f"example approval gates mismatch: {payload.get('approval_gates')}")
                crewai_flow = payload.get("crewai_flow", {})
                if crewai_flow.get("human_in_loop") != ["gate_1", "gate_2"]:
                    failures.append(f"CrewAI-style flow must preserve approval gates, found {crewai_flow.get('human_in_loop')}")
                if len(crewai_flow.get("steps", [])) != 9:
                    failures.append("CrewAI-style flow must contain 9 steps")

    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("Runtime example checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
