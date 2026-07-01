# Platform Onboarding

## Quick Start

```bash
python3 scripts/build_adapters.py
./install.sh --provider all --project --force
```

## License and Commercial Use

Nunneri is published as an AGPLv3 Community Edition with commercial licensing available.

- Use `LICENSE` for AGPLv3 Community Edition terms.
- Use `COMMERCIAL_LICENSE.md` when a team needs proprietary, embedded, SaaS, OEM, managed-service, indemnity, or enterprise procurement terms.
- Use `TRADEMARKS.md` for Nunneri name and logo usage.
- Contact `core@nunneri.com` for commercial licensing. Use `yamini.sk@suranku.com` as the temporary fallback until Nunneri domain email is active.

Before installing Nunneri into a customer, enterprise, or closed-source repository, confirm whether AGPLv3 obligations are acceptable or whether a commercial license is required.

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

## Runtime Export Example

```bash
python3 scripts/build_adapters.py
./install.sh --runtime nunneri-runtime --project --dry-run
./install.sh --runtime langgraph --project --dry-run
./install.sh --runtime langgraph --project --force
```

The neutral contract installs under `.nunneri-runtime/`. LangGraph installs graph definitions, command manifests, agent manifests, and pre-dispatch context under `.langgraph/`.

Additional runtime exports are available for integration work without adding SDK dependencies:

```bash
./install.sh --runtime crewai --project --force
./install.sh --runtime autogen --project --force
./install.sh --runtime semantic-kernel --project --force
```

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

## Graph Studio and API Server

The `api/` directory contains a FastAPI server that turns the generated manifests into a running
agent execution environment with a browser UI.

### Quick start (local dev)

```bash
# 1. Start PostgreSQL
cd api && docker compose up -d

# 2. Install dependencies
pip install -r api/requirements.txt

# 3. Start the server (from repo root)
AUTH_ENABLED=false uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

Open `http://localhost:8000/ui` for the Graph Studio, `http://localhost:8000` for the portal.

### LLM providers

| Prefix | Provider | Env var needed |
|---|---|---|
| `mistral`, `phi3`, … (none) | Local Ollama | — |
| `gemini:gemini-2.0-flash` | Google AI | `GEMINI_API_KEY` |
| `claude:claude-sonnet-4-6` | Anthropic | `ANTHROPIC_API_KEY` |

### Key env vars

```bash
DATABASE_URL=postgresql://nunneri:nunneri@localhost:5432/nunneri
AUTH_ENABLED=false          # set true + OIDC_* for production
OLLAMA_MAX_CONCURRENT=2     # parallel Ollama slots
GEMINI_API_KEY=…            # optional cloud provider
ANTHROPIC_API_KEY=…         # optional cloud provider
```

See `guides/api-server.md` for the full developer reference and `guides/graph-studio.md` for the
end-user UI guide.

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
