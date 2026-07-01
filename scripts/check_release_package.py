#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import tarfile
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
RELEASES = ROOT / "dist" / "releases"
PACKAGE = f"nunneri-ai-assets-{VERSION}"

REQUIRED_PATHS = [
    "install.sh",
    "uninstall.sh",
    "VERSION",
    "LICENSE",
    "README.md",
    "ARCHITECTURE.md",
    "AI_ASSETS.md",
    "COMMERCIAL_LICENSE.md",
    "CONTRIBUTOR_LICENSE_AGREEMENT.md",
    "DEFENSIVE_PUBLICATION.md",
    "MAINTAINERS.md",
    "NOTICE.md",
    "RELEASE.md",
    "TRADEMARKS.md",
    "CHANGELOG.md",
    "dist/claude/CLAUDE.md",
    "dist/codex/AGENTS.md",
    "dist/gemini/GEMINI.md",
    "dist/langgraph/LANGGRAPH.md",
    "dist/open-source/AGENT_MANIFEST.md",
    "docs/reference/README.md",
    "docs/reference/ARCHITECTURE.md",
    "docs/reference/DEFENSIVE_PUBLICATION.md",
    "docs/reference/guides/end-user-langgraph-setup.md",
    "docs/reference/guides/end-user-setup-demo.html",
    "docs/reference/examples/consumer-repo/README.md",
    "examples/consumer-repo/README.md",
]

FORBIDDEN_PARTS = {".git", "__pycache__", ".DS_Store", "releases"}
FORBIDDEN_SUFFIXES = {".pyc"}


def fail(message: str) -> None:
    raise AssertionError(message)


def assert_exists(path: Path) -> None:
    if not path.exists():
        fail(f"missing expected package path: {path}")


def check_tree(root: Path) -> None:
    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    if version != VERSION:
        fail(f"package VERSION {version} does not match {VERSION}")
    for rel in REQUIRED_PATHS:
        assert_exists(root / rel)
    for path in root.rglob("*"):
        rel_parts = set(path.relative_to(root).parts)
        if rel_parts & FORBIDDEN_PARTS:
            fail(f"forbidden path in package: {path}")
        if path.suffix in FORBIDDEN_SUFFIXES:
            fail(f"forbidden file suffix in package: {path}")


def run_install(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["bash", "install.sh", *args],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=True,
    )
    return completed.stdout


def check_install_from_package(root: Path) -> None:
    output = run_install(root, "--provider", "claude", "--project", "--context-only", "--dry-run")
    if "Would install CLAUDE.md (root-context)" not in output:
        fail(f"dry-run output did not include root CLAUDE.md target:\n{output}")
    with tempfile.TemporaryDirectory(prefix="nunneri-package-consumer-") as tmp:
        consumer = Path(tmp)
        for name in ("install.sh", "VERSION"):
            shutil.copyfile(root / name, consumer / name)
        shutil.copytree(root / "dist", consumer / "dist")
        run_install(consumer, "--provider", "claude", "--project", "--context-only", "--force", "--skip-build")
        assert_exists(consumer / "CLAUDE.md")
        assert_exists(consumer / ".ai-assets-version")


def safe_zip_extractall(zf: zipfile.ZipFile, dest: Path) -> None:
    dest = dest.resolve()
    for member in zf.namelist():
        target = (dest / member).resolve()
        if not target.is_relative_to(dest):
            fail(f"zip-slip detected: {member}")
    zf.extractall(dest)


def check_zip() -> None:
    archive = RELEASES / f"{PACKAGE}.zip"
    assert_exists(archive)
    with tempfile.TemporaryDirectory(prefix="nunneri-release-zip-") as tmp:
        with zipfile.ZipFile(archive) as zf:
            safe_zip_extractall(zf, Path(tmp))
        root = Path(tmp) / PACKAGE
        check_tree(root)
        check_install_from_package(root)


def check_tar() -> None:
    archive = RELEASES / f"{PACKAGE}.tar.gz"
    assert_exists(archive)
    with tempfile.TemporaryDirectory(prefix="nunneri-release-tar-") as tmp:
        with tarfile.open(archive, "r:gz") as tf:
            try:
                tf.extractall(tmp, filter="data")
            except TypeError:
                # Python < 3.12: apply manual path validation before extracting
                dest = Path(tmp).resolve()
                for member in tf.getmembers():
                    target = (dest / member.name).resolve()
                    if not target.is_relative_to(dest):
                        fail(f"tar-slip detected: {member.name}")
                tf.extractall(tmp)
        root = Path(tmp) / PACKAGE
        check_tree(root)


def check_checksums() -> None:
    checksum = RELEASES / f"{PACKAGE}.sha256"
    assert_exists(checksum)
    text = checksum.read_text(encoding="utf-8")
    for name in (f"{PACKAGE}.zip", f"{PACKAGE}.tar.gz"):
        if name not in text:
            fail(f"checksum file missing {name}")


def main() -> int:
    check_zip()
    check_tar()
    check_checksums()
    print("Release package checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
