#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from textwrap import dedent


ROOT = Path(__file__).resolve().parents[1]

ORG = "Nuneri Engineering"
PLATFORM = "Nuneri AI Assets"
REPO_URL = "github.com/Yamini-Suranku/nuneri-public-ai-assets"
TEAM = "Nuneri Platform"
STACKS = ["python", "javascript", "java", "go"]
DOMAINS = ["Platform", "Applications", "Data", "Reporting"]
CODEOWNERS = ["yamini.sk@suranku.com"]
JIRA_PREFIX = "NUN"
VERSION = "0.1.0"
RELEASE_OWNER = "yamini.sk@suranku.com"
DEFAULT_BRANCH = "main"
COMPANION_REPO = "Not configured"


def write(path: str, content: str, executable: bool = False) -> None:
    full = ROOT / path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(content.strip() + "\n", encoding="utf-8")
    if executable:
        full.chmod(0o755)


def readme(path: str, title: str) -> None:
    write(path, f"# {title}\n\nThis directory is part of the {PLATFORM} repository.\n")


def yaml_list(values: list[str], indent: int = 2) -> str:
    pad = " " * indent
    return "\n".join(f"{pad}- {value}" for value in values)


def asset_frontmatter(name: str, description: str, category: str, stacks: list[str] | None = None) -> str:
    stack_lines = yaml_list(stacks or ["all"], 2)
    return f"""---
name: {name}
description: {description}
category: {category}
stacks:
{stack_lines}
providers:
  claude:
    model: claude-sonnet-4-6
    tools: Read, Grep, Glob, Bash, Write, Edit
  codex:
    model: gpt-5-codex
    tools: read, search, shell, edit
  gemini:
    model: gemini-2.5-pro
    tools: read, search, shell, edit
  open_source:
    model: local-default
    tools:
      - read
      - search
      - shell
      - edit
---"""


def agent_body(name: str, description: str, category: str, stacks: list[str] | None = None) -> str:
    return f"""{asset_frontmatter(name, description, category, stacks)}

# {name}

## Role

You are the {name} for {ORG}. You work across {TEAM} repositories and focus on {description.lower()}.

## When To Activate

- The user asks for help related to {description.lower()}.
- The repository, error message, ticket, or changed files match the `{category}` domain.
- A command or workflow explicitly routes to this agent.

## Core Workflow

1. Read the provider-neutral repository context and relevant project context files.
2. Identify the affected stack, provider adapter, domain, and asset type.
3. Gather evidence from code, configuration, tests, logs, and git history.
4. Classify the issue and separate confirmed facts from assumptions.
5. Produce a concise plan with validation steps.
6. Stop for human approval before making code, prompt, workflow, or release-impacting changes.
7. Implement the smallest correct change after approval.
8. Run relevant validation and summarize residual risk.

## Output Format

- Summary
- Evidence
- Classification
- Recommended action
- Validation performed
- Follow-up items

## Human Approval Gates

- Stop before modifying files.
- Stop before committing.
- Stop before tagging, pushing, creating releases, or opening PRs.

## Related Agents

- `impact-analyst`
- `release-ops-analyst`
- `logging-standards-analyst`
"""


def command_frontmatter(name: str, description: str, category: str, required: list[str]) -> str:
    req = yaml_list(required, 4) if required else "    []"
    return f"""---
name: {name}
description: {description}
category: {category}
inputs:
  required:
{req}
  optional:
    - --provider
    - --dry-run
providers:
  claude:
    slash_command: /{name}
  codex:
    invocation: {name}
  gemini:
    invocation: {name}
  open_source:
    manifest_id: {name}
---"""


def command_body(name: str, description: str, category: str, required: list[str]) -> str:
    args = " ".join(f"<{item}>" for item in required) or "[options]"
    return f"""{command_frontmatter(name, description, category, required)}

# /{name}

## What It Does

{description}. It routes the request through the provider-neutral asset model and only applies provider-specific behavior at the adapter layer.

## Activated Agents

- Primary: `{category}-specialist` where available
- Supporting: `impact-analyst`, `release-ops-analyst`

## Inputs

Required inputs: {", ".join(required) if required else "none"}.

Optional flags: `--provider`, `--dry-run`, `--json`.

## Examples

```text
/{name} {args}
/{name} {args} --provider codex
```

## Expected Output

- Request classification
- Evidence gathered
- Recommended next action
- Approval gates
- Validation plan

## Provider Notes

Claude uses slash command Markdown, Codex and Gemini use prompt/workflow invocation metadata, and open-source frameworks use exported manifests.
"""


def skill(name: str, title: str, body: str) -> None:
    write(f"assets/skills/{name}/SKILL.md", f"""---
name: {name}
description: {title}
category: skill
providers:
  claude:
    enabled: true
  codex:
    enabled: true
  gemini:
    enabled: true
  open_source:
    enabled: true
---

# {title}

{body}
""")


def workflow(name: str, title: str, body: str) -> None:
    write(f"assets/workflows/{name}.md", f"""---
name: {name}
description: {title}
category: workflow
providers:
  claude:
    enabled: true
  codex:
    enabled: true
  gemini:
    enabled: true
  open_source:
    enabled: true
---

# {title}

{body}
""")


def simple_html(title: str, subtitle: str, interactive: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} - {PLATFORM}</title>
  <style>
    :root {{
      --bg:#0a0e1a; --bg2:#111827; --border:#1e2d45; --blue:#3b82f6; --cyan:#22d3ee;
      --green:#10b981; --orange:#f59e0b; --red:#ef4444; --purple:#8b5cf6; --text:#e2e8f0; --muted:#64748b;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin:0; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background:var(--bg); color:var(--text); }}
    nav {{ position:sticky; top:0; z-index:2; display:flex; gap:16px; align-items:center; padding:14px 24px; background:rgba(10,14,26,.92); border-bottom:1px solid var(--border); }}
    nav a {{ color:var(--text); text-decoration:none; font-size:14px; }}
    main {{ max-width:1100px; margin:0 auto; padding:48px 20px; }}
    section {{ padding:28px 0; }}
    h1 {{ font-size:clamp(34px, 6vw, 68px); line-height:1; margin:0 0 16px; letter-spacing:0; }}
    h2 {{ font-size:28px; margin:0 0 16px; }}
    p {{ color:var(--muted); line-height:1.7; }}
    .hero {{ min-height:68vh; display:grid; align-content:center; }}
    .stats, .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:14px; }}
    .card, details {{ border:1px solid var(--border); background:var(--bg2); border-radius:8px; padding:18px; }}
    .badge {{ display:inline-block; border:1px solid var(--border); border-radius:999px; padding:5px 10px; color:var(--cyan); font-size:13px; }}
    button {{ border:1px solid var(--blue); background:transparent; color:var(--text); padding:10px 14px; border-radius:6px; cursor:pointer; }}
    button:hover, .active {{ background:var(--blue); }}
    .panel {{ margin-top:16px; border-left:3px solid var(--cyan); padding:16px; background:rgba(34,211,238,.08); }}
    table {{ width:100%; border-collapse:collapse; overflow:hidden; border-radius:8px; }}
    th, td {{ border-bottom:1px solid var(--border); padding:12px; text-align:left; }}
    footer {{ border-top:1px solid var(--border); padding:28px 20px; color:var(--muted); text-align:center; }}
  </style>
</head>
<body>
  <nav>
    <a href="../docs/index.html">Home</a>
    <a href="#problem">Problem</a>
    <a href="#solution">Solution</a>
    <a href="#interactive">Interactive</a>
  </nav>
  <main>
    <section class="hero">
      <span class="badge">Provider agnostic</span>
      <h1>{title}</h1>
      <p>{subtitle}</p>
      <div class="stats">
        <div class="card">4 providers</div>
        <div class="card">Canonical source of truth</div>
        <div class="card">Issue-first contribution</div>
      </div>
    </section>
    <section id="problem">
      <h2>The Problem Before</h2>
      <div class="grid">
        <details open><summary>Provider lock-in</summary><p>Assets often work only for one assistant and cannot move cleanly across teams.</p></details>
        <details><summary>Unclear ownership</summary><p>Feedback arrives without enough context to triage, prioritize, or release.</p></details>
        <details><summary>Manual drift</summary><p>Repeated copies diverge when commands, agents, and docs are maintained separately.</p></details>
      </div>
    </section>
    <section id="solution">
      <h2>The Solution</h2>
      <p>Canonical assets live once under assets, then adapters generate Claude, Codex, Gemini, and open-source outputs.</p>
    </section>
    <section id="interactive">
      <h2>Interactive</h2>
      {interactive}
    </section>
  </main>
  <footer><a href="../docs/index.html">Portal</a> | <a href="../CONTRIBUTING.md">CONTRIBUTING.md</a></footer>
  <script>
    document.querySelectorAll("button[data-panel]").forEach((button) => {{
      button.addEventListener("click", () => {{
        document.querySelectorAll("[data-content]").forEach((panel) => panel.hidden = true);
        document.querySelectorAll("button[data-panel]").forEach((item) => item.classList.remove("active"));
        document.querySelector(`[data-content="${{button.dataset.panel}}"]`).hidden = false;
        button.classList.add("active");
      }});
    }});
  </script>
</body>
</html>"""


def portal_html() -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{PLATFORM}</title>
  <style>
    :root {{
      --bg:#0a0e1a; --bg2:#111827; --border:#1e2d45; --blue:#3b82f6; --cyan:#22d3ee;
      --green:#10b981; --orange:#f59e0b; --red:#ef4444; --purple:#8b5cf6; --text:#e2e8f0; --muted:#64748b;
    }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; font-family:Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background:var(--bg); color:var(--text); }}
    nav {{ position:fixed; top:0; left:0; right:0; z-index:5; display:flex; gap:14px; padding:14px 24px; background:rgba(10,14,26,.92); border-bottom:1px solid var(--border); overflow:auto; }}
    nav a {{ color:var(--text); text-decoration:none; white-space:nowrap; font-size:14px; }}
    main {{ max-width:1180px; margin:0 auto; padding:84px 20px 44px; }}
    section {{ padding:40px 0; }}
    h1 {{ font-size:clamp(40px,7vw,82px); line-height:1; margin:0 0 18px; letter-spacing:0; }}
    h2 {{ font-size:30px; margin:0 0 18px; }}
    p {{ color:var(--muted); line-height:1.7; }}
    .hero {{ min-height:74vh; display:grid; align-content:center; }}
    .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(230px,1fr)); gap:14px; }}
    .card, details {{ border:1px solid var(--border); background:var(--bg2); border-radius:8px; padding:18px; }}
    .card[data-reveal] {{ opacity:.15; transform:translateY(10px); transition:.35s ease; }}
    .card.visible {{ opacity:1; transform:none; }}
    .muted {{ color:var(--muted); }}
    .badge {{ display:inline-block; border:1px solid var(--border); border-radius:999px; padding:5px 10px; color:var(--cyan); font-size:13px; }}
    input, select {{ width:100%; padding:11px 12px; border-radius:6px; border:1px solid var(--border); background:#070b14; color:var(--text); margin-bottom:14px; }}
    a {{ color:var(--cyan); }}
    code, pre {{ background:#070b14; border:1px solid var(--border); border-radius:8px; color:var(--text); }}
    pre {{ padding:16px; overflow:auto; }}
    footer {{ border-top:1px solid var(--border); padding:28px 20px; text-align:center; color:var(--muted); }}
  </style>
</head>
<body>
  <nav>
    <a href="#hero">Home</a><a href="#problem">Problem</a><a href="#quick-start">Quick Start</a><a href="#providers">Providers</a>
    <a href="#commands">Commands</a><a href="#agents">Agents</a><a href="#skills">Skills</a><a href="#guides">Guides</a><a href="#reference">Reference</a>
  </nav>
  <main>
    <section id="hero" class="hero">
      <span class="badge">Claude | Codex | Gemini | open-source</span>
      <h1>{PLATFORM}</h1>
      <p>Provider-agnostic AI agents, skills, commands, workflows, guides, and adapters for {TEAM}.</p>
      <div id="stats" class="grid"></div>
    </section>
    <section id="problem">
      <h2>Why This Exists</h2>
      <div class="grid">
        <details open><summary>Before: assets trapped in one assistant</summary><p>After: canonical assets generate provider-specific outputs.</p></details>
        <details><summary>Before: unclear feedback paths</summary><p>After: GitHub Issues collect provider, priority, asset type, and release target.</p></details>
        <details><summary>Before: manual release notes</summary><p>After: issues and labels drive changelog and release readiness checks.</p></details>
        <details><summary>Before: duplicated prompts drift</summary><p>After: adapters are rebuilt from one source of truth.</p></details>
      </div>
    </section>
    <section id="quick-start">
      <h2>Quick Start</h2>
      <pre><code>git clone https://{REPO_URL}
cd nuneri-public-ai-assets
python3 scripts/build_adapters.py
./install.sh --provider all --project --force</code></pre>
    </section>
    <section id="providers">
      <h2>Providers</h2>
      <div class="grid">
        <div class="card" data-reveal><h3>Claude Code</h3><p>Claude-compatible agents, commands, skills, and CLAUDE.md.</p></div>
        <div class="card" data-reveal><h3>Codex</h3><p>Codex-ready skills, workflows, prompts, and AGENTS.md.</p></div>
        <div class="card" data-reveal><h3>Gemini</h3><p>Gemini prompts, workflows, command mappings, and GEMINI.md.</p></div>
        <div class="card" data-reveal><h3>Open Source</h3><p>Portable manifests, prompts, and workflow definitions.</p></div>
      </div>
    </section>
    <section id="commands">
      <h2>Commands</h2>
      <input id="search" placeholder="Filter commands, agents, or skills">
      <div id="command-list" class="grid"></div>
    </section>
    <section id="agents"><h2>Agents</h2><div id="agent-list" class="grid"></div></section>
    <section id="skills"><h2>Skills</h2><div id="skill-list" class="grid"></div></section>
    <section id="guides"><h2>Interactive Guides</h2><div id="guide-list" class="grid"></div></section>
    <section id="reference">
      <h2>Reference Documents</h2>
      <div class="grid">
        <div class="card"><h3>Executive Summaries</h3><p><a href="reference/guides/triage-executive-summary.md">Triage</a></p><p><a href="reference/guides/compliance-executive-summary.md">Compliance</a></p><p><a href="reference/guides/schema-lineage-executive-summary.md">Schema and Lineage</a></p></div>
        <div class="card"><h3>Templates and References</h3><p><a href="reference/AI_ASSETS.md">AI_ASSETS.md</a></p><p><a href="reference/CONTRIBUTING.md">CONTRIBUTING.md</a></p><p><a href="reference/RELEASE.md">RELEASE.md</a></p></div>
      </div>
    </section>
  </main>
  <footer>{PLATFORM} | <a href="reference/CONTRIBUTING.md">Contribute</a></footer>
  <script>
    const fallback = {{counts:{{agents:0,commands:0,skills:0,workflows:0,providers:4,guides:8}}, agents:[], commands:[], skills:[], guides:[]}};
    const card = (item) => `<div class="card" data-reveal><h3><code>${{item.name}}</code></h3><p>${{item.description || item.category || ""}}</p></div>`;
    function render(data) {{
      const counts = data.counts || fallback.counts;
      document.getElementById("stats").innerHTML = Object.entries(counts).map(([k,v]) => `<div class="card" data-reveal><strong>${{v}}</strong><p>${{k}}</p></div>`).join("");
      document.getElementById("command-list").innerHTML = (data.commands || []).map(card).join("");
      document.getElementById("agent-list").innerHTML = (data.agents || []).map(card).join("");
      document.getElementById("skill-list").innerHTML = (data.skills || []).map(card).join("");
      document.getElementById("guide-list").innerHTML = (data.guides || []).filter(g => g.name.endsWith(".html")).map(g => `<div class="card" data-reveal><h3>${{g.title}}</h3><p>${{g.description}}</p><a href="${{g.href || `reference/guides/${{g.name}}`}}">Open guide</a></div>`).join("");
      reveal();
    }}
    function reveal() {{
      const observer = new IntersectionObserver((entries) => entries.forEach((entry) => {{
        if (entry.isIntersecting) entry.target.classList.add("visible");
      }}), {{threshold:.12}});
      document.querySelectorAll("[data-reveal]").forEach((item) => observer.observe(item));
    }}
    fetch("assets/manifest.json").then((response) => response.json()).then(render).catch(() => render(fallback));
    document.getElementById("search").addEventListener("input", (event) => {{
      const q = event.target.value.toLowerCase();
      document.querySelectorAll("#command-list .card, #agent-list .card, #skill-list .card").forEach((item) => {{
        item.style.display = item.textContent.toLowerCase().includes(q) ? "" : "none";
      }});
    }});
  </script>
</body>
</html>"""


def executive_summary(title: str, commands: list[str]) -> str:
    rows = "\n".join(f"| `/{cmd}` | Runs the {cmd} workflow | Use when the request maps to {cmd} |" for cmd in commands)
    examples = "\n".join(f"/{cmd} sample-input --provider claude" for cmd in commands[:3])
    return f"""> **One-liner:** {title} gives teams a provider-neutral way to use AI assets across Claude, Codex, Gemini, and open-source runtimes.

## The Problem Before

Teams duplicated prompts and workflows for each assistant, making quality, approvals, and releases hard to govern.

## The Solution

Canonical assets live once under `assets/` and provider adapters generate the runtime-specific files.

## Command Reference

| Command | What it does | When to use |
| --- | --- | --- |
{rows}

## How It Works

```text
issue -> canonical asset -> provider adapter -> validation -> release
```

## Real Examples

```text
{examples}
```
"""


def create_assets() -> None:
    dirs = [
        "assets/agents/triage", "assets/agents/analysis", "assets/agents/compliance", "assets/agents/operations", "assets/agents/reporting",
        "assets/skills", "assets/commands/triage", "assets/commands/analysis", "assets/commands/compliance", "assets/commands/operations", "assets/commands/reporting",
        "assets/workflows", "adapters/claude/agents", "adapters/claude/skills", "adapters/claude/commands",
        "adapters/codex/skills", "adapters/codex/prompts", "adapters/codex/workflows",
        "adapters/gemini/prompts", "adapters/gemini/workflows", "adapters/gemini/context",
        "adapters/open-source/manifests", "adapters/open-source/prompts", "adapters/open-source/workflows",
        "guides", "docs/assets", "scripts", "dist/claude", "dist/codex", "dist/gemini", "dist/open-source",
        ".github/ISSUE_TEMPLATE", ".github/workflows",
    ]
    for directory in dirs:
        (ROOT / directory).mkdir(parents=True, exist_ok=True)
        readme(f"{directory}/README.md", directory)

    for stack in STACKS:
        write(f"assets/agents/triage/{stack}-triage-specialist.md", agent_body(f"{stack}-triage-specialist", f"Full 9-phase bug triage workflow for {stack}", "triage", [stack]))
        write(f"assets/agents/triage/{stack}-bug-analyzer.md", agent_body(f"{stack}-bug-analyzer", f"Read-only diagnosis for {stack} bugs", "triage", [stack]))
        write(f"assets/agents/compliance/{stack}-eh-specialist.md", agent_body(f"{stack}-eh-specialist", f"Exception handling compliance audit for {stack}", "compliance", [stack]))

    agents = {
        "analysis/schema-drift-analyst": ("Detect breaking schema changes", "analysis"),
        "analysis/impact-analyst": ("Forward lineage from any changed object", "analysis"),
        "analysis/column-lineage-analyst": ("Field-level lineage tracing", "analysis"),
        "analysis/ingestion-dependency-analyst": ("Backward trace from API to data sources", "analysis"),
        "operations/prodops-specialist": ("Incident classification against known patterns", "operations"),
        "operations/changelog-analyst": ("Summarize what changed between builds or releases", "operations"),
        "operations/release-ops-analyst": ("Version tracking and environment comparison", "operations"),
        "compliance/logging-standards-analyst": ("Logging standards audit", "compliance"),
        "compliance/nfr-governance-analyst": ("Domain-level NFR readiness coordination", "compliance"),
        "compliance/agent-context-generator": ("Generate or augment provider-specific repo context files", "compliance"),
        "reporting/report-gap-analyst": ("BRD-to-code gap analysis", "reporting"),
        "reporting/report-bug-analyzer": ("Diagnose report rendering bugs", "reporting"),
    }
    for path, (description, category) in agents.items():
        name = path.split("/")[-1]
        write(f"assets/agents/{path}.md", agent_body(name, description, category, STACKS))

    skill("triage-workflow", "Universal Triage Workflow", """Use this skill whenever an agent handles a bug, incident, failing validation, or governance finding that may require diagnosis or a fix.

Follow the canonical nine-phase workflow in `assets/workflows/triage-nine-phase.md`.

## Phase Checklist

1. Intake
2. Context Load
3. Classification
4. Evidence Collection
5. Root Cause Analysis
6. Gate 1: RCA and Fix Plan Approval
7. Test-First Fix
8. Validation
9. Gate 2: Summary and Release Impact

## Gate Rules

Gate 1 is mandatory before edits. Present the RCA, evidence, fix plan, expected files, test plan, and risks. Wait for explicit approval.

Gate 2 is mandatory before commit, push, PR creation, tag, or publish. Present what changed, validation results, provider impact, release impact, compatibility notes, and recommended commit or PR text.

## Read-Only Triage

If the user asks for diagnosis only, complete phases 1 through 6 and stop. Do not edit files, create tests, or run fix phases unless the user approves implementation.

## Fix-Capable Triage

If the user approves a fix, create or update a failing test or equivalent validation before implementing. Keep the fix minimal and run checks appropriate to the stack and asset type.

## Provider-Neutral Rule

Change canonical assets first. Rebuild provider outputs after canonical asset changes. Do not hand-edit generated `dist/` files unless debugging the adapter builder itself.

## Required Output

Every triage response should report:

- Current phase
- Classification
- Evidence gathered
- Approval gate status
- Validation status
- Remaining risk""")
    for stack in STACKS:
        skill(f"{stack}-patterns", f"{stack.title()} Patterns", f"Use these commands and gotchas when working on {stack} repositories for {TEAM}. Include build, test, coverage, commit, and PR conventions.")
    skill("exception-handling-audit", "Exception Handling Audit", "Audit exception handling for consistency, observability, user impact, and recovery behavior.")
    skill("logging-standards", "Logging Standards", "Check structured logging, correlation identifiers, sensitive data handling, and actionable error messages.")
    skill("provider-adapter-guidelines", "Provider Adapter Guidelines", "Map canonical assets into Claude, Codex, Gemini, and open-source formats without changing the provider-neutral source of truth.")

    commands = {
        "triage/triage": ("Detect stack and dispatch to the right specialist", "triage", ["TICKET-ID", "symptom"]),
        "triage/prodops-triage": ("Classify an incident into a known runbook or JIRA defect", "triage", ["INC-ID", "ENV", "error"]),
        "triage/devhub-fix": ("Fix a governance finding with test-first workflow and PR", "triage", ["JSON"]),
        "analysis/schema-drift": ("Detect breaking schema changes from the latest build", "analysis", []),
        "analysis/impact-analysis": ("Trace forward lineage from a table to downstream consumers", "analysis", ["table", "name"]),
        "analysis/column-trace": ("Trace one field through the full stack", "analysis", ["field"]),
        "analysis/what-changed": ("Create a changelog of new and removed objects", "analysis", []),
        "analysis/ddl-impact": ("Assess blast radius for a table DDL change", "analysis", ["table"]),
        "reporting/report-lineage": ("Identify objects that feed or use a report", "reporting", ["report"]),
        "operations/ingestion-check": ("Trace upstream dependencies for an API endpoint", "operations", ["endpoint"]),
        "operations/pipeline-health": ("Check chain completeness and gaps for a domain", "operations", ["domain"]),
        "operations/release-lookup": ("Compare module versions and latest releases", "operations", ["latest"]),
        "compliance/exception-handling": ("Run exception handling audit and static scan", "compliance", []),
        "compliance/nfr-readiness": ("Produce EH and logging readiness heatmap for a domain", "compliance", ["domain"]),
        "compliance/generate-agent-context": ("Generate or augment provider-specific repo context files", "compliance", []),
        "compliance/check-logging": ("Audit logging against standards", "compliance", []),
    }
    for path, (description, category, required) in commands.items():
        name = path.split("/")[-1]
        write(f"assets/commands/{path}.md", command_body(name, description, category, required))

    workflow("issue-to-release", "Issue to Release Workflow", "GitHub Issue -> triage labels -> accepted scope -> PR -> validation -> changelog -> release.")
    workflow("adapter-build", "Provider Adapter Build Workflow", "Build Claude, Codex, Gemini, and open-source outputs from canonical assets.")
    workflow("triage-nine-phase", "Nine Phase Triage Workflow", """Use this workflow for bug reports, incidents that may require code changes, and governance findings such as `/devhub-fix`.

The workflow has exactly nine phases. Keep the phase count stable so teams can teach, audit, and compare triage runs consistently. Add detail as substeps inside phases instead of adding new top-level phases.

## Phase 1 - Intake

Capture the request, ticket or incident id, affected environment, symptom, expected behavior, actual behavior, user impact, and any error text.

## Phase 2 - Context Load

Read the repo context and provider context before inspecting code. Prefer provider-neutral context first, then provider-specific context when relevant.

## Phase 3 - Classification

Classify the issue as code, configuration, data, schema, infrastructure, dependency, framework or runtime, documentation or asset metadata, or unknown.

## Phase 4 - Evidence Collection

Gather enough evidence to support or reject a root cause. Do not implement a fix in this phase.

## Phase 5 - Root Cause Analysis

State the root cause as a testable claim. Separate confirmed evidence from assumptions.

## Phase 6 - Gate 1: RCA and Fix Plan Approval

Stop and wait for explicit human approval before changing implementation files, provider assets, generated outputs, or release metadata.

## Phase 7 - Test-First Fix

After approval, create or update a failing test, assertion, fixture, or validation case that demonstrates the bug. Then implement the smallest correct fix.

## Phase 8 - Validation

Run the relevant checks for the stack and asset type.

## Phase 9 - Gate 2: Summary and Release Impact

Stop and present the final validation summary before committing, pushing, opening a PR, tagging, or publishing.

## Post-Triage Actions

Commit, push, PR creation, release tagging, and publishing are outside the nine phases. They require explicit human confirmation even when Phase 9 passes.

## Read-Only Mode

For read-only triage, complete phases 1 through 6 and stop after Gate 1 with an RCA and recommended plan. Do not run phases 7 through 9 unless the user explicitly approves a fix.""")


def create_scripts() -> None:
    write("scripts/validate.py", r'''#!/usr/bin/env python3
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
            if path.match("assets/agents/**/*.md") or path.match("assets/commands/**/*.md"):
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
''', True)

    write("scripts/build_adapters.py", r'''#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROVIDERS = ("claude", "codex", "gemini", "open-source")


def frontmatter_and_body(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    end = text.find("\n---", 4)
    data: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" in line and not line.startswith(" "):
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip()
    return data, text[end + 4:].strip()


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")


def reset_dist() -> None:
    for provider in PROVIDERS:
        target = ROOT / "dist" / provider
        if target.exists():
            shutil.rmtree(target)
        target.mkdir(parents=True, exist_ok=True)


def build_claude_agent(src: Path, data: dict[str, str], body: str) -> None:
    content = f"""---
name: {data['name']}
description: {data['description']}
model: claude-sonnet-4-6
tools: Read, Grep, Glob, Bash, Write, Edit
---

> Generated from `{src.relative_to(ROOT)}`. Edit the canonical asset, not this file.

{body}
"""
    write(ROOT / "dist/claude/agents" / src.name, content)


def build_command(src: Path, data: dict[str, str], body: str) -> None:
    for provider in PROVIDERS:
        suffix = ".md" if provider != "open-source" else ".json"
        if provider == "open-source":
            payload = {
                "name": data["name"],
                "description": data["description"],
                "category": data.get("category", "command"),
                "source": str(src.relative_to(ROOT)),
                "body": body,
            }
            write(ROOT / "dist/open-source/manifests/commands" / f"{data['name']}.json", json.dumps(payload, indent=2))
        else:
            target_dir = "commands" if provider == "claude" else "workflows"
            write(ROOT / f"dist/{provider}/{target_dir}" / f"{data['name']}{suffix}", f"> Generated from `{src.relative_to(ROOT)}`.\n\n{body}")


def copy_skill(src: Path) -> None:
    relative = src.parent.name
    for provider in PROVIDERS:
        if provider == "open-source":
            write(ROOT / "dist/open-source/workflows" / f"{relative}.md", f"> Generated from `{src.relative_to(ROOT)}`.\n\n{src.read_text(encoding='utf-8')}")
        else:
            write(ROOT / f"dist/{provider}/skills/{relative}/SKILL.md", f"> Generated from `{src.relative_to(ROOT)}`.\n\n{src.read_text(encoding='utf-8')}")


def build() -> None:
    reset_dist()
    for src in sorted(path for path in (ROOT / "assets/agents").glob("**/*.md") if path.name != "README.md"):
        data, body = frontmatter_and_body(src)
        build_claude_agent(src, data, body)
        for provider in ("codex", "gemini"):
            write(ROOT / f"dist/{provider}/prompts/agents" / src.name, f"> Generated from `{src.relative_to(ROOT)}`.\n\n{body}")
        write(ROOT / "dist/open-source/manifests/agents" / f"{data['name']}.json", json.dumps({"name": data["name"], "description": data["description"], "category": data.get("category"), "source": str(src.relative_to(ROOT)), "body": body}, indent=2))
    for src in sorted(path for path in (ROOT / "assets/commands").glob("**/*.md") if path.name != "README.md"):
        data, body = frontmatter_and_body(src)
        build_command(src, data, body)
    for src in sorted((ROOT / "assets/skills").glob("*/SKILL.md")):
        copy_skill(src)
    for src in sorted((ROOT / "assets/workflows").glob("*.md")):
        for provider in PROVIDERS:
            folder = "workflows" if provider != "open-source" else "workflows"
            write(ROOT / f"dist/{provider}/{folder}" / src.name, f"> Generated from `{src.relative_to(ROOT)}`.\n\n{src.read_text(encoding='utf-8')}")
    write(ROOT / "dist/claude/CLAUDE.md", "# Claude Context\n\nGenerated from provider-neutral assets. Use `AI_ASSETS.md` for canonical rules.")
    write(ROOT / "dist/codex/AGENTS.md", "# Codex Context\n\nGenerated from provider-neutral assets. Use `AI_ASSETS.md` for canonical rules.")
    write(ROOT / "dist/gemini/GEMINI.md", "# Gemini Context\n\nGenerated from provider-neutral assets. Use `AI_ASSETS.md` for canonical rules.")
    write(ROOT / "dist/open-source/AGENT_MANIFEST.md", "# Open Source Manifest\n\nGenerated from provider-neutral assets.")
    print("Built provider adapters: claude, codex, gemini, open-source")


if __name__ == "__main__":
    build()
''', True)

    write("scripts/build_portal_manifest.py", r'''#!/usr/bin/env python3
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
        "counts": {"agents": len(agents), "commands": len(commands), "skills": len(skills), "workflows": len(workflows), "providers": 4, "guides": len(guides)},
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
''', True)

    write("scripts/check_docs_links.py", r'''#!/usr/bin/env python3
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
''', True)

    write("scripts/prepare_release.py", r'''#!/usr/bin/env python3
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
''', True)

    write("scripts/check_release_ready.py", r'''#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--local-only", action="store_true")
    parser.parse_args()
    required = ["CHANGELOG.md", "RELEASE.md", "VERSION", ".github/PULL_REQUEST_TEMPLATE.md", ".github/labels.yml"]
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
''', True)


def create_installers() -> None:
    write("install.sh", r'''#!/usr/bin/env bash
set -euo pipefail

PROVIDER=""
PROJECT=0
FORCE=0
SKIP_BUILD=0
INCLUDE_AGENTS=1
INCLUDE_SKILLS=1
INCLUDE_COMMANDS=1
INCLUDE_WORKFLOWS=1
INCLUDE_GUIDES=1

usage() {
  echo "Usage: ./install.sh --provider claude|codex|gemini|open-source|all [--project] [--force] [--skip-build] [filters]"
  echo "Filters: --agents-only --skills-only --commands-only --workflows-only --no-agents --no-skills --no-commands --no-workflows --no-guides"
}

only_one() {
  INCLUDE_AGENTS=0
  INCLUDE_SKILLS=0
  INCLUDE_COMMANDS=0
  INCLUDE_WORKFLOWS=0
  INCLUDE_GUIDES=0
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --provider) PROVIDER="$2"; shift 2 ;;
    --project) PROJECT=1; shift ;;
    --force) FORCE=1; shift ;;
    --skip-build) SKIP_BUILD=1; shift ;;
    --agents-only) only_one; INCLUDE_AGENTS=1; shift ;;
    --skills-only) only_one; INCLUDE_SKILLS=1; shift ;;
    --commands-only) only_one; INCLUDE_COMMANDS=1; shift ;;
    --workflows-only) only_one; INCLUDE_WORKFLOWS=1; shift ;;
    --no-agents) INCLUDE_AGENTS=0; shift ;;
    --no-skills) INCLUDE_SKILLS=0; shift ;;
    --no-commands) INCLUDE_COMMANDS=0; shift ;;
    --no-workflows) INCLUDE_WORKFLOWS=0; shift ;;
    --no-guides) INCLUDE_GUIDES=0; shift ;;
    --selective)
      if [ ! -t 0 ]; then
        echo "--selective requires an interactive terminal"
        exit 1
      fi
      printf "Install agents? [Y/n] "; read answer; case "$answer" in n|N|no|NO) INCLUDE_AGENTS=0 ;; esac
      printf "Install skills? [Y/n] "; read answer; case "$answer" in n|N|no|NO) INCLUDE_SKILLS=0 ;; esac
      printf "Install commands? [Y/n] "; read answer; case "$answer" in n|N|no|NO) INCLUDE_COMMANDS=0 ;; esac
      printf "Install workflows? [Y/n] "; read answer; case "$answer" in n|N|no|NO) INCLUDE_WORKFLOWS=0 ;; esac
      printf "Install guides/reference docs? [Y/n] "; read answer; case "$answer" in n|N|no|NO) INCLUDE_GUIDES=0 ;; esac
      shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1"; usage; exit 1 ;;
  esac
done

if [ -z "$PROVIDER" ]; then
  usage
  exit 1
fi

if [ "$SKIP_BUILD" -eq 0 ]; then
  python3 scripts/build_adapters.py
fi

should_install() {
  rel="$1"
  case "$rel" in
    agents/*|prompts/agents/*|manifests/agents/*)
      [ "$INCLUDE_AGENTS" -eq 1 ] ;;
    skills/*)
      [ "$INCLUDE_SKILLS" -eq 1 ] ;;
    commands/*|manifests/commands/*)
      [ "$INCLUDE_COMMANDS" -eq 1 ] ;;
    workflows/*)
      [ "$INCLUDE_WORKFLOWS" -eq 1 ] ;;
    guides/*|reference/*|docs/*)
      [ "$INCLUDE_GUIDES" -eq 1 ] ;;
    CLAUDE.md|AGENTS.md|GEMINI.md|AGENT_MANIFEST.md)
      [ "$INCLUDE_GUIDES" -eq 1 ] ;;
    *)
      return 0 ;;
  esac
}

install_one() {
  provider="$1"
  src="dist/$provider"
  if [ ! -d "$src" ]; then
    echo "Missing $src"
    exit 1
  fi
  case "$provider" in
    claude) target="$HOME/.claude" ;;
    codex) target="$HOME/.codex" ;;
    gemini) target="$HOME/.gemini" ;;
    open-source) target="dist/open-source" ;;
    *) echo "Unsupported provider: $provider"; exit 1 ;;
  esac
  if [ "$PROJECT" -eq 1 ]; then
    case "$provider" in
      claude) target=".claude" ;;
      codex) target=".codex" ;;
      gemini) target=".gemini" ;;
      open-source) target="dist/open-source" ;;
    esac
  fi
  if [ "$src" = "$target" ]; then
    count=0
    while IFS= read -r file; do
      rel="${file#$src/}"
      if should_install "$rel"; then
        ((++count))
      fi
    done < <(find "$src" -type f | sort)
    version="$(cat VERSION)"
    printf "%s\n" "$version" > "$target/.ai-assets-version"
    echo "Prepared $count files for $provider in $target"
    return 0
  fi
  mkdir -p "$target"
  count=0
  while IFS= read -r file; do
    rel="${file#$src/}"
    if ! should_install "$rel"; then
      continue
    fi
    mkdir -p "$target/$(dirname "$rel")"
    if [ -e "$target/$rel" ] && [ "$FORCE" -ne 1 ]; then
      echo "Skip existing $target/$rel"
    else
      cp "$file" "$target/$rel"
      ((++count))
    fi
  done < <(find "$src" -type f | sort)
  version="$(cat VERSION)"
  printf "%s\n" "$version" > "$target/.ai-assets-version"
  echo "Installed $count files for $provider into $target"
}

if [ "$PROVIDER" = "all" ]; then
  install_one claude
  install_one codex
  install_one gemini
  install_one open-source
else
  install_one "$PROVIDER"
fi
''', True)

    write("uninstall.sh", r'''#!/usr/bin/env bash
set -euo pipefail

PROVIDER=""
FORCE=0
PROJECT=0

while [ "$#" -gt 0 ]; do
  case "$1" in
    --provider) PROVIDER="$2"; shift 2 ;;
    --project) PROJECT=1; shift ;;
    --force) FORCE=1; shift ;;
    *) echo "Unknown argument: $1"; exit 1 ;;
  esac
done

if [ -z "$PROVIDER" ]; then
  echo "Usage: ./uninstall.sh --provider claude|codex|gemini|open-source [--project] [--force]"
  exit 1
fi

case "$PROVIDER" in
  claude) target="$HOME/.claude" ;;
  codex) target="$HOME/.codex" ;;
  gemini) target="$HOME/.gemini" ;;
  open-source) target="dist/open-source" ;;
  *) echo "Unsupported provider: $PROVIDER"; exit 1 ;;
esac

if [ "$PROJECT" -eq 1 ]; then
  case "$PROVIDER" in
    claude) target=".claude" ;;
    codex) target=".codex" ;;
    gemini) target=".gemini" ;;
    open-source) target="dist/open-source" ;;
  esac
fi

if [ ! -d "$target" ]; then
  echo "Nothing to uninstall at $target"
  exit 0
fi

if [ "$FORCE" -ne 1 ]; then
  printf "Remove AI assets from %s? [y/N] " "$target"
  read answer
  case "$answer" in
    y|Y|yes|YES) ;;
    *) echo "Cancelled"; exit 0 ;;
  esac
fi

find "$target" -name ".ai-assets-version" -delete
echo "Removed AI asset version marker from $target. Review provider files manually before deleting shared directories."
''', True)


def create_docs() -> None:
    write("AI_ASSETS.md", f"""# {PLATFORM}

## What This Is

{PLATFORM} is a provider-neutral library of AI agents, skills, commands, workflows, guides, and adapter outputs for {ORG}.

## Provider-Neutral Source of Truth

Canonical assets live under `assets/`. Provider-specific files are generated into `dist/`.

## Provider Adapters

- Claude Code: `dist/claude`
- Codex: `dist/codex`
- Gemini: `dist/gemini`
- Open-source frameworks: `dist/open-source`

## Commands

Run `python3 scripts/validate.py`, `python3 scripts/build_adapters.py`, and `python3 scripts/build_portal_manifest.py` before release.

## Repository Structure

```text
assets/      canonical assets
adapters/    adapter source notes
dist/        generated provider outputs
docs/        GitHub Pages portal
guides/      demos and summaries
scripts/     validation, build, and release utilities
```

## Adding a New Agent

Create a provider-neutral Markdown file under `assets/agents/<category>/`, include required frontmatter, then rebuild adapters.

## Adding a New Provider Adapter

Add provider metadata to canonical frontmatter, add a builder target in `scripts/build_adapters.py`, document the install target, and update validation.

## Validation

Run:

```bash
python3 scripts/validate.py
python3 scripts/build_adapters.py
python3 scripts/build_portal_manifest.py
```

## NFR Compliance Overrides

N/A. This is a Markdown, HTML, and script repository.
""")

    write("README.md", f"""# {PLATFORM}

Provider-agnostic AI assets for Claude Code, Codex, Gemini, and open-source agent frameworks.

## What's Included

| Category | Source |
| --- | --- |
| Agents | `assets/agents/` |
| Skills | `assets/skills/` |
| Commands | `assets/commands/` |
| Workflows | `assets/workflows/` |
| Guides | `guides/` |

## Supported Providers

- Claude Code
- OpenAI Codex
- Google Gemini / Gemini CLI
- Open-source agent frameworks

## Quick Start

```bash
python3 scripts/build_adapters.py
python3 scripts/build_portal_manifest.py
./install.sh --provider all --project --force
```

## Install for Claude

```bash
./install.sh --provider claude --project --force
```

## Install for Codex

```bash
./install.sh --provider codex --project --force
```

## Install for Gemini

```bash
./install.sh --provider gemini --project --force
```

## Export for Open-Source Tools

```bash
./install.sh --provider open-source --force
```

## Command Reference

See `assets/commands/` and the GitHub Pages portal at `docs/index.html`.

## Contributing

Use GitHub Issues first. See `CONTRIBUTING.md`.
""")

    write("CONTRIBUTING.md", f"""# Contributing

Contributions to {PLATFORM} start with GitHub Issues.

## Feedback and Enhancement Workflow

```text
issue -> admin triage -> accepted scope -> branch -> PR -> CI -> CODEOWNERS approval -> release
```

## Step 1 - Open a GitHub Issue

Use the closest issue template. Include provider, asset type, impact, expected behavior, and acceptance criteria.

## Step 2 - Admin Triage to JIRA Story

Admins triage within 2 business days and may link a `{JIRA_PREFIX}` story.

## Step 3 - Branch and Develop

Use `feature/<issue-number>-short-description` or `fix/<issue-number>-short-description`.

## Step 4 - Open Pull Request and CI

Every PR must link the accepted issue, include validation output, and declare provider impact.

## Step 5 - CODEOWNERS Approval, Merge, and Distribute

CODEOWNERS approval is required before merge.

## Issue Labels and Triage States

Use type, asset, provider, priority, and status labels from `.github/labels.yml`.

## Issue to Release Flow

Accepted issues are assigned a release target and must be referenced in `CHANGELOG.md` before release.

## Release Participation

Release owner: {RELEASE_OWNER}.

## Provider Adapter Guidelines

Change canonical assets first. Adapter outputs are generated.

## Asset Frontmatter Reference

Required fields are `name`, `description`, and `category` where applicable.

## Questions

Open an issue using the feedback template.

Note: GitHub issue templates only become visible after `.github/ISSUE_TEMPLATE/` is merged to the default branch.
""")

    write("RELEASE.md", f"""# Release Strategy

## Release Philosophy

Ship stable provider-neutral assets and generated provider adapters together.

## Semantic Versioning

- Patch: documentation fixes, prompt wording changes, non-breaking adapter fixes
- Minor: new agents, skills, commands, workflows, or provider adapters
- Major: breaking frontmatter, installer, invocation, or adapter contract changes

## Release Cadence

Monthly by default, with ad hoc patch releases for urgent fixes.

## Release Roles

Release owner: {RELEASE_OWNER}.

## Branch Strategy

- Default branch: `{DEFAULT_BRANCH}`
- Feature: `feature/<issue-number>-short-description`
- Fix: `fix/<issue-number>-short-description`
- Release: `release/vX.Y.Z`
- Tags: `vX.Y.Z`

## Versioning Rules

Update `VERSION` and `CHANGELOG.md` before tagging.

## Changelog Rules

Every release-targeted issue must be represented in `CHANGELOG.md`.

## Provider Adapter Compatibility

Claude, Codex, Gemini, and open-source outputs must build from the same canonical assets.

## Release Checklist

1. Confirm planned issues are accepted and linked to merged PRs.
2. Run validation and adapter builds.
3. Run project-level installs.
4. Update `CHANGELOG.md`.
5. Run `scripts/prepare_release.py`.
6. Create release commit.
7. Ask before tagging.
8. Ask before pushing tags or creating GitHub releases.

## Rollback Strategy

Revert the release commit or publish a patch release that restores the previous adapter contract.

## Deprecation Policy

Mark deprecated assets in canonical metadata for one minor release before removal.
""")

    write("CHANGELOG.md", """# Changelog

All notable changes to this project are documented here.

## [Unreleased]

### Added

- Initial provider-neutral asset library for Claude, Codex, Gemini, and open-source exports.

### Changed

### Fixed

### Deprecated

### Removed

### Security
""")
    write("VERSION", VERSION)
    write("CODEOWNERS", "* " + " ".join(CODEOWNERS))
    write("docs/_config.yml", f"title: {PLATFORM}\n")
    write("docs/index.html", portal_html())

    write("adapters/claude/CLAUDE.md", "# Claude Adapter\n\nGenerated Claude outputs are built into `dist/claude/`.")
    write("adapters/codex/AGENTS.md", "# Codex Adapter\n\nGenerated Codex outputs are built into `dist/codex/`.")
    write("adapters/gemini/GEMINI.md", "# Gemini Adapter\n\nGenerated Gemini outputs are built into `dist/gemini/`.")
    write("adapters/open-source/AGENT_MANIFEST.md", "# Open Source Adapter\n\nGenerated open-source manifests are built into `dist/open-source/`.")


def create_guides() -> None:
    guide_specs = {
        "triage-demo.html": ("Triage Demo", "A clickable nine-phase triage workflow with two approval gates.", ["1 Intake", "2 Context", "3 Classify", "4 Evidence", "5 RCA", "6 Gate 1", "7 Test + Fix", "8 Validate", "9 Gate 2"]),
        "compliance-demo.html": ("Compliance Demo", "Tabbed audit results for compliance commands.", ["Exception Handling", "NFR Readiness", "Agent Context"]),
        "schema-lineage-demo.html": ("Schema and Lineage Demo", "Command switcher for schema and lineage analysis.", ["Schema Drift", "Impact", "Column Trace", "DDL Impact"]),
        "ingestion-pipeline-demo.html": ("Ingestion Pipeline Demo", "Pipeline dependency explorer.", ["Proto", "Topic", "Table", "SQL", "API"]),
        "reporting-demo.html": ("Reporting Demo", "Sortable gap analysis results.", ["GAP-001", "GAP-002", "GAP-003"]),
        "operations-demo.html": ("Operations Demo", "Incident classification and runbook output.", ["Known", "Novel", "Release Lookup"]),
        "developer-tools-demo.html": ("Developer Tools Demo", "Dev Hub fix workflow with coverage gate.", ["JSON", "Branch", "Test", "Fix", "PR"]),
        "contribute-demo.html": ("Contribute Demo", "Issue-first contribution and release flow.", ["Issue", "Triage", "PR", "CI", "Release"]),
    }
    for filename, (title, subtitle, panels) in guide_specs.items():
        buttons = "\n".join(f'<button data-panel="{i}" class="{"active" if i == 0 else ""}">{panel}</button>' for i, panel in enumerate(panels))
        contents = "\n".join(f'<div class="panel" data-content="{i}" {"hidden" if i else ""}><strong>{panel}</strong><p>{panel} produces evidence that feeds the provider-neutral workflow.</p></div>' for i, panel in enumerate(panels))
        write(f"guides/{filename}", simple_html(title, subtitle, f"<div>{buttons}</div>{contents}"))

    summaries = {
        "triage-executive-summary.md": ("Triage", ["triage", "prodops-triage", "devhub-fix"]),
        "compliance-executive-summary.md": ("Compliance", ["exception-handling", "nfr-readiness", "check-logging"]),
        "schema-lineage-executive-summary.md": ("Schema and Lineage", ["schema-drift", "impact-analysis", "column-trace"]),
        "operations-executive-summary.md": ("Operations", ["ingestion-check", "pipeline-health", "release-lookup"]),
        "reporting-executive-summary.md": ("Reporting", ["report-lineage"]),
        "ingestion-pipeline-executive-summary.md": ("Ingestion Pipeline", ["ingestion-check", "pipeline-health"]),
        "developer-tools-executive-summary.md": ("Developer Tools", ["devhub-fix", "generate-agent-context"]),
    }
    for filename, (title, cmds) in summaries.items():
        write(f"guides/{filename}", executive_summary(title, cmds))

    write("guides/platform-onboarding.md", f"""# Platform Onboarding

## Quick Start

```bash
python3 scripts/build_adapters.py
./install.sh --provider all --project --force
```

## Supported Providers

Claude Code, Codex, Gemini, and open-source agent frameworks.

## Installing for Claude Code

`./install.sh --provider claude --project --force`

## Installing for Codex

`./install.sh --provider codex --project --force`

## Installing for Gemini

`./install.sh --provider gemini --project --force`

## Exporting for Open-Source Frameworks

`./install.sh --provider open-source --force`

## Key Commands

See `assets/commands/`.

## AI_ASSETS.md as the Provider-Neutral Foundation

Canonical behavior belongs in `AI_ASSETS.md` and `assets/`.

## Provider Context Files

Claude uses `CLAUDE.md`, Codex uses `AGENTS.md`, and Gemini uses `GEMINI.md`.

## Repos with Context Files

| Stack | Repos |
| --- | --- |
| Python | To be registered through issues |
| JavaScript | To be registered through issues |
| Java | To be registered through issues |
| Go | To be registered through issues |

## Applications and Stack Detection

Commands inspect files, build tools, and repo context to choose stack-specific agents.

## AI Agent Groups

Triage, analysis, compliance, operations, and reporting.

## Known Error Pattern Format

```text
pattern:
classification:
evidence:
runbook:
```

## Environment Reference Convention

Do not hardcode environments. Link to approved environment references.

## Coverage Requirements

Target 85 percent coverage where the application stack supports coverage measurement.

## Contribution Through GitHub Issues

Open an issue first and wait for acceptance before implementation.

## Release Cadence and Versioning

See `RELEASE.md`.
""")


def issue_form(name: str, title: str, labels: list[str]) -> str:
    label_text = ", ".join(labels)
    return f"""name: {name}
description: {title}
title: "[{name}] "
labels: [{label_text}, status:needs-triage]
body:
  - type: dropdown
    id: provider
    attributes:
      label: Affected provider
      options:
        - Claude
        - Codex
        - Gemini
        - Open-source
        - Provider-neutral canonical asset
        - All providers
    validations:
      required: true
  - type: dropdown
    id: asset
    attributes:
      label: Asset type
      options:
        - Agent
        - Skill
        - Command
        - Workflow
        - Guide
        - Installer
        - Portal
        - Provider adapter
    validations:
      required: true
  - type: textarea
    id: problem
    attributes:
      label: Problem or request
    validations:
      required: true
  - type: textarea
    id: expected
    attributes:
      label: Expected behavior
    validations:
      required: true
  - type: textarea
    id: acceptance
    attributes:
      label: Acceptance criteria
    validations:
      required: true
  - type: dropdown
    id: priority
    attributes:
      label: Priority
      options:
        - critical
        - high
        - medium
        - low
    validations:
      required: true
  - type: dropdown
    id: release
    attributes:
      label: Release target
      options:
        - next patch
        - next minor
        - backlog
        - not sure
    validations:
      required: true
"""


def create_github() -> None:
    templates = {
        "agent-feedback.yml": ("Agent Feedback", "Feedback about an existing agent", ["type:feedback"]),
        "enhancement-request.yml": ("Enhancement Request", "Request a new or changed capability", ["type:enhancement"]),
        "bug-report.yml": ("Bug Report", "Report broken asset behavior", ["type:bug"]),
        "provider-adapter-request.yml": ("Provider Adapter Request", "Request provider adapter work", ["type:provider-adapter"]),
        "release-request.yml": ("Release Request", "Request release inclusion or release action", ["type:release"]),
    }
    for filename, (name, title, labels) in templates.items():
        write(f".github/ISSUE_TEMPLATE/{filename}", issue_form(name, title, labels))
    write(".github/ISSUE_TEMPLATE/config.yml", """blank_issues_enabled: false
contact_links:
  - name: Discussions
    url: https://github.com/Yamini-Suranku/nuneri-public-ai-assets/discussions
    about: Ask questions before opening a structured request.
""")
    write(".github/labels.yml", "\n".join([
        "- name: type:bug\n  color: d73a4a",
        "- name: type:enhancement\n  color: a2eeef",
        "- name: type:feedback\n  color: 7057ff",
        "- name: type:provider-adapter\n  color: 5319e7",
        "- name: type:release\n  color: 0e8a16",
        "- name: asset:agent\n  color: c5def5",
        "- name: asset:skill\n  color: c5def5",
        "- name: asset:command\n  color: c5def5",
        "- name: asset:workflow\n  color: c5def5",
        "- name: asset:guide\n  color: c5def5",
        "- name: asset:installer\n  color: c5def5",
        "- name: asset:portal\n  color: c5def5",
        "- name: provider:claude\n  color: 1d76db",
        "- name: provider:codex\n  color: 1d76db",
        "- name: provider:gemini\n  color: 1d76db",
        "- name: provider:open-source\n  color: 1d76db",
        "- name: provider:neutral\n  color: 1d76db",
        "- name: priority:critical\n  color: b60205",
        "- name: priority:high\n  color: d93f0b",
        "- name: priority:medium\n  color: fbca04",
        "- name: priority:low\n  color: 0e8a16",
        "- name: status:needs-triage\n  color: fef2c0",
        "- name: status:accepted\n  color: 0e8a16",
        "- name: status:blocked\n  color: b60205",
        "- name: status:in-progress\n  color: 0052cc",
        "- name: status:ready-for-release\n  color: 5319e7",
    ]))
    write(".github/PULL_REQUEST_TEMPLATE.md", """# Pull Request

## Linked Issue

Fixes #

## Summary

## Provider Impact

- [ ] Claude
- [ ] Codex
- [ ] Gemini
- [ ] Open-source
- [ ] Provider-neutral only

## Asset Impact

- [ ] Agent
- [ ] Skill
- [ ] Command
- [ ] Workflow
- [ ] Guide
- [ ] Installer
- [ ] Portal
- [ ] Provider adapter

## Validation Commands

```bash
python3 scripts/validate.py
python3 scripts/build_adapters.py
python3 scripts/build_portal_manifest.py
```

## Screenshots

Required for portal or guide changes.

## Release Note

## Breaking Change

- [ ] No
- [ ] Yes
""")
    write(".github/workflows/validate.yml", """name: Validate

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Validate frontmatter
        run: python3 scripts/validate.py
      - name: Build adapters
        run: python3 scripts/build_adapters.py
      - name: Build portal manifest
        run: python3 scripts/build_portal_manifest.py
      - name: Sync public reference docs
        run: python3 scripts/sync_docs_reference.py
      - name: Check docs links
        run: python3 scripts/check_docs_links.py
      - name: Check release readiness
        run: python3 scripts/check_release_ready.py --local-only
      - name: Validate shell scripts
        run: |
          bash -n install.sh
          bash -n uninstall.sh
      - name: Ensure generated files are committed
        run: git diff --exit-code
""")
    write(".github/release-drafter.yml", """name-template: "v$RESOLVED_VERSION"
tag-template: "v$RESOLVED_VERSION"
categories:
  - title: "Added"
    labels: ["type:enhancement"]
  - title: "Fixed"
    labels: ["type:bug"]
  - title: "Provider Adapters"
    labels: ["type:provider-adapter"]
change-template: "- $TITLE (#$NUMBER)"
template: |
  ## Changes

  $CHANGES
""")


def sync_reference_docs() -> None:
    reference = ROOT / "docs/reference"
    guide_reference = reference / "guides"
    reference.mkdir(parents=True, exist_ok=True)
    guide_reference.mkdir(parents=True, exist_ok=True)
    for name in ("README.md", "AI_ASSETS.md", "CONTRIBUTING.md", "RELEASE.md", "CHANGELOG.md", "VERSION"):
        shutil.copyfile(ROOT / name, reference / name)
    for src in sorted((ROOT / "guides").glob("*.md")):
        shutil.copyfile(src, guide_reference / src.name)
    for src in sorted((ROOT / "guides").glob("*.html")):
        dest = guide_reference / src.name
        shutil.copyfile(src, dest)
        text = dest.read_text(encoding="utf-8")
        text = text.replace("../docs/index.html", "../../index.html")
        dest.write_text(text, encoding="utf-8")


def main() -> None:
    create_assets()
    create_scripts()
    create_installers()
    create_docs()
    create_guides()
    create_github()
    sync_reference_docs()


if __name__ == "__main__":
    main()
