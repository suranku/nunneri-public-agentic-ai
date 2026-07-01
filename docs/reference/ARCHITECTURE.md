# Nunneri Architecture

Nunneri is a provider- and runtime-neutral control plane for AI assets, agentic workflows, human approval gates, and auditable execution.

Nunneri was originated by Suranku and Yamini and is stewarded by the Nunneri Core Team.

## System Components

```text
assets/
  canonical agents, skills, commands, workflows, context
        |
        v
scripts/build_adapters.py
        |
        v
dist/nunneri-runtime/
  neutral runtime contract
        |
        +--> dist/claude/
        +--> dist/codex/
        +--> dist/gemini/
        +--> dist/open-source/
        +--> dist/langgraph/
        +--> dist/crewai/
        +--> dist/autogen/
        +--> dist/semantic-kernel/
        |
        v
api/
  FastAPI server, provider routing, tenant/RBAC checks, run persistence
        |
        v
Graph Studio
  browser UI for workflow phases, approvals, traces, outputs, reruns
```

## Canonical Assets

Authors edit provider-neutral source files under `assets/`:

- agents define reusable roles and activation rules
- skills define reusable implementation guidance
- commands define user-facing entrypoints
- workflows define ordered phases and approval gates
- context defines repository-level instructions and provider overrides

Generated provider and runtime outputs are derived from these canonical files. Generated outputs should not become the source of truth.

## Neutral Runtime Contract

`dist/nunneri-runtime/` is the bridge between canonical assets and runtime adapters. It contains a contract index and per-asset JSON files for agents, commands, workflows, and repository context.

The contract includes:

- asset identity and source path
- inputs and dispatch metadata
- workflow nodes and edges
- node types such as `work`, `human_approval`, and `terminal`
- approval metadata and rejection policy
- context injection stage
- runtime hints for state, human-in-the-loop behavior, and observability

Runtime adapters consume this contract rather than reading provider-specific files.

## Runtime Adapters

Nunneri treats runtime frameworks as adapter targets:

- LangGraph maps contract workflows into graph JSON and runnable server graphs.
- CrewAI maps contract agents and workflows into agent and flow manifests.
- AutoGen maps contract agents and workflows into orchestration manifests.
- Semantic Kernel maps contract agents and workflows into agent and orchestration manifests.

The adapter rule is simple: preserve contract semantics, especially `human_approval` nodes. A rejected approval gate must not route to downstream implementation work.

## Provider Adapters

Provider adapters map canonical assets into assistant-specific surfaces:

- Claude Code uses `CLAUDE.md` and `.claude/` assets.
- Codex uses `AGENTS.md` and `.codex/` assets.
- Gemini uses `GEMINI.md` and `.gemini/` assets.
- Open-source exports use portable manifests and prompts.

Provider-specific overrides are allowed only in the context template's provider sections. The generator emits only the matching override into each provider root file.

## API Server

The API server is a FastAPI application that serves Graph Studio and runs the first runnable LangGraph-backed execution path.

Core responsibilities:

- load generated manifests and graph definitions
- run LangGraph workflows with SSE streaming
- route model calls to Ollama, Gemini, Claude, or OpenAI by model prefix
- persist threads, runs, run nodes, node configs, users, organizations, teams, and projects
- enforce OIDC or local-token authentication when enabled
- apply tenant/RBAC checks to project-scoped operations
- expose gate approval and rejection endpoints

## Graph Studio

Graph Studio is the browser UI for operating the runtime control plane. It reads graph definitions from the API and presents technical nodes as user-facing workflow phases.

It supports:

- selecting agents and commands
- creating and reopening threads
- running workflows with live SSE events
- viewing phase descriptions, expected outputs, classification options, edge conditions, and approval context
- approving or rejecting human gates
- cancelling stuck runs
- rerunning as a new thread
- inspecting per-phase outputs and final summaries
- saving project-specific node configuration overrides

## Human Approval Flow

```text
work phase -> gate phase -> waiting_approval
                         |
                         +-- approve -> resume same checkpoint -> downstream work
                         |
                         +-- reject  -> record rejection -> terminal cancellation
```

Gate phases emit a JSON approval payload and pause the runtime. Approval resumes the checkpoint with an approved decision. Rejection resumes with a rejected decision and prevents downstream implementation nodes from executing.

Run records and node records reflect these states:

- `running`
- `waiting_approval`
- `approved`
- `rejected`
- `cancelled`
- `done`
- `error`

## Durable State Model

Nunneri keeps workflow state outside the LLM context window:

```text
organization
  team
    project
      thread
        run
          run node
            output, status, timing, error detail, approval decision
```

This structure supports auditability, replay, rerun, stuck-run cancellation, approval review, and final summaries without requiring the model to carry prior state in prompt context.

## Tenant and RBAC Model

The tenant hierarchy is organization -> team -> project. Threads and runs are project scoped where project metadata is provided.

RBAC applies to:

- organization administration
- team administration
- project access
- agent and command dispatch
- gate approval and rejection
- thread and run history
- node configuration persistence

Org admins can satisfy lower-scope checks. Team admins can satisfy project-level checks for projects in the team. Project roles control normal project execution.

## Provider Routing

Model routing is prefix based:

- no prefix or `ollama:` uses local Ollama
- `gemini:` uses `GEMINI_API_KEY`
- `claude:` uses `ANTHROPIC_API_KEY`
- `openai:` uses `OPENAI_API_KEY`

This allows one workflow to run across local or cloud model providers without rewriting the canonical workflow.

## Observability and Run Evidence

Nunneri records:

- SSE event stream state
- run status
- per-node status and output
- gate decisions
- timing
- model metadata
- queue status for local Ollama execution
- error detail and stale-run cancellation state

The UI and API expose completed runs as stage-by-stage reports with a final summary.

## Object Storage Guidance

Object storage is not required for the core runtime. The default architecture uses PostgreSQL for operational records and local/generated files for assets.

If artifact storage is added, use a pluggable storage boundary:

- filesystem for local development
- cloud object storage for managed deployments
- S3-compatible adapter for optional self-hosted storage
- MinIO only as an optional deployment choice, not a bundled requirement

MinIO has independent licensing considerations. Nunneri should not make MinIO a mandatory core dependency for commercial packaging unless the deployment has appropriate MinIO licensing or the user supplies it separately.

## Extension Points

Nunneri can be extended by:

- adding new canonical agents, commands, skills, or workflows
- adding provider adapters
- adding runtime adapters
- adding model-provider routing prefixes
- adding storage adapters
- adding Graph Studio panels that consume contract metadata
- adding tenant-scoped policies for dispatch, approval, and release impact

All extensions should preserve the canonical source of truth and runtime-neutral approval semantics.
