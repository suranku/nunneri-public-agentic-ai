# Platform Onboarding

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
