#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROVIDERS = ("claude", "codex", "gemini", "open-source")
RUNTIMES = ("langgraph",)

TRIAGE_NINE_PHASE_GRAPH = {
    "name": "triage-nine-phase",
    "description": "Nine Phase Triage Workflow",
    "runtime": "langgraph",
    "source": "assets/workflows/triage-nine-phase.md",
    "nodes": [
        {"id": "intake", "label": "Intake", "phase": 1, "type": "work"},
        {"id": "context_load", "label": "Context Load", "phase": 2, "type": "work"},
        {"id": "classification", "label": "Classification", "phase": 3, "type": "work"},
        {"id": "evidence_collection", "label": "Evidence Collection", "phase": 4, "type": "work"},
        {"id": "root_cause_analysis", "label": "Root Cause Analysis", "phase": 5, "type": "work"},
        {"id": "gate_1", "label": "Gate 1: RCA and Fix Plan Approval", "phase": 6, "type": "human_approval", "approval_checkpoint": True},
        {"id": "test_first_fix", "label": "Test-First Fix", "phase": 7, "type": "work"},
        {"id": "validation", "label": "Validation", "phase": 8, "type": "work"},
        {"id": "gate_2", "label": "Gate 2: Summary and Release Impact", "phase": 9, "type": "human_approval", "approval_checkpoint": True},
    ],
    "edges": [
        {"from": "intake", "to": "context_load"},
        {"from": "context_load", "to": "classification"},
        {"from": "classification", "to": "evidence_collection"},
        {"from": "evidence_collection", "to": "root_cause_analysis"},
        {"from": "root_cause_analysis", "to": "gate_1"},
        {"from": "gate_1", "to": "test_first_fix", "condition": "approved"},
        {"from": "test_first_fix", "to": "validation"},
        {"from": "validation", "to": "gate_2"},
    ],
    "post_triage_actions": ["commit", "push", "pull_request", "release_tag", "publish"],
}


def frontmatter_and_body(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    end = text.find("\n---", 4)
    data: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" in line and not line.startswith(" "):
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip()
    return data, text[end + 4:].strip()


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")


def reset_dist() -> None:
    for target_name in PROVIDERS + RUNTIMES:
        target = ROOT / "dist" / target_name
        if target.exists():
            shutil.rmtree(target)
        target.mkdir(parents=True, exist_ok=True)


def build_claude_agent(src: Path, data: dict[str, str], body: str) -> None:
    content = f"""---
name: {data['name']}
description: {data['description']}
model: claude-sonnet-4-6
tools: Read, Grep, Glob, Bash, Write, Edit
---

> Generated from `{src.relative_to(ROOT)}`. Edit the canonical asset, not this file.

{body}
"""
    write(ROOT / "dist/claude/agents" / src.name, content)


def build_command(src: Path, data: dict[str, str], body: str) -> None:
    for provider in PROVIDERS:
        suffix = ".md" if provider != "open-source" else ".json"
        if provider == "open-source":
            payload = {
                "name": data["name"],
                "description": data["description"],
                "category": data.get("category", "command"),
                "source": str(src.relative_to(ROOT)),
                "body": body,
            }
            write(ROOT / "dist/open-source/manifests/commands" / f"{data['name']}.json", json.dumps(payload, indent=2))
        else:
            target_dir = "commands" if provider == "claude" else "workflows"
            write(ROOT / f"dist/{provider}/{target_dir}" / f"{data['name']}{suffix}", f"> Generated from `{src.relative_to(ROOT)}`.\n\n{body}")


def build_langgraph_agent(src: Path, data: dict[str, str], body: str) -> None:
    payload = {
        "name": data["name"],
        "description": data["description"],
        "category": data.get("category"),
        "runtime": "langgraph",
        "source": str(src.relative_to(ROOT)),
        "node": {
            "id": data["name"].replace("-", "_"),
            "type": "agent",
            "body": body,
        },
    }
    write(ROOT / "dist/langgraph/manifests/agents" / f"{data['name']}.json", json.dumps(payload, indent=2))


def build_langgraph_command(src: Path, data: dict[str, str], body: str) -> None:
    payload = {
        "name": data["name"],
        "description": data["description"],
        "category": data.get("category", "command"),
        "runtime": "langgraph",
        "source": str(src.relative_to(ROOT)),
        "entrypoint": {
            "id": data["name"].replace("-", "_"),
            "type": "command",
            "body": body,
        },
    }
    write(ROOT / "dist/langgraph/manifests/commands" / f"{data['name']}.json", json.dumps(payload, indent=2))


def build_langgraph_workflow(src: Path, data: dict[str, str], body: str) -> None:
    if data["name"] == "triage-nine-phase":
        payload = TRIAGE_NINE_PHASE_GRAPH
        payload = {**payload, "body": body}
    else:
        payload = {
            "name": data["name"],
            "description": data["description"],
            "runtime": "langgraph",
            "source": str(src.relative_to(ROOT)),
            "nodes": [{"id": data["name"].replace("-", "_"), "label": data["description"], "type": "workflow"}],
            "edges": [],
            "body": body,
        }
    write(ROOT / "dist/langgraph/graphs" / f"{data['name']}.json", json.dumps(payload, indent=2))


def copy_skill(src: Path) -> None:
    relative = src.parent.name
    for provider in PROVIDERS:
        if provider == "open-source":
            write(ROOT / "dist/open-source/workflows" / f"{relative}.md", f"> Generated from `{src.relative_to(ROOT)}`.\n\n{src.read_text(encoding='utf-8')}")
        else:
            write(ROOT / f"dist/{provider}/skills/{relative}/SKILL.md", f"> Generated from `{src.relative_to(ROOT)}`.\n\n{src.read_text(encoding='utf-8')}")


def build() -> None:
    reset_dist()
    for src in sorted(path for path in (ROOT / "assets/agents").glob("**/*.md") if path.name != "README.md"):
        data, body = frontmatter_and_body(src)
        build_claude_agent(src, data, body)
        for provider in ("codex", "gemini"):
            write(ROOT / f"dist/{provider}/prompts/agents" / src.name, f"> Generated from `{src.relative_to(ROOT)}`.\n\n{body}")
        write(ROOT / "dist/open-source/manifests/agents" / f"{data['name']}.json", json.dumps({"name": data["name"], "description": data["description"], "category": data.get("category"), "source": str(src.relative_to(ROOT)), "body": body}, indent=2))
        build_langgraph_agent(src, data, body)
    for src in sorted(path for path in (ROOT / "assets/commands").glob("**/*.md") if path.name != "README.md"):
        data, body = frontmatter_and_body(src)
        build_command(src, data, body)
        build_langgraph_command(src, data, body)
    for src in sorted((ROOT / "assets/skills").glob("*/SKILL.md")):
        copy_skill(src)
    for src in sorted((ROOT / "assets/workflows").glob("*.md")):
        if src.name == "README.md":
            for provider in PROVIDERS:
                write(ROOT / f"dist/{provider}/workflows" / src.name, f"> Generated from `{src.relative_to(ROOT)}`.\n\n{src.read_text(encoding='utf-8')}")
            continue
        data, body = frontmatter_and_body(src)
        build_langgraph_workflow(src, data, body)
        for provider in PROVIDERS:
            folder = "workflows" if provider != "open-source" else "workflows"
            write(ROOT / f"dist/{provider}/{folder}" / src.name, f"> Generated from `{src.relative_to(ROOT)}`.\n\n{src.read_text(encoding='utf-8')}")
    write(ROOT / "dist/claude/CLAUDE.md", "# Claude Context\n\nGenerated from provider-neutral assets. Use `AI_ASSETS.md` for canonical rules.")
    write(ROOT / "dist/codex/AGENTS.md", "# Codex Context\n\nGenerated from provider-neutral assets. Use `AI_ASSETS.md` for canonical rules.")
    write(ROOT / "dist/gemini/GEMINI.md", "# Gemini Context\n\nGenerated from provider-neutral assets. Use `AI_ASSETS.md` for canonical rules.")
    write(ROOT / "dist/open-source/AGENT_MANIFEST.md", "# Open Source Manifest\n\nGenerated from provider-neutral assets.")
    write(ROOT / "dist/langgraph/LANGGRAPH.md", "# LangGraph Runtime\n\nGenerated graph and runtime manifests from provider-neutral assets. LangGraph is an orchestration runtime, not a model provider.")
    print("Built provider adapters: claude, codex, gemini, open-source; runtime adapters: langgraph")


if __name__ == "__main__":
    build()
