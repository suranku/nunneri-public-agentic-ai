#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "examples/crewai-runtime-runner/run_crewai_contract.py"


def run_runner(*args: str) -> tuple[int, dict | None, str]:
    completed = subprocess.run(
        [sys.executable, str(RUNNER), "--repo-root", str(ROOT), *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        payload = None
    return completed.returncode, payload, completed.stdout


def main() -> int:
    failures: list[str] = []

    if not RUNNER.exists():
        failures.append("examples/crewai-runtime-runner/run_crewai_contract.py is missing")
    else:
        code, payload, output = run_runner("--auto-approve")
        if code != 0 or payload is None:
            failures.append(f"CrewAI contract runner approve path failed:\n{output}")
        else:
            if payload.get("runtime") != "crewai":
                failures.append("CrewAI contract runner must report runtime=crewai")
            if payload.get("status") != "completed":
                failures.append(f"approve path must complete, found {payload.get('status')}")
            if payload.get("step_count") != 9:
                failures.append(f"approve path must expose 9 steps, found {payload.get('step_count')}")
            if payload.get("completed_steps", [])[-1:] != ["gate_2"]:
                failures.append("approve path must complete through gate_2")
            decisions = payload.get("gate_decisions", {})
            if decisions.get("gate_1", {}).get("approved") is not True:
                failures.append("approve path must approve gate_1")
            if decisions.get("gate_2", {}).get("approved") is not True:
                failures.append("approve path must approve gate_2")

        code, payload, output = run_runner("--reject-gate", "gate_1")
        if code != 0 or payload is None:
            failures.append(f"CrewAI contract runner reject path failed:\n{output}")
        else:
            if payload.get("status") != "cancelled":
                failures.append(f"reject path must cancel, found {payload.get('status')}")
            if payload.get("cancelled_at") != "gate_1":
                failures.append(f"reject path must cancel at gate_1, found {payload.get('cancelled_at')}")
            if "test_first_fix" in payload.get("completed_steps", []):
                failures.append("reject path must not continue to test_first_fix")
            if payload.get("gate_decisions", {}).get("gate_1", {}).get("approved") is not False:
                failures.append("reject path must record gate_1 approval=false")

    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("CrewAI runtime runner checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
