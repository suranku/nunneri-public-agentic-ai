# Nunneri AI Assets

## What This Is

Nunneri AI Assets is a provider-neutral library of AI agents, skills, commands, workflows, guides, and adapter outputs for Nunneri Engineering.

Nunneri was originated by Suranku and Yamini and is stewarded by the Nunneri Core Team.

## Licensing Model

Nunneri AI Assets are published as an AGPLv3 Community Edition with commercial licensing available.

- AGPLv3 Community Edition: `LICENSE`
- Commercial license path: `COMMERCIAL_LICENSE.md`
- Trademark policy: `TRADEMARKS.md`
- Maintainers and originators: `MAINTAINERS.md`

Contact `core@nunneri.com` for commercial licensing. Use `yamini.sk@suranku.com` as the temporary fallback until Nunneri domain email is active.

## Architecture and Defensive Publication

- `ARCHITECTURE.md` documents the product and engineering architecture.
- `DEFENSIVE_PUBLICATION.md` documents the runtime-neutral control plane for defensive-publication and public-disclosure purposes.
- `NUNNERI_RUNTIME_CONTRACT.md` documents the neutral runtime contract and adapter mapping rules.

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
