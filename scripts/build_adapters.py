#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROVIDERS = ("claude", "codex", "gemini", "open-source")
RUNTIMES = ("nunneri-runtime", "langgraph", "crewai", "autogen", "semantic-kernel")
CONTRACT_VERSION = "1.0"
PROVIDER_OVERRIDE_HEADINGS = {
    "claude": "### Claude Code",
    "codex": "### Codex",
    "gemini": "### Gemini",
}

TRIAGE_NINE_PHASE_CONTRACT = {
    "contract_version": CONTRACT_VERSION,
    "name": "triage-nine-phase",
    "kind": "workflow",
    "description": "Nine Phase Triage Workflow",
    "source": "assets/workflows/triage-nine-phase.md",
    "inputs": [],
    "agents": [],
    "commands": [],
    "nodes": [
        {"id": "intake", "label": "Intake", "phase": 1, "type": "work", "prompt": ""},
        {"id": "context_load", "label": "Context Load", "phase": 2, "type": "work", "prompt": ""},
        {"id": "classification", "label": "Classification", "phase": 3, "type": "work", "prompt": ""},
        {"id": "evidence_collection", "label": "Evidence Collection", "phase": 4, "type": "work", "prompt": ""},
        {"id": "root_cause_analysis", "label": "Root Cause Analysis", "phase": 5, "type": "work", "prompt": ""},
        {
            "id": "gate_1",
            "label": "Gate 1: RCA and Fix Plan Approval",
            "phase": 6,
            "type": "human_approval",
            "prompt": "",
            "approval": {"required": True, "actions": ["approve", "reject"], "on_reject": "cancel"},
        },
        {"id": "test_first_fix", "label": "Test-First Fix", "phase": 7, "type": "work", "prompt": ""},
        {"id": "validation", "label": "Validation", "phase": 8, "type": "work", "prompt": ""},
        {
            "id": "gate_2",
            "label": "Gate 2: Summary and Release Impact",
            "phase": 9,
            "type": "human_approval",
            "prompt": "",
            "approval": {"required": True, "actions": ["approve", "reject"], "on_reject": "cancel"},
        },
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
    "context": {"injection_stage": "pre_dispatch", "source": "assets/context/repo-agent-instructions.md"},
    "runtime_hints": {"stateful": True, "human_in_loop": True, "observability": ["events", "runs", "nodes"]},
}


def frontmatter_and_body(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    end = text.find("\n---", 4)
    if end == -1:
        raise ValueError(f"{path}: unterminated YAML frontmatter")
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
    structured = structured_override_block(body)
    payload = {
        "name": data["name"],
        "description": data["description"],
        "category": data.get("category", "context"),
        "source": str(src.relative_to(ROOT)),
        "body": body,
        "structured_overrides": structured,
    }
    write(ROOT / "dist/open-source/manifests/context/repo-agent-instructions.json", json.dumps(payload, indent=2))
    write(ROOT / "dist/langgraph/context/repo-agent-instructions.json", json.dumps({**payload, "runtime": "langgraph", "injection_stage": "pre_dispatch"}, indent=2))
    neutral = build_neutral_context(src, data, body, structured)
    write(ROOT / "dist/crewai/context/repo-agent-instructions.json", json.dumps({**neutral, "runtime": "crewai"}, indent=2))
    write(ROOT / "dist/autogen/context/repo-agent-instructions.json", json.dumps({**neutral, "runtime": "autogen"}, indent=2))
    write(ROOT / "dist/semantic-kernel/context/repo-agent-instructions.json", json.dumps({**neutral, "runtime": "semantic-kernel"}, indent=2))


def reset_dist() -> None:
    for target_name in PROVIDERS + RUNTIMES:
        target = ROOT / "dist" / target_name
        if target.exists():
            shutil.rmtree(target)
        target.mkdir(parents=True, exist_ok=True)


def neutral_base(src: Path, data: dict[str, str], body: str, kind: str) -> dict:
    return {
        "contract_version": CONTRACT_VERSION,
        "name": data["name"],
        "kind": kind,
        "source": str(src.relative_to(ROOT)),
        "description": data["description"],
        "inputs": [],
        "agents": [],
        "commands": [],
        "nodes": [],
        "edges": [],
        "context": {
            "injection_stage": "pre_dispatch",
            "source": "assets/context/repo-agent-instructions.md",
        },
        "runtime_hints": {
            "stateful": True,
            "human_in_loop": "approval" in body.lower() or "gate" in body.lower(),
            "observability": ["events", "runs", "nodes"],
        },
        "body": body,
    }


def write_neutral_contract(payload: dict) -> None:
    folder = {
        "agent": "agents",
        "command": "commands",
        "workflow": "workflows",
        "context": "context",
    }[payload["kind"]]
    write(ROOT / f"dist/nunneri-runtime/{folder}" / f"{payload['name']}.json", json.dumps(payload, indent=2))


def build_neutral_agent(src: Path, data: dict[str, str], body: str) -> dict:
    payload = neutral_base(src, data, body, "agent")
    payload["category"] = data.get("category")
    payload["nodes"] = [{
        "id": data["name"].replace("-", "_"),
        "label": data["name"],
        "type": "agent",
        "prompt": body,
    }]
    write_neutral_contract(payload)
    return payload


def build_neutral_command(src: Path, data: dict[str, str], body: str) -> dict:
    payload = neutral_base(src, data, body, "command")
    payload["category"] = data.get("category", "command")
    payload["commands"] = [data["name"]]
    payload["nodes"] = [{
        "id": data["name"].replace("-", "_"),
        "label": data["name"],
        "type": "command",
        "prompt": body,
    }]
    write_neutral_contract(payload)
    return payload


def build_neutral_workflow(src: Path, data: dict[str, str], body: str) -> dict:
    if data["name"] == "triage-nine-phase":
        payload = {**TRIAGE_NINE_PHASE_CONTRACT, "body": body}
    else:
        payload = neutral_base(src, data, body, "workflow")
        payload["nodes"] = [{
            "id": data["name"].replace("-", "_"),
            "label": data["description"],
            "type": "workflow",
            "prompt": body,
        }]
    write_neutral_contract(payload)
    return payload


def build_runtime_contract_index(agent_names: list[str], command_names: list[str], workflow_names: list[str]) -> None:
    payload = {
        "contract_version": CONTRACT_VERSION,
        "name": "nunneri-runtime-contract",
        "kind": "runtime_contract_index",
        "description": "Provider- and framework-neutral Nunneri runtime export index.",
        "generated_from": "assets",
        "providers": list(PROVIDERS),
        "runtimes": ["nunneri-runtime", "langgraph", "crewai", "autogen", "semantic-kernel"],
        "folders": {
            "agents": "agents",
            "commands": "commands",
            "workflows": "workflows",
            "context": "context",
        },
        "node_types": ["agent", "command", "workflow", "work", "router", "human_approval", "terminal"],
        "exports": {
            "agents": [f"agents/{name}.json" for name in agent_names],
            "commands": [f"commands/{name}.json" for name in command_names],
            "workflows": [f"workflows/{name}.json" for name in workflow_names],
            "context": ["context/repo-agent-instructions.json"],
        },
    }
    write(ROOT / "dist/nunneri-runtime/contract.json", json.dumps(payload, indent=2))


def build_neutral_context(src: Path, data: dict[str, str], body: str, structured: str) -> dict:
    payload = {
        "contract_version": CONTRACT_VERSION,
        "name": data["name"],
        "kind": "context",
        "source": str(src.relative_to(ROOT)),
        "description": data["description"],
        "category": data.get("category", "context"),
        "inputs": [],
        "agents": [],
        "commands": [],
        "nodes": [],
        "edges": [],
        "context": {"injection_stage": "pre_dispatch", "source": str(src.relative_to(ROOT))},
        "runtime_hints": {"stateful": False, "human_in_loop": False, "observability": ["events"]},
        "body": body,
        "structured_overrides": structured,
    }
    write_neutral_contract(payload)
    return payload


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


def build_langgraph_agent(contract: dict) -> None:
    node = contract["nodes"][0]
    payload = {
        "name": contract["name"],
        "description": contract["description"],
        "category": contract.get("category"),
        "runtime": "langgraph",
        "source": contract["source"],
        "contract_source": f"dist/nunneri-runtime/agents/{contract['name']}.json",
        "node": {
            "id": node["id"],
            "type": "agent",
            "body": node["prompt"],
        },
    }
    write(ROOT / "dist/langgraph/manifests/agents" / f"{contract['name']}.json", json.dumps(payload, indent=2))


def build_langgraph_command(contract: dict) -> None:
    node = contract["nodes"][0]
    payload = {
        "name": contract["name"],
        "description": contract["description"],
        "category": contract.get("category", "command"),
        "runtime": "langgraph",
        "source": contract["source"],
        "contract_source": f"dist/nunneri-runtime/commands/{contract['name']}.json",
        "entrypoint": {
            "id": node["id"],
            "type": "command",
            "body": node["prompt"],
        },
    }
    write(ROOT / "dist/langgraph/manifests/commands" / f"{contract['name']}.json", json.dumps(payload, indent=2))


def build_langgraph_workflow(contract: dict) -> None:
    nodes = []
    for node in contract["nodes"]:
        out = {k: v for k, v in node.items() if k not in {"prompt", "approval"}}
        if node.get("type") == "human_approval":
            out["approval_checkpoint"] = True
            out["approval"] = node.get("approval", {})
        nodes.append(out)
    payload = {
        "name": contract["name"],
        "description": contract["description"],
        "runtime": "langgraph",
        "source": contract["source"],
        "contract_source": f"dist/nunneri-runtime/workflows/{contract['name']}.json",
        "nodes": nodes,
        "edges": contract["edges"],
        "post_triage_actions": contract.get("post_triage_actions", []),
        "body": contract["body"],
    }
    write(ROOT / "dist/langgraph/graphs" / f"{contract['name']}.json", json.dumps(payload, indent=2))


def build_crewai_agent(contract: dict) -> None:
    node = contract["nodes"][0]
    payload = {
        "runtime": "crewai",
        "contract_source": f"dist/nunneri-runtime/agents/{contract['name']}.json",
        "agent": {
            "role": contract["name"],
            "goal": contract["description"],
            "backstory": node["prompt"],
            "allow_delegation": False,
        },
    }
    write(ROOT / "dist/crewai/agents" / f"{contract['name']}.json", json.dumps(payload, indent=2))


def build_crewai_command(contract: dict) -> None:
    payload = {
        "runtime": "crewai",
        "contract_source": f"dist/nunneri-runtime/commands/{contract['name']}.json",
        "task": {
            "description": contract["description"],
            "expected_output": "Nunneri command result with evidence, decision, and validation summary.",
            "prompt": contract["body"],
        },
    }
    write(ROOT / "dist/crewai/tasks" / f"{contract['name']}.json", json.dumps(payload, indent=2))


def build_crewai_workflow(contract: dict) -> None:
    payload = {
        "runtime": "crewai",
        "contract_source": f"dist/nunneri-runtime/workflows/{contract['name']}.json",
        "flow": {
            "name": contract["name"],
            "description": contract["description"],
            "steps": contract["nodes"],
            "edges": contract["edges"],
            "human_in_loop": [n["id"] for n in contract["nodes"] if n.get("type") == "human_approval"],
        },
    }
    write(ROOT / "dist/crewai/flows" / f"{contract['name']}.json", json.dumps(payload, indent=2))


def build_autogen_agent(contract: dict) -> None:
    node = contract["nodes"][0]
    payload = {
        "runtime": "autogen",
        "contract_source": f"dist/nunneri-runtime/agents/{contract['name']}.json",
        "agent": {
            "name": contract["name"].replace("-", "_"),
            "description": contract["description"],
            "system_message": node["prompt"],
        },
    }
    write(ROOT / "dist/autogen/agents" / f"{contract['name']}.json", json.dumps(payload, indent=2))


def build_autogen_command(contract: dict) -> None:
    payload = {
        "runtime": "autogen",
        "contract_source": f"dist/nunneri-runtime/commands/{contract['name']}.json",
        "agentchat_task": {
            "name": contract["name"],
            "description": contract["description"],
            "prompt": contract["body"],
        },
    }
    write(ROOT / "dist/autogen/tasks" / f"{contract['name']}.json", json.dumps(payload, indent=2))


def build_autogen_workflow(contract: dict) -> None:
    payload = {
        "runtime": "autogen",
        "contract_source": f"dist/nunneri-runtime/workflows/{contract['name']}.json",
        "group_orchestration": {
            "name": contract["name"],
            "participants": contract.get("agents", []),
            "nodes": contract["nodes"],
            "edges": contract["edges"],
            "human_approval_nodes": [n["id"] for n in contract["nodes"] if n.get("type") == "human_approval"],
        },
    }
    write(ROOT / "dist/autogen/workflows" / f"{contract['name']}.json", json.dumps(payload, indent=2))


def build_semantic_kernel_agent(contract: dict) -> None:
    node = contract["nodes"][0]
    payload = {
        "runtime": "semantic-kernel",
        "contract_source": f"dist/nunneri-runtime/agents/{contract['name']}.json",
        "agent": {
            "name": contract["name"].replace("-", "_"),
            "description": contract["description"],
            "instructions": node["prompt"],
        },
    }
    write(ROOT / "dist/semantic-kernel/agents" / f"{contract['name']}.json", json.dumps(payload, indent=2))


def build_semantic_kernel_command(contract: dict) -> None:
    payload = {
        "runtime": "semantic-kernel",
        "contract_source": f"dist/nunneri-runtime/commands/{contract['name']}.json",
        "function": {
            "name": contract["name"].replace("-", "_"),
            "description": contract["description"],
            "instructions": contract["body"],
        },
    }
    write(ROOT / "dist/semantic-kernel/functions" / f"{contract['name']}.json", json.dumps(payload, indent=2))


def build_semantic_kernel_workflow(contract: dict) -> None:
    payload = {
        "runtime": "semantic-kernel",
        "contract_source": f"dist/nunneri-runtime/workflows/{contract['name']}.json",
        "orchestration": {
            "name": contract["name"],
            "description": contract["description"],
            "steps": contract["nodes"],
            "edges": contract["edges"],
            "human_agent_interaction": [n["id"] for n in contract["nodes"] if n.get("type") == "human_approval"],
        },
    }
    write(ROOT / "dist/semantic-kernel/orchestrations" / f"{contract['name']}.json", json.dumps(payload, indent=2))


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
    agent_names: list[str] = []
    command_names: list[str] = []
    workflow_names: list[str] = []
    for src in sorted(path for path in (ROOT / "assets/agents").glob("**/*.md") if path.name != "README.md"):
        data, body = frontmatter_and_body(src)
        contract = build_neutral_agent(src, data, body)
        agent_names.append(contract["name"])
        build_claude_agent(src, data, body)
        for provider in ("codex", "gemini"):
            write(ROOT / f"dist/{provider}/prompts/agents" / src.name, f"> Generated from `{src.relative_to(ROOT)}`.\n\n{body}")
        write(ROOT / "dist/open-source/manifests/agents" / f"{data['name']}.json", json.dumps({"name": data["name"], "description": data["description"], "category": data.get("category"), "source": str(src.relative_to(ROOT)), "body": body}, indent=2))
        build_langgraph_agent(contract)
        build_crewai_agent(contract)
        build_autogen_agent(contract)
        build_semantic_kernel_agent(contract)
    for src in sorted(path for path in (ROOT / "assets/commands").glob("**/*.md") if path.name != "README.md"):
        data, body = frontmatter_and_body(src)
        contract = build_neutral_command(src, data, body)
        command_names.append(contract["name"])
        build_command(src, data, body)
        build_langgraph_command(contract)
        build_crewai_command(contract)
        build_autogen_command(contract)
        build_semantic_kernel_command(contract)
    for src in sorted((ROOT / "assets/skills").glob("*/SKILL.md")):
        copy_skill(src)
    for src in sorted((ROOT / "assets/workflows").glob("*.md")):
        if src.name == "README.md":
            for provider in PROVIDERS:
                write(ROOT / f"dist/{provider}/workflows" / src.name, f"> Generated from `{src.relative_to(ROOT)}`.\n\n{src.read_text(encoding='utf-8')}")
            continue
        data, body = frontmatter_and_body(src)
        contract = build_neutral_workflow(src, data, body)
        workflow_names.append(contract["name"])
        build_langgraph_workflow(contract)
        build_crewai_workflow(contract)
        build_autogen_workflow(contract)
        build_semantic_kernel_workflow(contract)
        for provider in PROVIDERS:
            folder = "workflows" if provider != "open-source" else "workflows"
            write(ROOT / f"dist/{provider}/{folder}" / src.name, f"> Generated from `{src.relative_to(ROOT)}`.\n\n{src.read_text(encoding='utf-8')}")
    build_runtime_contract_index(agent_names, command_names, workflow_names)
    write(ROOT / "dist/open-source/AGENT_MANIFEST.md", "# Open Source Manifest\n\nGenerated from provider-neutral assets. Context metadata is available in `manifests/context/repo-agent-instructions.json`.")
    write(ROOT / "dist/langgraph/LANGGRAPH.md", "# LangGraph Runtime\n\nGenerated graph and runtime manifests from provider-neutral assets. LangGraph is an orchestration runtime, not a model provider. Pre-dispatch context is available in `context/repo-agent-instructions.json`.")
    write(ROOT / "dist/nunneri-runtime/NUNNERI_RUNTIME.md", "# Nunneri Runtime Contract\n\nGenerated provider- and framework-neutral runtime contracts. Runtime adapters should consume these files instead of provider-specific exports.")
    write(ROOT / "dist/crewai/CREWAI.md", "# CrewAI Runtime Adapter\n\nGenerated CrewAI-compatible JSON manifests from `dist/nunneri-runtime/`. These are export contracts only; CrewAI SDK dependencies are optional for consumers.")
    write(ROOT / "dist/autogen/AUTOGEN.md", "# AutoGen Runtime Adapter\n\nGenerated Microsoft AutoGen-compatible JSON manifests from `dist/nunneri-runtime/`. These are export contracts only; AutoGen SDK dependencies are optional for consumers.")
    write(ROOT / "dist/semantic-kernel/SEMANTIC_KERNEL.md", "# Semantic Kernel Runtime Adapter\n\nGenerated Microsoft Semantic Kernel-compatible JSON manifests from `dist/nunneri-runtime/`. These are export contracts only; Semantic Kernel dependencies are optional for consumers.")
    print("Built provider adapters: claude, codex, gemini, open-source; runtime adapters: nunneri-runtime, langgraph, crewai, autogen, semantic-kernel")


if __name__ == "__main__":
    build()
