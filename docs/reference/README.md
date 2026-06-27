# Nuneri AI Assets

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

## Command Reference

See `assets/commands/` and the GitHub Pages portal at `docs/index.html`.

## Contributing

Use GitHub Issues first. See `CONTRIBUTING.md`.
