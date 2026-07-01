#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--local-only", action="store_true")
    args = parser.parse_args()
    # args.local_only reserved for future remote-only gate differentiation
    required = [
        "LICENSE",
        "ARCHITECTURE.md",
        "DEFENSIVE_PUBLICATION.md",
        "CITATION.cff",
        "COMMERCIAL_LICENSE.md",
        "TRADEMARKS.md",
        "GOVERNANCE.md",
        "MAINTAINERS.md",
        "NOTICE.md",
        "ROADMAP.md",
        "SECURITY.md",
        "CONTRIBUTOR_LICENSE_AGREEMENT.md",
        "CHANGELOG.md",
        "RELEASE.md",
        "VERSION",
        ".github/PULL_REQUEST_TEMPLATE.md",
        ".github/labels.yml",
        ".github/workflows/release.yml",
        "examples/consumer-repo/README.md",
        "examples/runtime-contract-consumer/README.md",
        "examples/runtime-contract-consumer/consume_runtime_contract.py",
        "examples/crewai-runtime-runner/README.md",
        "examples/crewai-runtime-runner/run_crewai_contract.py",
        "scripts/check_consumer_install.py",
        "scripts/check_runtime_examples.py",
        "scripts/check_crewai_runtime_runner.py",
        "scripts/check_runtime_contract_demo.py",
        "scripts/check_graph_studio_contract.py",
        "scripts/check_graph_definition_api.py",
        "scripts/check_user_setup_docs.py",
        "scripts/check_runtime_contract.py",
        "scripts/check_human_gates.py",
        "schemas/nunneri-runtime-contract.schema.json",
        "NUNNERI_RUNTIME_CONTRACT.md",
        "guides/end-user-langgraph-setup.md",
        "guides/end-user-setup-demo.html",
        "guides/runtime-contract-demo.html",
        "scripts/package_release.py",
        "scripts/check_release_package.py",
    ]
    missing = [path for path in required if not (ROOT / path).exists()]
    if missing:
        for path in missing:
            print(f"missing release file: {path}")
        return 1
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    if "## [Unreleased]" not in changelog:
        print("CHANGELOG.md must contain ## [Unreleased]")
        return 1
    required_text = {
        "README.md": ["AGPLv3 Community Edition", "Commercial licensing"],
        "AI_ASSETS.md": ["AGPLv3 Community Edition", "COMMERCIAL_LICENSE.md", "DEFENSIVE_PUBLICATION.md"],
        "ARCHITECTURE.md": ["runtime-neutral", "Graph Studio", "MinIO"],
        "DEFENSIVE_PUBLICATION.md": ["Publication date", "Do not describe Nunneri as \"patent pending\"", "runtime-neutral control plane"],
        "CITATION.cff": ["Nunneri Public Agentic AI", "AGPL-3.0-only", "runtime contract"],
        "CONTRIBUTING.md": ["Contributor License Agreement", "commercial licensing"],
        "GOVERNANCE.md": ["Nunneri Core Team", "Runtime Contract Stewardship"],
        "ROADMAP.md": ["Community Edition", "Commercial and Enterprise Options"],
        "SECURITY.md": ["Reporting a Vulnerability", "provider keys"],
        "NUNNERI_RUNTIME_CONTRACT.md": ["ARCHITECTURE.md", "DEFENSIVE_PUBLICATION.md"],
        "docs/index.html": ["AGPLv3 Community Edition", "Commercial License", "Defensive Publication"],
    }
    for rel, needles in required_text.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                print(f"{rel} must mention {needle!r}")
                return 1
    forbidden_text = {
        "README.md": ["free forever", "fully open source"],
        "docs/index.html": ["Free Forever", "free forever", "fully open source"],
    }
    for rel, needles in forbidden_text.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle in text:
                print(f"{rel} contains outdated licensing phrase {needle!r}")
                return 1
    print("Release readiness local checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
