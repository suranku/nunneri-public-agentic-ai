#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    raise AssertionError(message)


def require(path: Path) -> str:
    if not path.exists():
        fail(f"missing required setup doc artifact: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def main() -> int:
    guide = require(ROOT / "guides" / "end-user-langgraph-setup.md")
    demo = require(ROOT / "guides" / "end-user-setup-demo.html")
    reference_guide = require(ROOT / "docs" / "reference" / "guides" / "end-user-langgraph-setup.md")
    reference_demo = require(ROOT / "docs" / "reference" / "guides" / "end-user-setup-demo.html")
    portal = require(ROOT / "docs" / "index.html")
    manifest_text = require(ROOT / "docs" / "assets" / "manifest.json")
    manifest = json.loads(manifest_text)

    for snippet in (
        "NUNNERI_RUNTIME=langgraph",
        "NUNNERI_STATE_STORE=sqlite",
        "NUNNERI_TRACE_MODE=otel|langsmith|none",
        "LANGSMITH_API_KEY",
        ".nunneri/langgraph/state.sqlite",
        "OpenTelemetry",
        "LangSmith",
    ):
        if snippet not in guide:
            fail(f"setup guide missing snippet: {snippet}")

    for snippet in (
        "Select Provider",
        "Preview Context",
        "Install Assets",
        "Export Runtime",
        "Persist State",
        "Trace and Monitor",
        "Validate Setup",
        "NUNNERI_TRACE_MODE=otel",
    ):
        if snippet not in demo:
            fail(f"setup demo missing step or config snippet: {snippet}")

    if "End-User Setup" not in portal or "end-user-setup-demo.html" not in portal:
        fail("portal does not link the end-user setup demo")

    guide_names = {item.get("name") for item in manifest.get("guides", [])}
    if "end-user-setup-demo.html" not in guide_names:
        fail("portal manifest does not include end-user-setup-demo.html")

    if guide != reference_guide:
        fail("reference setup guide is out of sync")
    if "../../index.html" not in reference_demo:
        fail("reference setup demo link rewrite is missing")

    print("End-user setup docs checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
