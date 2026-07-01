# Nunneri AI Assets

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
