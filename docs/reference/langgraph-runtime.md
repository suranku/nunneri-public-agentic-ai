# LangGraph Runtime Adapter

LangGraph support is provided as a runtime adapter, not as a model provider.

Claude, Codex, and Gemini are provider adapters because they map prompts, skills, commands, and context into model-specific coding assistant surfaces. LangGraph is different: it is an orchestration runtime for stateful agent workflows. This repository exports graph metadata that can be consumed by a future LangGraph application without requiring LangGraph as a dependency in this repo.

## Generated Outputs

Run:

```bash
python3 scripts/build_adapters.py
```

Generated LangGraph files are written to:

```text
dist/langgraph/
  LANGGRAPH.md
  manifests/
    agents/
    commands/
  graphs/
```

## Triage Graph Contract

`dist/langgraph/graphs/triage-nine-phase.json` exports the canonical nine-phase triage workflow.

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

## Installation

Install generated runtime exports into a project-local `.langgraph/` directory:

```bash
./install.sh --runtime langgraph --project --force
```

Install only graph workflows:

```bash
./install.sh --runtime langgraph --project --force --workflows-only
```

## Validation

Run:

```bash
python3 scripts/check_langgraph_exports.py
```

This verifies that the LangGraph export exists, the triage graph has exactly nine nodes, the edge order follows the canonical workflow, and both approval gates are marked.
