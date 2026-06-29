# LangGraph Runtime Adapter

LangGraph support is provided as a runtime adapter, not as a model provider.

Claude, Codex, and Gemini are provider adapters because they map prompts, skills, commands, and context into model-specific coding assistant surfaces. LangGraph is different: it is an orchestration runtime for stateful agent workflows. This repository exports graph metadata from the neutral Nunneri Runtime Contract without requiring LangGraph as a dependency in this repo.

## Generated Outputs

Run:

```bash
python3 scripts/build_adapters.py
```

Generated LangGraph files are written to:

```text
dist/nunneri-runtime/
  workflows/triage-nine-phase.json

dist/langgraph/
  LANGGRAPH.md
  manifests/
    agents/
    commands/
  graphs/
```

## Triage Graph Contract

`dist/nunneri-runtime/workflows/triage-nine-phase.json` is the neutral contract. `dist/langgraph/graphs/triage-nine-phase.json` is derived from that contract.

Required nodes:

```text
intake
context_load
classification
evidence_collection
root_cause_analysis
gate_1
test_first_fix
validation
gate_2
```

`gate_1` and `gate_2` are marked as human approval checkpoints.

## Human-Blocking Gate Runtime

When the API server runs a LangGraph workflow, human approval checkpoints use LangGraph `interrupt()` and durable checkpoint state. A gate does not auto-pass.

Runtime behavior:

- The graph pauses at the gate and stores the checkpoint under the same `thread_id`.
- SSE emits `gate_waiting` with a JSON approval payload.
- `nunneri_runs.status` becomes `waiting_approval`.
- The gate's `nunneri_run_nodes.status` becomes `waiting_approval`.
- The graph resumes only through an explicit decision endpoint.

Resume endpoints:

```text
POST /threads/{thread_id}/gates/{gate_id}/approve
POST /threads/{thread_id}/gates/{gate_id}/reject
```

Approval resumes the checkpoint with `Command(resume={"approved": true, ...})` and continues downstream. Rejection resumes with `approved: false`, marks the gate `rejected`, emits `run_rejected`, and routes to a terminal cancellation node instead of executing downstream work.

The legacy `/agents/{name}/invoke/trace` path is only a simulated trace. It stops at a gate with `gate_waiting` and does not imply real approval.

## Installation

Install generated runtime exports into a project-local `.langgraph/` directory:

```bash
./install.sh --runtime langgraph --project --force
```

Install only graph workflows:

```bash
./install.sh --runtime langgraph --project --force --workflows-only
```

## End-User Runtime Setup

Use LangGraph as an orchestration runtime target after installing the provider context for Claude, Codex, or Gemini. The base repository exports manifests only; it does not add LangGraph, LangSmith, OpenTelemetry, or provider SDK dependencies to the root project.

Recommended portable configuration:

```bash
NUNNERI_RUNTIME=langgraph
NUNNERI_STATE_STORE=sqlite
NUNNERI_TRACE_MODE=otel
```

Use repository-local durable state for checkpoints and resumable workflow context:

```text
.nunneri/langgraph/state.sqlite
```

Supported trace modes:

```text
otel       OpenTelemetry-first monitoring path
langsmith  Optional hosted LangGraph tracing UI path
none       No tracing
```

`LANGSMITH_API_KEY` is only required when `NUNNERI_TRACE_MODE=langsmith`.

See `guides/end-user-langgraph-setup.md` and `guides/end-user-setup-demo.html` for the end-user walkthrough.

## Validation

Run:

```bash
python3 scripts/check_langgraph_exports.py
python3 scripts/check_runtime_contract.py
python3 scripts/check_user_setup_docs.py
```

This verifies that the neutral contract exists, the LangGraph export was generated from it, the triage graph has exactly nine nodes, the edge order follows the canonical workflow, and both approval gates are marked.
