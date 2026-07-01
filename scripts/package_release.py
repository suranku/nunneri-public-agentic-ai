#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import shutil
import tarfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RELEASES = ROOT / "dist" / "releases"
PACKAGE_PREFIX = "nunneri-ai-assets"

ROOT_FILES = [
    "install.sh",
    "uninstall.sh",
    "VERSION",
    "LICENSE",
    "README.md",
    "ARCHITECTURE.md",
    "AI_ASSETS.md",
    "CITATION.cff",
    "COMMERCIAL_LICENSE.md",
    "CONTRIBUTOR_LICENSE_AGREEMENT.md",
    "DEFENSIVE_PUBLICATION.md",
    "GOVERNANCE.md",
    "MAINTAINERS.md",
    "NOTICE.md",
    "ROADMAP.md",
    "SECURITY.md",
    "RELEASE.md",
    "TRADEMARKS.md",
    "CHANGELOG.md",
]


def copy_tree(src: Path, dest: Path) -> None:
    shutil.copytree(
        src,
        dest,
        ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", ".DS_Store", "releases"),
    )


def package_dir(version: str) -> Path:
    return RELEASES / f"{PACKAGE_PREFIX}-{version}"


def build_package(version: str) -> Path:
    target = package_dir(version)
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)
    for name in ROOT_FILES:
        shutil.copyfile(ROOT / name, target / name)
    copy_tree(ROOT / "dist", target / "dist")
    copy_tree(ROOT / "docs" / "reference", target / "docs" / "reference")
    copy_tree(ROOT / "examples" / "consumer-repo", target / "examples" / "consumer-repo")
    return target


def write_zip(source: Path, archive: Path) -> None:
    if archive.exists():
        archive.unlink()
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(source.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(source.parent))


def write_tar(source: Path, archive: Path) -> None:
    if archive.exists():
        archive.unlink()
    with tarfile.open(archive, "w:gz") as tf:
        tf.add(source, arcname=source.name)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_checksums(paths: list[Path], checksum_file: Path) -> None:
    checksum_file.write_text("\n".join(f"{sha256(path)}  {path.name}" for path in paths) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", default=(ROOT / "VERSION").read_text(encoding="utf-8").strip())
    args = parser.parse_args()
    version = args.version
    if version != (ROOT / "VERSION").read_text(encoding="utf-8").strip():
        print(f"--version {version} must match VERSION")
        return 1
    RELEASES.mkdir(parents=True, exist_ok=True)
    source = build_package(version)
    zip_path = RELEASES / f"{PACKAGE_PREFIX}-{version}.zip"
    tar_path = RELEASES / f"{PACKAGE_PREFIX}-{version}.tar.gz"
    checksum_path = RELEASES / f"{PACKAGE_PREFIX}-{version}.sha256"
    write_zip(source, zip_path)
    write_tar(source, tar_path)
    write_checksums([zip_path, tar_path], checksum_path)
    print(f"Wrote {zip_path}")
    print(f"Wrote {tar_path}")
    print(f"Wrote {checksum_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
