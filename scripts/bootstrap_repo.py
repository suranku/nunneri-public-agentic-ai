#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from textwrap import dedent


ROOT = Path(__file__).resolve().parents[1]

ORG = "Nunneri Engineering"
PLATFORM = "Nunneri AI Assets"
REPO_URL = "github.com/suranku/nunneri-public-agentic-ai"
TEAM = "Nunneri Platform"
STACKS = ["python", "javascript", "java", "go"]
DOMAINS = ["Platform", "Applications", "Data", "Reporting"]
CODEOWNERS = ["yamini.sk@suranku.com"]
JIRA_PREFIX = "NUN"
VERSION = "0.1.0"
RELEASE_OWNER = "yamini.sk@suranku.com"
DEFAULT_BRANCH = "main"
COMPANION_REPO = "https://github.com/suranku/nunneri-public-agentic-ai"


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
runtimes:
  nunneri_runtime:
    enabled: true
  langgraph:
    enabled: true
  crewai:
    enabled: true
  autogen:
    enabled: true
  semantic_kernel:
    enabled: true
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
runtimes:
  nunneri_runtime:
    enabled: true
  langgraph:
    enabled: true
  crewai:
    enabled: true
  autogen:
    enabled: true
  semantic_kernel:
    enabled: true
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
runtimes:
  nunneri_runtime:
    enabled: true
  langgraph:
    enabled: true
  crewai:
    enabled: true
  autogen:
    enabled: true
  semantic_kernel:
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
runtimes:
  nunneri_runtime:
    enabled: true
  langgraph:
    enabled: true
  crewai:
    enabled: true
  autogen:
    enabled: true
  semantic_kernel:
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
      --bg:#101114; --surface:#181b20; --surface2:#20242b; --border:#343a43;
      --text:#f4f7fb; --muted:#a1aab8; --teal:#2dd4bf; --green:#34d399;
      --amber:#fbbf24; --red:#fb7185; --blue:#60a5fa; --focus:#f8fafc;
    }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{ margin:0; font-family:Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background:var(--bg); color:var(--text); overflow-x:hidden; }}
    nav {{ position:sticky; top:0; z-index:5; display:flex; gap:16px; align-items:center; padding:14px 24px; background:rgba(16,17,20,.94); border-bottom:1px solid var(--border); backdrop-filter:blur(12px); overflow:auto; }}
    nav a {{ color:var(--text); text-decoration:none; font-size:14px; white-space:nowrap; }}
    main {{ max-width:1180px; margin:0 auto; padding:44px 20px; }}
    section {{ padding:34px 0; }}
    h1 {{ font-size:clamp(36px, 6vw, 72px); line-height:1; margin:0 0 16px; letter-spacing:0; max-width:900px; }}
    h2 {{ font-size:28px; margin:0 0 16px; }}
    h3 {{ margin:0 0 10px; }}
    p {{ color:var(--muted); line-height:1.7; }}
    pre, code {{ background:#0c0d10; border:1px solid var(--border); border-radius:8px; color:var(--text); }}
    code {{ padding:1px 5px; }}
    pre {{ padding:14px; overflow:auto; }}
    .hero {{ min-height:64vh; display:grid; align-content:center; gap:22px; }}
    .stats, .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:14px; }}
    .card, details {{ min-width:0; border:1px solid var(--border); background:var(--surface); border-radius:8px; padding:18px; box-shadow:0 18px 55px rgba(0,0,0,.22); }}
    .card strong {{ display:block; font-size:24px; margin-bottom:6px; }}
    .badge {{ display:inline-block; width:max-content; border:1px solid var(--border); border-radius:999px; padding:5px 10px; color:var(--teal); font-size:13px; }}
    .demo-shell {{ display:grid; grid-template-columns:minmax(220px,300px) 1fr; gap:18px; align-items:stretch; }}
    .timeline {{ border:1px solid var(--border); border-radius:8px; background:var(--surface); padding:12px; max-height:520px; overflow:auto; }}
    .timeline button {{ width:100%; display:grid; grid-template-columns:34px 1fr; gap:10px; align-items:center; text-align:left; margin:0 0 8px; border:1px solid transparent; background:transparent; color:var(--text); padding:10px; border-radius:6px; cursor:pointer; }}
    .timeline button:hover, .timeline button:focus-visible {{ border-color:var(--teal); outline:none; }}
    .timeline button.active {{ background:var(--surface2); border-color:var(--teal); }}
    .step-index {{ display:grid; place-items:center; width:28px; height:28px; border-radius:999px; background:#2a3038; color:var(--teal); font-size:13px; }}
    .active .step-index {{ background:var(--teal); color:#08110f; }}
    .progress-wrap {{ height:8px; border:1px solid var(--border); background:#0c0d10; border-radius:999px; overflow:hidden; margin:0 0 14px; }}
    .progress {{ height:100%; width:0; background:var(--green); transition:width .28s ease; }}
    .panel-stage {{ border:1px solid var(--border); border-radius:8px; background:var(--surface); padding:18px; min-height:360px; position:relative; overflow:hidden; }}
    .panel-stage::before {{ content:""; position:absolute; inset:0 0 auto; height:4px; background:var(--teal); }}
    .panel {{ display:none; animation:panelIn .28s ease both; }}
    .panel.active-panel {{ display:block; }}
    .panel[hidden] {{ display:none; }}
    .panel strong {{ display:block; color:var(--text); font-size:24px; margin:6px 0 10px; }}
    .evidence-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:10px; margin-top:18px; }}
    .metric {{ min-width:0; border:1px solid var(--border); border-radius:8px; padding:12px; background:var(--surface2); }}
    .metric span {{ color:var(--muted); font-size:12px; display:block; }}
    .metric b {{ display:block; margin-top:4px; }}
    .status-line {{ margin-top:14px; color:var(--muted); min-height:24px; }}
    [data-reveal] {{ opacity:0; transform:translateY(10px); transition:opacity .4s ease, transform .4s ease; }}
    [data-reveal].visible {{ opacity:1; transform:none; }}
    table {{ width:100%; border-collapse:collapse; overflow:hidden; border-radius:8px; }}
    th, td {{ border-bottom:1px solid var(--border); padding:12px; text-align:left; }}
    footer {{ border-top:1px solid var(--border); padding:28px 20px; color:var(--muted); text-align:center; }}
    a {{ color:var(--teal); }}
    @keyframes panelIn {{ from {{ opacity:0; transform:translateY(8px); }} to {{ opacity:1; transform:none; }} }}
    @media (max-width:760px) {{
      nav {{ padding:12px 16px; }}
      main {{ width:100%; max-width:100vw; padding:30px 14px; overflow:hidden; }}
      section, .hero, .stats, .grid, .demo-shell, .panel-stage, .timeline, .card, details {{ width:100%; max-width:100%; overflow:hidden; }}
      h1 {{ max-width:100%; overflow-wrap:anywhere; font-size:36px; }}
      p {{ width:300px; max-width:100%; }}
      .card p, .metric p {{ width:280px; max-width:100%; }}
      p, b, strong, code, summary, span {{ white-space:normal; word-break:normal; overflow-wrap:break-word; }}
      pre {{ max-width:100%; }}
      .stats, .grid, .evidence-grid {{ grid-template-columns:1fr; }}
      .demo-shell {{ grid-template-columns:1fr; }}
      .timeline {{ max-height:none; }}
    }}
    @media (prefers-reduced-motion: reduce) {{
      html {{ scroll-behavior:auto; }}
      *, *::before, *::after {{ animation:none !important; transition:none !important; }}
    }}
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
        <div class="card" data-reveal><strong>4</strong><p>Provider adapters generated from one source.</p></div>
        <div class="card" data-reveal><strong>1</strong><p>Canonical asset model for commands and workflows.</p></div>
        <div class="card" data-reveal><strong>2</strong><p>Approval gates before implementation and release actions.</p></div>
      </div>
    </section>
    <section id="problem">
      <h2>The Problem Before</h2>
      <div class="grid">
        <details open data-reveal><summary>Provider lock-in</summary><p>Assets often work only for one assistant and cannot move cleanly across teams.</p></details>
        <details data-reveal><summary>Unclear ownership</summary><p>Feedback arrives without enough context to triage, prioritize, or release.</p></details>
        <details data-reveal><summary>Manual drift</summary><p>Repeated copies diverge when commands, agents, and docs are maintained separately.</p></details>
      </div>
    </section>
    <section id="solution">
      <h2>The Solution</h2>
      <p>Canonical assets live once under assets, then adapters generate Claude, Codex, Gemini, and open-source outputs.</p>
    </section>
    <section id="interactive">
      <h2>Interactive</h2>
      <div class="progress-wrap" aria-hidden="true"><div class="progress" id="progress"></div></div>
      <div class="demo-shell">
        {interactive}
      </div>
      <p class="status-line" id="status" aria-live="polite"></p>
    </section>
  </main>
  <footer><a href="../docs/index.html">Portal</a> | <a href="../CONTRIBUTING.md">CONTRIBUTING.md</a></footer>
  <script>
    const buttons = Array.from(document.querySelectorAll("button[data-panel]"));
    const panels = Array.from(document.querySelectorAll("[data-content]"));
    const progress = document.getElementById("progress");
    const status = document.getElementById("status");
    function activate(index) {{
      buttons.forEach((button) => {{
        const active = Number(button.dataset.panel) === index;
        button.classList.toggle("active", active);
        button.setAttribute("aria-selected", active ? "true" : "false");
        button.tabIndex = active ? 0 : -1;
      }});
      panels.forEach((panel) => {{
        const active = Number(panel.dataset.content) === index;
        panel.hidden = !active;
        panel.classList.toggle("active-panel", active);
      }});
      if (progress) progress.style.width = `${{((index + 1) / Math.max(buttons.length, 1)) * 100}}%`;
      if (status && buttons[index]) status.textContent = `Showing ${{buttons[index].textContent.trim()}} of ${{buttons.length}}`;
    }}
    buttons.forEach((button, index) => {{
      button.setAttribute("role", "tab");
      button.addEventListener("click", () => activate(index));
      button.addEventListener("keydown", (event) => {{
        if (!["ArrowRight", "ArrowDown", "ArrowLeft", "ArrowUp", "Home", "End"].includes(event.key)) return;
        event.preventDefault();
        let next = index;
        if (event.key === "ArrowRight" || event.key === "ArrowDown") next = (index + 1) % buttons.length;
        if (event.key === "ArrowLeft" || event.key === "ArrowUp") next = (index - 1 + buttons.length) % buttons.length;
        if (event.key === "Home") next = 0;
        if (event.key === "End") next = buttons.length - 1;
        buttons[next].focus();
        activate(next);
      }});
    }});
    panels.forEach((panel) => panel.setAttribute("role", "tabpanel"));
    activate(0);
    const observer = new IntersectionObserver((entries) => entries.forEach((entry) => {{
      if (entry.isIntersecting) entry.target.classList.add("visible");
    }}), {{threshold:.12}});
    document.querySelectorAll("[data-reveal]").forEach((item) => observer.observe(item));
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
    .section-lede {{ max-width:760px; margin-top:-8px; }}
    .example-shell {{ display:grid; grid-template-columns:minmax(230px,320px) 1fr; gap:16px; align-items:stretch; }}
    .example-list {{ border:1px solid var(--border); background:var(--bg2); border-radius:8px; padding:10px; }}
    .example-button {{ width:100%; display:grid; grid-template-columns:30px 1fr; gap:10px; align-items:start; text-align:left; border:1px solid transparent; background:transparent; color:var(--text); border-radius:6px; padding:12px; cursor:pointer; }}
    .example-button:hover, .example-button:focus-visible, .example-button.active {{ border-color:var(--cyan); background:#0d1628; outline:none; }}
    .example-index {{ display:grid; place-items:center; width:26px; height:26px; border-radius:999px; background:#07111f; color:var(--cyan); font-size:12px; }}
    .example-button.active .example-index {{ background:var(--cyan); color:#04101a; }}
    .example-button strong {{ display:block; margin-bottom:3px; }}
    .example-button span:last-child {{ color:var(--muted); font-size:13px; line-height:1.4; }}
    .example-preview {{ border:1px solid var(--border); background:linear-gradient(180deg,#111827,#0b1220); border-radius:8px; padding:18px; min-height:360px; position:relative; overflow:hidden; }}
    .example-preview::before {{ content:""; position:absolute; inset:0 0 auto; height:3px; background:var(--cyan); }}
    .example-panel {{ display:none; animation:exampleIn .25s ease both; }}
    .example-panel.active-example {{ display:block; }}
    .example-kicker {{ color:var(--cyan); font-size:13px; margin:4px 0 8px; }}
    .example-command {{ margin:16px 0; }}
    .example-output {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:10px; margin-top:16px; }}
    .example-output div {{ border:1px solid var(--border); border-radius:8px; padding:12px; background:#070b14; }}
    .example-output span {{ display:block; color:var(--muted); font-size:12px; margin-bottom:4px; }}
    .muted {{ color:var(--muted); }}
    .badge {{ display:inline-block; border:1px solid var(--border); border-radius:999px; padding:5px 10px; color:var(--cyan); font-size:13px; }}
    input, select {{ width:100%; padding:11px 12px; border-radius:6px; border:1px solid var(--border); background:#070b14; color:var(--text); margin-bottom:14px; }}
    a {{ color:var(--cyan); }}
    code, pre {{ background:#070b14; border:1px solid var(--border); border-radius:8px; color:var(--text); }}
    pre {{ padding:16px; overflow:auto; }}
    footer {{ border-top:1px solid var(--border); padding:28px 20px; text-align:center; color:var(--muted); }}
    @keyframes exampleIn {{ from {{ opacity:0; transform:translateY(8px); }} to {{ opacity:1; transform:none; }} }}
    @media (max-width:760px) {{
      .example-shell {{ grid-template-columns:1fr; }}
      main {{ padding-left:16px; padding-right:16px; }}
    }}
  </style>
</head>
<body>
  <nav>
    <a href="#hero">Home</a><a href="#problem">Problem</a><a href="#quick-start">Quick Start</a><a href="#examples">Examples</a><a href="#providers">Providers</a>
    <a href="#licensing">Licensing</a><a href="#why-different">Why Different</a><a href="#publication">Publication</a><a href="#commands">Commands</a><a href="#agents">Agents</a><a href="#skills">Skills</a><a href="#context">Context</a><a href="#guides">Guides</a><a href="#reference">Reference</a>
  </nav>
  <main>
    <section id="hero" class="hero">
      <span class="badge">AGPLv3 Community Edition | Commercial License Available | Security | Governance | Defensive Publication</span>
      <h1>{PLATFORM}</h1>
      <p>Runtime-neutral agentic AI control plane for provider adapters, runtime contracts, human-blocking gates, durable state, and Graph Studio execution.</p>
      <p>AGPLv3 Community Edition with Commercial License options for proprietary, embedded, SaaS, OEM, and enterprise procurement use.</p>
      <div id="stats" class="grid"></div>
    </section>
    <section id="architecture">
      <h2>Runtime-Neutral Architecture</h2>
      <p class="section-lede">Canonical assets generate one neutral contract, then project into providers, runtimes, Graph Studio, and release evidence.</p>
      <div class="grid">
        <div class="card" data-reveal><h3>Canonical Assets</h3><p>Agents, skills, commands, workflows, and repo context under <code>assets/</code>.</p></div>
        <div class="card" data-reveal><h3>Nunneri Runtime Contract</h3><p>Generated neutral JSON for phases, edges, approvals, context, and observability hints.</p></div>
        <div class="card" data-reveal><h3>Providers and Runtimes</h3><p>Claude, Codex, Gemini, open-source exports, LangGraph, CrewAI, AutoGen, and Semantic Kernel.</p></div>
        <div class="card" data-reveal><h3>Graph Studio and State</h3><p>FastAPI, provider routing, PostgreSQL-backed runs, RBAC, approvals, traces, and final summaries.</p></div>
        <div class="card" data-reveal><h3>Trust Layer</h3><p>Security, governance, roadmap, citation, release packaging, licensing, and defensive publication stay aligned.</p></div>
      </div>
    </section>
    <section id="licensing">
      <h2>Licensing</h2>
      <div class="grid">
        <div class="card" data-reveal><h3>AGPLv3 Community Edition</h3><p>Use, modify, and distribute under AGPLv3. Review network-use source-sharing obligations before modified hosted deployments.</p></div>
        <div class="card" data-reveal><h3>Commercial License</h3><p>Contact core@nunneri.com for proprietary, embedded, hosted, managed-service, indemnity, or enterprise procurement terms.</p></div>
        <div class="card" data-reveal><h3>Originators</h3><p>Nunneri was originated by Suranku and Yamini and is stewarded by the Nunneri Core Team.</p></div>
      </div>
    </section>
    <section id="publication">
      <h2>Architecture and Defensive Publication</h2>
      <div class="grid">
        <div class="card" data-reveal><h3>Architecture</h3><p><a href="reference/ARCHITECTURE.md">ARCHITECTURE.md</a> documents the runtime-neutral control plane, Graph Studio, RBAC, and storage boundaries.</p></div>
        <div class="card" data-reveal><h3>Defensive Publication</h3><p><a href="reference/DEFENSIVE_PUBLICATION.md">DEFENSIVE_PUBLICATION.md</a> documents implementation-level public disclosure. Do not use patent-pending language unless an application has been filed.</p></div>
        <div class="card" data-reveal><h3>Project Trust</h3><p><a href="reference/SECURITY.md">Security</a>, <a href="reference/GOVERNANCE.md">governance</a>, <a href="reference/ROADMAP.md">roadmap</a>, and <a href="reference/CITATION.cff">citation</a> records are part of the release posture.</p></div>
      </div>
    </section>
    <section id="why-different">
      <h2>Why Nunneri is different</h2>
      <div class="grid">
        <div class="card" data-reveal><h3>Neutral source of truth</h3><p>Canonical assets generate provider files, runtime exports, and Graph Studio metadata from the same contract.</p></div>
        <div class="card" data-reveal><h3>Human gates are control flow</h3><p>Approval phases pause execution and resume only through explicit approve or reject actions.</p></div>
        <div class="card" data-reveal><h3>State outside the model</h3><p>Threads, runs, node outputs, approvals, errors, timing, and summaries are persisted outside the LLM context window.</p></div>
        <div class="card" data-reveal><h3>Tenant-aware execution</h3><p>RBAC scopes dispatch, history, phase configuration, and approvals across organization, team, project, thread, and run boundaries.</p></div>
      </div>
    </section>
    <section id="problem">
      <h2>Why This Exists</h2>
      <div class="grid">
        <details open><summary>Before: assets trapped in one assistant</summary><p>After: canonical assets generate provider-specific outputs.</p></details>
        <details><summary>Before: unclear feedback paths</summary><p>After: GitHub Issues collect provider, priority, asset type, and release target.</p></details>
        <details><summary>Before: manual release notes</summary><p>After: issues and labels drive changelog and release readiness checks.</p></details>
        <details><summary>Before: duplicated prompts drift</summary><p>After: adapters are rebuilt from one source of truth.</p></details>
        <details><summary>Before: repo instructions vary by assistant</summary><p>After: one context template renders provider-native root files and structured override manifests.</p></details>
      </div>
    </section>
    <section id="quick-start">
      <h2>Quick Start</h2>
      <pre><code>git clone https://{REPO_URL}
cd nunneri-public-agentic-ai
python3 scripts/build_adapters.py
./install.sh --provider all --project --force</code></pre>
    </section>
    <section id="examples">
      <h2>Examples</h2>
      <p class="section-lede">Switch between common rollout paths and see the exact command, artifact target, and validation signal for each one.</p>
      <div class="example-shell" data-reveal>
        <div class="example-list" role="tablist" aria-label="Example workflows">
          <button class="example-button active" data-example="0" role="tab" aria-selected="true" aria-controls="example-panel-0" tabindex="0"><span class="example-index">1</span><span><strong>Preview Context</strong>Inspect root context writes first.</span></button>
          <button class="example-button" data-example="1" role="tab" aria-selected="false" aria-controls="example-panel-1" tabindex="-1"><span class="example-index">2</span><span><strong>Install Claude</strong>Write provider context safely.</span></button>
          <button class="example-button" data-example="2" role="tab" aria-selected="false" aria-controls="example-panel-2" tabindex="-1"><span class="example-index">3</span><span><strong>Run Triage</strong>Route a defect through workflow assets.</span></button>
          <button class="example-button" data-example="3" role="tab" aria-selected="false" aria-controls="example-panel-3" tabindex="-1"><span class="example-index">4</span><span><strong>Export Runtime</strong>Generate LangGraph artifacts.</span></button>
          <button class="example-button" data-example="4" role="tab" aria-selected="false" aria-controls="example-panel-4" tabindex="-1"><span class="example-index">5</span><span><strong>Verify Consumer</strong>Smoke-test install behavior.</span></button>
          <button class="example-button" data-example="5" role="tab" aria-selected="false" aria-controls="example-panel-5" tabindex="-1"><span class="example-index">6</span><span><strong>End-User Setup</strong>Walk through state and tracing.</span></button>
        </div>
        <div class="example-preview">
          <article class="example-panel active-example" id="example-panel-0" data-example-panel="0" role="tabpanel">
            <p class="example-kicker">Project context preview</p>
            <h3>See root context targets without writing files.</h3>
            <pre class="example-command"><code>./install.sh --provider claude --project --context-only --dry-run</code></pre>
            <div class="example-output"><div><span>Writes</span><strong>None</strong></div><div><span>Shows</span><strong>CLAUDE.md root target</strong></div><div><span>Use before</span><strong>Overwriting repo context</strong></div></div>
          </article>
          <article class="example-panel" id="example-panel-1" data-example-panel="1" role="tabpanel" hidden>
            <p class="example-kicker">Provider context install</p>
            <h3>Install Claude context at the consumer repository root.</h3>
            <pre class="example-command"><code>./install.sh --provider claude --project --context-only --force</code></pre>
            <div class="example-output"><div><span>Root file</span><strong>CLAUDE.md</strong></div><div><span>Metadata</span><strong>.ai-assets-version</strong></div><div><span>Provider assets</span><strong>Skipped by filter</strong></div></div>
          </article>
          <article class="example-panel" id="example-panel-2" data-example-panel="2" role="tabpanel" hidden>
            <p class="example-kicker">Workflow command</p>
            <h3>Start triage from a real ticket and symptom.</h3>
            <pre class="example-command"><code>/triage NUN-1024 "Checkout API returns 500 after deploy" --provider claude</code></pre>
            <div class="example-output"><div><span>Workflow</span><strong>Nine-phase triage</strong></div><div><span>Gates</span><strong>RCA and release impact</strong></div><div><span>Output</span><strong>Evidence-backed action</strong></div></div>
          </article>
          <article class="example-panel" id="example-panel-3" data-example-panel="3" role="tabpanel" hidden>
            <p class="example-kicker">Runtime export</p>
            <h3>Install LangGraph graph and manifest exports.</h3>
            <pre class="example-command"><code>./install.sh --runtime langgraph --project --force</code></pre>
            <div class="example-output"><div><span>Target</span><strong>.langgraph/</strong></div><div><span>Graph</span><strong>triage-nine-phase.json</strong></div><div><span>Context</span><strong>Pre-dispatch manifest</strong></div></div>
          </article>
          <article class="example-panel" id="example-panel-4" data-example-panel="4" role="tabpanel" hidden>
            <p class="example-kicker">Consumer verification</p>
            <h3>Prove installs work in a clean temporary repository.</h3>
            <pre class="example-command"><code>python3 scripts/check_consumer_install.py</code></pre>
            <div class="example-output"><div><span>Checks</span><strong>Dry-run and force</strong></div><div><span>Providers</span><strong>Claude context</strong></div><div><span>Runtime</span><strong>LangGraph export</strong></div></div>
          </article>
          <article class="example-panel" id="example-panel-5" data-example-panel="5" role="tabpanel" hidden>
            <p class="example-kicker">Stateful runtime setup</p>
            <h3>Guide users through provider install, LangGraph state, and tracing.</h3>
            <pre class="example-command"><code>NUNNERI_RUNTIME=langgraph
NUNNERI_STATE_STORE=sqlite
NUNNERI_TRACE_MODE=otel</code></pre>
            <div class="example-output"><div><span>Guide</span><strong><a href="reference/guides/end-user-langgraph-setup.md">Read setup</a></strong></div><div><span>Demo</span><strong><a href="reference/guides/end-user-setup-demo.html">Open walkthrough</a></strong></div><div><span>Optional UI</span><strong>LangSmith via opt-in key</strong></div></div>
          </article>
        </div>
      </div>
    </section>
    <section id="providers">
      <h2>Providers</h2>
      <div class="grid">
        <div class="card" data-reveal><h3>Claude Code</h3><p>Claude-compatible agents, commands, skills, and CLAUDE.md.</p></div>
        <div class="card" data-reveal><h3>Codex</h3><p>Codex-ready skills, workflows, prompts, and AGENTS.md.</p></div>
        <div class="card" data-reveal><h3>Gemini</h3><p>Gemini prompts, workflows, command mappings, and GEMINI.md.</p></div>
        <div class="card" data-reveal><h3>Open Source</h3><p>Portable manifests, prompts, and workflow definitions.</p></div>
        <div class="card" data-reveal><h3>LangGraph Runtime</h3><p>Graph and runtime manifests for stateful workflow orchestration. LangGraph is not a model provider.</p></div>
      </div>
    </section>
    <section id="commands">
      <h2>Commands</h2>
      <input id="search" placeholder="Filter commands, agents, or skills">
      <div id="command-list" class="grid"></div>
    </section>
    <section id="agents"><h2>Agents</h2><div id="agent-list" class="grid"></div></section>
    <section id="skills"><h2>Skills</h2><div id="skill-list" class="grid"></div></section>
    <section id="context">
      <h2>Repository Context</h2>
      <div class="grid">
        <div class="card" data-reveal><h3>Standard Template</h3><p>One provider-neutral template generates CLAUDE.md, AGENTS.md, GEMINI.md, open-source context metadata, and LangGraph pre-dispatch context.</p></div>
        <div class="card" data-reveal><h3>Override Registry</h3><p>Structured YAML captures known issues, DevOps overrides, library links, workflow overrides, exceptions, skill overrides, dispatch rules, and approval gates.</p></div>
      </div>
    </section>
    <section id="guides"><h2>Interactive Guides</h2><div id="guide-list" class="grid"></div></section>
    <section id="reference">
      <h2>Reference Documents</h2>
      <div class="grid">
        <div class="card"><h3>Executive Summaries</h3><p><a href="reference/guides/triage-executive-summary.md">Triage</a></p><p><a href="reference/guides/compliance-executive-summary.md">Compliance</a></p><p><a href="reference/guides/schema-lineage-executive-summary.md">Schema and Lineage</a></p></div>
        <div class="card"><h3>Templates and References</h3><p><a href="reference/AI_ASSETS.md">AI_ASSETS.md</a></p><p><a href="reference/ARCHITECTURE.md">Architecture</a></p><p><a href="reference/DEFENSIVE_PUBLICATION.md">Defensive Publication</a></p><p><a href="reference/COMMERCIAL_LICENSE.md">Commercial License</a></p><p><a href="reference/TRADEMARKS.md">Trademark Policy</a></p><p><a href="reference/SECURITY.md">Security Policy</a></p><p><a href="reference/GOVERNANCE.md">Governance</a></p><p><a href="reference/ROADMAP.md">Roadmap</a></p><p><a href="reference/CITATION.cff">Citation</a></p><p><a href="reference/context/repo-agent-instructions.md">Repo Agent Instructions</a></p><p><a href="reference/guides/end-user-langgraph-setup.md">End-User LangGraph Setup</a></p><p><a href="reference/guides/end-user-setup-demo.html">End-User Setup Demo</a></p><p><a href="reference/guides/runtime-contract-demo.html">Runtime Contract Demo</a></p><p><a href="reference/examples/consumer-repo/README.md">Consumer Repo Example</a></p><p><a href="reference/examples/runtime-contract-consumer/README.md">Runtime Contract Consumer</a></p><p><a href="reference/CONTRIBUTING.md">CONTRIBUTING.md</a></p><p><a href="reference/RELEASE.md">RELEASE.md</a></p><p><a href="reference/langgraph-runtime.md">LangGraph Runtime</a></p></div>
      </div>
    </section>
  </main>
  <footer>{PLATFORM} | <a href="reference/CONTRIBUTING.md">Contribute</a></footer>
  <script>
    const fallback = {{counts:{{agents:0,commands:0,skills:0,workflows:0,context:1,providers:4,runtimes:1,guides:8}}, agents:[], commands:[], skills:[], guides:[]}};
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
    const exampleButtons = Array.from(document.querySelectorAll("[data-example]"));
    const examplePanels = Array.from(document.querySelectorAll("[data-example-panel]"));
    function activateExample(index) {{
      exampleButtons.forEach((button) => {{
        const active = Number(button.dataset.example) === index;
        button.classList.toggle("active", active);
        button.setAttribute("aria-selected", active ? "true" : "false");
        button.tabIndex = active ? 0 : -1;
      }});
      examplePanels.forEach((panel) => {{
        const active = Number(panel.dataset.examplePanel) === index;
        panel.hidden = !active;
        panel.classList.toggle("active-example", active);
      }});
    }}
    exampleButtons.forEach((button, index) => {{
      button.addEventListener("click", () => activateExample(index));
      button.addEventListener("keydown", (event) => {{
        if (!["ArrowRight", "ArrowDown", "ArrowLeft", "ArrowUp", "Home", "End"].includes(event.key)) return;
        event.preventDefault();
        let next = index;
        if (event.key === "ArrowRight" || event.key === "ArrowDown") next = (index + 1) % exampleButtons.length;
        if (event.key === "ArrowLeft" || event.key === "ArrowUp") next = (index - 1 + exampleButtons.length) % exampleButtons.length;
        if (event.key === "Home") next = 0;
        if (event.key === "End") next = exampleButtons.length - 1;
        exampleButtons[next].focus();
        activateExample(next);
      }});
    }});
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


EXAMPLE_INVOCATIONS = {
    "check-logging": '/check-logging src/payments --provider claude',
    "column-trace": '/column-trace customer_id reports/revenue.sql --provider gemini',
    "devhub-fix": '/devhub-fix \'{"finding":"missing correlation id","repo":"payments-api"}\' --provider gemini',
    "exception-handling": '/exception-handling services/checkout --provider claude',
    "generate-agent-context": '/generate-agent-context . --provider codex',
    "impact-analysis": '/impact-analysis orders.customer_id --provider codex',
    "ingestion-check": '/ingestion-check orders-topic --provider claude',
    "nfr-readiness": '/nfr-readiness services/reporting --provider codex',
    "pipeline-health": '/pipeline-health prod orders-ingestion --provider codex',
    "release-lookup": '/release-lookup payments-api v1.8.0 --provider gemini',
    "report-lineage": '/report-lineage revenue-dashboard --provider claude',
    "schema-drift": '/schema-drift ddl/orders.sql --provider claude',
    "prodops-triage": '/prodops-triage INC-204 prod "Kafka consumer lag exceeded threshold" --provider codex',
    "triage": '/triage NUN-1024 "Checkout API returns 500 after deploy" --provider claude',
}


def executive_summary(title: str, commands: list[str]) -> str:
    if title == "Triage":
        examples = "\n".join(EXAMPLE_INVOCATIONS.get(cmd, f"/{cmd} --project . --provider claude") for cmd in commands[:3])
        return f"""> **One-liner:** Triage gives teams a provider-neutral nine-phase workflow for moving from symptom to evidence, approved fix plan, validation, and release impact.

## The Problem Before

Teams duplicated triage prompts for each assistant, mixed diagnosis with implementation, and often skipped approval gates before edits or release actions.

## The Solution

Canonical triage assets define one stable nine-phase workflow. Claude, Codex, Gemini, open-source exports, and LangGraph runtime manifests are generated from the same source of truth.

## Command Reference

| Command | What it does | When to use |
| --- | --- | --- |
| `/triage` | Runs bug triage from intake through RCA and approval gates | Use for application bugs or unclear symptoms |
| `/prodops-triage` | Classifies incidents and determines whether a runbook or defect is needed | Use for production incidents or environment-specific failures |
| `/devhub-fix` | Fixes a governance finding with test-first validation and approval gates | Use when DevHub or governance JSON identifies a remediable issue |

## How It Works

```text
1 intake
  -> 2 context load
  -> 3 classification
  -> 4 evidence collection
  -> 5 root cause analysis
  -> 6 gate 1: RCA and fix plan approval
  -> 7 test-first fix
  -> 8 validation
  -> 9 gate 2: summary and release impact
```

Post-triage actions such as commit, push, PR creation, release tagging, and publishing require explicit human confirmation.

## Real Examples

```text
{examples}
```
"""

    rows = "\n".join(f"| `/{cmd}` | Runs the {cmd} workflow | Use when the request maps to {cmd} |" for cmd in commands)
    examples = "\n".join(EXAMPLE_INVOCATIONS.get(cmd, f"/{cmd} --project . --provider claude") for cmd in commands[:3])
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
        "assets/skills", "assets/context", "assets/commands/triage", "assets/commands/analysis", "assets/commands/compliance", "assets/commands/operations", "assets/commands/reporting",
        "assets/workflows", "adapters/claude/agents", "adapters/claude/skills", "adapters/claude/commands",
        "adapters/codex/skills", "adapters/codex/prompts", "adapters/codex/workflows",
        "adapters/gemini/prompts", "adapters/gemini/workflows", "adapters/gemini/context",
        "adapters/langgraph",
        "adapters/open-source/manifests", "adapters/open-source/prompts", "adapters/open-source/workflows",
        "guides", "docs/assets", "scripts", "dist/claude", "dist/codex", "dist/gemini", "dist/langgraph", "dist/open-source",
        ".github/ISSUE_TEMPLATE", ".github/workflows",
    ]
    for directory in dirs:
        (ROOT / directory).mkdir(parents=True, exist_ok=True)
        readme(f"{directory}/README.md", directory)

    write("assets/context/repo-agent-instructions.md", f"""---
name: repo-agent-instructions
description: Standard repository agent instruction template
category: context
providers:
  claude:
    enabled: true
  codex:
    enabled: true
  gemini:
    enabled: true
  open_source:
    enabled: true
runtimes:
  langgraph:
    enabled: true
---

# Repository Agent Instructions

> Generated from `assets/context/repo-agent-instructions.md`. Customize a repo-local copy when installing into a consuming repository.

## Repository Identity and Ownership

- Repository: set the repository name here.
- Owner: set the owning team or maintainer here.
- Primary domain: describe the business or platform area.
- Primary contacts: link team channel, issue tracker, on-call page, or ownership doc.

## Golden Setup, Build, and Test Commands

- Setup: document the standard dependency installation command.
- Build: document the standard build command.
- Test: document the standard unit and integration test commands.
- Validation: document required lint, static analysis, schema, security, or release checks.
- Local services: list required local services, ports, credentials, and safe defaults.

## Common Library and Source-Code Links

- Add links to shared libraries, generated clients, framework extensions, schemas, and platform contracts.
- Prefer repository-relative paths for local code and canonical URLs for external source of truth.
- Include ownership or escalation notes when a shared dependency is outside this repository.

## Known Issues and Recurring Failure Modes

- Record known flaky tests, framework quirks, migration hazards, data issues, and operational failure modes.
- Include detection signals, safe workarounds, and links to tracking issues.
- Do not treat a known issue as permission to ignore a failing check unless an explicit override says so.

## DevOps and Environment Overrides

- List environment-specific rules for CI, deployment, secrets, feature flags, queues, topics, databases, and cloud resources.
- Call out commands that are forbidden, require approval, or must run only in sandboxed environments.
- Include rollback, cleanup, and operational safety notes for changes that affect runtime infrastructure.

## Agentic Workflow Overrides

- State repo-specific workflow changes that should be applied before dispatching an agent or command.
- Keep global workflow gates intact unless the override explicitly strengthens them.
- Repo overrides must not weaken human approval gates for code changes, publishing, production access, or release-impacting operations.

## Exception Handling and Escalation Rules

- Define exceptions to normal workflow, including emergency fixes, read-only investigations, production incidents, and compliance holds.
- Each exception should describe trigger conditions, allowed actions, required evidence, approver, and expiration or review policy.
- If an exception conflicts with provider-neutral governance, stop and ask for human approval.

## Skill Invocation Overrides

- Map repo-specific file patterns, services, languages, or commands to preferred skills.
- Use overrides to add context before a skill runs, not to bypass the skill's safety rules.
- When multiple skills match, prefer the most specific repo override, then the canonical command or workflow default.

## Agent Dispatch Rules Before Task Routing

- Load this repository instruction file before selecting a specialized agent.
- Apply known issues, DevOps overrides, exceptions, and skill overrides before dispatch.
- If a task matches a restricted area, stop at the appropriate approval gate before changing files or running side-effectful commands.

## Approval Gates and Release-Impact Rules

- Require explicit human approval before implementation changes, production-affecting commands, release tagging, publishing, or pushing.
- Summarize changed files, validation results, release impact, rollback notes, and open risks before release-impacting actions.
- For read-only work, complete evidence gathering and stop with findings unless the user explicitly authorizes changes.

## Provider-Specific Instruction Overrides

Use this section only for behavior that is specific to one assistant or runtime surface. Keep shared repository rules in the provider-neutral sections above.

### Claude Code

- Add Claude-only phrases, slash-command conventions, subagent routing terms, and behaviors here.
- Example: if this repo uses the phrase `agent team` to trigger a Claude-specific behavior, define that behavior here and do not repeat it in Codex or Gemini sections.

### Codex

- Add Codex-only AGENTS.md guidance, coding-agent workflow preferences, sandbox expectations, and tool-use constraints here.
- Do not copy Claude-specific trigger phrases unless Codex should intentionally interpret them.

### Gemini

- Add Gemini-only prompt, workflow, and context-loading guidance here.
- Keep Gemini CLI command behavior separate from Claude slash-command behavior.

### Open Source

- Add runtime-neutral or framework-specific guidance for open-source agent consumers here.
- Keep SDK-specific behavior optional unless the consuming repo explicitly adopts that framework.

## Structured Override Registry

```yaml
repo_agent_instructions:
  version: 1
  known_issues: []
  devops_overrides: []
  library_sources: []
  workflow_overrides: []
  exceptions: []
  skill_overrides: []
  dispatch_overrides: []
  provider_overrides:
    claude: []
    codex: []
    gemini: []
    open_source: []
  approval_gates:
    - name: implementation_changes
      required: true
      applies_to:
        - code_changes
        - generated_outputs
        - release_metadata
    - name: production_or_release_actions
      required: true
      applies_to:
        - production_access
        - push
        - pull_request
        - release_tag
        - publish
```
""")

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
    write("scripts/README.md", """# scripts

This directory is part of the Nunneri AI Assets repository.

## Release Packaging

- `package_release.py` builds versioned internal release archives under `dist/releases/`.
- `check_release_package.py` verifies the archives contain installer payloads, generated provider outputs, LangGraph runtime exports, reference docs, and consumer examples.

Run both from a `release/vX.Y.Z` branch before tagging:

```bash
python3 scripts/package_release.py
python3 scripts/check_release_package.py
```
""")

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
''', True)

    write("scripts/build_adapters.py", r'''#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROVIDERS = ("claude", "codex", "gemini", "open-source")
RUNTIMES = ("nunneri-runtime", "langgraph", "crewai", "autogen", "semantic-kernel")
CONTRACT_VERSION = "1.0"
PROVIDER_OVERRIDE_HEADINGS = {
    "claude": "### Claude Code",
    "codex": "### Codex",
    "gemini": "### Gemini",
}

TRIAGE_NINE_PHASE_CONTRACT = {
    "contract_version": CONTRACT_VERSION,
    "name": "triage-nine-phase",
    "kind": "workflow",
    "description": "Nine Phase Triage Workflow",
    "source": "assets/workflows/triage-nine-phase.md",
    "inputs": [],
    "agents": [],
    "commands": [],
    "nodes": [
        {
            "id": "intake",
            "label": "Intake",
            "phase": 1,
            "type": "work",
            "prompt": "",
            "description": "Capture the reported issue, requested outcome, environment, and constraints.",
            "instructions": "Normalize the request into a clear problem statement and list missing information without starting implementation.",
            "expected_outputs": ["problem_statement", "scope", "missing_context"],
        },
        {
            "id": "context_load",
            "label": "Context Load",
            "phase": 2,
            "type": "work",
            "prompt": "",
            "description": "Load repository context, previous decisions, relevant docs, and current workspace state.",
            "instructions": "Read the smallest useful set of files and summarize repository conventions before choosing an approach.",
            "expected_outputs": ["relevant_files", "repo_conventions", "current_state"],
        },
        {
            "id": "classification",
            "label": "Classification",
            "phase": 3,
            "type": "work",
            "prompt": "",
            "description": "Classify the request so the workflow can dispatch the right agent, command, or runtime path.",
            "instructions": "Identify the primary work category, risk level, affected runtime/provider, and whether human approval is needed.",
            "classification_options": [
                "code",
                "configuration",
                "data",
                "schema",
                "infrastructure",
                "dependency",
                "framework_or_runtime",
                "documentation_or_asset_metadata",
                "unknown",
            ],
            "expected_outputs": ["category", "risk", "runtime_or_provider", "approval_required"],
        },
        {
            "id": "evidence_collection",
            "label": "Evidence Collection",
            "phase": 4,
            "type": "work",
            "prompt": "",
            "description": "Gather concrete evidence before proposing root cause or changes.",
            "instructions": "Use local validation, logs, generated artifacts, and source references to support the diagnosis.",
            "expected_outputs": ["evidence", "commands_run", "observed_failures"],
        },
        {
            "id": "root_cause_analysis",
            "label": "Root Cause Analysis",
            "phase": 5,
            "type": "work",
            "prompt": "",
            "description": "Explain the root cause and produce a focused implementation plan.",
            "instructions": "Tie each proposed change to evidence and state what will not be changed.",
            "expected_outputs": ["root_cause", "fix_plan", "non_goals"],
        },
        {
            "id": "gate_1",
            "label": "Gate 1: RCA and Fix Plan Approval",
            "phase": 6,
            "type": "human_approval",
            "prompt": "",
            "description": "Human review checkpoint before implementation changes begin.",
            "instructions": "Pause the runtime and wait for an explicit approve or reject decision.",
            "expected_outputs": ["approval_decision", "reviewer_reason"],
            "approval": {
                "required": True,
                "actions": ["approve", "reject"],
                "on_reject": "cancel",
                "question": "Approve the root cause analysis and fix plan before implementation?",
                "required_context": ["root_cause", "fix_plan", "evidence"],
                "allowed_before_approval": ["read_context", "collect_evidence", "draft_plan"],
                "blocked_before_approval": ["edit_files", "run_release", "publish"],
            },
        },
        {
            "id": "test_first_fix",
            "label": "Test-First Fix",
            "phase": 7,
            "type": "work",
            "prompt": "",
            "description": "Create or update focused validation before applying the implementation change.",
            "instructions": "Add the smallest meaningful test or check, then make the implementation pass it.",
            "expected_outputs": ["test_or_check", "implementation_change", "files_changed"],
        },
        {
            "id": "validation",
            "label": "Validation",
            "phase": 8,
            "type": "work",
            "prompt": "",
            "description": "Run the required checks and summarize remaining risk.",
            "instructions": "Execute repository validation commands and explain any skipped checks with reasons.",
            "expected_outputs": ["validation_commands", "results", "residual_risk"],
        },
        {
            "id": "gate_2",
            "label": "Gate 2: Summary and Release Impact",
            "phase": 9,
            "type": "human_approval",
            "prompt": "",
            "description": "Human review checkpoint before release-impact actions.",
            "instructions": "Pause the runtime before commit, push, pull request, tagging, or publish actions.",
            "expected_outputs": ["approval_decision", "release_impact_summary"],
            "approval": {
                "required": True,
                "actions": ["approve", "reject"],
                "on_reject": "cancel",
                "question": "Approve the validation summary and release-impact actions?",
                "required_context": ["validation_results", "files_changed", "release_impact"],
                "allowed_before_approval": ["summarize_validation", "draft_release_notes"],
                "blocked_before_approval": ["commit", "push", "pull_request", "release_tag", "publish"],
            },
        },
    ],
    "edges": [
        {"from": "intake", "to": "context_load"},
        {"from": "context_load", "to": "classification"},
        {"from": "classification", "to": "evidence_collection"},
        {"from": "evidence_collection", "to": "root_cause_analysis"},
        {"from": "root_cause_analysis", "to": "gate_1"},
        {"from": "gate_1", "to": "test_first_fix", "condition": "approved"},
        {"from": "test_first_fix", "to": "validation"},
        {"from": "validation", "to": "gate_2"},
    ],
    "post_triage_actions": ["commit", "push", "pull_request", "release_tag", "publish"],
    "context": {"injection_stage": "pre_dispatch", "source": "assets/context/repo-agent-instructions.md"},
    "runtime_hints": {"stateful": True, "human_in_loop": True, "observability": ["events", "runs", "nodes"]},
}


def frontmatter_and_body(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    end = text.find("\n---", 4)
    if end == -1:
        raise ValueError(f"{path}: unterminated YAML frontmatter")
    data: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" in line and not line.startswith(" "):
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip()
    return data, text[end + 4:].strip()


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")


def structured_override_block(body: str) -> str:
    start = body.find("```yaml\n")
    if start == -1:
        return ""
    start += len("```yaml\n")
    end = body.find("\n```", start)
    if end == -1:
        return ""
    return body[start:end].strip()


def provider_context_body(body: str, provider: str) -> str:
    body = body.replace("# Repository Agent Instructions\n\n", "", 1)
    body = body.replace("> Generated from `assets/context/repo-agent-instructions.md`. Customize a repo-local copy when installing into a consuming repository.\n\n", "", 1)
    section = "\n## Provider-Specific Instruction Overrides\n"
    structured = "\n## Structured Override Registry\n"
    section_start = body.find(section)
    structured_start = body.find(structured)
    if section_start == -1 or structured_start == -1 or structured_start < section_start:
        return body
    common = body[:section_start].rstrip()
    provider_area = body[section_start:structured_start]
    structured_body = body[structured_start:].lstrip()
    heading = PROVIDER_OVERRIDE_HEADINGS[provider]
    provider_start = provider_area.find(heading)
    if provider_start == -1:
        selected = ""
    else:
        next_start = provider_area.find("\n### ", provider_start + 1)
        selected = provider_area[provider_start: next_start if next_start != -1 else len(provider_area)].strip()
    provider_section = f"## Provider-Specific Instruction Overrides\n\n{selected}" if selected else "## Provider-Specific Instruction Overrides\n\n- No provider-specific overrides are defined."
    return f"{common}\n\n{provider_section}\n\n{structured_body}".strip()


def build_context() -> None:
    src = ROOT / "assets/context/repo-agent-instructions.md"
    data, body = frontmatter_and_body(src)
    provider_files = {
        "claude": ("CLAUDE.md", "Claude Repository Context"),
        "codex": ("AGENTS.md", "Codex Repository Context"),
        "gemini": ("GEMINI.md", "Gemini Repository Context"),
    }
    for provider, (filename, title) in provider_files.items():
        provider_body = provider_context_body(body, provider)
        content = f"""# {title}

> Generated from `{src.relative_to(ROOT)}`. Edit the canonical context template, then rebuild adapters.

{provider_body}
"""
        write(ROOT / f"dist/{provider}" / filename, content)
    structured = structured_override_block(body)
    payload = {
        "name": data["name"],
        "description": data["description"],
        "category": data.get("category", "context"),
        "source": str(src.relative_to(ROOT)),
        "body": body,
        "structured_overrides": structured,
    }
    write(ROOT / "dist/open-source/manifests/context/repo-agent-instructions.json", json.dumps(payload, indent=2))
    write(ROOT / "dist/langgraph/context/repo-agent-instructions.json", json.dumps({**payload, "runtime": "langgraph", "injection_stage": "pre_dispatch"}, indent=2))
    neutral = build_neutral_context(src, data, body, structured)
    write(ROOT / "dist/crewai/context/repo-agent-instructions.json", json.dumps({**neutral, "runtime": "crewai"}, indent=2))
    write(ROOT / "dist/autogen/context/repo-agent-instructions.json", json.dumps({**neutral, "runtime": "autogen"}, indent=2))
    write(ROOT / "dist/semantic-kernel/context/repo-agent-instructions.json", json.dumps({**neutral, "runtime": "semantic-kernel"}, indent=2))


def reset_dist() -> None:
    for target_name in PROVIDERS + RUNTIMES:
        target = ROOT / "dist" / target_name
        if target.exists():
            shutil.rmtree(target)
        target.mkdir(parents=True, exist_ok=True)


def neutral_base(src: Path, data: dict[str, str], body: str, kind: str) -> dict:
    return {
        "contract_version": CONTRACT_VERSION,
        "name": data["name"],
        "kind": kind,
        "source": str(src.relative_to(ROOT)),
        "description": data["description"],
        "inputs": [],
        "agents": [],
        "commands": [],
        "nodes": [],
        "edges": [],
        "context": {
            "injection_stage": "pre_dispatch",
            "source": "assets/context/repo-agent-instructions.md",
        },
        "runtime_hints": {
            "stateful": True,
            "human_in_loop": "approval" in body.lower() or "gate" in body.lower(),
            "observability": ["events", "runs", "nodes"],
        },
        "body": body,
    }


def write_neutral_contract(payload: dict) -> None:
    folder = {
        "agent": "agents",
        "command": "commands",
        "workflow": "workflows",
        "context": "context",
    }[payload["kind"]]
    write(ROOT / f"dist/nunneri-runtime/{folder}" / f"{payload['name']}.json", json.dumps(payload, indent=2))


def build_neutral_agent(src: Path, data: dict[str, str], body: str) -> dict:
    payload = neutral_base(src, data, body, "agent")
    payload["category"] = data.get("category")
    payload["nodes"] = [{
        "id": data["name"].replace("-", "_"),
        "label": data["name"],
        "type": "agent",
        "prompt": body,
    }]
    write_neutral_contract(payload)
    return payload


def build_neutral_command(src: Path, data: dict[str, str], body: str) -> dict:
    payload = neutral_base(src, data, body, "command")
    payload["category"] = data.get("category", "command")
    payload["commands"] = [data["name"]]
    payload["nodes"] = [{
        "id": data["name"].replace("-", "_"),
        "label": data["name"],
        "type": "command",
        "prompt": body,
    }]
    write_neutral_contract(payload)
    return payload


def build_neutral_workflow(src: Path, data: dict[str, str], body: str) -> dict:
    if data["name"] == "triage-nine-phase":
        payload = {**TRIAGE_NINE_PHASE_CONTRACT, "body": body}
    else:
        payload = neutral_base(src, data, body, "workflow")
        payload["nodes"] = [{
            "id": data["name"].replace("-", "_"),
            "label": data["description"],
            "type": "workflow",
            "prompt": body,
        }]
    write_neutral_contract(payload)
    return payload


def build_runtime_contract_index(agent_names: list[str], command_names: list[str], workflow_names: list[str]) -> None:
    payload = {
        "contract_version": CONTRACT_VERSION,
        "name": "nunneri-runtime-contract",
        "kind": "runtime_contract_index",
        "description": "Provider- and framework-neutral Nunneri runtime export index.",
        "generated_from": "assets",
        "providers": list(PROVIDERS),
        "runtimes": ["nunneri-runtime", "langgraph", "crewai", "autogen", "semantic-kernel"],
        "folders": {
            "agents": "agents",
            "commands": "commands",
            "workflows": "workflows",
            "context": "context",
        },
        "node_types": ["agent", "command", "workflow", "work", "router", "human_approval", "terminal"],
        "exports": {
            "agents": [f"agents/{name}.json" for name in agent_names],
            "commands": [f"commands/{name}.json" for name in command_names],
            "workflows": [f"workflows/{name}.json" for name in workflow_names],
            "context": ["context/repo-agent-instructions.json"],
        },
    }
    write(ROOT / "dist/nunneri-runtime/contract.json", json.dumps(payload, indent=2))


def build_neutral_context(src: Path, data: dict[str, str], body: str, structured: str) -> dict:
    payload = {
        "contract_version": CONTRACT_VERSION,
        "name": data["name"],
        "kind": "context",
        "source": str(src.relative_to(ROOT)),
        "description": data["description"],
        "category": data.get("category", "context"),
        "inputs": [],
        "agents": [],
        "commands": [],
        "nodes": [],
        "edges": [],
        "context": {"injection_stage": "pre_dispatch", "source": str(src.relative_to(ROOT))},
        "runtime_hints": {"stateful": False, "human_in_loop": False, "observability": ["events"]},
        "body": body,
        "structured_overrides": structured,
    }
    write_neutral_contract(payload)
    return payload


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


def build_langgraph_agent(contract: dict) -> None:
    node = contract["nodes"][0]
    payload = {
        "name": contract["name"],
        "description": contract["description"],
        "category": contract.get("category"),
        "runtime": "langgraph",
        "source": contract["source"],
        "contract_source": f"dist/nunneri-runtime/agents/{contract['name']}.json",
        "node": {
            "id": node["id"],
            "type": "agent",
            "body": node["prompt"],
        },
    }
    write(ROOT / "dist/langgraph/manifests/agents" / f"{contract['name']}.json", json.dumps(payload, indent=2))


def build_langgraph_command(contract: dict) -> None:
    node = contract["nodes"][0]
    payload = {
        "name": contract["name"],
        "description": contract["description"],
        "category": contract.get("category", "command"),
        "runtime": "langgraph",
        "source": contract["source"],
        "contract_source": f"dist/nunneri-runtime/commands/{contract['name']}.json",
        "entrypoint": {
            "id": node["id"],
            "type": "command",
            "body": node["prompt"],
        },
    }
    write(ROOT / "dist/langgraph/manifests/commands" / f"{contract['name']}.json", json.dumps(payload, indent=2))


def build_langgraph_workflow(contract: dict) -> None:
    nodes = []
    for node in contract["nodes"]:
        out = {k: v for k, v in node.items() if k not in {"prompt", "approval"}}
        if node.get("type") == "human_approval":
            out["approval_checkpoint"] = True
            out["approval"] = node.get("approval", {})
        nodes.append(out)
    payload = {
        "name": contract["name"],
        "description": contract["description"],
        "runtime": "langgraph",
        "source": contract["source"],
        "contract_source": f"dist/nunneri-runtime/workflows/{contract['name']}.json",
        "nodes": nodes,
        "edges": contract["edges"],
        "post_triage_actions": contract.get("post_triage_actions", []),
        "body": contract["body"],
    }
    write(ROOT / "dist/langgraph/graphs" / f"{contract['name']}.json", json.dumps(payload, indent=2))


def build_crewai_agent(contract: dict) -> None:
    node = contract["nodes"][0]
    payload = {
        "runtime": "crewai",
        "contract_source": f"dist/nunneri-runtime/agents/{contract['name']}.json",
        "agent": {
            "role": contract["name"],
            "goal": contract["description"],
            "backstory": node["prompt"],
            "allow_delegation": False,
        },
    }
    write(ROOT / "dist/crewai/agents" / f"{contract['name']}.json", json.dumps(payload, indent=2))


def build_crewai_command(contract: dict) -> None:
    payload = {
        "runtime": "crewai",
        "contract_source": f"dist/nunneri-runtime/commands/{contract['name']}.json",
        "task": {
            "description": contract["description"],
            "expected_output": "Nunneri command result with evidence, decision, and validation summary.",
            "prompt": contract["body"],
        },
    }
    write(ROOT / "dist/crewai/tasks" / f"{contract['name']}.json", json.dumps(payload, indent=2))


def build_crewai_workflow(contract: dict) -> None:
    payload = {
        "runtime": "crewai",
        "contract_source": f"dist/nunneri-runtime/workflows/{contract['name']}.json",
        "flow": {
            "name": contract["name"],
            "description": contract["description"],
            "steps": contract["nodes"],
            "edges": contract["edges"],
            "human_in_loop": [n["id"] for n in contract["nodes"] if n.get("type") == "human_approval"],
        },
    }
    write(ROOT / "dist/crewai/flows" / f"{contract['name']}.json", json.dumps(payload, indent=2))


def build_autogen_agent(contract: dict) -> None:
    node = contract["nodes"][0]
    payload = {
        "runtime": "autogen",
        "contract_source": f"dist/nunneri-runtime/agents/{contract['name']}.json",
        "agent": {
            "name": contract["name"].replace("-", "_"),
            "description": contract["description"],
            "system_message": node["prompt"],
        },
    }
    write(ROOT / "dist/autogen/agents" / f"{contract['name']}.json", json.dumps(payload, indent=2))


def build_autogen_command(contract: dict) -> None:
    payload = {
        "runtime": "autogen",
        "contract_source": f"dist/nunneri-runtime/commands/{contract['name']}.json",
        "agentchat_task": {
            "name": contract["name"],
            "description": contract["description"],
            "prompt": contract["body"],
        },
    }
    write(ROOT / "dist/autogen/tasks" / f"{contract['name']}.json", json.dumps(payload, indent=2))


def build_autogen_workflow(contract: dict) -> None:
    payload = {
        "runtime": "autogen",
        "contract_source": f"dist/nunneri-runtime/workflows/{contract['name']}.json",
        "group_orchestration": {
            "name": contract["name"],
            "participants": contract.get("agents", []),
            "nodes": contract["nodes"],
            "edges": contract["edges"],
            "human_approval_nodes": [n["id"] for n in contract["nodes"] if n.get("type") == "human_approval"],
        },
    }
    write(ROOT / "dist/autogen/workflows" / f"{contract['name']}.json", json.dumps(payload, indent=2))


def build_semantic_kernel_agent(contract: dict) -> None:
    node = contract["nodes"][0]
    payload = {
        "runtime": "semantic-kernel",
        "contract_source": f"dist/nunneri-runtime/agents/{contract['name']}.json",
        "agent": {
            "name": contract["name"].replace("-", "_"),
            "description": contract["description"],
            "instructions": node["prompt"],
        },
    }
    write(ROOT / "dist/semantic-kernel/agents" / f"{contract['name']}.json", json.dumps(payload, indent=2))


def build_semantic_kernel_command(contract: dict) -> None:
    payload = {
        "runtime": "semantic-kernel",
        "contract_source": f"dist/nunneri-runtime/commands/{contract['name']}.json",
        "function": {
            "name": contract["name"].replace("-", "_"),
            "description": contract["description"],
            "instructions": contract["body"],
        },
    }
    write(ROOT / "dist/semantic-kernel/functions" / f"{contract['name']}.json", json.dumps(payload, indent=2))


def build_semantic_kernel_workflow(contract: dict) -> None:
    payload = {
        "runtime": "semantic-kernel",
        "contract_source": f"dist/nunneri-runtime/workflows/{contract['name']}.json",
        "orchestration": {
            "name": contract["name"],
            "description": contract["description"],
            "steps": contract["nodes"],
            "edges": contract["edges"],
            "human_agent_interaction": [n["id"] for n in contract["nodes"] if n.get("type") == "human_approval"],
        },
    }
    write(ROOT / "dist/semantic-kernel/orchestrations" / f"{contract['name']}.json", json.dumps(payload, indent=2))


def copy_skill(src: Path) -> None:
    relative = src.parent.name
    for provider in PROVIDERS:
        if provider == "open-source":
            write(ROOT / "dist/open-source/workflows" / f"{relative}.md", f"> Generated from `{src.relative_to(ROOT)}`.\n\n{src.read_text(encoding='utf-8')}")
        else:
            write(ROOT / f"dist/{provider}/skills/{relative}/SKILL.md", f"> Generated from `{src.relative_to(ROOT)}`.\n\n{src.read_text(encoding='utf-8')}")


def build() -> None:
    reset_dist()
    build_context()
    agent_names: list[str] = []
    command_names: list[str] = []
    workflow_names: list[str] = []
    for src in sorted(path for path in (ROOT / "assets/agents").glob("**/*.md") if path.name != "README.md"):
        data, body = frontmatter_and_body(src)
        contract = build_neutral_agent(src, data, body)
        agent_names.append(contract["name"])
        build_claude_agent(src, data, body)
        for provider in ("codex", "gemini"):
            write(ROOT / f"dist/{provider}/prompts/agents" / src.name, f"> Generated from `{src.relative_to(ROOT)}`.\n\n{body}")
        write(ROOT / "dist/open-source/manifests/agents" / f"{data['name']}.json", json.dumps({"name": data["name"], "description": data["description"], "category": data.get("category"), "source": str(src.relative_to(ROOT)), "body": body}, indent=2))
        build_langgraph_agent(contract)
        build_crewai_agent(contract)
        build_autogen_agent(contract)
        build_semantic_kernel_agent(contract)
    for src in sorted(path for path in (ROOT / "assets/commands").glob("**/*.md") if path.name != "README.md"):
        data, body = frontmatter_and_body(src)
        contract = build_neutral_command(src, data, body)
        command_names.append(contract["name"])
        build_command(src, data, body)
        build_langgraph_command(contract)
        build_crewai_command(contract)
        build_autogen_command(contract)
        build_semantic_kernel_command(contract)
    for src in sorted((ROOT / "assets/skills").glob("*/SKILL.md")):
        copy_skill(src)
    for src in sorted((ROOT / "assets/workflows").glob("*.md")):
        if src.name == "README.md":
            for provider in PROVIDERS:
                write(ROOT / f"dist/{provider}/workflows" / src.name, f"> Generated from `{src.relative_to(ROOT)}`.\n\n{src.read_text(encoding='utf-8')}")
            continue
        data, body = frontmatter_and_body(src)
        contract = build_neutral_workflow(src, data, body)
        workflow_names.append(contract["name"])
        build_langgraph_workflow(contract)
        build_crewai_workflow(contract)
        build_autogen_workflow(contract)
        build_semantic_kernel_workflow(contract)
        for provider in PROVIDERS:
            folder = "workflows" if provider != "open-source" else "workflows"
            write(ROOT / f"dist/{provider}/{folder}" / src.name, f"> Generated from `{src.relative_to(ROOT)}`.\n\n{src.read_text(encoding='utf-8')}")
    build_runtime_contract_index(agent_names, command_names, workflow_names)
    write(ROOT / "dist/open-source/AGENT_MANIFEST.md", "# Open Source Manifest\n\nGenerated from provider-neutral assets. Context metadata is available in `manifests/context/repo-agent-instructions.json`.")
    write(ROOT / "dist/langgraph/LANGGRAPH.md", "# LangGraph Runtime\n\nGenerated graph and runtime manifests from provider-neutral assets. LangGraph is an orchestration runtime, not a model provider. Pre-dispatch context is available in `context/repo-agent-instructions.json`.")
    write(ROOT / "dist/nunneri-runtime/NUNNERI_RUNTIME.md", "# Nunneri Runtime Contract\n\nGenerated provider- and framework-neutral runtime contracts. Runtime adapters should consume these files instead of provider-specific exports.")
    write(ROOT / "dist/crewai/CREWAI.md", "# CrewAI Runtime Adapter\n\nGenerated CrewAI-compatible JSON manifests from `dist/nunneri-runtime/`. These are export contracts only; CrewAI SDK dependencies are optional for consumers.")
    write(ROOT / "dist/autogen/AUTOGEN.md", "# AutoGen Runtime Adapter\n\nGenerated Microsoft AutoGen-compatible JSON manifests from `dist/nunneri-runtime/`. These are export contracts only; AutoGen SDK dependencies are optional for consumers.")
    write(ROOT / "dist/semantic-kernel/SEMANTIC_KERNEL.md", "# Semantic Kernel Runtime Adapter\n\nGenerated Microsoft Semantic Kernel-compatible JSON manifests from `dist/nunneri-runtime/`. These are export contracts only; Semantic Kernel dependencies are optional for consumers.")
    print("Built provider adapters: claude, codex, gemini, open-source; runtime adapters: nunneri-runtime, langgraph, crewai, autogen, semantic-kernel")


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
    context = items(path for path in (ROOT / "assets/context").glob("*.md") if path.name != "README.md")
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
        "counts": {"agents": len(agents), "commands": len(commands), "skills": len(skills), "workflows": len(workflows), "context": len(context), "providers": 4, "runtimes": 5, "guides": len(guides)},
        "agents": agents,
        "commands": commands,
        "skills": skills,
        "workflows": workflows,
        "context": context,
        "guides": guides,
    }
    target = ROOT / "docs/assets/manifest.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {target}")


if __name__ == "__main__":
    main()
''', True)

    write("scripts/sync_docs_reference.py", r'''#!/usr/bin/env python3
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "docs/reference"
GUIDE_REFERENCE = REFERENCE / "guides"
CONTEXT_REFERENCE = REFERENCE / "context"
EXAMPLES_REFERENCE = REFERENCE / "examples"

ROOT_DOCS = [
    "LICENSE",
    "README.md",
    "ARCHITECTURE.md",
    "AI_ASSETS.md",
    "CONTRIBUTING.md",
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

    write("scripts/check_context_exports.py", r'''#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "assets/context/repo-agent-instructions.md"
PROVIDER_FILES = [
    ("claude", ROOT / "dist/claude/CLAUDE.md", "### Claude Code", ["### Codex", "### Gemini"]),
    ("codex", ROOT / "dist/codex/AGENTS.md", "### Codex", ["### Claude Code", "### Gemini"]),
    ("gemini", ROOT / "dist/gemini/GEMINI.md", "### Gemini", ["### Claude Code", "### Codex"]),
]
REQUIRED_SECTIONS = [
    "## Repository Identity and Ownership",
    "## Golden Setup, Build, and Test Commands",
    "## Common Library and Source-Code Links",
    "## Known Issues and Recurring Failure Modes",
    "## DevOps and Environment Overrides",
    "## Agentic Workflow Overrides",
    "## Exception Handling and Escalation Rules",
    "## Skill Invocation Overrides",
    "## Agent Dispatch Rules Before Task Routing",
    "## Approval Gates and Release-Impact Rules",
    "## Provider-Specific Instruction Overrides",
    "## Structured Override Registry",
]
REQUIRED_KEYS = [
    "known_issues:",
    "devops_overrides:",
    "library_sources:",
    "workflow_overrides:",
    "exceptions:",
    "skill_overrides:",
    "dispatch_overrides:",
    "provider_overrides:",
    "approval_gates:",
]


def structured_yaml(text: str) -> str:
    start = text.find("```yaml\n")
    if start == -1:
        return ""
    start += len("```yaml\n")
    end = text.find("\n```", start)
    if end == -1:
        return ""
    return text[start:end]


def main() -> int:
    failures: list[str] = []
    if not TEMPLATE.exists():
        failures.append("assets/context/repo-agent-instructions.md is missing")
    else:
        text = TEMPLATE.read_text(encoding="utf-8")
        for section in REQUIRED_SECTIONS:
            if section not in text:
                failures.append(f"{TEMPLATE}: missing section {section}")
        yaml = structured_yaml(text)
        if not yaml:
            failures.append(f"{TEMPLATE}: missing structured YAML override block")
        for key in REQUIRED_KEYS:
            if key not in yaml:
                failures.append(f"{TEMPLATE}: missing YAML key {key}")
    for provider, path, expected_heading, forbidden_headings in PROVIDER_FILES:
        if not path.exists():
            failures.append(f"{path}: missing generated provider context")
            continue
        text = path.read_text(encoding="utf-8")
        for section in REQUIRED_SECTIONS:
            if section not in text:
                failures.append(f"{path}: missing section {section}")
        if not structured_yaml(text):
            failures.append(f"{path}: missing structured YAML override block")
        if expected_heading not in text:
            failures.append(f"{path}: missing provider-specific heading {expected_heading}")
        for heading in forbidden_headings:
            if heading in text:
                failures.append(f"{path}: leaked provider-specific heading {heading}")
        if provider != "claude" and "`agent team`" in text:
            failures.append(f"{path}: leaked Claude-only trigger phrase `agent team`")
    open_source = ROOT / "dist/open-source/manifests/context/repo-agent-instructions.json"
    langgraph = ROOT / "dist/langgraph/context/repo-agent-instructions.json"
    for path in (open_source, langgraph):
        if not path.exists():
            failures.append(f"{path}: missing generated context manifest")
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        if not data.get("structured_overrides"):
            failures.append(f"{path}: missing structured_overrides")
    if langgraph.exists():
        data = json.loads(langgraph.read_text(encoding="utf-8"))
        if data.get("injection_stage") != "pre_dispatch":
            failures.append(f"{langgraph}: injection_stage must be pre_dispatch")
    installer = ROOT / "install.sh"
    install_text = installer.read_text(encoding="utf-8")
    for snippet in ("--context-only", "--no-context", "--dry-run", "Dry run: skipping adapter build and writing no files", 'dest="$rel"', 'version_file=".ai-assets-version"', "Would install", "root context files=", "provider directory files="):
        if snippet not in install_text:
            failures.append(f"{installer}: missing context install contract snippet {snippet}")
    if failures:
        for failure in failures:
            print(failure)
        return 1
    print("Context export checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
''', True)

    write("scripts/check_langgraph_exports.py", r'''#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRIAGE_GRAPH = ROOT / "dist/langgraph/graphs/triage-nine-phase.json"
TRIAGE_CONTRACT = ROOT / "dist/nunneri-runtime/workflows/triage-nine-phase.json"


def main() -> int:
    failures: list[str] = []

    if not (ROOT / "dist/langgraph").is_dir():
        failures.append("dist/langgraph is missing")

    if not TRIAGE_CONTRACT.exists():
        failures.append("dist/nunneri-runtime/workflows/triage-nine-phase.json is missing")

    contract = {}
    if TRIAGE_CONTRACT.exists():
        contract = json.loads(TRIAGE_CONTRACT.read_text(encoding="utf-8"))

    if not TRIAGE_GRAPH.exists():
        failures.append("dist/langgraph/graphs/triage-nine-phase.json is missing")
    else:
        graph = json.loads(TRIAGE_GRAPH.read_text(encoding="utf-8"))
        nodes = graph.get("nodes", [])
        edges = graph.get("edges", [])
        approval_nodes = [node for node in nodes if node.get("approval_checkpoint") is True]
        contract_nodes = contract.get("nodes", [])
        contract_edges = contract.get("edges", [])

        if graph.get("contract_source") != "dist/nunneri-runtime/workflows/triage-nine-phase.json":
            failures.append("triage-nine-phase LangGraph export must point to the neutral contract source")

        if len(nodes) != 9:
            failures.append(f"triage-nine-phase must export exactly 9 nodes, found {len(nodes)}")

        expected_ids = [
            "intake",
            "context_load",
            "classification",
            "evidence_collection",
            "root_cause_analysis",
            "gate_1",
            "test_first_fix",
            "validation",
            "gate_2",
        ]
        actual_ids = [node.get("id") for node in nodes]
        if actual_ids != expected_ids:
            failures.append(f"triage-nine-phase node order mismatch: {actual_ids}")
        if contract_nodes and actual_ids != [node.get("id") for node in contract_nodes]:
            failures.append("triage-nine-phase LangGraph node order does not match neutral contract")

        approval_ids = sorted(node.get("id") for node in approval_nodes)
        if approval_ids != ["gate_1", "gate_2"]:
            failures.append(f"approval checkpoints must be gate_1 and gate_2, found {approval_ids}")
        for node in approval_nodes:
            approval = node.get("approval", {})
            if approval.get("on_reject") != "cancel":
                failures.append(f"{node.get('id')} approval rejection policy must be cancel")

        expected_edges = [
            ("intake", "context_load"),
            ("context_load", "classification"),
            ("classification", "evidence_collection"),
            ("evidence_collection", "root_cause_analysis"),
            ("root_cause_analysis", "gate_1"),
            ("gate_1", "test_first_fix"),
            ("test_first_fix", "validation"),
            ("validation", "gate_2"),
        ]
        actual_edges = [(edge.get("from"), edge.get("to")) for edge in edges]
        if actual_edges != expected_edges:
            failures.append(f"triage-nine-phase edge order mismatch: {actual_edges}")
        if contract_edges and actual_edges != [(edge.get("from"), edge.get("to")) for edge in contract_edges]:
            failures.append("triage-nine-phase LangGraph edges do not match neutral contract")

    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("LangGraph export checks passed")
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
        "ARCHITECTURE.md": ["runtime-neutral", "Graph Studio", "MinIO", "Trust, Governance"],
        "DEFENSIVE_PUBLICATION.md": ["Publication date", "Do not describe Nunneri as \"patent pending\"", "runtime-neutral control plane"],
        "CITATION.cff": ["Nunneri Public Agentic AI", "AGPL-3.0-only", "runtime contract"],
        "CONTRIBUTING.md": ["Contributor License Agreement", "commercial licensing"],
        "GOVERNANCE.md": ["Nunneri Core Team", "Runtime Contract Stewardship"],
        "ROADMAP.md": ["Community Edition", "Commercial and Enterprise Options"],
        "SECURITY.md": ["Reporting a Vulnerability", "provider keys"],
        "NUNNERI_RUNTIME_CONTRACT.md": ["ARCHITECTURE.md", "DEFENSIVE_PUBLICATION.md"],
        "docs/index.html": ["AGPLv3 Community Edition", "Commercial License", "Defensive Publication", "Why Nunneri is different"],
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
''', True)

    write("scripts/check_consumer_install.py", r'''#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def stage_payload(target: Path) -> None:
    for name in ("install.sh", "VERSION"):
        shutil.copyfile(ROOT / name, target / name)
    shutil.copytree(ROOT / "dist", target / "dist")


def run_install(target: Path, *args: str) -> str:
    completed = subprocess.run(
        ["bash", "install.sh", *args],
        cwd=target,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=True,
    )
    return completed.stdout


def assert_contains(text: str, expected: str) -> None:
    if expected not in text:
        raise AssertionError(f"expected output to contain {expected!r}; got:\n{text}")


def assert_exists(path: Path) -> None:
    if not path.exists():
        raise AssertionError(f"expected missing path: {path}")


def assert_missing(path: Path) -> None:
    if path.exists():
        raise AssertionError(f"unexpected path exists: {path}")


def assert_not_contains(path: Path, forbidden: str) -> None:
    if forbidden in path.read_text(encoding="utf-8"):
        raise AssertionError(f"{path} unexpectedly contains {forbidden!r}")


def write_consumer_repo(path: Path) -> None:
    (path / "README.md").write_text("# Consumer App\n", encoding="utf-8")
    (path / "pyproject.toml").write_text("[project]\nname = \"consumer-app\"\nversion = \"0.1.0\"\n", encoding="utf-8")


def check_context_only_dry_run() -> None:
    with tempfile.TemporaryDirectory(prefix="nunneri-consumer-dry-run-") as tmp:
        target = Path(tmp)
        stage_payload(target)
        write_consumer_repo(target)
        output = run_install(target, "--provider", "claude", "--project", "--context-only", "--dry-run")
        assert_contains(output, "Would install CLAUDE.md (root-context)")
        assert_contains(output, "Would write version metadata to .ai-assets-version")
        assert_missing(target / "CLAUDE.md")
        assert_missing(target / ".ai-assets-version")
        assert_missing(target / ".claude")


def check_context_only_force() -> None:
    with tempfile.TemporaryDirectory(prefix="nunneri-consumer-context-") as tmp:
        target = Path(tmp)
        stage_payload(target)
        write_consumer_repo(target)
        output = run_install(target, "--provider", "claude", "--project", "--context-only", "--force", "--skip-build")
        assert_contains(output, "Installed CLAUDE.md into project root")
        assert_exists(target / "CLAUDE.md")
        assert_exists(target / ".ai-assets-version")
        assert_missing(target / ".claude")
        assert_not_contains(target / "CLAUDE.md", "## Codex")
        assert_not_contains(target / "CLAUDE.md", "## Gemini")


def check_full_provider_install() -> None:
    with tempfile.TemporaryDirectory(prefix="nunneri-consumer-full-") as tmp:
        target = Path(tmp)
        stage_payload(target)
        write_consumer_repo(target)
        output = run_install(target, "--provider", "claude", "--project", "--force", "--skip-build")
        assert_contains(output, "Installed CLAUDE.md into project root")
        assert_exists(target / "CLAUDE.md")
        assert_exists(target / ".claude" / "agents" / "python-triage-specialist.md")
        assert_exists(target / ".claude" / "commands" / "triage.md")
        assert_exists(target / ".claude" / ".ai-assets-version")


def check_langgraph_runtime_install() -> None:
    with tempfile.TemporaryDirectory(prefix="nunneri-consumer-langgraph-") as tmp:
        target = Path(tmp)
        stage_payload(target)
        write_consumer_repo(target)
        output = run_install(target, "--runtime", "langgraph", "--project", "--force", "--skip-build")
        assert_contains(output, "Summary for langgraph runtime")
        assert_exists(target / ".langgraph" / "graphs" / "triage-nine-phase.json")
        assert_exists(target / ".langgraph" / "manifests" / "agents" / "python-triage-specialist.json")
        assert_exists(target / ".langgraph" / "context" / "repo-agent-instructions.json")
        assert_exists(target / ".langgraph" / ".ai-assets-version")


def check_neutral_runtime_contract_install() -> None:
    with tempfile.TemporaryDirectory(prefix="nunneri-consumer-runtime-contract-") as tmp:
        target = Path(tmp)
        stage_payload(target)
        write_consumer_repo(target)
        output = run_install(target, "--runtime", "nunneri-runtime", "--project", "--force", "--skip-build")
        assert_contains(output, "Summary for nunneri-runtime runtime")
        assert_exists(target / ".nunneri-runtime" / "contract.json")
        assert_exists(target / ".nunneri-runtime" / "workflows" / "triage-nine-phase.json")
        assert_exists(target / ".nunneri-runtime" / "context" / "repo-agent-instructions.json")
        assert_exists(target / ".nunneri-runtime" / ".ai-assets-version")


def check_existing_context_skip() -> None:
    with tempfile.TemporaryDirectory(prefix="nunneri-consumer-skip-") as tmp:
        target = Path(tmp)
        stage_payload(target)
        write_consumer_repo(target)
        (target / "CLAUDE.md").write_text("# Existing Claude Context\n", encoding="utf-8")
        output = run_install(target, "--provider", "claude", "--project", "--context-only", "--skip-build")
        assert_contains(output, "Skip existing CLAUDE.md")
        if (target / "CLAUDE.md").read_text(encoding="utf-8") != "# Existing Claude Context\n":
            raise AssertionError("existing CLAUDE.md was overwritten without --force")


def main() -> int:
    check_context_only_dry_run()
    check_context_only_force()
    check_full_provider_install()
    check_neutral_runtime_contract_install()
    check_langgraph_runtime_install()
    check_existing_context_skip()
    print("Consumer install smoke checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
''', True)

    write("scripts/package_release.py", r'''#!/usr/bin/env python3
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
''', True)

    write("scripts/check_user_setup_docs.py", r'''#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    raise AssertionError(message)


def require(path: Path) -> str:
    if not path.exists():
        fail(f"missing required setup doc artifact: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def main() -> int:
    guide = require(ROOT / "guides" / "end-user-langgraph-setup.md")
    demo = require(ROOT / "guides" / "end-user-setup-demo.html")
    reference_guide = require(ROOT / "docs" / "reference" / "guides" / "end-user-langgraph-setup.md")
    reference_demo = require(ROOT / "docs" / "reference" / "guides" / "end-user-setup-demo.html")
    portal = require(ROOT / "docs" / "index.html")
    manifest_text = require(ROOT / "docs" / "assets" / "manifest.json")
    manifest = json.loads(manifest_text)

    for snippet in (
        "NUNNERI_RUNTIME=langgraph",
        "NUNNERI_STATE_STORE=sqlite",
        "NUNNERI_TRACE_MODE=otel|langsmith|none",
        "LANGSMITH_API_KEY",
        ".nunneri/langgraph/state.sqlite",
        "OpenTelemetry",
        "LangSmith",
    ):
        if snippet not in guide:
            fail(f"setup guide missing snippet: {snippet}")

    for snippet in (
        "Select Provider",
        "Preview Context",
        "Install Assets",
        "Export Runtime",
        "Persist State",
        "Trace and Monitor",
        "Validate Setup",
        "NUNNERI_TRACE_MODE=otel",
    ):
        if snippet not in demo:
            fail(f"setup demo missing step or config snippet: {snippet}")

    if "End-User Setup" not in portal or "end-user-setup-demo.html" not in portal:
        fail("portal does not link the end-user setup demo")

    guide_names = {item.get("name") for item in manifest.get("guides", [])}
    if "end-user-setup-demo.html" not in guide_names:
        fail("portal manifest does not include end-user-setup-demo.html")

    if guide != reference_guide:
        fail("reference setup guide is out of sync")
    if "../../index.html" not in reference_demo:
        fail("reference setup demo link rewrite is missing")

    print("End-user setup docs checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
''', True)

    write("scripts/check_release_package.py", r'''#!/usr/bin/env python3
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
    "dist/claude/CLAUDE.md",
    "dist/codex/AGENTS.md",
    "dist/gemini/GEMINI.md",
    "dist/langgraph/LANGGRAPH.md",
    "dist/open-source/AGENT_MANIFEST.md",
    "docs/reference/README.md",
    "docs/reference/ARCHITECTURE.md",
    "docs/reference/CITATION.cff",
    "docs/reference/DEFENSIVE_PUBLICATION.md",
    "docs/reference/GOVERNANCE.md",
    "docs/reference/ROADMAP.md",
    "docs/reference/SECURITY.md",
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


def check_zip() -> None:
    archive = RELEASES / f"{PACKAGE}.zip"
    assert_exists(archive)
    with tempfile.TemporaryDirectory(prefix="nunneri-release-zip-") as tmp:
        with zipfile.ZipFile(archive) as zf:
            zf.extractall(tmp)
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
''', True)

    write("schemas/nunneri-runtime-contract.schema.json", r'''{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://nunneri.suranku.com/schemas/nunneri-runtime-contract.schema.json",
  "title": "Nunneri Runtime Contract",
  "type": "object",
  "required": [
    "contract_version",
    "name",
    "kind",
    "source",
    "description",
    "inputs",
    "agents",
    "commands",
    "nodes",
    "edges",
    "context",
    "runtime_hints"
  ],
  "properties": {
    "contract_version": {
      "const": "1.0"
    },
    "name": {
      "type": "string",
      "minLength": 1
    },
    "kind": {
      "enum": ["agent", "command", "workflow", "context"]
    },
    "source": {
      "type": "string",
      "minLength": 1
    },
    "description": {
      "type": "string",
      "minLength": 1
    },
    "inputs": {
      "type": "array"
    },
    "agents": {
      "type": "array"
    },
    "commands": {
      "type": "array"
    },
    "nodes": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "type"],
        "properties": {
          "id": {
            "type": "string",
            "minLength": 1
          },
          "label": {
            "type": "string"
          },
          "type": {
            "enum": ["agent", "command", "workflow", "work", "router", "human_approval", "terminal"]
          },
          "phase": {
            "type": "integer",
            "minimum": 1
          },
          "prompt": {
            "type": "string"
          },
          "approval": {
            "type": "object",
            "properties": {
              "required": {
                "type": "boolean"
              },
              "actions": {
                "type": "array",
                "items": {
                  "enum": ["approve", "reject"]
                }
              },
              "on_reject": {
                "enum": ["cancel"]
              }
            }
          }
        }
      }
    },
    "edges": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["from", "to"],
        "properties": {
          "from": {
            "type": "string",
            "minLength": 1
          },
          "to": {
            "type": "string",
            "minLength": 1
          },
          "condition": {
            "type": "string"
          }
        }
      }
    },
    "context": {
      "type": "object",
      "required": ["injection_stage", "source"],
      "properties": {
        "injection_stage": {
          "enum": ["pre_dispatch"]
        },
        "source": {
          "type": "string",
          "minLength": 1
        }
      }
    },
    "runtime_hints": {
      "type": "object",
      "required": ["stateful", "human_in_loop", "observability"],
      "properties": {
        "stateful": {
          "type": "boolean"
        },
        "human_in_loop": {
          "type": "boolean"
        },
        "observability": {
          "type": "array",
          "items": {
            "enum": ["events", "runs", "nodes"]
          }
        }
      }
    }
  }
}
''')

    write("scripts/check_runtime_contract.py", r'''#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_ROOT = ROOT / "dist/nunneri-runtime"
SCHEMA = ROOT / "schemas/nunneri-runtime-contract.schema.json"
ALLOWED_KINDS = {"agent", "command", "workflow", "context"}
ALLOWED_NODE_TYPES = {"agent", "command", "workflow", "work", "router", "human_approval", "terminal"}
RUNTIME_SMOKE_PATHS = [
    "dist/crewai/agents",
    "dist/crewai/tasks",
    "dist/crewai/flows",
    "dist/autogen/agents",
    "dist/autogen/tasks",
    "dist/autogen/workflows",
    "dist/semantic-kernel/agents",
    "dist/semantic-kernel/functions",
    "dist/semantic-kernel/orchestrations",
]


def generated_name(src: Path) -> str:
    text = src.read_text(encoding="utf-8")
    end = text.find("\n---", 4)
    if not text.startswith("---\n") or end == -1:
        raise ValueError(f"{src}: missing frontmatter")
    for line in text[4:end].splitlines():
        if line.startswith("name:"):
            return line.split(":", 1)[1].strip()
    raise ValueError(f"{src}: missing name frontmatter")


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def load_json(path: Path, failures: list[str]) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - validation script should report all JSON failures.
        failures.append(f"{path.relative_to(ROOT)} is not valid JSON: {exc}")
        return {}


def validate_contract(path: Path, failures: list[str]) -> dict:
    payload = load_json(path, failures)
    if not payload:
        return {}
    rel = path.relative_to(ROOT)
    required = [
        "contract_version",
        "name",
        "kind",
        "source",
        "description",
        "inputs",
        "agents",
        "commands",
        "nodes",
        "edges",
        "context",
        "runtime_hints",
    ]
    for key in required:
        require(key in payload, f"{rel} missing required field {key}", failures)
    require(payload.get("contract_version") == "1.0", f"{rel} contract_version must be 1.0", failures)
    require(payload.get("kind") in ALLOWED_KINDS, f"{rel} has invalid kind {payload.get('kind')}", failures)
    require(isinstance(payload.get("nodes"), list), f"{rel} nodes must be a list", failures)
    require(isinstance(payload.get("edges"), list), f"{rel} edges must be a list", failures)
    for node in payload.get("nodes", []):
        node_type = node.get("type")
        require(node.get("id") is not None, f"{rel} has a node without id", failures)
        require(node_type in ALLOWED_NODE_TYPES, f"{rel} has invalid node type {node_type}", failures)
        if node_type == "human_approval":
            approval = node.get("approval", {})
            require(approval.get("required") is True, f"{rel} approval node {node.get('id')} must require approval", failures)
            require(approval.get("actions") == ["approve", "reject"], f"{rel} approval node {node.get('id')} must allow approve/reject", failures)
            require(approval.get("on_reject") == "cancel", f"{rel} approval node {node.get('id')} must cancel on rejection", failures)
    for edge in payload.get("edges", []):
        require(edge.get("from") is not None and edge.get("to") is not None, f"{rel} has an edge without from/to", failures)
    return payload


def expected_exports(folder: str) -> list[str]:
    asset_root = ROOT / "assets" / folder
    if not asset_root.exists():
        return []
    return [generated_name(src) for src in sorted(asset_root.glob("**/*.md")) if src.name != "README.md"]


def main() -> int:
    failures: list[str] = []

    require(SCHEMA.exists(), "schemas/nunneri-runtime-contract.schema.json is missing", failures)
    require(CONTRACT_ROOT.is_dir(), "dist/nunneri-runtime is missing", failures)
    require((CONTRACT_ROOT / "contract.json").exists(), "dist/nunneri-runtime/contract.json is missing", failures)

    for folder in ("agents", "commands", "workflows"):
        for name in expected_exports(folder):
            path = CONTRACT_ROOT / folder / f"{name}.json"
            require(path.exists(), f"missing neutral {folder[:-1]} export: {path.relative_to(ROOT)}", failures)

    require((CONTRACT_ROOT / "context/repo-agent-instructions.json").exists(), "missing neutral context export", failures)

    for path in sorted(CONTRACT_ROOT.glob("*/*.json")):
        validate_contract(path, failures)

    triage_path = CONTRACT_ROOT / "workflows/triage-nine-phase.json"
    if triage_path.exists():
        triage = validate_contract(triage_path, failures)
        nodes = triage.get("nodes", [])
        require(len(nodes) == 9, f"triage-nine-phase must have exactly 9 nodes, found {len(nodes)}", failures)
        by_id = {node.get("id"): node for node in nodes}
        for gate_id in ("gate_1", "gate_2"):
            gate = by_id.get(gate_id, {})
            require(gate.get("type") == "human_approval", f"{gate_id} must be human_approval", failures)
            require(gate.get("approval", {}).get("on_reject") == "cancel", f"{gate_id} rejection policy must be cancel", failures)
            require(bool(gate.get("approval", {}).get("question")), f"{gate_id} must include an approval question", failures)
            require(
                bool(gate.get("approval", {}).get("required_context")),
                f"{gate_id} must include required approval context",
                failures,
            )
        classification = by_id.get("classification", {})
        require(
            bool(classification.get("classification_options")),
            "classification node must include classification_options",
            failures,
        )

    for path in RUNTIME_SMOKE_PATHS:
        full = ROOT / path
        require(full.is_dir(), f"{path} is missing", failures)
        if full.is_dir():
            require(any(full.glob("*.json")), f"{path} has no generated JSON files", failures)

    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("Runtime contract checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
''', True)


    write("scripts/check_runtime_examples.py", r'''#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples/runtime-contract-consumer/consume_runtime_contract.py"


def main() -> int:
    failures: list[str] = []

    if not EXAMPLE.exists():
        failures.append("examples/runtime-contract-consumer/consume_runtime_contract.py is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(EXAMPLE), "--repo-root", str(ROOT)],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        if completed.returncode != 0:
            failures.append(f"runtime contract consumer example failed:\n{completed.stdout}")
        else:
            try:
                payload = json.loads(completed.stdout)
            except json.JSONDecodeError as exc:
                failures.append(f"runtime contract consumer output is not JSON: {exc}")
                payload = {}
            if payload:
                if payload.get("contract_version") != "1.0":
                    failures.append("example must report contract_version 1.0")
                if payload.get("workflow_name") != "triage-nine-phase":
                    failures.append("example must load triage-nine-phase by default")
                if payload.get("node_count") != 9:
                    failures.append(f"example must report 9 workflow nodes, found {payload.get('node_count')}")
                if payload.get("approval_gates") != ["gate_1", "gate_2"]:
                    failures.append(f"example approval gates mismatch: {payload.get('approval_gates')}")
                crewai_flow = payload.get("crewai_flow", {})
                if crewai_flow.get("human_in_loop") != ["gate_1", "gate_2"]:
                    failures.append(f"CrewAI-style flow must preserve approval gates, found {crewai_flow.get('human_in_loop')}")
                if len(crewai_flow.get("steps", [])) != 9:
                    failures.append("CrewAI-style flow must contain 9 steps")

    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("Runtime example checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
''', True)


    write("scripts/check_graph_studio_contract.py", r'''#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def main() -> int:
    failures: list[str] = []
    api = (ROOT / "api/main.py").read_text(encoding="utf-8")
    ui = (ROOT / "api/ui.html").read_text(encoding="utf-8")
    triage = json.loads((ROOT / "dist/nunneri-runtime/workflows/triage-nine-phase.json").read_text(encoding="utf-8"))

    require("/agents/{agent_name}/graph-definition" in api, "api/main.py must expose graph-definition endpoint", failures)
    require("load_graph_definition" in api, "api/main.py must load graph definitions from runtime exports", failures)
    require("graph-definition" in ui, "api/ui.html must fetch graph-definition", failures)
    require("Phase Config" in ui, "api/ui.html must label the right panel as Phase Config", failures)
    require("renderContractDefaults" in ui, "api/ui.html must render contract defaults in the phase panel", failures)
    require("edge-label" in ui, "api/ui.html must render edge condition labels", failures)
    require("loadGraphDefinition" in ui, "api/ui.html must use loadGraphDefinition for selected assets", failures)

    nodes = {node["id"]: node for node in triage.get("nodes", [])}
    require(bool(nodes.get("classification", {}).get("classification_options")), "classification phase needs contract options", failures)
    for gate_id in ("gate_1", "gate_2"):
        approval = nodes.get(gate_id, {}).get("approval", {})
        require(bool(approval.get("question")), f"{gate_id} needs an approval question", failures)
        require(bool(approval.get("required_context")), f"{gate_id} needs required approval context", failures)

    if failures:
        for failure in failures:
            print(failure)
        return 1
    print("Graph Studio contract checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
''', True)

    write("scripts/check_runtime_contract_demo.py", r'''#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "guides/runtime-contract-demo.html"
REFERENCE = ROOT / "docs/reference/guides/runtime-contract-demo.html"


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def main() -> int:
    failures: list[str] = []
    require(GUIDE.exists(), "guides/runtime-contract-demo.html is missing", failures)
    require(REFERENCE.exists(), "docs/reference/guides/runtime-contract-demo.html is missing; run sync_docs_reference.py", failures)
    if GUIDE.exists():
        text = GUIDE.read_text(encoding="utf-8")
        for term in (
            "triage-nine-phase",
            "gate_1",
            "gate_2",
            "LangGraph",
            "CrewAI",
            "AutoGen",
            "Semantic Kernel",
            "scripts/check_runtime_examples.py",
            "scripts/check_graph_studio_contract.py",
        ):
            require(term in text, f"runtime contract demo must mention {term}", failures)
        require(text.count("data-step=") >= 6, "runtime contract demo must include at least six interactive steps", failures)
        require("addEventListener" in text, "runtime contract demo must include interactive JavaScript", failures)
    if failures:
        for failure in failures:
            print(failure)
        return 1
    print("Runtime contract demo checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
''', True)

    write("scripts/check_graph_definition_api.py", r'''#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def main() -> int:
    failures: list[str] = []
    api_path = ROOT / "api/main.py"
    graph_path = ROOT / "dist/langgraph/graphs/triage-nine-phase.json"
    contract_path = ROOT / "dist/nunneri-runtime/workflows/triage-nine-phase.json"

    api = api_path.read_text(encoding="utf-8")
    graph = json.loads(graph_path.read_text(encoding="utf-8"))
    contract = json.loads(contract_path.read_text(encoding="utf-8"))

    require('@app.get("/agents/{agent_name}/graph-definition"' in api, "graph-definition GET route is missing", failures)
    require("def get_agent_graph_definition" in api, "graph-definition handler is missing", failures)
    require("resolve_manifest(agent_name)" in api, "graph-definition handler must resolve agents and commands", failures)
    require("load_graph_definition(manifest, is_command)" in api, "graph-definition handler must use load_graph_definition", failures)
    require('"nodes": nodes' in api, "load_graph_definition must return nodes", failures)
    require('"edges": graph.get("edges", linear_edges(nodes))' in api, "load_graph_definition must return graph edges", failures)
    require('"terminology"' in api, "graph-definition response must include terminology", failures)

    require(graph.get("runtime") == "langgraph", "triage graph-definition source must be LangGraph", failures)
    require(graph.get("contract_source") == "dist/nunneri-runtime/workflows/triage-nine-phase.json", "triage graph must reference the neutral contract", failures)
    require(len(graph.get("nodes", [])) == 9, "triage graph must expose exactly 9 nodes", failures)
    require(len(graph.get("edges", [])) == 8, "triage graph must expose exactly 8 edges", failures)

    by_id = {node.get("id"): node for node in graph.get("nodes", [])}
    require(by_id.get("classification", {}).get("classification_options"), "classification options must be API-visible in graph nodes", failures)
    for gate_id in ("gate_1", "gate_2"):
        gate = by_id.get(gate_id, {})
        approval = gate.get("approval", {})
        require(gate.get("type") == "human_approval", f"{gate_id} must be a human_approval node", failures)
        require(gate.get("approval_checkpoint") is True, f"{gate_id} must be marked as an approval checkpoint", failures)
        require(approval.get("question"), f"{gate_id} must expose an approval question", failures)
        require(approval.get("required_context"), f"{gate_id} must expose required approval context", failures)

    approved_edges = [
        edge for edge in graph.get("edges", [])
        if edge.get("from") == "gate_1" and edge.get("to") == "test_first_fix"
    ]
    require(approved_edges and approved_edges[0].get("condition") == "approved", "gate_1 edge must expose approved condition", failures)
    contract_ids = [node.get("id") for node in contract.get("nodes", [])]
    graph_ids = [node.get("id") for node in graph.get("nodes", [])]
    require(contract_ids == graph_ids, "LangGraph graph-definition nodes must preserve neutral contract order", failures)
    contract_classification = next((node for node in contract.get("nodes", []) if node.get("id") == "classification"), {})
    require(
        by_id.get("classification", {}).get("classification_options") == contract_classification.get("classification_options"),
        "graph-definition classification options must match the neutral contract",
        failures,
    )

    if failures:
        for failure in failures:
            print(failure)
        return 1
    print("Graph-definition API contract checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
''', True)

    write("scripts/check_crewai_runtime_runner.py", r'''#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "examples/crewai-runtime-runner/run_crewai_contract.py"


def run_runner(*args: str) -> tuple[int, dict | None, str]:
    completed = subprocess.run(
        [sys.executable, str(RUNNER), "--repo-root", str(ROOT), *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        payload = None
    return completed.returncode, payload, completed.stdout


def main() -> int:
    failures: list[str] = []

    if not RUNNER.exists():
        failures.append("examples/crewai-runtime-runner/run_crewai_contract.py is missing")
    else:
        code, payload, output = run_runner("--auto-approve")
        if code != 0 or payload is None:
            failures.append(f"CrewAI contract runner approve path failed:\n{output}")
        else:
            if payload.get("runtime") != "crewai":
                failures.append("CrewAI contract runner must report runtime=crewai")
            if payload.get("status") != "completed":
                failures.append(f"approve path must complete, found {payload.get('status')}")
            if payload.get("step_count") != 9:
                failures.append(f"approve path must expose 9 steps, found {payload.get('step_count')}")
            if payload.get("completed_steps", [])[-1:] != ["gate_2"]:
                failures.append("approve path must complete through gate_2")
            decisions = payload.get("gate_decisions", {})
            if decisions.get("gate_1", {}).get("approved") is not True:
                failures.append("approve path must approve gate_1")
            if decisions.get("gate_2", {}).get("approved") is not True:
                failures.append("approve path must approve gate_2")

        code, payload, output = run_runner("--reject-gate", "gate_1")
        if code != 0 or payload is None:
            failures.append(f"CrewAI contract runner reject path failed:\n{output}")
        else:
            if payload.get("status") != "cancelled":
                failures.append(f"reject path must cancel, found {payload.get('status')}")
            if payload.get("cancelled_at") != "gate_1":
                failures.append(f"reject path must cancel at gate_1, found {payload.get('cancelled_at')}")
            if "test_first_fix" in payload.get("completed_steps", []):
                failures.append("reject path must not continue to test_first_fix")
            if payload.get("gate_decisions", {}).get("gate_1", {}).get("approved") is not False:
                failures.append("reject path must record gate_1 approval=false")

    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("CrewAI runtime runner checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
''', True)


def create_installers() -> None:
    write("install.sh", r'''#!/usr/bin/env bash
set -euo pipefail

PROVIDER=""
RUNTIME=""
PROJECT=0
FORCE=0
SKIP_BUILD=0
DRY_RUN=0
INCLUDE_AGENTS=1
INCLUDE_SKILLS=1
INCLUDE_COMMANDS=1
INCLUDE_WORKFLOWS=1
INCLUDE_GUIDES=1
INCLUDE_CONTEXT=1

usage() {
  echo "Usage: ./install.sh [--provider claude|codex|gemini|open-source|all] [--runtime nunneri-runtime|langgraph|crewai|autogen|semantic-kernel|all] [--project] [--force] [--dry-run] [--skip-build] [filters]"
  echo "Filters: --agents-only --skills-only --commands-only --workflows-only --context-only --no-agents --no-skills --no-commands --no-workflows --no-guides --no-context"
}

only_one() {
  INCLUDE_AGENTS=0
  INCLUDE_SKILLS=0
  INCLUDE_COMMANDS=0
  INCLUDE_WORKFLOWS=0
  INCLUDE_GUIDES=0
  INCLUDE_CONTEXT=0
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --provider) PROVIDER="$2"; shift 2 ;;
    --runtime) RUNTIME="$2"; shift 2 ;;
    --project) PROJECT=1; shift ;;
    --force) FORCE=1; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    --skip-build) SKIP_BUILD=1; shift ;;
    --agents-only) only_one; INCLUDE_AGENTS=1; shift ;;
    --skills-only) only_one; INCLUDE_SKILLS=1; shift ;;
    --commands-only) only_one; INCLUDE_COMMANDS=1; shift ;;
    --workflows-only) only_one; INCLUDE_WORKFLOWS=1; shift ;;
    --context-only) only_one; INCLUDE_CONTEXT=1; shift ;;
    --no-agents) INCLUDE_AGENTS=0; shift ;;
    --no-skills) INCLUDE_SKILLS=0; shift ;;
    --no-commands) INCLUDE_COMMANDS=0; shift ;;
    --no-workflows) INCLUDE_WORKFLOWS=0; shift ;;
    --no-guides) INCLUDE_GUIDES=0; shift ;;
    --no-context) INCLUDE_CONTEXT=0; shift ;;
    --selective)
      if [ ! -t 0 ]; then
        echo "--selective requires an interactive terminal"
        exit 1
      fi
      printf "Install agents? [Y/n] "; read answer; case "$answer" in n|N|no|NO) INCLUDE_AGENTS=0 ;; esac
      printf "Install skills? [Y/n] "; read answer; case "$answer" in n|N|no|NO) INCLUDE_SKILLS=0 ;; esac
      printf "Install commands? [Y/n] "; read answer; case "$answer" in n|N|no|NO) INCLUDE_COMMANDS=0 ;; esac
      printf "Install workflows? [Y/n] "; read answer; case "$answer" in n|N|no|NO) INCLUDE_WORKFLOWS=0 ;; esac
      printf "Install repository context? [Y/n] "; read answer; case "$answer" in n|N|no|NO) INCLUDE_CONTEXT=0 ;; esac
      printf "Install guides/reference docs? [Y/n] "; read answer; case "$answer" in n|N|no|NO) INCLUDE_GUIDES=0 ;; esac
      shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1"; usage; exit 1 ;;
  esac
done

if [ -z "$PROVIDER" ] && [ -z "$RUNTIME" ]; then
  usage
  exit 1
fi

if [ "$DRY_RUN" -eq 1 ]; then
  echo "Dry run: skipping adapter build and writing no files"
elif [ "$SKIP_BUILD" -eq 0 ]; then
  python3 scripts/build_adapters.py
fi

write_version() {
  version_file="$1"
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "Would write version metadata to $version_file"
    return 0
  fi
  mkdir -p "$(dirname "$version_file")"
  version="$(cat VERSION)"
  printf "%s\n" "$version" > "$version_file"
}

copy_or_report() {
  src_file="$1"
  dest_file="$2"
  label="$3"
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "Would install $dest_file ($label)"
    return 0
  fi
  mkdir -p "$(dirname "$dest_file")"
  if [ -e "$dest_file" ] && [ "$FORCE" -ne 1 ]; then
    echo "Skip existing $dest_file ($label; use --force to overwrite)"
    return 1
  fi
  cp "$src_file" "$dest_file"
  case "$label" in
    root-context) echo "Installed $dest_file into project root" ;;
    provider) echo "Installed $dest_file into provider directory" ;;
    runtime) echo "Installed $dest_file into runtime directory" ;;
    *) echo "Installed $dest_file" ;;
  esac
  return 0
}

should_install() {
  rel="$1"
  case "$rel" in
    agents/*|prompts/agents/*|manifests/agents/*)
      [ "$INCLUDE_AGENTS" -eq 1 ] ;;
    skills/*)
      [ "$INCLUDE_SKILLS" -eq 1 ] ;;
    commands/*|manifests/commands/*|tasks/*|functions/*)
      [ "$INCLUDE_COMMANDS" -eq 1 ] ;;
    workflows/*|flows/*|orchestrations/*)
      [ "$INCLUDE_WORKFLOWS" -eq 1 ] ;;
    graphs/*)
      [ "$INCLUDE_WORKFLOWS" -eq 1 ] ;;
    context/*|manifests/context/*)
      [ "$INCLUDE_CONTEXT" -eq 1 ] ;;
    guides/*|reference/*|docs/*)
      [ "$INCLUDE_GUIDES" -eq 1 ] ;;
    CLAUDE.md|AGENTS.md|GEMINI.md|AGENT_MANIFEST.md|LANGGRAPH.md|NUNNERI_RUNTIME.md|CREWAI.md|AUTOGEN.md|SEMANTIC_KERNEL.md|contract.json)
      [ "$INCLUDE_CONTEXT" -eq 1 ] ;;
    *)
      return 0 ;;
  esac
}

install_runtime() {
  runtime="$1"
  src="dist/$runtime"
  if [ ! -d "$src" ]; then
    echo "Missing $src"
    exit 1
  fi
  case "$runtime" in
    nunneri-runtime) target="$HOME/.nunneri-runtime" ;;
    langgraph) target="$HOME/.langgraph" ;;
    crewai) target="$HOME/.crewai" ;;
    autogen) target="$HOME/.autogen" ;;
    semantic-kernel) target="$HOME/.semantic-kernel" ;;
    *) echo "Unsupported runtime: $runtime"; exit 1 ;;
  esac
  if [ "$PROJECT" -eq 1 ]; then
    case "$runtime" in
      nunneri-runtime) target=".nunneri-runtime" ;;
      langgraph) target=".langgraph" ;;
      crewai) target=".crewai" ;;
      autogen) target=".autogen" ;;
      semantic-kernel) target=".semantic-kernel" ;;
    esac
  fi
  count=0
  skipped=0
  while IFS= read -r file; do
    rel="${file#$src/}"
    if ! should_install "$rel"; then
      continue
    fi
    dest="$target/$rel"
    if copy_or_report "$file" "$dest" "runtime"; then
      ((++count))
    else
      ((++skipped))
    fi
  done < <(find "$src" -type f | sort)
  write_version "$target/.ai-assets-version"
  echo "Summary for $runtime runtime: runtime directory files=$count skipped=$skipped version_metadata=1 target=$target dry_run=$DRY_RUN"
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
    write_version "$target/.ai-assets-version"
    echo "Summary for $provider: prepared_files=$count version_metadata=1 target=$target dry_run=$DRY_RUN"
    return 0
  fi
  provider_count=0
  root_context_count=0
  skipped=0
  while IFS= read -r file; do
    rel="${file#$src/}"
    if ! should_install "$rel"; then
      continue
    fi
    dest="$target/$rel"
    label="provider"
    case "$rel" in
      CLAUDE.md|AGENTS.md|GEMINI.md)
        if [ "$PROJECT" -eq 1 ]; then
          dest="$rel"
          label="root-context"
        fi ;;
    esac
    if copy_or_report "$file" "$dest" "$label"; then
      if [ "$label" = "root-context" ]; then
        ((++root_context_count))
      else
        ((++provider_count))
      fi
    else
      ((++skipped))
    fi
  done < <(find "$src" -type f | sort)
  version_file="$target/.ai-assets-version"
  if [ "$PROJECT" -eq 1 ] && [ "$INCLUDE_CONTEXT" -eq 1 ] && [ "$INCLUDE_AGENTS" -eq 0 ] && [ "$INCLUDE_SKILLS" -eq 0 ] && [ "$INCLUDE_COMMANDS" -eq 0 ] && [ "$INCLUDE_WORKFLOWS" -eq 0 ] && [ "$INCLUDE_GUIDES" -eq 0 ]; then
    version_file=".ai-assets-version"
  fi
  write_version "$version_file"
  echo "Summary for $provider: root context files=$root_context_count provider directory files=$provider_count skipped=$skipped version_metadata=1 target=$target dry_run=$DRY_RUN"
}

if [ "$PROVIDER" = "all" ]; then
  install_one claude
  install_one codex
  install_one gemini
  install_one open-source
elif [ -n "$PROVIDER" ]; then
  install_one "$PROVIDER"
fi

if [ "$RUNTIME" = "all" ]; then
  install_runtime nunneri-runtime
  install_runtime langgraph
  install_runtime crewai
  install_runtime autogen
  install_runtime semantic-kernel
elif [ -n "$RUNTIME" ]; then
  install_runtime "$RUNTIME"
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
    write("AI_ASSETS.md", r'''# Nunneri AI Assets

## What This Is

Nunneri AI Assets is a provider-neutral library of AI agents, skills, commands, workflows, guides, and adapter outputs for Nunneri Engineering.

Nunneri was originated by Suranku and Yamini and is stewarded by the Nunneri Core Team.

## Licensing Model

Nunneri AI Assets are published as an AGPLv3 Community Edition with commercial licensing available.

- AGPLv3 Community Edition: `LICENSE`
- Commercial license path: `COMMERCIAL_LICENSE.md`
- Trademark policy: `TRADEMARKS.md`
- Maintainers and originators: `MAINTAINERS.md`
- Security reporting: `SECURITY.md`
- Governance: `GOVERNANCE.md`
- Roadmap: `ROADMAP.md`
- Citation metadata: `CITATION.cff`

Contact `core@nunneri.com` for commercial licensing. Use `yamini.sk@suranku.com` as the temporary fallback until Nunneri domain email is active.

## Architecture and Defensive Publication

- `ARCHITECTURE.md` documents the product and engineering architecture.
- `DEFENSIVE_PUBLICATION.md` documents the runtime-neutral control plane for defensive-publication and public-disclosure purposes.
- `NUNNERI_RUNTIME_CONTRACT.md` documents the neutral runtime contract and adapter mapping rules.
- `SECURITY.md`, `GOVERNANCE.md`, `ROADMAP.md`, and `CITATION.cff` document the trust, stewardship, release, and citation layer.

Do not use "patent pending" language unless a provisional or nonprovisional patent application has actually been filed.

## Provider-Neutral Source of Truth

Canonical assets live under `assets/`. Provider-specific files are generated into `dist/`.

## Repository Context Template

`assets/context/repo-agent-instructions.md` is the canonical source for repo-level agent instructions. It generates provider-native root context files and structured manifests for open-source and runtime consumers.

Use it for known issues, DevOps overrides, common library links, workflow overrides, exceptions, skill overrides, dispatch rules, approval gates, and release-impact instructions.

Provider-specific behavior belongs in the template's provider override section. The generator renders only the matching override into `CLAUDE.md`, `AGENTS.md`, or `GEMINI.md` so provider-only trigger phrases do not leak across assistants.

Example:

```markdown
### Claude Code

- Treat "agent team" as a Claude-only request to coordinate specialist subagents.

### Codex

- Do not interpret "agent team" as a dispatch command. Ask which repo task should be planned or implemented.
```

## Provider Adapters

- Claude Code: `dist/claude`
- Codex: `dist/codex`
- Gemini: `dist/gemini`
- Open-source frameworks: `dist/open-source`

## Runtime Adapters

- Nunneri Runtime Contract: `dist/nunneri-runtime`
- LangGraph: `dist/langgraph`
- CrewAI: `dist/crewai`
- AutoGen: `dist/autogen`
- Semantic Kernel: `dist/semantic-kernel`

Runtime adapters are orchestration/runtime exports, not model providers. LangGraph is the first runnable runtime in Nunneri Graph Studio; CrewAI, AutoGen, and Semantic Kernel are generated export contracts only in this step.

Runtime adapters consume `dist/nunneri-runtime/` instead of provider-specific files. This preserves one neutral source of truth for approval gates, workflow nodes, dispatch context, and observability hints.

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
python3 scripts/check_context_exports.py
python3 scripts/check_runtime_contract.py
python3 scripts/check_langgraph_exports.py
```

## NFR Compliance Overrides

N/A. This is a Markdown, HTML, and script repository.
''')

    write("README.md", r'''# Nunneri AI Assets

Provider-agnostic AI assets for Claude Code, Codex, Gemini, and open-source agent frameworks.

Nunneri was originated by Suranku and Yamini and is stewarded by the Nunneri Core Team.

## Licensing

Nunneri is distributed as an AGPLv3 Community Edition. Commercial licensing is available for organizations that need closed-source, embedded, proprietary, SaaS, OEM, managed-service, indemnity, or enterprise procurement terms.

- Community Edition: see `LICENSE` for AGPLv3 terms.
- Commercial licensing: see `COMMERCIAL_LICENSE.md`.
- Trademark and brand usage: see `TRADEMARKS.md`.
- Maintainers and originators: see `MAINTAINERS.md`.
- Governance: see `GOVERNANCE.md`.
- Security reporting: see `SECURITY.md`.
- Roadmap: see `ROADMAP.md`.
- Citation metadata: see `CITATION.cff`.

Commercial contact: `core@nunneri.com` (`yamini.sk@suranku.com` is the temporary fallback until Nunneri domain email is active).

## Architecture and Defensive Publication

Nunneri publishes implementation-level architecture and defensive-publication material to establish clear public disclosure of the runtime-neutral control plane.

- Architecture reference: `ARCHITECTURE.md`
- Defensive publication: `DEFENSIVE_PUBLICATION.md`
- Runtime contract details: `NUNNERI_RUNTIME_CONTRACT.md`
- Citation and archival metadata: `CITATION.cff`

The defensive publication documents the architecture for public-disclosure purposes. Do not describe Nunneri as "patent pending" unless a provisional or nonprovisional patent application has actually been filed.

## What's Included

| Category | Source |
| --- | --- |
| Agents | `assets/agents/` |
| Skills | `assets/skills/` |
| Commands | `assets/commands/` |
| Workflows | `assets/workflows/` |
| Repository context | `assets/context/` |
| Guides | `guides/` |
| Runtime contract | `dist/nunneri-runtime/` |
| Runtime adapters | `dist/langgraph/`, `dist/crewai/`, `dist/autogen/`, `dist/semantic-kernel/` |

## Supported Providers

- Claude Code
- OpenAI Codex
- Google Gemini / Gemini CLI
- Open-source agent frameworks

## Supported Runtime Exports

- Nunneri Runtime Contract: neutral export layer consumed by runtime adapters
- LangGraph: first runnable runtime export for stateful workflow orchestration
- CrewAI: export contract for agents, tasks, flows, memory, and human-in-the-loop mapping
- Microsoft AutoGen: export contract for AgentChat/Core orchestration mapping
- Microsoft Semantic Kernel: export contract for agent and orchestration manifests

## Quick Start

```bash
python3 scripts/build_adapters.py
python3 scripts/build_portal_manifest.py
./install.sh --provider all --project --force
```

## Install Repository Context Only

```bash
./install.sh --provider claude --project --context-only --dry-run
./install.sh --provider claude --project --context-only --force
./install.sh --provider codex --project --context-only --force
./install.sh --provider gemini --project --context-only --force
```

The context template generates root files such as `CLAUDE.md`, `AGENTS.md`, and `GEMINI.md` with known issues, DevOps overrides, common library links, workflow overrides, exceptions, skill overrides, and dispatch rules.

Provider-specific instructions can be defined in the same template. During generation, Claude receives only the Claude override section, Codex receives only the Codex section, and Gemini receives only the Gemini section.

For project installs, provider context files are installed at the repository root. Provider assets such as agents, skills, commands, and workflows still install under `.claude/`, `.codex/`, or `.gemini/`.

Example dry run:

```text
$ ./install.sh --provider claude --project --context-only --dry-run
Dry run: skipping adapter build and writing no files
Would install CLAUDE.md (root-context)
Would write version metadata to .ai-assets-version
Summary for claude: root context files=1 provider directory files=0 skipped=0 version_metadata=1 target=.claude dry_run=1
```

Example provider-specific override:

```markdown
### Claude Code

- Treat "agent team" as a Claude-only request to coordinate specialist subagents.

### Codex

- Do not interpret "agent team" as a dispatch command. Ask which repo task should be planned or implemented.
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

## Export Runtime Contracts

```bash
python3 scripts/build_adapters.py
./install.sh --runtime nunneri-runtime --project --force
./install.sh --runtime langgraph --project --force
./install.sh --runtime crewai --project --force
./install.sh --runtime autogen --project --force
./install.sh --runtime semantic-kernel --project --force
```

Runtime exports are generated from the neutral Nunneri contract in `dist/nunneri-runtime/`. They do not install LangGraph, CrewAI, AutoGen, Semantic Kernel, LangSmith, OpenTelemetry, or any model-provider SDK as root dependencies.

See `NUNNERI_RUNTIME_CONTRACT.md` for the contract shape and runtime mapping rules.

For a dependency-free consumer example that reads the neutral contract and projects `triage-nine-phase` into a CrewAI-style flow shape, see `examples/runtime-contract-consumer/`.

For the first runnable CrewAI-facing contract harness, see `examples/crewai-runtime-runner/`. It executes the generated CrewAI flow manifest, supports approve/reject gate paths, and proves rejection cancels downstream work without requiring the CrewAI SDK.

For an interactive walkthrough of provider context, neutral workflow phases, human gates, and runtime adapter projections, open `guides/runtime-contract-demo.html`.

For an end-user setup path with durable state and tracing choices, see `guides/end-user-langgraph-setup.md` or open `guides/end-user-setup-demo.html`.

The API server's LangGraph runner uses human-blocking approval gates. Gate nodes pause with `interrupt()`, persist through the configured checkpointer, emit `gate_waiting`, and resume only through `POST /threads/{thread_id}/gates/{gate_id}/approve` or `/reject`. Nunneri Graph Studio reads the same runtime contract to show workflow phase config, classification options, edge conditions, and approval-gate context.

Recommended portable runtime configuration:

```bash
NUNNERI_RUNTIME=langgraph
NUNNERI_STATE_STORE=sqlite
NUNNERI_TRACE_MODE=otel
```

Use `NUNNERI_TRACE_MODE=langsmith` and `LANGSMITH_API_KEY` only when the consuming team chooses LangSmith as an optional hosted tracing UI. Use `NUNNERI_TRACE_MODE=none` for offline or no-observability installs.

## Install Into a Consumer Repository

Use `examples/consumer-repo/` as the reference flow for installing Nunneri AI Assets into another GitHub repository.

```bash
python3 scripts/check_consumer_install.py
```

The smoke check stages a temporary consumer repo and verifies context-only dry runs, root `CLAUDE.md` installs, provider assets under `.claude/`, LangGraph exports under `.langgraph/`, and skip behavior when a root context file already exists.

Use `examples/runtime-contract-consumer/` to see a direct runtime contract consumer that does not import any runtime SDK.

## Internal Releases

Internal dist releases use short-lived `release/vX.Y.Z` branches and `vX.Y.Z` tags. The GitHub release workflow publishes prerelease archives from tags that match `VERSION`.

```bash
git checkout main
git pull
git checkout -b release/v0.1.0
python3 scripts/package_release.py
python3 scripts/check_release_package.py
git tag v0.1.0
git push origin v0.1.0
```

See `RELEASE.md` for the full branch strategy and release checklist.

## Project Trust and Governance

- Security reports are handled privately through `SECURITY.md`.
- Project decisions, sensitive-change rules, and runtime contract stewardship are documented in `GOVERNANCE.md`.
- Near-term Community Edition priorities and commercial/enterprise options are documented in `ROADMAP.md`.
- Cite public releases using `CITATION.cff`; optionally archive GitHub releases with Zenodo for a DOI.

## Command Reference

See `assets/commands/` and the GitHub Pages portal at `docs/index.html`.

## Contributing

Use GitHub Issues first. Contributions must acknowledge the Nunneri Contributor License Agreement so the project can keep AGPLv3 Community Edition and commercial licensing available. See `CONTRIBUTING.md` and `CONTRIBUTOR_LICENSE_AGREEMENT.md`.
''')

    write("LANGGRAPH_RUNTIME.md", r'''# LangGraph Runtime Adapter

LangGraph support is provided as a runtime adapter, not as a model provider.

Claude, Codex, and Gemini are provider adapters because they map prompts, skills, commands, and context into model-specific coding assistant surfaces. LangGraph is different: it is an orchestration runtime for stateful agent workflows. This repository exports graph metadata from the neutral Nunneri Runtime Contract without requiring LangGraph as a dependency in this repo.

## Generated Outputs

Run:

```bash
python3 scripts/build_adapters.py
```

Generated LangGraph files are written to:

```text
dist/nunneri-runtime/
  workflows/triage-nine-phase.json

dist/langgraph/
  LANGGRAPH.md
  manifests/
    agents/
    commands/
  graphs/
```

## Triage Graph Contract

`dist/nunneri-runtime/workflows/triage-nine-phase.json` is the neutral contract. `dist/langgraph/graphs/triage-nine-phase.json` is derived from that contract.

Required nodes:

```text
intake
context_load
classification
evidence_collection
root_cause_analysis
gate_1
test_first_fix
validation
gate_2
```

`gate_1` and `gate_2` are marked as human approval checkpoints.

## Human-Blocking Gate Runtime

When the API server runs a LangGraph workflow, human approval checkpoints use LangGraph `interrupt()` and durable checkpoint state. A gate does not auto-pass.

Runtime behavior:

- The graph pauses at the gate and stores the checkpoint under the same `thread_id`.
- SSE emits `gate_waiting` with a JSON approval payload.
- `nunneri_runs.status` becomes `waiting_approval`.
- The gate's `nunneri_run_nodes.status` becomes `waiting_approval`.
- The graph resumes only through an explicit decision endpoint.

Resume endpoints:

```text
POST /threads/{thread_id}/gates/{gate_id}/approve
POST /threads/{thread_id}/gates/{gate_id}/reject
```

Approval resumes the checkpoint with `Command(resume={"approved": true, ...})` and continues downstream. Rejection resumes with `approved: false`, marks the gate `rejected`, emits `run_rejected`, and routes to a terminal cancellation node instead of executing downstream work.

The legacy `/agents/{name}/invoke/trace` path is only a simulated trace. It stops at a gate with `gate_waiting` and does not imply real approval.

## Installation

Install generated runtime exports into a project-local `.langgraph/` directory:

```bash
./install.sh --runtime langgraph --project --force
```

Install only graph workflows:

```bash
./install.sh --runtime langgraph --project --force --workflows-only
```

## End-User Runtime Setup

Use LangGraph as an orchestration runtime target after installing the provider context for Claude, Codex, or Gemini. The base repository exports manifests only; it does not add LangGraph, LangSmith, OpenTelemetry, or provider SDK dependencies to the root project.

Recommended portable configuration:

```bash
NUNNERI_RUNTIME=langgraph
NUNNERI_STATE_STORE=sqlite
NUNNERI_TRACE_MODE=otel
```

Use repository-local durable state for checkpoints and resumable workflow context:

```text
.nunneri/langgraph/state.sqlite
```

Supported trace modes:

```text
otel       OpenTelemetry-first monitoring path
langsmith  Optional hosted LangGraph tracing UI path
none       No tracing
```

`LANGSMITH_API_KEY` is only required when `NUNNERI_TRACE_MODE=langsmith`.

See `guides/end-user-langgraph-setup.md` and `guides/end-user-setup-demo.html` for the end-user walkthrough.

## Validation

Run:

```bash
python3 scripts/check_langgraph_exports.py
python3 scripts/check_runtime_contract.py
python3 scripts/check_user_setup_docs.py
```

This verifies that the neutral contract exists, the LangGraph export was generated from it, the triage graph has exactly nine nodes, the edge order follows the canonical workflow, and both approval gates are marked.
''')

    write("CONTRIBUTING.md", f"""# Contributing

Contributions to {PLATFORM} start with GitHub Issues.

Nunneri uses an AGPLv3 Community Edition plus commercial licensing model. Contributions must acknowledge the Nunneri Contributor License Agreement in `CONTRIBUTOR_LICENSE_AGREEMENT.md` so the project can continue distributing accepted contributions under both AGPLv3 and commercial terms.

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

Every PR must link the accepted issue, include validation output, declare provider impact, and confirm CLA acceptance.

## Step 5 - CODEOWNERS Approval, Merge, and Distribute

CODEOWNERS approval is required before merge.

License, trademark, commercial-license, homepage, release, and generated-reference changes require Nunneri Core Team review.

## Issue Labels and Triage States

Use type, asset, provider, priority, and status labels from `.github/labels.yml`.

## Issue to Release Flow

Accepted issues are assigned a release target and must be referenced in `CHANGELOG.md` before release.

## Release Participation

Release owner: `core@nunneri.com`.

Temporary fallback until Nunneri domain email is active: `{RELEASE_OWNER}`.

## Contributor License Agreement

Every pull request must include this acknowledgment:

```text
I agree that my contribution is submitted under the Nunneri Contributor License Agreement.
```

Do not merge PRs that change license, trademark, commercial-use, or ownership language without CODEOWNERS approval.

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

Ship stable provider-neutral assets, generated provider adapters, and runtime exports together.

## Semantic Versioning

- Patch: documentation fixes, prompt wording changes, non-breaking adapter fixes
- Minor: new agents, skills, commands, workflows, provider adapters, or runtime adapters
- Major: breaking frontmatter, installer, invocation, or adapter contract changes

## Release Cadence

Monthly by default, with ad hoc patch releases for urgent fixes.

## Release Roles

Release owner: `core@nunneri.com`.

Temporary fallback until Nunneri domain email is active: `{RELEASE_OWNER}`.

Commercial license and trademark-impacting release decisions require Nunneri Core Team approval.

## Branch Strategy

- `main`: default integration branch for feature and fix PRs. It must always pass validation.
- `feature/<issue-number>-short-description`: new assets, docs, installer changes, workflows, examples, and non-release enhancements.
- `fix/<issue-number>-short-description`: bug fixes and small corrections.
- `release/vX.Y.Z`: short-lived stabilization branch cut from `main` for internal releases.
- `vX.Y.Z`: release tag created from a commit contained in `release/vX.Y.Z`.

Do not use `develop` or `master` for this repository. The asset package is small enough that `main` plus short-lived release branches keeps the release process clear without adding another permanent integration branch.

## Versioning Rules

Update `VERSION` and `CHANGELOG.md` before tagging.

The GitHub release workflow requires the tag version to match `VERSION`. For example, tag `v0.1.0` requires `VERSION` to contain `0.1.0`.

## Changelog Rules

Every release-targeted issue must be represented in `CHANGELOG.md`.

## Adapter Compatibility

Claude, Codex, Gemini, open-source, and LangGraph outputs must build from the same canonical assets.

## Release Checklist

1. Confirm planned issues are accepted and linked to merged PRs.
2. Cut `release/vX.Y.Z` from `main`.
3. Update `VERSION` and `CHANGELOG.md`.
4. Run validation, adapter builds, docs sync, consumer install checks, and package checks.
5. Confirm `ARCHITECTURE.md`, `DEFENSIVE_PUBLICATION.md`, `LICENSE`, `COMMERCIAL_LICENSE.md`, `TRADEMARKS.md`, `MAINTAINERS.md`, `NOTICE.md`, and `CONTRIBUTOR_LICENSE_AGREEMENT.md` are present and synced to reference docs.
6. Create a release PR from `release/vX.Y.Z` back to `main`.
7. After approval, tag the release branch with `vX.Y.Z`.
8. Push the release branch and tag.
9. Confirm GitHub Actions publishes the internal prerelease with dist archives.
10. Merge release branch changes back to `main` if the branch contains release-only commits.

## Internal Dist Release Flow

```bash
git checkout main
git pull
git checkout -b release/v0.1.0
```

Update `VERSION` and `CHANGELOG.md`, then run:

```bash
python3 scripts/validate.py
python3 scripts/build_adapters.py
python3 scripts/build_portal_manifest.py
python3 scripts/sync_docs_reference.py
python3 scripts/check_docs_links.py
python3 scripts/check_context_exports.py
python3 scripts/check_langgraph_exports.py
python3 scripts/check_consumer_install.py
python3 scripts/package_release.py
python3 scripts/check_release_package.py
python3 scripts/check_release_ready.py --local-only
```

After review and approval:

```bash
git tag v0.1.0
git push origin release/v0.1.0
git push origin v0.1.0
```

The `Internal Dist Release` workflow publishes a GitHub prerelease with:

```text
nunneri-ai-assets-0.1.0.zip
nunneri-ai-assets-0.1.0.tar.gz
nunneri-ai-assets-0.1.0.sha256
```

Manual workflow dispatch is also supported for internal release reruns, but the requested version must match `VERSION`.

## Rollback Strategy

Revert the release commit or publish a patch release that restores the previous adapter contract.

## Deprecation Policy

Mark deprecated assets in canonical metadata for one minor release before removal.
""")

    write("ARCHITECTURE.md", """# Nunneri Architecture

Nunneri is a provider- and runtime-neutral control plane for AI assets, agentic workflows, human approval gates, and auditable execution.

Nunneri was originated by Suranku and Yamini and is stewarded by the Nunneri Core Team.

## System Components

- `assets/`: canonical agents, skills, commands, workflows, and repository context
- `dist/nunneri-runtime/`: runtime-neutral contract generated from canonical assets
- provider adapters: Claude, Codex, Gemini, and open-source exports
- runtime adapters: LangGraph, CrewAI, AutoGen, and Semantic Kernel exports
- `api/`: FastAPI server, provider routing, RBAC checks, run persistence, and graph execution
- Graph Studio: browser UI for workflow phases, approvals, traces, outputs, and reruns
- trust layer: `SECURITY.md`, `GOVERNANCE.md`, `ROADMAP.md`, `CITATION.cff`, release evidence, defensive publication, licensing, and trademark records

## Runtime-Neutral Flow

Canonical assets are generated into the Nunneri Runtime Contract. Runtime adapters consume that contract rather than provider-specific files. Human approval semantics, rejection cancellation, context injection, and observability hints must be preserved across adapter projections.

## Tenant and RBAC Model

Nunneri scopes execution through organization -> team -> project -> thread -> run -> node output. RBAC applies to dispatch, gate approval or rejection, run history, phase configuration, and release-impacting actions.

## Graph Studio

Graph Studio consumes the same runtime contract as the API server. It presents technical nodes as workflow phases and binds phase output, approval cards, errors, and final summaries to persisted run records.

## Trust, Governance, and Release Evidence

Nunneri treats project trust artifacts as part of the architecture, not detached paperwork.

The trust layer includes `SECURITY.md` for vulnerability reporting, `GOVERNANCE.md` for decision authority and runtime contract stewardship, `ROADMAP.md` for Community Edition and commercial/enterprise priorities, `CITATION.cff` for public release citation metadata, `DEFENSIVE_PUBLICATION.md` for implementation-level public disclosure, and license/trademark/notice/CLA documents for ownership and contribution boundaries.

Release packaging and release readiness checks require these documents, sync them into `docs/reference/`, and include them in generated release archives.

## Object Storage Guidance

Object storage is optional. Use a pluggable storage boundary for filesystem, cloud object storage, or S3-compatible storage. MinIO can be supported as an optional deployment choice, but it should not be a required bundled dependency because it has independent licensing considerations.
""")

    write("DEFENSIVE_PUBLICATION.md", """# Defensive Publication: Nunneri Runtime-Neutral Agentic Control Plane

Publication date: 2026-07-01

Originators: Suranku and Yamini

Steward: Nunneri Core Team

## Patent and Defensive Publication Notice

This document publicly discloses the Nunneri architecture and implementation concepts for defensive-publication purposes. It is not legal advice and is not a patent application.

Do not describe Nunneri as "patent pending" unless a provisional or nonprovisional patent application has actually been filed.

## Disclosed Runtime-Neutral Control Plane

Nunneri stores canonical provider-neutral assets in `assets/`, generates `dist/nunneri-runtime/` as the neutral contract, and then derives provider and runtime adapters for Claude, Codex, Gemini, open-source exports, LangGraph, CrewAI, AutoGen, and Semantic Kernel.

The runtime-neutral control plane preserves:

- provider-neutral assets compiled into a neutral runtime contract
- generated runtime adapters with SDK-specific details outside canonical assets
- Graph Studio consumption of the same contract for phases, traces, node outputs, and approvals
- human-blocking approval gates with approve/reject decisions and downstream cancellation on rejection
- durable state outside LLM context through threads, runs, checkpoints, and per-phase outputs
- RBAC and multi-tenant scoping across org, team, project, thread, run, and approval actions
- provider-specific context overrides without canonical-source drift

## Reproducibility

Representative validation:

```bash
python3 scripts/build_adapters.py
python3 scripts/check_runtime_contract.py
python3 scripts/check_langgraph_exports.py
python3 scripts/check_human_gates.py
python3 scripts/check_release_ready.py --local-only
```
""")

    license_text = (ROOT / "LICENSE").read_text(encoding="utf-8") if (ROOT / "LICENSE").exists() else """GNU Affero General Public License v3.0

This bootstrapped repository uses the AGPLv3 Community Edition licensing posture. Replace this fallback with the full standard AGPLv3 license text before public release.
"""
    write("LICENSE", license_text)
    write("COMMERCIAL_LICENSE.md", """# Commercial License

Nunneri is publicly available under the GNU Affero General Public License version 3.0 (AGPLv3). A commercial license is available for organizations that need rights outside the AGPLv3 Community Edition.

Contact `core@nunneri.com` for closed-source, embedded, hosted, SaaS, OEM, managed-service, indemnity, or enterprise procurement terms.

Temporary fallback until Nunneri domain email is active: `yamini.sk@suranku.com`.
""")
    write("TRADEMARKS.md", """# Trademark Policy

Nunneri, the Nunneri name, and Nunneri logos are project trademarks associated with the Nunneri Core Team.

Use the Nunneri name truthfully to refer to the project, describe compatibility, or link to official releases. Do not imply endorsement, certification, partnership, or official status for forks, hosted services, or commercial packages without written permission.

Contact `core@nunneri.com` for trademark permission. Temporary fallback: `yamini.sk@suranku.com`.
""")
    write("MAINTAINERS.md", """# Maintainers

Nunneri was originated by Suranku and Yamini and is stewarded by the Nunneri Core Team.

The core team owns repository direction, release readiness, licensing, commercial-use decisions, trademark decisions, CODEOWNERS review, and release-impact escalation.

Preferred contact: `core@nunneri.com`

Temporary fallback until Nunneri domain email is active: `yamini.sk@suranku.com`
""")
    write("SECURITY.md", """# Security Policy

Nunneri is public source under the AGPLv3 Community Edition with commercial licensing available. Security reports should be handled privately before public disclosure.

## Reporting a Vulnerability

Email `core@nunneri.com` with the subject `Nunneri Security Report`.

Temporary fallback until Nunneri domain email is active: `yamini.sk@suranku.com`.

Include the affected version or commit, affected component, reproduction steps, expected and actual impact, and any safe private proof-of-concept details.

Do not open a public GitHub issue for a suspected vulnerability until the Nunneri Core Team has reviewed it.

## Security Scope

In scope: authentication and authorization bypass, multi-tenant isolation failures, approval-gate bypass, provider key leakage, thread or run state leakage, unsafe installer behavior, and release validation bypass.

Never commit `.env`, API keys, OIDC client secrets, LangSmith keys, cloud credentials, or local database credentials.
""")
    write("GOVERNANCE.md", """# Governance

Nunneri was originated by Suranku and Yamini and is stewarded by the Nunneri Core Team.

This document defines how the public project makes decisions while preserving the AGPLv3 Community Edition plus commercial licensing model.

## Runtime Contract Stewardship

The neutral Nunneri Runtime Contract is the project control plane. Runtime adapters must consume the neutral contract rather than provider-specific files.

Sensitive changes require Nunneri Core Team review: license, commercial-license, CLA, notice, ownership text, trademark usage, security policy, release process, defensive publication, architecture, runtime contract compatibility, authentication, RBAC, tenant isolation, approval gates, and provider key handling.

## Community and Commercial Boundaries

The public repository is the AGPLv3 Community Edition. Commercial licensing is available for organizations that need closed-source, embedded, proprietary, SaaS, OEM, managed-service, indemnity, or enterprise procurement terms.
""")
    write("ROADMAP.md", """# Roadmap

Nunneri is focused on a provider- and runtime-neutral control plane for agentic workflows.

## Community Edition Priorities

- improve Graph Studio run inspection and per-stage output quality
- strengthen human approval UX for pending, approved, rejected, cancelled, and completed runs
- improve provider-key model routing and local development auth
- expand runtime contract validation and adapter smoke tests
- keep MinIO and other object storage optional through S3-compatible adapters

## Commercial and Enterprise Options

Commercial licensing is available for teams that need proprietary usage or enterprise terms. Potential commercial-facing work may include enterprise support, deployment hardening, managed-service packaging, indemnity, private adapter support, identity integrations, and compliance reporting.
""")
    write("CITATION.cff", """cff-version: 1.2.0
message: "If you use Nunneri in research, publications, demos, or derivative systems, please cite the public repository and release."
title: "Nunneri Public Agentic AI"
version: "0.1.0"
date-released: "2026-07-01"
repository-code: "https://github.com/suranku/nunneri-public-agentic-ai"
url: "https://github.com/suranku/nunneri-public-agentic-ai/releases/tag/v0.1.0"
license: "AGPL-3.0-only"
abstract: "Nunneri is a provider- and runtime-neutral control plane for agentic AI assets, runtime contracts, human-blocking approval gates, durable run state, and multi-tenant Graph Studio execution."
authors:
  - name: "Suranku"
  - name: "Yamini"
keywords:
  - "agentic-ai"
  - "runtime-contract"
  - "human-in-the-loop"
""")
    write("NOTICE.md", """# Notices

Nunneri AI Assets

Copyright (c) 2026 Suranku, Yamini, and the Nunneri Core Team.

Nunneri is distributed under the GNU Affero General Public License version 3.0 for the Community Edition. Commercial licensing is available from the Nunneri Core Team.

The Nunneri name and logos are project trademarks. See `TRADEMARKS.md` for brand usage guidance.
""")
    write("CONTRIBUTOR_LICENSE_AGREEMENT.md", """# Contributor License Agreement

This Contributor License Agreement (CLA) applies to contributions submitted to Nunneri AI Assets.

By submitting a contribution, you confirm that you have the right to submit it and grant Suranku, Yamini, and the Nunneri Core Team a perpetual, worldwide, non-exclusive, royalty-free license to use, reproduce, modify, distribute, sublicense, and relicense your contribution as part of Nunneri under AGPLv3 and separate commercial license terms.

Pull requests must confirm:

```text
I agree that my contribution is submitted under the Nunneri Contributor License Agreement.
```
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
    write("CODEOWNERS", """* @Yamini-Suranku @suranku

# Licensing, ownership, trademark, homepage, and release-sensitive changes require core review.
/LICENSE @Yamini-Suranku @suranku
/COMMERCIAL_LICENSE.md @Yamini-Suranku @suranku
/TRADEMARKS.md @Yamini-Suranku @suranku
/MAINTAINERS.md @Yamini-Suranku @suranku
/GOVERNANCE.md @Yamini-Suranku @suranku
/SECURITY.md @Yamini-Suranku @suranku
/ROADMAP.md @Yamini-Suranku @suranku
/CITATION.cff @Yamini-Suranku @suranku
/NOTICE.md @Yamini-Suranku @suranku
/CONTRIBUTOR_LICENSE_AGREEMENT.md @Yamini-Suranku @suranku
/ARCHITECTURE.md @Yamini-Suranku @suranku
/DEFENSIVE_PUBLICATION.md @Yamini-Suranku @suranku
/docs/index.html @Yamini-Suranku @suranku
/RELEASE.md @Yamini-Suranku @suranku
/.github/PULL_REQUEST_TEMPLATE.md @Yamini-Suranku @suranku
/.github/ISSUE_TEMPLATE/ @Yamini-Suranku @suranku
""")
    write("docs/_config.yml", f"title: {PLATFORM}\n")
    write(".gitignore", """.claude/
.codex/
.gemini/
.langgraph/
dist/open-source/.ai-assets-version
dist/releases/
__pycache__/
.DS_Store
""")
    write("docs/index.html", portal_html())

    write("adapters/claude/CLAUDE.md", "# Claude Adapter\n\nGenerated Claude outputs are built into `dist/claude/`.")
    write("adapters/codex/AGENTS.md", "# Codex Adapter\n\nGenerated Codex outputs are built into `dist/codex/`.")
    write("adapters/gemini/GEMINI.md", "# Gemini Adapter\n\nGenerated Gemini outputs are built into `dist/gemini/`.")
    write("adapters/langgraph/README.md", "# LangGraph Runtime Adapter\n\nLangGraph is treated as an orchestration runtime, not as a model provider.\n\nGenerated runtime files are written to `dist/langgraph/` by `scripts/build_adapters.py`.")
    write("NUNNERI_RUNTIME_CONTRACT.md", r'''# Nunneri Runtime Contract

The Nunneri Runtime Contract is the provider- and framework-neutral export layer between canonical assets and runtime adapters.

Authors edit `assets/`. The build step generates `dist/nunneri-runtime/` first, then derives runtime-specific exports for LangGraph, CrewAI, Microsoft AutoGen, and Microsoft Semantic Kernel.

For the broader system architecture and public-disclosure record, see `ARCHITECTURE.md` and `DEFENSIVE_PUBLICATION.md`.

Do not describe Nunneri as "patent pending" unless a provisional or nonprovisional patent application has actually been filed.

## Generated Contract

```text
dist/nunneri-runtime/
  contract.json
  agents/*.json
  commands/*.json
  workflows/*.json
  context/repo-agent-instructions.json
```

Each individual contract file uses `contract_version: "1.0"` and includes:

- asset identity, source, and description
- provider-neutral inputs, agents, commands, nodes, and edges
- context injection metadata
- runtime hints for state, human-in-the-loop behavior, and observability

## Runtime Mapping

- LangGraph maps workflow nodes and edges into graph JSON. `human_approval` nodes become interrupt-capable approval checkpoints.
- CrewAI maps agents into agent manifests, commands into task manifests, and workflows into flow manifests.
- AutoGen maps agents into AgentChat/Core agent specs and workflows into group orchestration manifests.
- Semantic Kernel maps agents into SK agent definitions and workflows into orchestration manifests.

Runtime-specific SDK fields belong in generated runtime adapter output, not in canonical `assets/`.

Graph Studio also consumes the contract projection exposed by the API. The UI names these executable steps **workflow phases** for users, while the JSON and runtime adapters continue to use the technical `nodes` field.

## Approval Semantics

Runtime adapters must preserve `human_approval` semantics:

- approval is required before downstream implementation work
- allowed actions are `approve` and `reject`
- rejection policy is `cancel`
- rejection must not continue to downstream implementation nodes

## Install

Install the neutral contract itself:

```bash
./install.sh --runtime nunneri-runtime --project --force
```

Install a runtime adapter export:

```bash
./install.sh --runtime langgraph --project --force
./install.sh --runtime crewai --project --force
./install.sh --runtime autogen --project --force
./install.sh --runtime semantic-kernel --project --force
```

No runtime SDK dependencies are installed by this repository.

## Consumer Example

`examples/runtime-contract-consumer/` contains a dependency-free Python example that reads `dist/nunneri-runtime/contract.json`, loads `triage-nine-phase`, and projects it into a CrewAI-style flow shape while preserving approval gates.

`examples/crewai-runtime-runner/` contains the first runnable CrewAI-facing contract harness. It reads `dist/crewai/flows/triage-nine-phase.json`, runs the generated steps, supports approve/reject gate paths, and verifies rejection cancels downstream implementation work. It does not require the CrewAI SDK.

Validate it with:

```bash
python3 scripts/check_runtime_examples.py
python3 scripts/check_crewai_runtime_runner.py
```

## Interactive Demo

Open `guides/runtime-contract-demo.html` for a step-by-step walkthrough covering provider context files, `triage-nine-phase`, `gate_1`, `gate_2`, LangGraph, CrewAI, AutoGen, Semantic Kernel, and the validation checks that keep the exports aligned.

```bash
python3 scripts/check_runtime_contract.py
python3 scripts/check_graph_studio_contract.py
python3 scripts/check_runtime_examples.py
```
''')
    write("adapters/crewai/README.md", r'''# CrewAI Runtime Adapter

CrewAI is treated as a runtime adapter target, not a model provider.

Generated files in `dist/crewai/` are derived from `dist/nunneri-runtime/` and map neutral Nunneri agents, commands, workflows, and approval gates into portable CrewAI-oriented JSON manifests.

This repository does not install CrewAI SDK dependencies. Consumers can use these manifests as an integration contract when they add a runnable CrewAI application.
''')
    write("adapters/autogen/README.md", r'''# AutoGen Runtime Adapter

Microsoft AutoGen is treated as a runtime adapter target, not a model provider.

Generated files in `dist/autogen/` are derived from `dist/nunneri-runtime/` and map neutral Nunneri agents, commands, workflows, and approval gates into portable AutoGen-oriented JSON manifests.

This repository does not install AutoGen SDK dependencies. Consumers can use these manifests as an integration contract when they add AgentChat, Core, Studio, extensions, or distributed-runtime implementations.
''')
    write("adapters/semantic-kernel/README.md", r'''# Semantic Kernel Runtime Adapter

Microsoft Semantic Kernel is treated as a runtime adapter target, not a model provider.

Generated files in `dist/semantic-kernel/` are derived from `dist/nunneri-runtime/` and map neutral Nunneri agents, commands, workflows, and approval gates into portable Semantic Kernel-oriented JSON manifests.

This repository does not install Semantic Kernel dependencies. Consumers can use these manifests as an integration contract when they add runnable agent orchestration.
''')
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
        buttons = "\n".join(
            f'<button data-panel="{i}" role="tab" aria-selected="{"true" if i == 0 else "false"}" aria-controls="panel-{i}" tabindex="{0 if i == 0 else -1}" class="{"active" if i == 0 else ""}"><span class="step-index">{i + 1}</span><span>{panel}</span></button>'
            for i, panel in enumerate(panels)
        )
        contents = "\n".join(
            f'''<div class="panel" id="panel-{i}" data-content="{i}" role="tabpanel" {"hidden" if i else ""}>
  <strong>{panel}</strong>
  <p>{panel} produces evidence that feeds the provider-neutral workflow, adapter generation, and release readiness checks.</p>
  <div class="evidence-grid">
    <div class="metric"><span>Input</span><b>Issue or command context</b></div>
    <div class="metric"><span>Output</span><b>Evidence-backed next action</b></div>
    <div class="metric"><span>Gate</span><b>{"Approval required" if "Gate" in panel or panel in {"PR", "Release", "Fix"} else "Continue when validated"}</b></div>
  </div>
</div>'''
            for i, panel in enumerate(panels)
        )
        write(f"guides/{filename}", simple_html(title, subtitle, f'<div class="timeline" role="tablist" aria-label="{title} steps">{buttons}</div><div class="panel-stage">{contents}</div>'))

    setup_steps = [
        ("Select Provider", "Choose Claude, Codex, or Gemini for the consuming repository. LangGraph remains the runtime export, not the provider.", "./install.sh --provider claude --project --context-only --dry-run\n./install.sh --provider codex --project --context-only --dry-run\n./install.sh --provider gemini --project --context-only --dry-run", "No files written"),
        ("Preview Context", "Dry-run the provider root context file before writing CLAUDE.md, AGENTS.md, or GEMINI.md.", "./install.sh --provider claude --project --context-only --dry-run", "Root context target"),
        ("Install Assets", "Install provider context at the repository root and provider assets under the provider folder.", "./install.sh --provider claude --project --force", "CLAUDE.md and .claude/"),
        ("Export Runtime", "Install LangGraph graph, command, agent, and pre-dispatch context manifests.", "python3 scripts/build_adapters.py\n./install.sh --runtime langgraph --project --force", ".langgraph/"),
        ("Persist State", "Keep checkpoints and durable runtime context outside the LLM context window.", "NUNNERI_RUNTIME=langgraph\nNUNNERI_STATE_STORE=sqlite\n.nunneri/langgraph/state.sqlite", "Repository-local state"),
        ("Trace and Monitor", "Default to OpenTelemetry. Use LangSmith only when a team chooses the hosted tracing UI.", "NUNNERI_TRACE_MODE=otel\nNUNNERI_TRACE_MODE=langsmith\nLANGSMITH_API_KEY=replace-with-your-key\nNUNNERI_TRACE_MODE=none", "otel, langsmith, or none"),
        ("Validate Setup", "Confirm the consumer install, LangGraph exports, and setup docs before sharing the pattern.", "python3 scripts/check_consumer_install.py\npython3 scripts/check_langgraph_exports.py\npython3 scripts/check_user_setup_docs.py", "Checks pass"),
    ]
    setup_buttons = "\n".join(
        f'<button data-panel="{i}" role="tab" aria-selected="{"true" if i == 0 else "false"}" aria-controls="panel-{i}" tabindex="{0 if i == 0 else -1}" class="{"active" if i == 0 else ""}"><span class="step-index">{i + 1}</span><span>{title}</span></button>'
        for i, (title, _, _, _) in enumerate(setup_steps)
    )
    setup_contents = "\n".join(
        f'''<div class="panel" id="panel-{i}" data-content="{i}" role="tabpanel" {"hidden" if i else ""}>
  <strong>{title}</strong>
  <p>{description}</p>
  <pre><code>{command}</code></pre>
  <div class="evidence-grid">
    <div class="metric"><span>Step</span><b>{i + 1} of {len(setup_steps)}</b></div>
    <div class="metric"><span>Signal</span><b>{signal}</b></div>
    <div class="metric"><span>Runtime</span><b>{"LangGraph" if i >= 3 else "Provider context first"}</b></div>
  </div>
</div>'''
        for i, (title, description, command, signal) in enumerate(setup_steps)
    )
    write("guides/end-user-setup-demo.html", simple_html(
        "End-User Setup Demo",
        "Install provider context, export LangGraph runtime manifests, keep workflow state outside the LLM context, and choose tracing without mandatory hosted dependencies.",
        f'<div class="timeline" role="tablist" aria-label="End-user setup steps">{setup_buttons}</div><div class="panel-stage">{setup_contents}</div>',
    ))

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

    write("guides/end-user-langgraph-setup.md", """# End-User LangGraph Setup

This guide shows how a consumer repository can install Nunneri provider context, add LangGraph runtime exports, and prepare for stateful orchestration with optional tracing.

LangGraph is a runtime adapter target in Nunneri, not a model provider. Claude, Codex, Gemini, and open-source exports remain the provider targets. LangGraph consumes the generated graph, agent, command, and context manifests.

## Setup Path

Start from a clone or an internal release package:

```bash
git clone https://github.com/suranku/nunneri-public-agentic-ai.git
cd nunneri-public-agentic-ai
python3 scripts/build_adapters.py
```

Preview what provider context would write into your project root:

```bash
./install.sh --provider claude --project --context-only --dry-run
```

Install the provider context and assets you need:

```bash
./install.sh --provider claude --project --force
./install.sh --provider codex --project --force
./install.sh --provider gemini --project --force
```

Install LangGraph runtime exports:

```bash
./install.sh --runtime langgraph --project --force
```

The runtime install writes generated graph, command, agent, and pre-dispatch context manifests under `.langgraph/`.

## Runtime Configuration

Use repository-local configuration so orchestration state can live outside the LLM context window:

```bash
NUNNERI_RUNTIME=langgraph
NUNNERI_STATE_STORE=sqlite
NUNNERI_TRACE_MODE=otel|langsmith|none
```

Recommended default:

```bash
NUNNERI_RUNTIME=langgraph
NUNNERI_STATE_STORE=sqlite
NUNNERI_TRACE_MODE=otel
```

For optional LangSmith tracing, add:

```bash
LANGSMITH_API_KEY=replace-with-your-key
```

Do not require `LANGSMITH_API_KEY` for base setup. OpenTelemetry is the open-source-first monitoring path; LangSmith is an optional hosted tracing UI path.

## Durable State

Use a project-local state path such as:

```text
.nunneri/langgraph/state.sqlite
```

This file is for runtime checkpoints, resumable workflow state, and context that should persist outside the LLM prompt. Add it to the consuming repo's ignore rules unless the team has a deliberate reason to commit runtime state.

## Validation

Run the repo checks before sharing the setup:

```bash
python3 scripts/check_consumer_install.py
python3 scripts/check_langgraph_exports.py
python3 scripts/check_user_setup_docs.py
```

For the interactive walkthrough, open:

```text
guides/end-user-setup-demo.html
```

## What This Does Not Add Yet

This setup does not add a Python LangGraph application, SDK dependency, hosted monitoring dependency, or provider SDK dependency. It defines the portable install and runtime contract first.
""")

    write("guides/README.md", r'''# Guides

This directory contains executive summaries and static interactive demos for Nunneri AI Assets.

## Setup and Installation

- `platform-onboarding.md` — provider installs, root context files, neutral runtime contracts, LangGraph runtime exports, API server quick start, and release flow.
- `end-user-langgraph-setup.md` — how a consuming repository installs provider context, adds `.langgraph/` runtime exports, keeps durable state, and chooses tracing.
- `end-user-setup-demo.html` — interactive step-by-step setup walkthrough.
- `runtime-contract-demo.html` — interactive walkthrough of the neutral contract, workflow phases, human gates, and runtime adapter projections.

## Graph Studio (Users)

- `graph-studio.md` — how to use the browser UI: running assets, reading thread history, configuring workflow phase behavior, and understanding error states.

## API Server (Developers)

- `api-server.md` — setting up and running the FastAPI server locally, environment variables, LLM providers (Ollama, Gemini, Claude), database schema, key endpoints, and troubleshooting.

## Demos

Open the HTML files directly or through the GitHub Pages portal under `docs/index.html`.
''')

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

Preview root context installation:

`./install.sh --provider claude --project --context-only --dry-run`

Install or overwrite root Claude context:

`./install.sh --provider claude --project --context-only --force`

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

During project installs, provider context files are written to the repository root. Provider-specific assets still install under `.claude/`, `.codex/`, or `.gemini/`.

Example dry run:

```text
$ ./install.sh --provider claude --project --context-only --dry-run
Dry run: skipping adapter build and writing no files
Would install CLAUDE.md (root-context)
Would write version metadata to .ai-assets-version
Summary for claude: root context files=1 provider directory files=0 skipped=0 version_metadata=1 target=.claude dry_run=1
```

Example full Claude project install:

```text
$ ./install.sh --provider claude --project --force --skip-build
Installed CLAUDE.md into project root
Installed .claude/agents/go-triage-specialist.md into provider directory
Installed .claude/commands/triage.md into provider directory
Summary for claude: root context files=1 provider directory files=52 skipped=0 version_metadata=1 target=.claude dry_run=0
```

## Provider-Specific Override Example

Put shared rules in the neutral sections of `assets/context/repo-agent-instructions.md`. Put assistant-specific trigger phrases in the matching provider section.

```markdown
### Claude Code

- Treat "agent team" as a Claude-only request to coordinate specialist subagents.

### Codex

- Do not interpret "agent team" as a dispatch command. Ask which repo task should be planned or implemented.
```

Generated result:

```text
dist/claude/CLAUDE.md   includes only the Claude Code override
dist/codex/AGENTS.md    includes only the Codex override
dist/gemini/GEMINI.md   includes only the Gemini override
```

## LangGraph Export Example

```bash
python3 scripts/build_adapters.py
./install.sh --runtime langgraph --project --dry-run
./install.sh --runtime langgraph --project --force
```

The LangGraph export includes graph definitions, command manifests, agent manifests, and pre-dispatch context under `.langgraph/`.

## End-User LangGraph Setup

For a consuming repository, install the provider context first, then add LangGraph runtime exports:

```bash
./install.sh --provider claude --project --context-only --dry-run
./install.sh --provider claude --project --force
./install.sh --runtime langgraph --project --force
```

Use OpenTelemetry as the open-source-first tracing default:

```bash
NUNNERI_RUNTIME=langgraph
NUNNERI_STATE_STORE=sqlite
NUNNERI_TRACE_MODE=otel
```

Use `.nunneri/langgraph/state.sqlite` as the recommended project-local checkpoint path for stateful workflows. Use `NUNNERI_TRACE_MODE=langsmith` plus `LANGSMITH_API_KEY` only when the team chooses LangSmith as an optional hosted tracing UI. Use `NUNNERI_TRACE_MODE=none` for no tracing.

Open `guides/end-user-setup-demo.html` for the interactive setup walkthrough.

## Consumer Repository Example

Use `examples/consumer-repo/` to see the expected install layout for a normal GitHub repository.

```bash
python3 scripts/check_consumer_install.py
```

The check stages a temporary consumer repository and verifies:

- context-only dry run writes nothing
- context-only Claude install writes root `CLAUDE.md` and `.ai-assets-version`
- full Claude install writes root context plus `.claude/` assets
- LangGraph install writes `.langgraph/` graph, agent, and context manifests
- existing root context is skipped unless `--force` is used

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

## Internal Dist Release Branches

Use `main` as the default integration branch and cut `release/vX.Y.Z` branches for internal release stabilization. Do not introduce `develop` or `master` for this repo.

```bash
git checkout main
git pull
git checkout -b release/v0.1.0
```

Before tagging, run the release package checks:

```bash
python3 scripts/package_release.py
python3 scripts/check_release_package.py
```

Tags must match `VERSION` exactly. Tag `v0.1.0` requires `VERSION` to contain `0.1.0`.
""")

    write("guides/runtime-contract-demo.html", r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Nunneri Runtime Contract Demo</title>
<style>
:root{
  --bg:#0b0d10;--panel:#151922;--panel2:#1d2430;--line:#2a3444;--text:#e7edf6;
  --muted:#8a96a8;--accent:#4f8cff;--cyan:#2dd4bf;--green:#22c55e;--yellow:#f59e0b;--red:#ef4444;
  --font:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);font-family:var(--font);line-height:1.45}
a{color:#9cc2ff;text-decoration:none}
a:hover{text-decoration:underline}
.shell{max-width:1180px;margin:0 auto;padding:28px 20px 44px}
.top{display:grid;grid-template-columns:minmax(0,1.25fr) minmax(280px,.75fr);gap:22px;align-items:end;margin-bottom:22px}
.eyebrow{font-size:12px;text-transform:uppercase;letter-spacing:.12em;color:var(--cyan);font-weight:800;margin-bottom:8px}
h1{font-size:36px;line-height:1.05;margin:0 0 12px;letter-spacing:0}
.lead{color:var(--muted);font-size:15px;max-width:760px;margin:0}
.status{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:14px}
.status-row{display:flex;justify-content:space-between;gap:12px;padding:6px 0;border-bottom:1px solid var(--line);font-size:12px}
.status-row:last-child{border-bottom:0}
.status-row span:first-child{color:var(--muted)}
.layout{display:grid;grid-template-columns:260px minmax(0,1fr);gap:18px}
.steps{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:8px;position:sticky;top:16px;align-self:start}
.step{width:100%;display:flex;align-items:center;gap:10px;text-align:left;background:transparent;border:0;color:var(--muted);
  padding:10px;border-radius:6px;cursor:pointer;font:inherit;font-size:13px}
.step:hover{background:var(--panel2);color:var(--text)}
.step.active{background:#20304a;color:var(--text)}
.num{width:24px;height:24px;border-radius:999px;background:var(--panel2);display:grid;place-items:center;color:var(--muted);font-size:11px;font-weight:800}
.step.active .num{background:var(--accent);color:white}
.stage{background:var(--panel);border:1px solid var(--line);border-radius:8px;min-height:620px;overflow:hidden}
.stage-hd{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:14px 16px;border-bottom:1px solid var(--line)}
.stage-hd h2{font-size:18px;margin:0;letter-spacing:0}
.pill{font-size:11px;color:var(--muted);border:1px solid var(--line);border-radius:999px;padding:4px 8px;background:var(--panel2)}
.panel{display:none;padding:18px}
.panel.active{display:block;animation:fade .22s ease-out}
@keyframes fade{from{opacity:.5;transform:translateY(6px)}to{opacity:1;transform:none}}
.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
.card{border:1px solid var(--line);background:var(--panel2);border-radius:8px;padding:14px}
.card h3{font-size:14px;margin:0 0 8px}
.card p{color:var(--muted);font-size:13px;margin:0 0 8px}
.workflow{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin:12px 0}
.phase{border:1px solid var(--line);background:#121722;border-radius:8px;padding:10px;min-height:86px;position:relative;transition:transform .18s,border-color .18s}
.phase:hover{transform:translateY(-2px);border-color:#4f8cff99}
.phase .p{font-size:10px;color:var(--muted);font-weight:800}
.phase .name{font-size:13px;font-weight:800;margin:4px 0}
.phase .meta{font-size:11px;color:var(--muted)}
.phase.gate{border-color:#f59e0b66;background:#211b0c}
.phase.gate:after{content:"Human gate";position:absolute;right:8px;top:8px;font-size:10px;color:var(--yellow)}
.adapter-row{display:grid;grid-template-columns:160px minmax(0,1fr);gap:12px;align-items:center;border-bottom:1px solid var(--line);padding:12px 0}
.adapter-row:last-child{border-bottom:0}
.adapter-name{font-weight:800}
.adapter-desc{color:var(--muted);font-size:13px}
pre{margin:10px 0 0;background:#090b0f;border:1px solid var(--line);border-radius:8px;padding:12px;overflow:auto;color:#c8d5e6;font-size:12px}
code{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
.gate-preview{border:1px solid #f59e0b66;background:#211b0c;border-radius:8px;padding:12px;margin-top:12px}
.gate-preview strong{color:var(--yellow)}
.actions{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}
.actions button{border:1px solid var(--line);background:var(--panel2);color:var(--text);border-radius:6px;padding:7px 10px;cursor:pointer}
.actions button.approve{border-color:#22c55e77;color:var(--green)}
.actions button.reject{border-color:#ef444477;color:var(--red)}
.result{margin-top:10px;color:var(--muted);font-size:13px}
@media (max-width:840px){
  .top,.layout{grid-template-columns:1fr}
  .steps{position:relative;top:auto;display:grid;grid-template-columns:repeat(2,minmax(0,1fr))}
  .grid,.workflow{grid-template-columns:1fr}
}
</style>
</head>
<body>
<main class="shell">
  <section class="top">
    <div>
      <div class="eyebrow">Neutral runtime setup</div>
      <h1>Nunneri Runtime Contract to stateful agent workflows</h1>
      <p class="lead">
        This interactive guide shows how one provider-neutral contract becomes LangGraph, CrewAI,
        AutoGen, and Semantic Kernel exports while preserving human approval gates and project context.
      </p>
    </div>
    <aside class="status" aria-label="Contract summary">
      <div class="status-row"><span>Contract</span><strong>triage-nine-phase</strong></div>
      <div class="status-row"><span>Phases</span><strong>9</strong></div>
      <div class="status-row"><span>Human gates</span><strong>gate_1, gate_2</strong></div>
      <div class="status-row"><span>Validators</span><strong>contract + Studio + examples</strong></div>
    </aside>
  </section>

  <section class="layout">
    <nav class="steps" aria-label="Demo steps">
      <button class="step active" data-step="1"><span class="num">1</span>Select provider context</button>
      <button class="step" data-step="2"><span class="num">2</span>Load neutral contract</button>
      <button class="step" data-step="3"><span class="num">3</span>Inspect workflow phases</button>
      <button class="step" data-step="4"><span class="num">4</span>Review human gates</button>
      <button class="step" data-step="5"><span class="num">5</span>Project to runtimes</button>
      <button class="step" data-step="6"><span class="num">6</span>Validate setup</button>
    </nav>

    <section class="stage">
      <div class="stage-hd">
        <h2 id="stage-title">Select provider context</h2>
        <span class="pill" id="stage-pill">Provider-neutral assets</span>
      </div>

      <article class="panel active" data-panel="1">
        <div class="grid">
          <div class="card">
            <h3>Install repo instructions</h3>
            <p>Provider files stay at the consuming repository root while assets remain under provider folders.</p>
            <pre><code>./install.sh --provider claude --project --context-only --dry-run
./install.sh --provider codex --project --context-only --dry-run
./install.sh --provider gemini --project --context-only --dry-run</code></pre>
          </div>
          <div class="card">
            <h3>Provider-specific overrides</h3>
            <p>Claude, Codex, and Gemini can each receive native guidance without changing the neutral workflow contract.</p>
            <pre><code>assets/context/repo-agent-instructions.md
dist/claude/CLAUDE.md
dist/codex/AGENTS.md
dist/gemini/GEMINI.md</code></pre>
          </div>
        </div>
      </article>

      <article class="panel" data-panel="2">
        <div class="card">
          <h3>Neutral contract is the shared export layer</h3>
          <p>Runtime adapters consume <code>dist/nunneri-runtime/</code> instead of reading provider-specific files.</p>
          <pre><code>python3 scripts/build_adapters.py
cat dist/nunneri-runtime/workflows/triage-nine-phase.json
cat dist/nunneri-runtime/context/repo-agent-instructions.json</code></pre>
        </div>
      </article>

      <article class="panel" data-panel="3">
        <div class="workflow" aria-label="Nine phase workflow">
          <div class="phase"><div class="p">P1</div><div class="name">Intake</div><div class="meta">Problem and scope</div></div>
          <div class="phase"><div class="p">P2</div><div class="name">Context Load</div><div class="meta">Repo context</div></div>
          <div class="phase"><div class="p">P3</div><div class="name">Classification</div><div class="meta">Code, config, runtime, docs</div></div>
          <div class="phase"><div class="p">P4</div><div class="name">Evidence Collection</div><div class="meta">Commands and failures</div></div>
          <div class="phase"><div class="p">P5</div><div class="name">Root Cause Analysis</div><div class="meta">Cause and plan</div></div>
          <div class="phase gate"><div class="p">P6</div><div class="name">gate_1</div><div class="meta">Approve RCA and fix plan</div></div>
          <div class="phase"><div class="p">P7</div><div class="name">Test-First Fix</div><div class="meta">Checks before change</div></div>
          <div class="phase"><div class="p">P8</div><div class="name">Validation</div><div class="meta">Run checks</div></div>
          <div class="phase gate"><div class="p">P9</div><div class="name">gate_2</div><div class="meta">Approve release impact</div></div>
        </div>
      </article>

      <article class="panel" data-panel="4">
        <div class="gate-preview">
          <strong>gate_1</strong>
          <p>Approve the root cause analysis and fix plan before implementation?</p>
          <div class="actions">
            <button class="approve" data-action="approve">Approve</button>
            <button class="reject" data-action="reject">Reject</button>
          </div>
          <div class="result" id="gate-result">A LangGraph runtime pauses here with interrupt/resume. Rejection cancels downstream work.</div>
        </div>
        <pre><code>{
  "id": "gate_1",
  "type": "human_approval",
  "approval": {
    "actions": ["approve", "reject"],
    "on_reject": "cancel"
  }
}</code></pre>
      </article>

      <article class="panel" data-panel="5">
        <div class="adapter-row"><div class="adapter-name">LangGraph</div><div class="adapter-desc">Graph JSON with checkpointed interrupts and approval gates.</div></div>
        <div class="adapter-row"><div class="adapter-name">CrewAI</div><div class="adapter-desc">Agent and flow manifests derived from the same contract.</div></div>
        <div class="adapter-row"><div class="adapter-name">AutoGen</div><div class="adapter-desc">AgentChat/Core style specs for orchestration experiments.</div></div>
        <div class="adapter-row"><div class="adapter-name">Semantic Kernel</div><div class="adapter-desc">Agent and orchestration manifests with approval metadata.</div></div>
        <pre><code>./install.sh --runtime nunneri-runtime --project --dry-run --skip-build
./install.sh --runtime langgraph --project --dry-run --skip-build
./install.sh --runtime crewai --project --dry-run --skip-build</code></pre>
      </article>

      <article class="panel" data-panel="6">
        <div class="grid">
          <div class="card">
            <h3>Contract and Studio checks</h3>
            <pre><code>python3 scripts/check_runtime_contract.py
python3 scripts/check_graph_studio_contract.py
python3 scripts/check_langgraph_exports.py</code></pre>
          </div>
          <div class="card">
            <h3>Consumer example checks</h3>
            <pre><code>python3 scripts/check_runtime_examples.py
python3 examples/runtime-contract-consumer/consume_runtime_contract.py \
  --workflow dist/nunneri-runtime/workflows/triage-nine-phase.json</code></pre>
          </div>
        </div>
      </article>
    </section>
  </section>
</main>
<script>
const titles = {
  1:["Select provider context","Provider-neutral assets"],
  2:["Load neutral contract","dist/nunneri-runtime"],
  3:["Inspect workflow phases","9 phase triage"],
  4:["Review human gates","gate_1 and gate_2"],
  5:["Project to runtimes","Adapters, not providers"],
  6:["Validate setup","Release-ready checks"]
};
document.querySelectorAll("[data-step]").forEach(button => {
  button.addEventListener("click", () => {
    const step = button.dataset.step;
    document.querySelectorAll("[data-step]").forEach(el => el.classList.toggle("active", el === button));
    document.querySelectorAll("[data-panel]").forEach(el => el.classList.toggle("active", el.dataset.panel === step));
    document.getElementById("stage-title").textContent = titles[step][0];
    document.getElementById("stage-pill").textContent = titles[step][1];
  });
});
document.querySelectorAll("[data-action]").forEach(button => {
  button.addEventListener("click", () => {
    const result = document.getElementById("gate-result");
    if (button.dataset.action === "approve") {
      result.textContent = "Approved: the runtime resumes with Command(resume={approved: true}) and continues to Test-First Fix.";
      result.style.color = "var(--green)";
    } else {
      result.textContent = "Rejected: the runtime resumes with approved: false and cancels downstream implementation nodes.";
      result.style.color = "var(--red)";
    }
  });
});
</script>
</body>
</html>
''')

    write("guides/graph-studio.md", r'''# Graph Studio

Graph Studio is the browser-based UI for running Nunneri assets, inspecting execution state in real time,
and reviewing run history. It is served by the Nunneri API server at `/ui`.

## Prerequisites

| Requirement | Default |
|---|---|
| API server running | `http://localhost:8000` |
| Ollama running | `http://localhost:11434` |
| At least one Ollama model pulled | `ollama pull mistral` |
| PostgreSQL | `postgresql://nunneri:nunneri@localhost:5432/nunneri` |

See [api-server.md](api-server.md) for setup instructions.

---

## Opening the Studio

Navigate to `http://localhost:8000/ui`.

The header shows:
- **Ollama ✓ · N models** — Ollama is reachable and the model count is shown. Red means Ollama is offline.
- **Queue badge** — appears yellow when Ollama slots are busy, red when requests are waiting.

## Resizing the Workspace

Graph Studio panes are resizable:

| Area | Drag target |
|---|---|
| Left navigation | Border between the navigation pane and graph canvas |
| Right inspector / phase config | Border between the graph canvas and inspector pane |
| Bottom output | Border above the output transcript |

Pane sizes are saved in browser local storage so the workspace reopens with the same proportions.

---

## Selecting an Asset

The left panel lists all available agents and commands loaded from `dist/langgraph/manifests/`.

- **Agents** run multi-phase agentic workflows (intake → analysis → gate → output).
- **Commands** run targeted single-purpose workflows (dispatch → execute → summarize).
- **Workflow phases** are the user-facing steps shown on the graph canvas.
- **Nodes** are the technical IDs used by the JSON contract, API, and runtime adapters.

Click any item to select it. The graph canvas updates from the runtime contract projection exposed by `/agents/{name}/graph-definition`, including phase metadata, edge conditions, and approval-gate context.

---

## Running an Asset

1. Select an agent or command from the left panel.
2. (Optional) Enter a local path or git URL in the **Project Path** field. The server will inject the
   repository structure and key files as context for the LLM.
3. Type your message in the input field and press **Enter** or click **▶ Run**.

The graph canvas activates and workflow phases light up as execution progresses:

| Colour | Meaning |
|---|---|
| Blue pulse | Phase is active (LLM call in progress) |
| Green | Phase completed |
| Diamond / teal | Approval gate passed |
| Red | Phase errored |

The **Transcript** panel below the canvas shows token-by-token output as each node produces it.

### Queue position

If Ollama is busy, a **Queued** banner appears in the transcript showing your position and estimated wait.

### Routing rules

If a routing rule matched on a phase, a `⤳ Rule match: from → to` line appears and the target phase briefly flashes cyan. Static edge conditions such as `approved` are shown directly on the graph.

### Context trimming

If older messages were dropped to fit within the model's context window, a yellow warning appears in the transcript.

---

## Thread History

Every run is attached to a **thread** — a persistent conversation context. The left panel's
**Threads** tab lists all threads, most recent first.

Click a thread to:
- Restore the graph view with node completion states from the last run.
- Show the run output and error details in the transcript.
- See the full run ID and model in the transcript header (click either to copy to clipboard).

Thread IDs are shown in full and are click-to-copy for debugging and support.

### Run status indicators

| Indicator | Meaning |
|---|---|
| `✓ Run complete` | The run finished successfully. |
| `Waiting for approval` | The graph is paused at a human approval gate and is waiting for Approve or Reject. |
| `✕ Run rejected` | A human rejected a gate; downstream execution was cancelled. |
| `✕ Run failed` + error detail | The run errored. The exact exception is shown in red. |
| `⚠ Run appears stuck` | Status is still "running" but started more than 2 minutes ago — the server or browser disconnected mid-run. |

Stuck runs are automatically closed with `status=error` on the next server restart if they are older than 1 hour. You can also open the thread and click **Cancel run** to mark a stale running run as `cancelled` immediately.

If the run is complete but the header still shows an active Ollama slot, click **Reset** in the queue badge. This resets only the in-memory queue counter; it does not change persisted runs or checkpoints.

### Approval gates

Human approval phases are real LangGraph interrupts, not visual markers. When a run reaches a gate, Graph Studio shows an approval card in the transcript and keeps downstream phases pending.

Available actions:

| Action | Result |
|---|---|
| Approve and resume | Calls `POST /threads/{thread_id}/gates/{gate_id}/approve`, then streams the resumed run from the same checkpoint. |
| Reject and stop | Calls `POST /threads/{thread_id}/gates/{gate_id}/reject`, marks the gate rejected, and prevents downstream work. |

The legacy trace fallback is simulated only. It can show where a gate would occur, but it cannot approve or resume because no durable checkpoint exists for that path.

---

## Phase Configuration

Click any workflow phase in the graph to open the **Phase Config** tab on the right panel.

The top of the panel shows contract defaults generated from `dist/nunneri-runtime/`, including phase descriptions, expected outputs, classification options, approval questions, required approval context, and outgoing routes. The editable fields below are project-specific overrides.

| Field | Purpose |
|---|---|
| Instructions Override | Override the contract/default instructions for this phase only. |
| Classification Labels | Comma-separated labels; the LLM is instructed to classify output into one of these. |
| Routing Overrides | Conditions that determine which node the graph routes to after this phase exits. |
| Notes | Free-text notes for your team. |

### Routing rules

Each rule has a condition, a match value, and a target node ID:

| Condition | Matches when |
|---|---|
| `contains` | Output contains the value (case-insensitive). |
| `starts_with` | Output starts with the value. |
| `ends_with` | Output ends with the value. |
| `regex` | Output matches the regular expression. |
| `always` | Always routes to this target (use as a default/fallback). |

Rules are evaluated in priority order (lowest number first). The first match wins.
Click **Save** to persist. Phase configs are stored in PostgreSQL and applied to every run of that agent.

---

## Stopping a Run

Click **■ Stop** to abort the current browser stream. If Graph Studio has received the run id, it also calls `POST /runs/{run_id}/cancel` so the database no longer shows the run as active.

For an already-stuck historical run:

1. Open the thread.
2. Click **Cancel run**.
3. Click **Rerun as new thread** to retry the same agent, model, project path, and message without reusing the stuck checkpoint.

Runs that do not complete within **10 minutes** are aborted automatically and a timeout message appears in the transcript.

---

## State Inspector

The right panel **State** tab shows:

| Field | Value |
|---|---|
| Thread | Current thread UUID (click to copy) |
| Phase | Last node that ran |
| Output | Tail of the last node's output |
| Checkpoints | Phase breadcrumb trail for the current run |

---

## Errors and Debugging

If a run errors, the transcript shows a red block with the exception class and message, for example:

```
✕ Error
TimeoutError: Ollama queue timeout after 300s (0 still waiting, 2 active)
```

The same detail is stored on the run record in PostgreSQL and is shown when you reload the thread
from history. To query it directly:

```sql
SELECT id, agent, status, error_detail, started_at
FROM nunneri_runs
WHERE status = 'error'
ORDER BY started_at DESC
LIMIT 10;
```

Common errors:

| Error | Likely cause |
|---|---|
| `TimeoutError: Ollama queue timeout` | Too many concurrent runs; increase `OLLAMA_MAX_CONCURRENT` or wait. |
| `ConnectionRefusedError` connecting to Ollama | Ollama is not running. Start it with `ollama serve`. |
| `model not found` from Ollama | The selected model has not been pulled. Run `ollama pull <model>`. |
| `asyncio.CancelledError` | The browser disconnected mid-run. The run will be marked error on the next server start. |
''')


def create_examples() -> None:
    write("examples/consumer-repo/README.md", f"""# Consumer Repository Example

This fixture shows how a normal GitHub repository can consume {PLATFORM} without becoming tied to one AI provider.

## What This Example Proves

- Provider context files install at the consumer repository root.
- Provider assets install under provider directories such as `.claude/`, `.codex/`, and `.gemini/`.
- LangGraph runtime exports install under `.langgraph/`.
- Dry runs show planned writes without modifying the consumer repository.
- Existing root context files are skipped unless `--force` is used.

## Preview a Context-Only Install

```bash
./install.sh --provider claude --project --context-only --dry-run
```

Expected output includes:

```text
Would install CLAUDE.md (root-context)
Would write version metadata to .ai-assets-version
```

## Install Claude Context Only

```bash
./install.sh --provider claude --project --context-only --force --skip-build
```

Expected consumer files:

```text
CLAUDE.md
.ai-assets-version
```

## Install Full Claude Assets

```bash
./install.sh --provider claude --project --force --skip-build
```

Expected consumer files:

```text
CLAUDE.md
.claude/.ai-assets-version
.claude/agents/python-triage-specialist.md
.claude/commands/triage.md
```

## Install Codex or Gemini

```bash
./install.sh --provider codex --project --force --skip-build
./install.sh --provider gemini --project --force --skip-build
```

Expected root context files:

```text
AGENTS.md
GEMINI.md
```

## Install LangGraph Runtime Exports

```bash
./install.sh --runtime langgraph --project --force --skip-build
```

Expected consumer files:

```text
.langgraph/.ai-assets-version
.langgraph/context/repo-agent-instructions.json
.langgraph/graphs/triage-nine-phase.json
.langgraph/manifests/agents/python-triage-specialist.json
```

## Automated Verification

Run the smoke check from the asset repository root:

```bash
python3 scripts/check_consumer_install.py
```

The check stages a temporary consumer repository, runs the installer in dry-run, context-only, full provider, LangGraph, and existing-file scenarios, and verifies the expected files.
""")
    write("examples/runtime-contract-consumer/README.md", r'''# Runtime Contract Consumer Example

This example shows how a consuming tool can read the neutral Nunneri Runtime Contract without depending on LangGraph, CrewAI, AutoGen, Semantic Kernel, or any model-provider SDK.

## What This Example Proves

- `dist/nunneri-runtime/contract.json` is usable as the runtime export index.
- Workflow contracts can be loaded directly from `dist/nunneri-runtime/workflows/`.
- Human approval nodes are visible through the neutral `human_approval` node type.
- A framework adapter can map the neutral workflow into a CrewAI-style flow shape without reading provider-specific files.

## Run

```bash
python3 examples/runtime-contract-consumer/consume_runtime_contract.py
```

The script prints JSON with:

- the neutral contract version
- the selected workflow name
- total node and edge counts
- approval gate IDs
- a dependency-free CrewAI-style flow projection

## Expected Signals

For `triage-nine-phase`, the output should report:

```text
workflow_name: triage-nine-phase
node_count: 9
approval_gates: gate_1, gate_2
crewai_flow.human_in_loop: gate_1, gate_2
```

## Automated Verification

Run from the repository root:

```bash
python3 scripts/check_runtime_examples.py
```

The check runs this example and verifies that it preserves the neutral contract's human approval semantics.
''')
    write("examples/runtime-contract-consumer/consume_runtime_contract.py", r'''#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def crewai_flow_from_workflow(workflow: dict) -> dict:
    approval_nodes = [node["id"] for node in workflow["nodes"] if node.get("type") == "human_approval"]
    return {
        "name": workflow["name"],
        "description": workflow["description"],
        "steps": [
            {
                "id": node["id"],
                "label": node.get("label", node["id"]),
                "kind": "human_input" if node.get("type") == "human_approval" else "task",
                "approval": node.get("approval"),
            }
            for node in workflow["nodes"]
        ],
        "edges": workflow["edges"],
        "human_in_loop": approval_nodes,
    }


def summarize_contract(repo_root: Path, workflow_name: str) -> dict:
    contract_root = repo_root / "dist/nunneri-runtime"
    index = load_json(contract_root / "contract.json")
    workflow = load_json(contract_root / "workflows" / f"{workflow_name}.json")
    approval_gates = [node["id"] for node in workflow["nodes"] if node.get("type") == "human_approval"]
    return {
        "contract_version": index["contract_version"],
        "workflow_name": workflow["name"],
        "workflow_source": workflow["source"],
        "node_count": len(workflow["nodes"]),
        "edge_count": len(workflow["edges"]),
        "approval_gates": approval_gates,
        "runtime_hints": workflow.get("runtime_hints", {}),
        "crewai_flow": crewai_flow_from_workflow(workflow),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Read a Nunneri neutral runtime contract and project it into a CrewAI-style flow.")
    parser.add_argument("--repo-root", default=Path(__file__).resolve().parents[2], type=Path)
    parser.add_argument("--workflow", default="triage-nine-phase")
    args = parser.parse_args()
    payload = summarize_contract(args.repo_root.resolve(), args.workflow)
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
''', True)

    write("examples/consumer-repo/expected/README.md", """# Expected Install Artifacts

These files document the key artifacts a consumer repository should see after installing Nunneri AI Assets.

The full generated provider and runtime payload is intentionally not duplicated here. The authoritative outputs are generated under `dist/` and verified by `scripts/check_consumer_install.py`.

## Context-Only Claude Install

```text
CLAUDE.md
.ai-assets-version
```

## Full Claude Install

```text
CLAUDE.md
.claude/.ai-assets-version
.claude/agents/python-triage-specialist.md
.claude/commands/triage.md
```

## Codex and Gemini Context Files

```text
AGENTS.md
GEMINI.md
```

## LangGraph Runtime Install

```text
.langgraph/.ai-assets-version
.langgraph/context/repo-agent-instructions.json
.langgraph/graphs/triage-nine-phase.json
.langgraph/manifests/agents/python-triage-specialist.json
```
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
  - type: checkboxes
    id: license_impact
    attributes:
      label: License, commercial, or trademark impact
      options:
        - label: This request may affect license, commercial-use, ownership, trademark, brand, or homepage language.
        - label: This request does not affect license, commercial-use, ownership, trademark, brand, or homepage language.
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

    write("examples/crewai-runtime-runner/README.md", r'''# CrewAI Runtime Runner Example

This example is the first runnable CrewAI-facing adapter harness for the Nunneri Runtime Contract.

It reads generated files from:

```text
dist/nunneri-runtime/workflows/triage-nine-phase.json
dist/crewai/flows/triage-nine-phase.json
```

Then it executes the flow shape deterministically without installing the CrewAI SDK. This keeps the repository dependency-free while proving that the CrewAI export preserves:

- ordered workflow steps
- `human_input` approval gates
- approve/reject actions
- cancellation on rejection
- no downstream implementation work after rejection

Run an all-approved flow:

```bash
python3 examples/crewai-runtime-runner/run_crewai_contract.py --auto-approve
```

Run a rejection path:

```bash
python3 examples/crewai-runtime-runner/run_crewai_contract.py --reject-gate gate_1
```

This is not a CrewAI SDK application yet. It is the contract runner that a later SDK-backed implementation should match.
''')

    write("examples/crewai-runtime-runner/run_crewai_contract.py", r'''#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def index_by_id(items: list[dict]) -> dict[str, dict]:
    return {item["id"]: item for item in items}


def run_contract(repo_root: Path, workflow_name: str, auto_approve: bool, reject_gate: str | None) -> dict:
    neutral = load_json(repo_root / "dist/nunneri-runtime/workflows" / f"{workflow_name}.json")
    crewai = load_json(repo_root / "dist/crewai/flows" / f"{workflow_name}.json")
    flow = crewai["flow"]
    steps = flow["steps"]
    neutral_nodes = index_by_id(neutral["nodes"])

    completed: list[str] = []
    gate_decisions: dict[str, dict] = {}
    status = "completed"
    cancelled_at = None

    for step in steps:
        step_id = step["id"]
        node = neutral_nodes.get(step_id, {})
        if step.get("kind") == "human_input" or node.get("type") == "human_approval":
            if reject_gate == step_id:
                gate_decisions[step_id] = {"approved": False, "action": "reject", "on_reject": "cancel"}
                status = "cancelled"
                cancelled_at = step_id
                break
            if not auto_approve:
                gate_decisions[step_id] = {"approved": None, "action": "waiting"}
                status = "waiting_approval"
                cancelled_at = step_id
                break
            gate_decisions[step_id] = {"approved": True, "action": "approve"}
        completed.append(step_id)

    return {
        "runtime": "crewai",
        "mode": "contract_runner",
        "workflow_name": neutral["name"],
        "contract_source": crewai["contract_source"],
        "status": status,
        "completed_steps": completed,
        "cancelled_at": cancelled_at,
        "gate_decisions": gate_decisions,
        "human_in_loop": flow.get("human_in_loop", []),
        "step_count": len(steps),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a generated CrewAI flow manifest from the Nunneri neutral runtime contract.")
    parser.add_argument("--repo-root", default=Path(__file__).resolve().parents[2], type=Path)
    parser.add_argument("--workflow", default="triage-nine-phase")
    parser.add_argument("--auto-approve", action="store_true", help="Approve all human_input gates and complete the flow.")
    parser.add_argument("--reject-gate", help="Reject a specific gate id and cancel downstream execution.")
    args = parser.parse_args()

    payload = run_contract(args.repo_root.resolve(), args.workflow, args.auto_approve, args.reject_gate)
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
''', True)


def create_github() -> None:
    write(".github/workflows/README.md", """# .github/workflows

This directory is part of the Nunneri AI Assets repository.

## Workflows

- `validate.yml` runs on `main`, `release/**`, and PRs into those branches.
- `release.yml` publishes internal GitHub prereleases for `vX.Y.Z` tags or approved manual dispatch runs.

Release tags must match `VERSION` and tag commits must be contained in the corresponding `release/vX.Y.Z` branch.
""")

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
    url: https://github.com/suranku/nunneri-public-agentic-ai/discussions
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

## License and Trademark Impact

- [ ] No license, commercial-use, ownership, or trademark impact
- [ ] Changes licensing or commercial-use language
- [ ] Changes trademark, brand, logo, or ownership language
- [ ] Changes homepage, release, or generated-reference docs that mention license/commercial terms

## Contributor License Agreement

- [ ] I agree that my contribution is submitted under the Nunneri Contributor License Agreement.

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
    write(".github/workflows/validate.yml", r'''name: Validate

on:
  push:
    branches:
      - main
      - "release/**"
  pull_request:
    branches:
      - main
      - "release/**"

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
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
      - name: Check context exports
        run: python3 scripts/check_context_exports.py
      - name: Check runtime contract
        run: python3 scripts/check_runtime_contract.py
      - name: Check LangGraph exports
        run: python3 scripts/check_langgraph_exports.py
      - name: Check runtime examples
        run: python3 scripts/check_runtime_examples.py
      - name: Check CrewAI runtime runner
        run: python3 scripts/check_crewai_runtime_runner.py
      - name: Check runtime contract demo
        run: python3 scripts/check_runtime_contract_demo.py
      - name: Check Graph Studio contract wiring
        run: python3 scripts/check_graph_studio_contract.py
      - name: Check graph-definition API contract
        run: python3 scripts/check_graph_definition_api.py
      - name: Check human-blocking gates
        run: python3 scripts/check_human_gates.py
      - name: Check consumer install
        run: python3 scripts/check_consumer_install.py
      - name: Check end-user setup docs
        run: python3 scripts/check_user_setup_docs.py
      - name: Check release readiness
        run: python3 scripts/check_release_ready.py --local-only
      - name: Validate shell scripts
        run: |
          bash -n install.sh
          bash -n uninstall.sh
      - name: Ensure generated files are committed
        run: git diff --exit-code
''')
    write(".github/workflows/release.yml", """name: Internal Dist Release

on:
  workflow_dispatch:
    inputs:
      version:
        description: "Release version without leading v, for example 0.1.0"
        required: true
        type: string
  push:
    tags:
      - "v*.*.*"

permissions:
  contents: write

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Resolve release version
        id: version
        shell: bash
        run: |
          set -euo pipefail
          version_file="$(cat VERSION)"
          if [ "${GITHUB_EVENT_NAME}" = "workflow_dispatch" ]; then
            requested="${{ inputs.version }}"
            if [[ ! "$requested" =~ ^[0-9]+\\.[0-9]+\\.[0-9]+$ ]]; then
              echo "Manual release version must look like X.Y.Z"
              exit 1
            fi
            if [ "$requested" != "$version_file" ]; then
              echo "Manual release version $requested must match VERSION $version_file"
              exit 1
            fi
            tag="v$requested"
          else
            tag="${GITHUB_REF_NAME}"
            if [[ ! "$tag" =~ ^v[0-9]+\\.[0-9]+\\.[0-9]+$ ]]; then
              echo "Tag $tag must look like vX.Y.Z"
              exit 1
            fi
            requested="${tag#v}"
            if [ "$requested" != "$version_file" ]; then
              echo "Tag version $requested must match VERSION $version_file"
              exit 1
            fi
            release_branch="origin/release/$tag"
            git fetch origin "+refs/heads/release/$tag:refs/remotes/origin/release/$tag" || true
            if ! git branch -r --contains "$GITHUB_SHA" | grep -qx "  $release_branch"; then
              echo "Tag $tag must point to a commit contained in release/$tag"
              exit 1
            fi
          fi
          echo "version=$requested" >> "$GITHUB_OUTPUT"
          echo "tag=$tag" >> "$GITHUB_OUTPUT"

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
      - name: Check context exports
        run: python3 scripts/check_context_exports.py
      - name: Check LangGraph exports
        run: python3 scripts/check_langgraph_exports.py
      - name: Check consumer install
        run: python3 scripts/check_consumer_install.py
      - name: Check end-user setup docs
        run: python3 scripts/check_user_setup_docs.py
      - name: Check release readiness
        run: python3 scripts/check_release_ready.py --local-only
      - name: Validate shell scripts
        run: |
          bash -n install.sh
          bash -n uninstall.sh
      - name: Package release
        run: python3 scripts/package_release.py --version "${{ steps.version.outputs.version }}"
      - name: Check release package
        run: python3 scripts/check_release_package.py
      - name: Ensure generated files are committed before package output
        run: git diff --exit-code -- . ":(exclude)dist/releases"

      - name: Publish prerelease
        uses: softprops/action-gh-release@v2
        with:
          tag_name: ${{ steps.version.outputs.tag }}
          name: Nunneri AI Assets ${{ steps.version.outputs.tag }}
          prerelease: true
          generate_release_notes: true
          files: |
            dist/releases/nunneri-ai-assets-${{ steps.version.outputs.version }}.zip
            dist/releases/nunneri-ai-assets-${{ steps.version.outputs.version }}.tar.gz
            dist/releases/nunneri-ai-assets-${{ steps.version.outputs.version }}.sha256
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
    context_reference = reference / "context"
    examples_reference = reference / "examples"
    reference.mkdir(parents=True, exist_ok=True)
    guide_reference.mkdir(parents=True, exist_ok=True)
    context_reference.mkdir(parents=True, exist_ok=True)
    examples_reference.mkdir(parents=True, exist_ok=True)
    for name in ("README.md", "AI_ASSETS.md", "CONTRIBUTING.md", "RELEASE.md", "CHANGELOG.md", "VERSION"):
        shutil.copyfile(ROOT / name, reference / name)
    shutil.copyfile(ROOT / "LANGGRAPH_RUNTIME.md", reference / "langgraph-runtime.md")
    for src in sorted((ROOT / "assets/context").glob("*.md")):
        shutil.copyfile(src, context_reference / src.name)
    for src in sorted((ROOT / "guides").glob("*.md")):
        shutil.copyfile(src, guide_reference / src.name)
    for src in sorted((ROOT / "guides").glob("*.html")):
        dest = guide_reference / src.name
        shutil.copyfile(src, dest)
        text = dest.read_text(encoding="utf-8")
        text = text.replace("../docs/index.html", "../../index.html")
        dest.write_text(text, encoding="utf-8")
    for src in sorted((ROOT / "examples").glob("**/*.md")):
        dest = examples_reference / src.relative_to(ROOT / "examples")
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest)


def main() -> None:
    create_assets()
    create_scripts()
    create_installers()
    create_docs()
    create_guides()
    create_examples()
    create_github()
    sync_reference_docs()


if __name__ == "__main__":
    main()
