#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "guides/runtime-contract-demo.html"
REFERENCE = ROOT / "docs/reference/guides/runtime-contract-demo.html"


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def main() -> int:
    failures: list[str] = []
    require(GUIDE.exists(), "guides/runtime-contract-demo.html is missing", failures)
    require(REFERENCE.exists(), "docs/reference/guides/runtime-contract-demo.html is missing; run sync_docs_reference.py", failures)
    if GUIDE.exists():
        text = GUIDE.read_text(encoding="utf-8")
        for term in (
            "triage-nine-phase",
            "gate_1",
            "gate_2",
            "LangGraph",
            "CrewAI",
            "AutoGen",
            "Semantic Kernel",
            "scripts/check_runtime_examples.py",
            "scripts/check_graph_studio_contract.py",
        ):
            require(term in text, f"runtime contract demo must mention {term}", failures)
        require(text.count("data-step=") >= 6, "runtime contract demo must include at least six interactive steps", failures)
        require("addEventListener" in text, "runtime contract demo must include interactive JavaScript", failures)
    if failures:
        for failure in failures:
            print(failure)
        return 1
    print("Runtime contract demo checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
