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
