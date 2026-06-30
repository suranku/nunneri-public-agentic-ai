#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_ROOT = ROOT / "dist/nunneri-runtime"
SCHEMA = ROOT / "schemas/nunneri-runtime-contract.schema.json"
ALLOWED_KINDS = {"agent", "command", "workflow", "context"}
ALLOWED_NODE_TYPES = {"agent", "command", "workflow", "work", "router", "human_approval", "terminal"}
RUNTIME_SMOKE_PATHS = [
    "dist/crewai/agents",
    "dist/crewai/tasks",
    "dist/crewai/flows",
    "dist/autogen/agents",
    "dist/autogen/tasks",
    "dist/autogen/workflows",
    "dist/semantic-kernel/agents",
    "dist/semantic-kernel/functions",
    "dist/semantic-kernel/orchestrations",
]


def generated_name(src: Path) -> str:
    text = src.read_text(encoding="utf-8")
    end = text.find("\n---", 4)
    if not text.startswith("---\n") or end == -1:
        raise ValueError(f"{src}: missing frontmatter")
    for line in text[4:end].splitlines():
        if line.startswith("name:"):
            return line.split(":", 1)[1].strip()
    raise ValueError(f"{src}: missing name frontmatter")


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def load_json(path: Path, failures: list[str]) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - validation script should report all JSON failures.
        failures.append(f"{path.relative_to(ROOT)} is not valid JSON: {exc}")
        return {}


def validate_contract(path: Path, failures: list[str]) -> dict:
    payload = load_json(path, failures)
    if not payload:
        return {}
    rel = path.relative_to(ROOT)
    required = [
        "contract_version",
        "name",
        "kind",
        "source",
        "description",
        "inputs",
        "agents",
        "commands",
        "nodes",
        "edges",
        "context",
        "runtime_hints",
    ]
    for key in required:
        require(key in payload, f"{rel} missing required field {key}", failures)
    require(payload.get("contract_version") == "1.0", f"{rel} contract_version must be 1.0", failures)
    require(payload.get("kind") in ALLOWED_KINDS, f"{rel} has invalid kind {payload.get('kind')}", failures)
    require(isinstance(payload.get("nodes"), list), f"{rel} nodes must be a list", failures)
    require(isinstance(payload.get("edges"), list), f"{rel} edges must be a list", failures)
    for node in payload.get("nodes", []):
        node_type = node.get("type")
        require(node.get("id") is not None, f"{rel} has a node without id", failures)
        require(node_type in ALLOWED_NODE_TYPES, f"{rel} has invalid node type {node_type}", failures)
        if node_type == "human_approval":
            approval = node.get("approval", {})
            require(approval.get("required") is True, f"{rel} approval node {node.get('id')} must require approval", failures)
            require(approval.get("actions") == ["approve", "reject"], f"{rel} approval node {node.get('id')} must allow approve/reject", failures)
            require(approval.get("on_reject") == "cancel", f"{rel} approval node {node.get('id')} must cancel on rejection", failures)
    for edge in payload.get("edges", []):
        require(edge.get("from") is not None and edge.get("to") is not None, f"{rel} has an edge without from/to", failures)
    return payload


def expected_exports(folder: str) -> list[str]:
    asset_root = ROOT / "assets" / folder
    if not asset_root.exists():
        return []
    return [generated_name(src) for src in sorted(asset_root.glob("**/*.md")) if src.name != "README.md"]


def main() -> int:
    failures: list[str] = []

    require(SCHEMA.exists(), "schemas/nunneri-runtime-contract.schema.json is missing", failures)
    require(CONTRACT_ROOT.is_dir(), "dist/nunneri-runtime is missing", failures)
    require((CONTRACT_ROOT / "contract.json").exists(), "dist/nunneri-runtime/contract.json is missing", failures)

    for folder in ("agents", "commands", "workflows"):
        for name in expected_exports(folder):
            path = CONTRACT_ROOT / folder / f"{name}.json"
            require(path.exists(), f"missing neutral {folder[:-1]} export: {path.relative_to(ROOT)}", failures)

    require((CONTRACT_ROOT / "context/repo-agent-instructions.json").exists(), "missing neutral context export", failures)

    for path in sorted(CONTRACT_ROOT.glob("*/*.json")):
        validate_contract(path, failures)

    triage_path = CONTRACT_ROOT / "workflows/triage-nine-phase.json"
    if triage_path.exists():
        triage = validate_contract(triage_path, failures)
        nodes = triage.get("nodes", [])
        require(len(nodes) == 9, f"triage-nine-phase must have exactly 9 nodes, found {len(nodes)}", failures)
        by_id = {node.get("id"): node for node in nodes}
        for gate_id in ("gate_1", "gate_2"):
            gate = by_id.get(gate_id, {})
            require(gate.get("type") == "human_approval", f"{gate_id} must be human_approval", failures)
            require(gate.get("approval", {}).get("on_reject") == "cancel", f"{gate_id} rejection policy must be cancel", failures)
            require(bool(gate.get("approval", {}).get("question")), f"{gate_id} must include an approval question", failures)
            require(
                bool(gate.get("approval", {}).get("required_context")),
                f"{gate_id} must include required approval context",
                failures,
            )
        classification = by_id.get("classification", {})
        require(
            bool(classification.get("classification_options")),
            "classification node must include classification_options",
            failures,
        )

    for path in RUNTIME_SMOKE_PATHS:
        full = ROOT / path
        require(full.is_dir(), f"{path} is missing", failures)
        if full.is_dir():
            require(any(full.glob("*.json")), f"{path} has no generated JSON files", failures)

    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("Runtime contract checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
