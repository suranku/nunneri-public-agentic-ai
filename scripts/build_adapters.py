#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROVIDERS = ("claude", "codex", "gemini", "open-source")
RUNTIMES = ("langgraph",)
PROVIDER_OVERRIDE_HEADINGS = {
    "claude": "### Claude Code",
    "codex": "### Codex",
    "gemini": "### Gemini",
}

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


def structured_override_block(body: str) -> str:
    start = body.find("```yaml\n")
    if start == -1:
        return ""
    start += len("```yaml\n")
    end = body.find("\n```", start)
    if end == -1:
        return ""
    return body[start:end].strip()


def provider_context_body(body: str, provider: str) -> str:
    body = body.replace("# Repository Agent Instructions\n\n", "", 1)
    body = body.replace("> Generated from `assets/context/repo-agent-instructions.md`. Customize a repo-local copy when installing into a consuming repository.\n\n", "", 1)
    section = "\n## Provider-Specific Instruction Overrides\n"
    structured = "\n## Structured Override Registry\n"
    section_start = body.find(section)
    structured_start = body.find(structured)
    if section_start == -1 or structured_start == -1 or structured_start < section_start:
        return body
    common = body[:section_start].rstrip()
    provider_area = body[section_start:structured_start]
    structured_body = body[structured_start:].lstrip()
    heading = PROVIDER_OVERRIDE_HEADINGS[provider]
    provider_start = provider_area.find(heading)
    if provider_start == -1:
        selected = ""
    else:
        next_start = provider_area.find("\n### ", provider_start + 1)
        selected = provider_area[provider_start: next_start if next_start != -1 else len(provider_area)].strip()
    provider_section = f"## Provider-Specific Instruction Overrides\n\n{selected}" if selected else "## Provider-Specific Instruction Overrides\n\n- No provider-specific overrides are defined."
    return f"{common}\n\n{provider_section}\n\n{structured_body}".strip()


def build_context() -> None:
    src = ROOT / "assets/context/repo-agent-instructions.md"
    data, body = frontmatter_and_body(src)
    provider_files = {
        "claude": ("CLAUDE.md", "Claude Repository Context"),
        "codex": ("AGENTS.md", "Codex Repository Context"),
        "gemini": ("GEMINI.md", "Gemini Repository Context"),
    }
    for provider, (filename, title) in provider_files.items():
        provider_body = provider_context_body(body, provider)
        content = f"""# {title}

> Generated from `{src.relative_to(ROOT)}`. Edit the canonical context template, then rebuild adapters.

{provider_body}
"""
        write(ROOT / f"dist/{provider}" / filename, content)
    payload = {
        "name": data["name"],
        "description": data["description"],
        "category": data.get("category", "context"),
        "source": str(src.relative_to(ROOT)),
        "body": body,
        "structured_overrides": structured_override_block(body),
    }
    write(ROOT / "dist/open-source/manifests/context/repo-agent-instructions.json", json.dumps(payload, indent=2))
    write(ROOT / "dist/langgraph/context/repo-agent-instructions.json", json.dumps({**payload, "runtime": "langgraph", "injection_stage": "pre_dispatch"}, indent=2))


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
    build_context()
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
    write(ROOT / "dist/open-source/AGENT_MANIFEST.md", "# Open Source Manifest\n\nGenerated from provider-neutral assets. Context metadata is available in `manifests/context/repo-agent-instructions.json`.")
    write(ROOT / "dist/langgraph/LANGGRAPH.md", "# LangGraph Runtime\n\nGenerated graph and runtime manifests from provider-neutral assets. LangGraph is an orchestration runtime, not a model provider. Pre-dispatch context is available in `context/repo-agent-instructions.json`.")
    print("Built provider adapters: claude, codex, gemini, open-source; runtime adapters: langgraph")


if __name__ == "__main__":
    build()
