#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    end = text.find("\n---", 4)
    data: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" in line and not line.startswith(" "):
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip()
    return data


def items(paths):
    out = []
    for path in sorted(paths):
        try:
            data = frontmatter(path)
            out.append({"name": data.get("name", path.stem), "description": data.get("description", ""), "category": data.get("category", ""), "path": str(path.relative_to(ROOT))})
        except Exception:
            out.append({"name": path.stem, "description": "", "category": "", "path": str(path.relative_to(ROOT))})
    return out


def main() -> None:
    agents = items(path for path in (ROOT / "assets/agents").glob("**/*.md") if path.name != "README.md")
    commands = items(path for path in (ROOT / "assets/commands").glob("**/*.md") if path.name != "README.md")
    skills = []
    for path in sorted((ROOT / "assets/skills").glob("*/SKILL.md")):
        data = frontmatter(path)
        skills.append({"name": data.get("name", path.parent.name), "description": data.get("description", ""), "path": str(path.relative_to(ROOT))})
    workflows = items(path for path in (ROOT / "assets/workflows").glob("*.md") if path.name != "README.md")
    guides = [
        {
            "name": path.name,
            "title": path.stem.replace("-", " ").title(),
            "description": "Interactive provider-neutral guide.",
            "href": f"reference/guides/{path.name}",
        }
        for path in sorted((ROOT / "guides").glob("*.html"))
    ]
    manifest = {
        "counts": {"agents": len(agents), "commands": len(commands), "skills": len(skills), "workflows": len(workflows), "providers": 4, "runtimes": 1, "guides": len(guides)},
        "agents": agents,
        "commands": commands,
        "skills": skills,
        "workflows": workflows,
        "guides": guides,
    }
    target = ROOT / "docs/assets/manifest.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {target}")


if __name__ == "__main__":
    main()
