# Nunneri AI Assets

## What This Is

Nunneri AI Assets is a provider-neutral library of AI agents, skills, commands, workflows, guides, and adapter outputs for Nunneri Engineering.

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
