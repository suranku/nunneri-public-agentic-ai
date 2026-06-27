#!/usr/bin/env python3
from __future__ import annotations

import html.parser
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


class LinkParser(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if name in {"href", "src"} and value:
                self.links.append(value)


def is_external(link: str) -> bool:
    parsed = urlparse(link)
    return parsed.scheme in {"http", "https", "mailto", "tel"} or link.startswith("#")


def target_exists(source: Path, link: str) -> bool:
    parsed = urlparse(link)
    if parsed.scheme or link.startswith("#"):
        return True
    raw_path = unquote(parsed.path)
    if not raw_path:
        return True
    target = (source.parent / raw_path).resolve()
    try:
        target.relative_to(DOCS.resolve())
    except ValueError:
        return False
    return target.exists()


def html_links(path: Path) -> list[str]:
    parser = LinkParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser.links


def markdown_links(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    links: list[str] = []
    start = 0
    while True:
        marker = text.find("](", start)
        if marker == -1:
            break
        end = text.find(")", marker + 2)
        if end == -1:
            break
        links.append(text[marker + 2 : end])
        start = end + 1
    return links


def main() -> int:
    failures: list[str] = []
    for path in sorted(DOCS.rglob("*")):
        if path.suffix == ".html":
            links = html_links(path)
        elif path.suffix == ".md":
            links = markdown_links(path)
        else:
            continue
        for link in links:
            if is_external(link):
                continue
            if not target_exists(path, link):
                failures.append(f"{path.relative_to(ROOT)} -> {link}")
    if failures:
        print("Broken local docs links:")
        for failure in failures:
            print(failure)
        return 1
    print("Docs link check passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
