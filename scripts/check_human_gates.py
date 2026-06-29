#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def require(text: str, needle: str, label: str, failures: list[str]) -> None:
    if needle not in text:
        failures.append(f"missing {label}: {needle}")


def main() -> int:
    failures: list[str] = []
    base = (ROOT / "api/graphs/base.py").read_text(encoding="utf-8")
    main_py = (ROOT / "api/main.py").read_text(encoding="utf-8")
    models = (ROOT / "api/models.py").read_text(encoding="utf-8")
    ui = (ROOT / "api/ui.html").read_text(encoding="utf-8")

    if "auto-approved" in base or "[auto-approved]" in base:
        failures.append("gate node must not auto-approve")

    require(base, "from langgraph.types import interrupt", "LangGraph interrupt import", failures)
    require(base, "decision = interrupt(payload)", "gate interrupt call", failures)
    require(base, '"allowed_actions": ["approve", "reject"]', "approval payload actions", failures)
    require(base, '"route_to": "" if approved else "__cancelled__"', "rejection route", failures)

    require(main_py, "from langgraph.types import Command", "LangGraph Command import", failures)
    require(main_py, '@app.post("/threads/{thread_id}/gates/{gate_id}/approve"', "approve endpoint", failures)
    require(main_py, '@app.post("/threads/{thread_id}/gates/{gate_id}/reject"', "reject endpoint", failures)
    require(main_py, '@app.post("/runs/{run_id}/cancel"', "run cancel endpoint", failures)
    require(main_py, '@app.post("/queue/reset"', "queue reset endpoint", failures)
    require(main_py, '"type": "gate_waiting"', "gate_waiting SSE event", failures)
    require(main_py, '"type": "gate_approved"', "gate_approved SSE event", failures)
    require(main_py, '"type": "gate_rejected"', "gate_rejected SSE event", failures)
    require(main_py, 'Command(resume=decision)', "resume command", failures)

    for status in ("waiting_approval", "approved", "rejected", "cancelled"):
        require(models, f'"{status}"', f"{status} status", failures)

    require(ui, "Approve and resume", "Graph Studio approval button", failures)
    require(ui, "Reject and stop", "Graph Studio rejection button", failures)
    require(ui, "Cancel run", "Graph Studio cancel button", failures)
    require(ui, "Rerun as new thread", "Graph Studio rerun button", failures)
    require(ui, "resetQueue", "Graph Studio queue reset handler", failures)
    require(ui, "case 'gate_waiting':", "Graph Studio waiting handler", failures)

    if failures:
        for failure in failures:
            print(f"human gate check failed: {failure}")
        return 1
    print("Human-blocking gate checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
