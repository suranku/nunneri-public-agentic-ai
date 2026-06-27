#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def bump(version: str, part: str) -> str:
    major, minor, patch = [int(piece) for piece in version.split(".")]
    if part == "major":
        return f"{major + 1}.0.0"
    if part == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--major", action="store_true")
    group.add_argument("--minor", action="store_true")
    group.add_argument("--patch", action="store_true")
    args = parser.parse_args()
    part = "major" if args.major else "minor" if args.minor else "patch"
    version_path = ROOT / "VERSION"
    current = version_path.read_text(encoding="utf-8").strip()
    target = bump(current, part)
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    if f"## [{target}]" not in changelog:
        print(f"CHANGELOG.md must include ## [{target}] before release")
        return 1
    subprocess.check_call([sys.executable, "scripts/validate.py"], cwd=ROOT)
    subprocess.check_call([sys.executable, "scripts/build_adapters.py"], cwd=ROOT)
    version_path.write_text(target + "\n", encoding="utf-8")
    print(f"Prepared release {target}")
    print(f"Next, after approval: git tag v{target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
