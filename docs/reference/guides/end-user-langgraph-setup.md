# End-User LangGraph Setup

This guide shows how a consumer repository can install Nunneri provider context, add LangGraph runtime exports, and prepare for stateful orchestration with optional tracing.

LangGraph is a runtime adapter target in Nunneri, not a model provider. Claude, Codex, Gemini, and open-source exports remain the provider targets. LangGraph consumes the generated graph, agent, command, and context manifests.

## Setup Path

Start from a clone or an internal release package:

```bash
git clone https://github.com/suranku/nunneri-public-agentic-ai.git
cd nunneri-public-agentic-ai
python3 scripts/build_adapters.py
```

Preview what provider context would write into your project root:

```bash
./install.sh --provider claude --project --context-only --dry-run
```

Install the provider context and assets you need:

```bash
./install.sh --provider claude --project --force
./install.sh --provider codex --project --force
./install.sh --provider gemini --project --force
```

Install LangGraph runtime exports:

```bash
./install.sh --runtime langgraph --project --force
```

The runtime install writes generated graph, command, agent, and pre-dispatch context manifests under `.langgraph/`.

## Runtime Configuration

Use repository-local configuration so orchestration state can live outside the LLM context window:

```bash
NUNNERI_RUNTIME=langgraph
NUNNERI_STATE_STORE=sqlite
NUNNERI_TRACE_MODE=otel|langsmith|none
```

Recommended default:

```bash
NUNNERI_RUNTIME=langgraph
NUNNERI_STATE_STORE=sqlite
NUNNERI_TRACE_MODE=otel
```

For optional LangSmith tracing, add:

```bash
LANGSMITH_API_KEY=replace-with-your-key
```

Do not require `LANGSMITH_API_KEY` for base setup. OpenTelemetry is the open-source-first monitoring path; LangSmith is an optional hosted tracing UI path.

## Durable State

Use a project-local state path such as:

```text
.nunneri/langgraph/state.sqlite
```

This file is for runtime checkpoints, resumable workflow state, and context that should persist outside the LLM prompt. Add it to the consuming repo's ignore rules unless the team has a deliberate reason to commit runtime state.

## Validation

Run the repo checks before sharing the setup:

```bash
python3 scripts/check_consumer_install.py
python3 scripts/check_langgraph_exports.py
python3 scripts/check_user_setup_docs.py
```

For the interactive walkthrough, open:

```text
guides/end-user-setup-demo.html
```

## What This Does Not Add Yet

This setup does not add a Python LangGraph application, SDK dependency, hosted monitoring dependency, or provider SDK dependency. It defines the portable install and runtime contract first.
