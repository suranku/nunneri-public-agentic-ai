# Runtime Contract Consumer Example

This example shows how a consuming tool can read the neutral Nunneri Runtime Contract without depending on LangGraph, CrewAI, AutoGen, Semantic Kernel, or any model-provider SDK.

## What This Example Proves

- `dist/nunneri-runtime/contract.json` is usable as the runtime export index.
- Workflow contracts can be loaded directly from `dist/nunneri-runtime/workflows/`.
- Human approval nodes are visible through the neutral `human_approval` node type.
- A framework adapter can map the neutral workflow into a CrewAI-style flow shape without reading provider-specific files.

## Run

```bash
python3 examples/runtime-contract-consumer/consume_runtime_contract.py
```

The script prints JSON with:

- the neutral contract version
- the selected workflow name
- total node and edge counts
- approval gate IDs
- a dependency-free CrewAI-style flow projection

## Expected Signals

For `triage-nine-phase`, the output should report:

```text
workflow_name: triage-nine-phase
node_count: 9
approval_gates: gate_1, gate_2
crewai_flow.human_in_loop: gate_1, gate_2
```

## Automated Verification

Run from the repository root:

```bash
python3 scripts/check_runtime_examples.py
```

The check runs this example and verifies that it preserves the neutral contract's human approval semantics.
