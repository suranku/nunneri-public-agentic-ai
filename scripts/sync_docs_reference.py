#!/usr/bin/env python3
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "docs/reference"
GUIDE_REFERENCE = REFERENCE / "guides"
CONTEXT_REFERENCE = REFERENCE / "context"
EXAMPLES_REFERENCE = REFERENCE / "examples"

ROOT_DOCS = [
    "README.md",
    "AI_ASSETS.md",
    "CONTRIBUTING.md",
    "RELEASE.md",
    "CHANGELOG.md",
    "VERSION",
]

RENAMED_DOCS = {
    "LANGGRAPH_RUNTIME.md": "langgraph-runtime.md",
    "NUNNERI_RUNTIME_CONTRACT.md": "nunneri-runtime-contract.md",
}


def copy_file(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dest)


def sync() -> None:
    REFERENCE.mkdir(parents=True, exist_ok=True)
    GUIDE_REFERENCE.mkdir(parents=True, exist_ok=True)
    CONTEXT_REFERENCE.mkdir(parents=True, exist_ok=True)
    EXAMPLES_REFERENCE.mkdir(parents=True, exist_ok=True)

    for name in ROOT_DOCS:
        copy_file(ROOT / name, REFERENCE / name)

    for source, dest in RENAMED_DOCS.items():
        copy_file(ROOT / source, REFERENCE / dest)

    for src in sorted((ROOT / "assets/context").glob("*.md")):
        copy_file(src, CONTEXT_REFERENCE / src.name)

    for src in sorted((ROOT / "guides").glob("*.md")):
        copy_file(src, GUIDE_REFERENCE / src.name)

    for src in sorted((ROOT / "guides").glob("*.html")):
        dest = GUIDE_REFERENCE / src.name
        copy_file(src, dest)
        text = dest.read_text(encoding="utf-8")
        text = text.replace("../docs/index.html", "../../index.html")
        dest.write_text(text, encoding="utf-8")

    for src in sorted((ROOT / "examples").glob("**/*.md")):
        copy_file(src, EXAMPLES_REFERENCE / src.relative_to(ROOT / "examples"))

    print(f"Synced public reference docs into {REFERENCE}")


if __name__ == "__main__":
    sync()
