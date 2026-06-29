#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def stage_payload(target: Path) -> None:
    for name in ("install.sh", "VERSION"):
        shutil.copyfile(ROOT / name, target / name)
    shutil.copytree(ROOT / "dist", target / "dist")


def run_install(target: Path, *args: str) -> str:
    completed = subprocess.run(
        ["bash", "install.sh", *args],
        cwd=target,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=True,
    )
    return completed.stdout


def assert_contains(text: str, expected: str) -> None:
    if expected not in text:
        raise AssertionError(f"expected output to contain {expected!r}; got:\n{text}")


def assert_exists(path: Path) -> None:
    if not path.exists():
        raise AssertionError(f"expected missing path: {path}")


def assert_missing(path: Path) -> None:
    if path.exists():
        raise AssertionError(f"unexpected path exists: {path}")


def assert_not_contains(path: Path, forbidden: str) -> None:
    if forbidden in path.read_text(encoding="utf-8"):
        raise AssertionError(f"{path} unexpectedly contains {forbidden!r}")


def write_consumer_repo(path: Path) -> None:
    (path / "README.md").write_text("# Consumer App\n", encoding="utf-8")
    (path / "pyproject.toml").write_text("[project]\nname = \"consumer-app\"\nversion = \"0.1.0\"\n", encoding="utf-8")


def check_context_only_dry_run() -> None:
    with tempfile.TemporaryDirectory(prefix="nunneri-consumer-dry-run-") as tmp:
        target = Path(tmp)
        stage_payload(target)
        write_consumer_repo(target)
        output = run_install(target, "--provider", "claude", "--project", "--context-only", "--dry-run")
        assert_contains(output, "Would install CLAUDE.md (root-context)")
        assert_contains(output, "Would write version metadata to .ai-assets-version")
        assert_missing(target / "CLAUDE.md")
        assert_missing(target / ".ai-assets-version")
        assert_missing(target / ".claude")


def check_context_only_force() -> None:
    with tempfile.TemporaryDirectory(prefix="nunneri-consumer-context-") as tmp:
        target = Path(tmp)
        stage_payload(target)
        write_consumer_repo(target)
        output = run_install(target, "--provider", "claude", "--project", "--context-only", "--force", "--skip-build")
        assert_contains(output, "Installed CLAUDE.md into project root")
        assert_exists(target / "CLAUDE.md")
        assert_exists(target / ".ai-assets-version")
        assert_missing(target / ".claude")
        assert_not_contains(target / "CLAUDE.md", "## Codex")
        assert_not_contains(target / "CLAUDE.md", "## Gemini")


def check_full_provider_install() -> None:
    with tempfile.TemporaryDirectory(prefix="nunneri-consumer-full-") as tmp:
        target = Path(tmp)
        stage_payload(target)
        write_consumer_repo(target)
        output = run_install(target, "--provider", "claude", "--project", "--force", "--skip-build")
        assert_contains(output, "Installed CLAUDE.md into project root")
        assert_exists(target / "CLAUDE.md")
        assert_exists(target / ".claude" / "agents" / "python-triage-specialist.md")
        assert_exists(target / ".claude" / "commands" / "triage.md")
        assert_exists(target / ".claude" / ".ai-assets-version")


def check_langgraph_runtime_install() -> None:
    with tempfile.TemporaryDirectory(prefix="nunneri-consumer-langgraph-") as tmp:
        target = Path(tmp)
        stage_payload(target)
        write_consumer_repo(target)
        output = run_install(target, "--runtime", "langgraph", "--project", "--force", "--skip-build")
        assert_contains(output, "Summary for langgraph runtime")
        assert_exists(target / ".langgraph" / "graphs" / "triage-nine-phase.json")
        assert_exists(target / ".langgraph" / "manifests" / "agents" / "python-triage-specialist.json")
        assert_exists(target / ".langgraph" / "context" / "repo-agent-instructions.json")
        assert_exists(target / ".langgraph" / ".ai-assets-version")


def check_neutral_runtime_contract_install() -> None:
    with tempfile.TemporaryDirectory(prefix="nunneri-consumer-runtime-contract-") as tmp:
        target = Path(tmp)
        stage_payload(target)
        write_consumer_repo(target)
        output = run_install(target, "--runtime", "nunneri-runtime", "--project", "--force", "--skip-build")
        assert_contains(output, "Summary for nunneri-runtime runtime")
        assert_exists(target / ".nunneri-runtime" / "contract.json")
        assert_exists(target / ".nunneri-runtime" / "workflows" / "triage-nine-phase.json")
        assert_exists(target / ".nunneri-runtime" / "context" / "repo-agent-instructions.json")
        assert_exists(target / ".nunneri-runtime" / ".ai-assets-version")


def check_existing_context_skip() -> None:
    with tempfile.TemporaryDirectory(prefix="nunneri-consumer-skip-") as tmp:
        target = Path(tmp)
        stage_payload(target)
        write_consumer_repo(target)
        (target / "CLAUDE.md").write_text("# Existing Claude Context\n", encoding="utf-8")
        output = run_install(target, "--provider", "claude", "--project", "--context-only", "--skip-build")
        assert_contains(output, "Skip existing CLAUDE.md")
        if (target / "CLAUDE.md").read_text(encoding="utf-8") != "# Existing Claude Context\n":
            raise AssertionError("existing CLAUDE.md was overwritten without --force")


def main() -> int:
    check_context_only_dry_run()
    check_context_only_force()
    check_full_provider_install()
    check_neutral_runtime_contract_install()
    check_langgraph_runtime_install()
    check_existing_context_skip()
    print("Consumer install smoke checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
