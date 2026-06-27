# Nuneri AI Assets

Provider-agnostic AI assets for Claude Code, Codex, Gemini, and open-source agent frameworks.

## What's Included

| Category | Source |
| --- | --- |
| Agents | `assets/agents/` |
| Skills | `assets/skills/` |
| Commands | `assets/commands/` |
| Workflows | `assets/workflows/` |
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
