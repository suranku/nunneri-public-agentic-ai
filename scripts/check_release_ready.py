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
        "CHANGELOG.md",
        "RELEASE.md",
        "VERSION",
        ".github/PULL_REQUEST_TEMPLATE.md",
        ".github/labels.yml",
        ".github/workflows/release.yml",
        "examples/consumer-repo/README.md",
        "scripts/check_consumer_install.py",
        "scripts/check_user_setup_docs.py",
        "scripts/check_runtime_contract.py",
        "scripts/check_human_gates.py",
        "schemas/nunneri-runtime-contract.schema.json",
        "NUNNERI_RUNTIME_CONTRACT.md",
        "guides/end-user-langgraph-setup.md",
        "guides/end-user-setup-demo.html",
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
    print("Release readiness local checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
