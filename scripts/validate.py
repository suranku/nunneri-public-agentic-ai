#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = ("name", "description")


def frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError("missing YAML frontmatter")
    end = text.find("\n---", 4)
    if end == -1:
        raise ValueError("unterminated YAML frontmatter")
    data: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" in line and not line.startswith(" "):
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip()
    return data


def check_placeholders(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    allowed = {"<TICKET-ID>", "<symptom>", "<INC-ID>", "<ENV>", "<error>", "<JSON>", "<path>", "<field>", "<table>", "<name>", "<domain>", "<report>", "<issue-number>", "<endpoint>", "<latest>"}
    findings = []
    for match in re.findall(r"<[^>\n]+>", text):
        if match not in allowed:
            findings.append(match)
    return findings


def main() -> int:
    failures: list[str] = []
    patterns = [
        "assets/agents/**/*.md",
        "assets/skills/*/SKILL.md",
        "assets/commands/**/*.md",
        "assets/workflows/**/*.md",
        "assets/context/**/*.md",
    ]
    files: list[Path] = []
    for pattern in patterns:
        files.extend(ROOT.glob(pattern))
    files = [path for path in files if path.name != "README.md"]
    for path in sorted(set(files)):
        try:
            data = frontmatter(path)
            for field in REQUIRED:
                if not data.get(field):
                    failures.append(f"{path}: missing required field {field}")
            if path.match("assets/agents/**/*.md") or path.match("assets/commands/**/*.md") or path.match("assets/context/**/*.md"):
                if not data.get("category"):
                    failures.append(f"{path}: missing required field category")
            placeholders = check_placeholders(path)
            for placeholder in placeholders:
                failures.append(f"{path}: unresolved placeholder {placeholder}")
        except Exception as exc:
            failures.append(f"{path}: {exc}")
    for required in ("AI_ASSETS.md", "README.md", "CONTRIBUTING.md", "RELEASE.md", "CHANGELOG.md", "VERSION"):
        if not (ROOT / required).exists():
            failures.append(f"{required}: missing")
    if failures:
        for failure in failures:
            print(failure)
        return 1
    print(f"Validated {len(set(files))} asset files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
