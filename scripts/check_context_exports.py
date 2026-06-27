#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "assets/context/repo-agent-instructions.md"
PROVIDER_FILES = [
    ("claude", ROOT / "dist/claude/CLAUDE.md", "### Claude Code", ["### Codex", "### Gemini"]),
    ("codex", ROOT / "dist/codex/AGENTS.md", "### Codex", ["### Claude Code", "### Gemini"]),
    ("gemini", ROOT / "dist/gemini/GEMINI.md", "### Gemini", ["### Claude Code", "### Codex"]),
]
REQUIRED_SECTIONS = [
    "## Repository Identity and Ownership",
    "## Golden Setup, Build, and Test Commands",
    "## Common Library and Source-Code Links",
    "## Known Issues and Recurring Failure Modes",
    "## DevOps and Environment Overrides",
    "## Agentic Workflow Overrides",
    "## Exception Handling and Escalation Rules",
    "## Skill Invocation Overrides",
    "## Agent Dispatch Rules Before Task Routing",
    "## Approval Gates and Release-Impact Rules",
    "## Provider-Specific Instruction Overrides",
    "## Structured Override Registry",
]
REQUIRED_KEYS = [
    "known_issues:",
    "devops_overrides:",
    "library_sources:",
    "workflow_overrides:",
    "exceptions:",
    "skill_overrides:",
    "dispatch_overrides:",
    "provider_overrides:",
    "approval_gates:",
]


def structured_yaml(text: str) -> str:
    start = text.find("```yaml\n")
    if start == -1:
        return ""
    start += len("```yaml\n")
    end = text.find("\n```", start)
    if end == -1:
        return ""
    return text[start:end]


def main() -> int:
    failures: list[str] = []
    if not TEMPLATE.exists():
        failures.append("assets/context/repo-agent-instructions.md is missing")
    else:
        text = TEMPLATE.read_text(encoding="utf-8")
        for section in REQUIRED_SECTIONS:
            if section not in text:
                failures.append(f"{TEMPLATE}: missing section {section}")
        yaml = structured_yaml(text)
        if not yaml:
            failures.append(f"{TEMPLATE}: missing structured YAML override block")
        for key in REQUIRED_KEYS:
            if key not in yaml:
                failures.append(f"{TEMPLATE}: missing YAML key {key}")
    for provider, path, expected_heading, forbidden_headings in PROVIDER_FILES:
        if not path.exists():
            failures.append(f"{path}: missing generated provider context")
            continue
        text = path.read_text(encoding="utf-8")
        for section in REQUIRED_SECTIONS:
            if section not in text:
                failures.append(f"{path}: missing section {section}")
        if not structured_yaml(text):
            failures.append(f"{path}: missing structured YAML override block")
        if expected_heading not in text:
            failures.append(f"{path}: missing provider-specific heading {expected_heading}")
        for heading in forbidden_headings:
            if heading in text:
                failures.append(f"{path}: leaked provider-specific heading {heading}")
        if provider != "claude" and "`agent team`" in text:
            failures.append(f"{path}: leaked Claude-only trigger phrase `agent team`")
    open_source = ROOT / "dist/open-source/manifests/context/repo-agent-instructions.json"
    langgraph = ROOT / "dist/langgraph/context/repo-agent-instructions.json"
    for path in (open_source, langgraph):
        if not path.exists():
            failures.append(f"{path}: missing generated context manifest")
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        if not data.get("structured_overrides"):
            failures.append(f"{path}: missing structured_overrides")
    if langgraph.exists():
        data = json.loads(langgraph.read_text(encoding="utf-8"))
        if data.get("injection_stage") != "pre_dispatch":
            failures.append(f"{langgraph}: injection_stage must be pre_dispatch")
    installer = ROOT / "install.sh"
    install_text = installer.read_text(encoding="utf-8")
    for snippet in ("--context-only", "--no-context", "--dry-run", "Dry run: skipping adapter build and writing no files", 'dest="$rel"', 'version_file=".ai-assets-version"', "Would install", "root context files=", "provider directory files="):
        if snippet not in install_text:
            failures.append(f"{installer}: missing context install contract snippet {snippet}")
    if failures:
        for failure in failures:
            print(failure)
        return 1
    print("Context export checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
