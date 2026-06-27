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
REPO_URL = "github.com/Yamini-Suranku/nunneri-public-ai-assets"
TEAM = "Nunneri Platform"
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
runtimes:
  langgraph:
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
  langgraph:
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
  langgraph:
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
  langgraph:
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
    body {{ margin:0; font-family:Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background:var(--bg); color:var(--text); }}
    nav {{ position:sticky; top:0; z-index:5; display:flex; gap:16px; align-items:center; padding:14px 24px; background:rgba(16,17,20,.94); border-bottom:1px solid var(--border); backdrop-filter:blur(12px); overflow:auto; }}
    nav a {{ color:var(--text); text-decoration:none; font-size:14px; white-space:nowrap; }}
    main {{ max-width:1180px; margin:0 auto; padding:44px 20px; }}
    section {{ padding:34px 0; }}
    h1 {{ font-size:clamp(36px, 6vw, 72px); line-height:1; margin:0 0 16px; letter-spacing:0; max-width:900px; }}
    h2 {{ font-size:28px; margin:0 0 16px; }}
    h3 {{ margin:0 0 10px; }}
    p {{ color:var(--muted); line-height:1.7; }}
    .hero {{ min-height:64vh; display:grid; align-content:center; gap:22px; }}
    .stats, .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:14px; }}
    .card, details {{ border:1px solid var(--border); background:var(--surface); border-radius:8px; padding:18px; box-shadow:0 18px 55px rgba(0,0,0,.22); }}
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
    .metric {{ border:1px solid var(--border); border-radius:8px; padding:12px; background:var(--surface2); }}
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
      main {{ padding:30px 16px; }}
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
    <a href="#hero">Home</a><a href="#problem">Problem</a><a href="#quick-start">Quick Start</a><a href="#examples">Examples</a><a href="#providers">Providers</a>
    <a href="#commands">Commands</a><a href="#agents">Agents</a><a href="#skills">Skills</a><a href="#context">Context</a><a href="#guides">Guides</a><a href="#reference">Reference</a>
  </nav>
  <main>
    <section id="hero" class="hero">
      <span class="badge">Claude | Codex | Gemini | open-source | LangGraph runtime</span>
      <h1>{PLATFORM}</h1>
      <p>Provider-agnostic AI agents, skills, commands, workflows, repository context, guides, and adapters for {TEAM}.</p>
      <div id="stats" class="grid"></div>
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
cd nunneri-public-ai-assets
python3 scripts/build_adapters.py
./install.sh --provider all --project --force</code></pre>
    </section>
    <section id="examples">
      <h2>Examples</h2>
      <div class="grid">
        <div class="card" data-reveal><h3>Preview Context</h3><pre><code>./install.sh --provider claude --project --context-only --dry-run</code></pre></div>
        <div class="card" data-reveal><h3>Install Claude Context</h3><pre><code>./install.sh --provider claude --project --context-only --force</code></pre></div>
        <div class="card" data-reveal><h3>Run Triage</h3><pre><code>/triage NUN-1024 "Checkout API returns 500 after deploy" --provider claude</code></pre></div>
        <div class="card" data-reveal><h3>Export LangGraph</h3><pre><code>./install.sh --runtime langgraph --project --force</code></pre></div>
        <div class="card" data-reveal><h3>Verify Consumer Install</h3><pre><code>python3 scripts/check_consumer_install.py</code></pre></div>
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
        <div class="card"><h3>Templates and References</h3><p><a href="reference/AI_ASSETS.md">AI_ASSETS.md</a></p><p><a href="reference/context/repo-agent-instructions.md">Repo Agent Instructions</a></p><p><a href="reference/examples/consumer-repo/README.md">Consumer Repo Example</a></p><p><a href="reference/CONTRIBUTING.md">CONTRIBUTING.md</a></p><p><a href="reference/RELEASE.md">RELEASE.md</a></p><p><a href="reference/langgraph-runtime.md">LangGraph Runtime</a></p></div>
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
RUNTIMES = ("langgraph",)
PROVIDER_OVERRIDE_HEADINGS = {
    "claude": "### Claude Code",
    "codex": "### Codex",
    "gemini": "### Gemini",
}

TRIAGE_NINE_PHASE_GRAPH = {
    "name": "triage-nine-phase",
    "description": "Nine Phase Triage Workflow",
    "runtime": "langgraph",
    "source": "assets/workflows/triage-nine-phase.md",
    "nodes": [
        {"id": "intake", "label": "Intake", "phase": 1, "type": "work"},
        {"id": "context_load", "label": "Context Load", "phase": 2, "type": "work"},
        {"id": "classification", "label": "Classification", "phase": 3, "type": "work"},
        {"id": "evidence_collection", "label": "Evidence Collection", "phase": 4, "type": "work"},
        {"id": "root_cause_analysis", "label": "Root Cause Analysis", "phase": 5, "type": "work"},
        {"id": "gate_1", "label": "Gate 1: RCA and Fix Plan Approval", "phase": 6, "type": "human_approval", "approval_checkpoint": True},
        {"id": "test_first_fix", "label": "Test-First Fix", "phase": 7, "type": "work"},
        {"id": "validation", "label": "Validation", "phase": 8, "type": "work"},
        {"id": "gate_2", "label": "Gate 2: Summary and Release Impact", "phase": 9, "type": "human_approval", "approval_checkpoint": True},
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
}


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
    payload = {
        "name": data["name"],
        "description": data["description"],
        "category": data.get("category", "context"),
        "source": str(src.relative_to(ROOT)),
        "body": body,
        "structured_overrides": structured_override_block(body),
    }
    write(ROOT / "dist/open-source/manifests/context/repo-agent-instructions.json", json.dumps(payload, indent=2))
    write(ROOT / "dist/langgraph/context/repo-agent-instructions.json", json.dumps({**payload, "runtime": "langgraph", "injection_stage": "pre_dispatch"}, indent=2))


def reset_dist() -> None:
    for target_name in PROVIDERS + RUNTIMES:
        target = ROOT / "dist" / target_name
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


def build_langgraph_agent(src: Path, data: dict[str, str], body: str) -> None:
    payload = {
        "name": data["name"],
        "description": data["description"],
        "category": data.get("category"),
        "runtime": "langgraph",
        "source": str(src.relative_to(ROOT)),
        "node": {
            "id": data["name"].replace("-", "_"),
            "type": "agent",
            "body": body,
        },
    }
    write(ROOT / "dist/langgraph/manifests/agents" / f"{data['name']}.json", json.dumps(payload, indent=2))


def build_langgraph_command(src: Path, data: dict[str, str], body: str) -> None:
    payload = {
        "name": data["name"],
        "description": data["description"],
        "category": data.get("category", "command"),
        "runtime": "langgraph",
        "source": str(src.relative_to(ROOT)),
        "entrypoint": {
            "id": data["name"].replace("-", "_"),
            "type": "command",
            "body": body,
        },
    }
    write(ROOT / "dist/langgraph/manifests/commands" / f"{data['name']}.json", json.dumps(payload, indent=2))


def build_langgraph_workflow(src: Path, data: dict[str, str], body: str) -> None:
    if data["name"] == "triage-nine-phase":
        payload = TRIAGE_NINE_PHASE_GRAPH
        payload = {**payload, "body": body}
    else:
        payload = {
            "name": data["name"],
            "description": data["description"],
            "runtime": "langgraph",
            "source": str(src.relative_to(ROOT)),
            "nodes": [{"id": data["name"].replace("-", "_"), "label": data["description"], "type": "workflow"}],
            "edges": [],
            "body": body,
        }
    write(ROOT / "dist/langgraph/graphs" / f"{data['name']}.json", json.dumps(payload, indent=2))


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
    for src in sorted(path for path in (ROOT / "assets/agents").glob("**/*.md") if path.name != "README.md"):
        data, body = frontmatter_and_body(src)
        build_claude_agent(src, data, body)
        for provider in ("codex", "gemini"):
            write(ROOT / f"dist/{provider}/prompts/agents" / src.name, f"> Generated from `{src.relative_to(ROOT)}`.\n\n{body}")
        write(ROOT / "dist/open-source/manifests/agents" / f"{data['name']}.json", json.dumps({"name": data["name"], "description": data["description"], "category": data.get("category"), "source": str(src.relative_to(ROOT)), "body": body}, indent=2))
        build_langgraph_agent(src, data, body)
    for src in sorted(path for path in (ROOT / "assets/commands").glob("**/*.md") if path.name != "README.md"):
        data, body = frontmatter_and_body(src)
        build_command(src, data, body)
        build_langgraph_command(src, data, body)
    for src in sorted((ROOT / "assets/skills").glob("*/SKILL.md")):
        copy_skill(src)
    for src in sorted((ROOT / "assets/workflows").glob("*.md")):
        if src.name == "README.md":
            for provider in PROVIDERS:
                write(ROOT / f"dist/{provider}/workflows" / src.name, f"> Generated from `{src.relative_to(ROOT)}`.\n\n{src.read_text(encoding='utf-8')}")
            continue
        data, body = frontmatter_and_body(src)
        build_langgraph_workflow(src, data, body)
        for provider in PROVIDERS:
            folder = "workflows" if provider != "open-source" else "workflows"
            write(ROOT / f"dist/{provider}/{folder}" / src.name, f"> Generated from `{src.relative_to(ROOT)}`.\n\n{src.read_text(encoding='utf-8')}")
    write(ROOT / "dist/open-source/AGENT_MANIFEST.md", "# Open Source Manifest\n\nGenerated from provider-neutral assets. Context metadata is available in `manifests/context/repo-agent-instructions.json`.")
    write(ROOT / "dist/langgraph/LANGGRAPH.md", "# LangGraph Runtime\n\nGenerated graph and runtime manifests from provider-neutral assets. LangGraph is an orchestration runtime, not a model provider. Pre-dispatch context is available in `context/repo-agent-instructions.json`.")
    print("Built provider adapters: claude, codex, gemini, open-source; runtime adapters: langgraph")


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
        "counts": {"agents": len(agents), "commands": len(commands), "skills": len(skills), "workflows": len(workflows), "context": len(context), "providers": 4, "runtimes": 1, "guides": len(guides)},
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
    "README.md",
    "AI_ASSETS.md",
    "CONTRIBUTING.md",
    "RELEASE.md",
    "CHANGELOG.md",
    "VERSION",
]

RENAMED_DOCS = {
    "LANGGRAPH_RUNTIME.md": "langgraph-runtime.md",
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


def main() -> int:
    failures: list[str] = []

    if not (ROOT / "dist/langgraph").is_dir():
        failures.append("dist/langgraph is missing")

    if not TRIAGE_GRAPH.exists():
        failures.append("dist/langgraph/graphs/triage-nine-phase.json is missing")
    else:
        graph = json.loads(TRIAGE_GRAPH.read_text(encoding="utf-8"))
        nodes = graph.get("nodes", [])
        edges = graph.get("edges", [])
        approval_nodes = [node for node in nodes if node.get("approval_checkpoint") is True]

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

        approval_ids = sorted(node.get("id") for node in approval_nodes)
        if approval_ids != ["gate_1", "gate_2"]:
            failures.append(f"approval checkpoints must be gate_1 and gate_2, found {approval_ids}")

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
    parser.parse_args()
    required = [
        "CHANGELOG.md",
        "RELEASE.md",
        "VERSION",
        ".github/PULL_REQUEST_TEMPLATE.md",
        ".github/labels.yml",
        ".github/workflows/release.yml",
        "examples/consumer-repo/README.md",
        "scripts/check_consumer_install.py",
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
    "README.md",
    "AI_ASSETS.md",
    "RELEASE.md",
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
    "README.md",
    "AI_ASSETS.md",
    "RELEASE.md",
    "CHANGELOG.md",
    "dist/claude/CLAUDE.md",
    "dist/codex/AGENTS.md",
    "dist/gemini/GEMINI.md",
    "dist/langgraph/LANGGRAPH.md",
    "dist/open-source/AGENT_MANIFEST.md",
    "docs/reference/README.md",
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
  echo "Usage: ./install.sh [--provider claude|codex|gemini|open-source|all] [--runtime langgraph|all] [--project] [--force] [--dry-run] [--skip-build] [filters]"
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
    commands/*|manifests/commands/*)
      [ "$INCLUDE_COMMANDS" -eq 1 ] ;;
    workflows/*)
      [ "$INCLUDE_WORKFLOWS" -eq 1 ] ;;
    graphs/*)
      [ "$INCLUDE_WORKFLOWS" -eq 1 ] ;;
    context/*|manifests/context/*)
      [ "$INCLUDE_CONTEXT" -eq 1 ] ;;
    guides/*|reference/*|docs/*)
      [ "$INCLUDE_GUIDES" -eq 1 ] ;;
    CLAUDE.md|AGENTS.md|GEMINI.md|AGENT_MANIFEST.md|LANGGRAPH.md)
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
    langgraph) target="$HOME/.langgraph" ;;
    *) echo "Unsupported runtime: $runtime"; exit 1 ;;
  esac
  if [ "$PROJECT" -eq 1 ]; then
    case "$runtime" in
      langgraph) target=".langgraph" ;;
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
  install_runtime langgraph
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
    write("AI_ASSETS.md", f"""# {PLATFORM}

## What This Is

{PLATFORM} is a provider-neutral library of AI agents, skills, commands, workflows, guides, and adapter outputs for {ORG}.

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

- LangGraph: `dist/langgraph`

LangGraph is an orchestration runtime export, not a model provider.

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
python3 scripts/check_langgraph_exports.py
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
| Repository context | `assets/context/` |
| Guides | `guides/` |
| Runtime adapters | `dist/langgraph/` |

## Supported Providers

- Claude Code
- OpenAI Codex
- Google Gemini / Gemini CLI
- Open-source agent frameworks

## Supported Runtimes

- LangGraph runtime export for stateful workflow orchestration

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

## Export for LangGraph

```bash
python3 scripts/build_adapters.py
./install.sh --runtime langgraph --project --force
```

## Install Into a Consumer Repository

Use `examples/consumer-repo/` as the reference flow for installing {PLATFORM} into another GitHub repository.

```bash
python3 scripts/check_consumer_install.py
```

The smoke check stages a temporary consumer repo and verifies context-only dry runs, root `CLAUDE.md` installs, provider assets under `.claude/`, LangGraph exports under `.langgraph/`, and skip behavior when a root context file already exists.

## Internal Releases

Internal dist releases use short-lived `release/vX.Y.Z` branches and `vX.Y.Z` tags. The GitHub release workflow publishes prerelease archives from tags that match `VERSION`.

```bash
git checkout main
git pull
git checkout -b release/v0.1.0
python3 scripts/package_release.py
python3 scripts/check_release_package.py
git tag v0.1.0
```

See `RELEASE.md` for the full branch strategy and release checklist.

## Command Reference

See `assets/commands/` and the GitHub Pages portal at `docs/index.html`.

## Contributing

Use GitHub Issues first. See `CONTRIBUTING.md`.
""")

    write("LANGGRAPH_RUNTIME.md", """# LangGraph Runtime Adapter

LangGraph support is provided as a runtime adapter, not as a model provider.

Claude, Codex, and Gemini are provider adapters because they map prompts, skills, commands, and context into model-specific coding assistant surfaces. LangGraph is different: it is an orchestration runtime for stateful agent workflows. This repository exports graph metadata that can be consumed by a future LangGraph application without requiring LangGraph as a dependency in this repo.

## Generated Outputs

Run:

```bash
python3 scripts/build_adapters.py
```

Generated LangGraph files are written to:

```text
dist/langgraph/
  LANGGRAPH.md
  manifests/
    agents/
    commands/
  graphs/
```

## Triage Graph Contract

`dist/langgraph/graphs/triage-nine-phase.json` exports the canonical nine-phase triage workflow.

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

## Installation

Install generated runtime exports into a project-local `.langgraph/` directory:

```bash
./install.sh --runtime langgraph --project --force
```

Install only graph workflows:

```bash
./install.sh --runtime langgraph --project --force --workflows-only
```

## Validation

Run:

```bash
python3 scripts/check_langgraph_exports.py
```

This verifies that the LangGraph export exists, the triage graph has exactly nine nodes, the edge order follows the canonical workflow, and both approval gates are marked.
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

Ship stable provider-neutral assets, generated provider adapters, and runtime exports together.

## Semantic Versioning

- Patch: documentation fixes, prompt wording changes, non-breaking adapter fixes
- Minor: new agents, skills, commands, workflows, provider adapters, or runtime adapters
- Major: breaking frontmatter, installer, invocation, or adapter contract changes

## Release Cadence

Monthly by default, with ad hoc patch releases for urgent fixes.

## Release Roles

Release owner: {RELEASE_OWNER}.

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
5. Create a release PR from `release/vX.Y.Z` back to `main`.
6. After approval, tag the release branch with `vX.Y.Z`.
7. Push the release branch and tag.
8. Confirm GitHub Actions publishes the internal prerelease with dist archives.
9. Merge release branch changes back to `main` if the branch contains release-only commits.

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
    url: https://github.com/Yamini-Suranku/nunneri-public-ai-assets/discussions
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
      - name: Check context exports
        run: python3 scripts/check_context_exports.py
      - name: Check LangGraph exports
        run: python3 scripts/check_langgraph_exports.py
      - name: Check consumer install
        run: python3 scripts/check_consumer_install.py
      - name: Check release readiness
        run: python3 scripts/check_release_ready.py --local-only
      - name: Validate shell scripts
        run: |
          bash -n install.sh
          bash -n uninstall.sh
      - name: Ensure generated files are committed
        run: git diff --exit-code
""")
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
