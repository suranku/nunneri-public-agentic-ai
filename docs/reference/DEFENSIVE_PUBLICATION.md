# Defensive Publication: Nunneri Runtime-Neutral Agentic Control Plane

Publication date: 2026-07-01

Originators: Suranku and Yamini

Steward: Nunneri Core Team

## Patent and Defensive Publication Notice

This document publicly discloses the Nunneri architecture and implementation concepts for defensive-publication purposes, including the runtime-neutral control plane. It is intended to document the system in enough technical detail that a practitioner can understand and reproduce the architecture from the published repository.

This document is not legal advice and is not a patent application. Do not describe Nunneri as "patent pending" unless a provisional or nonprovisional patent application has actually been filed.

## Technical Field

Nunneri relates to agentic software systems, AI coding assistants, workflow orchestration, human-in-the-loop control, multi-tenant execution governance, and runtime-neutral adapter generation.

## Problem

AI agent instructions, commands, workflows, and runtime integrations are often duplicated across assistant products and orchestration frameworks. This creates drift between provider-specific instructions, weakens governance over human approval gates, makes execution state hard to audit, and couples user-facing workflow state to one model provider or runtime SDK.

Nunneri addresses this by separating:

- canonical provider-neutral assets
- a generated framework-neutral runtime contract
- provider-specific context exports
- runtime-specific graph or flow exports
- a browser execution UI that consumes the same contract and persisted runtime state

## Disclosed Architecture

Nunneri stores canonical assets in `assets/`, including agents, skills, commands, workflows, and repository context instructions. The build process generates `dist/nunneri-runtime/` first, then derives provider and runtime adapters from that neutral contract.

The generated neutral contract includes:

- contract version and asset identity
- source paths back to canonical assets
- provider-neutral inputs, agents, commands, workflow phases, nodes, and edges
- context injection metadata such as `pre_dispatch`
- runtime hints for statefulness, human-in-the-loop gates, observability, and execution records
- `human_approval` nodes with required approval actions and rejection behavior

The runtime-neutral contract is projected into:

- Claude, Codex, Gemini, and open-source provider context exports
- LangGraph graph JSON and manifests
- CrewAI flow and agent-oriented manifests
- AutoGen orchestration manifests
- Semantic Kernel agent and orchestration manifests
- Nunneri Graph Studio graph definitions and phase configuration UI

Runtime-specific SDK fields are kept in generated adapter output rather than canonical assets. This preserves one canonical source of truth while allowing multiple providers and runtimes to evolve independently.

## Human-Blocking Approval Gates

Nunneri distinguishes visual gate markers from runtime-blocking human approval checkpoints. In the runnable LangGraph path, approval gates pause execution with durable checkpoint state and resume only through an explicit user decision.

The disclosed gate behavior includes:

1. A workflow reaches a `human_approval` phase such as `gate_1` or `gate_2`.
2. The runtime emits a JSON approval payload containing the gate id, phase, question, latest node output, and allowed actions.
3. The run and node records are marked `waiting_approval`.
4. Nunneri Graph Studio displays an approval card to an authorized reviewer.
5. An approval call resumes the same thread checkpoint and allows downstream work.
6. A rejection call records rejection and routes to cancellation so downstream implementation nodes do not execute.
7. The final run report includes per-phase status, gate decisions, timings, and output records.

This preserves the contract-level rule that rejection must not continue into implementation phases.

## Durable State Outside LLM Context

Nunneri keeps operational state outside the LLM context window. The runtime stores and exposes:

- thread identity
- run identity
- phase/node records
- run status
- gate status
- checkpoint state
- per-phase outputs
- error detail
- final summaries
- queue and model metadata

This allows review, replay, cancellation, rerun, and audit workflows without relying on the model to remember prior steps.

## Graph Studio Contract Binding

Nunneri Graph Studio is not merely a visual trace. It consumes the same contract projection as the runtime server and binds UI state to persisted run records.

The UI exposes:

- workflow phases derived from contract nodes
- phase descriptions and expected outputs
- classification options
- edge conditions
- approval questions and required approval context
- tenant-scoped thread and run history
- live SSE events for node entry, node exit, gate waiting, approval, rejection, completion, cancellation, and errors
- per-stage outputs and final summaries after completion

The UI names executable steps as workflow phases for users while preserving the technical `nodes` contract for runtime adapters.

## Multi-Tenant RBAC Scope

Nunneri includes multi-tenant governance over agentic execution. The disclosed hierarchy is:

```text
organization -> team -> project -> thread -> run -> node output
```

RBAC controls are applied to:

- tenant membership
- project access
- agent or command dispatch
- human approval and rejection
- thread and run history access
- node configuration persistence
- model/provider routing where configured
- release-impacting workflow actions

RBAC and tenancy alone are not presented as the invention. The disclosed combination is the use of tenant-scoped permissions over a runtime-neutral agentic workflow control plane, human gates, persisted state, provider routing, and adapter-generated executions.

## Provider-Specific Context Without Canonical Drift

Nunneri uses a provider-neutral repository instruction template that can include provider-specific override sections. The generator renders only the matching provider section into provider-native files such as `CLAUDE.md`, `AGENTS.md`, and `GEMINI.md`.

This allows provider-specific triggers, dispatch language, and tool preferences without contaminating the canonical workflow or leaking provider-only behavior across assistant surfaces.

## Runtime and Storage Extensibility

Nunneri treats runtime frameworks as adapter targets, not model providers. The neutral contract can be projected to LangGraph, CrewAI, AutoGen, Semantic Kernel, or future runtimes while preserving human gate semantics and run observability.

Object storage is intentionally not required as core infrastructure. If artifact storage is needed, Nunneri should use a pluggable storage interface such as filesystem, PostgreSQL-backed metadata with external blob storage, or S3-compatible adapters. MinIO can be supported as an optional S3-compatible deployment choice, but should not be a required bundled dependency because it has independent licensing considerations.

## Reproducible Examples

Representative public artifacts include:

- `NUNNERI_RUNTIME_CONTRACT.md`
- `LANGGRAPH_RUNTIME.md`
- `dist/nunneri-runtime/contract.json`
- `dist/nunneri-runtime/workflows/triage-nine-phase.json`
- `dist/langgraph/graphs/triage-nine-phase.json`
- `examples/runtime-contract-consumer/`
- `examples/crewai-runtime-runner/`
- `guides/runtime-contract-demo.html`
- `guides/graph-studio.md`
- `api/main.py`
- `api/graphs/base.py`
- `api/graphs/triage.py`

Representative validation commands:

```bash
python3 scripts/validate.py
python3 scripts/build_adapters.py
python3 scripts/check_runtime_contract.py
python3 scripts/check_langgraph_exports.py
python3 scripts/check_human_gates.py
python3 scripts/check_graph_studio_contract.py
python3 scripts/check_crewai_runtime_runner.py
python3 scripts/check_release_ready.py --local-only
```

## Distinguishing Technical Combination

The disclosed system is not merely a generic agent workflow, generic RBAC system, generic graph runner, or generic human approval UI. The distinguishing technical combination is:

- canonical provider-neutral agentic assets
- a generated runtime-neutral contract
- multiple generated runtime adapters
- enforced `human_approval` semantics across adapter projections
- stateful execution with durable checkpoints and per-phase outputs
- Graph Studio consuming the same contract and persisted state
- tenant-scoped RBAC over dispatch, approvals, history, configuration, and state
- provider-specific context overrides generated without canonical drift

This combination creates a repeatable control plane for AI-assisted work across model providers, assistant surfaces, and orchestration frameworks.
