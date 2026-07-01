# Nunneri Runtime Contract

The Nunneri Runtime Contract is the provider- and framework-neutral export layer between canonical assets and runtime adapters.

Authors edit `assets/`. The build step generates `dist/nunneri-runtime/` first, then derives runtime-specific exports for LangGraph, CrewAI, Microsoft AutoGen, and Microsoft Semantic Kernel.

For the broader system architecture, public-disclosure record, governance, roadmap, and citation metadata, see `ARCHITECTURE.md`, `DEFENSIVE_PUBLICATION.md`, `GOVERNANCE.md`, `ROADMAP.md`, and `CITATION.cff`.

Do not describe Nunneri as "patent pending" unless a provisional or nonprovisional patent application has actually been filed.

## Generated Contract

```text
dist/nunneri-runtime/
  contract.json
  agents/*.json
  commands/*.json
  workflows/*.json
  context/repo-agent-instructions.json
```

Each individual contract file uses `contract_version: "1.0"` and includes:

- asset identity, source, and description
- provider-neutral inputs, agents, commands, nodes, and edges
- context injection metadata
- runtime hints for state, human-in-the-loop behavior, and observability

## Runtime Mapping

- LangGraph maps workflow nodes and edges into graph JSON. `human_approval` nodes become interrupt-capable approval checkpoints.
- CrewAI maps agents into agent manifests, commands into task manifests, and workflows into flow manifests.
- AutoGen maps agents into AgentChat/Core agent specs and workflows into group orchestration manifests.
- Semantic Kernel maps agents into SK agent definitions and workflows into orchestration manifests.

Runtime-specific SDK fields belong in generated runtime adapter output, not in canonical `assets/`.

Graph Studio also consumes the contract projection exposed by the API. The UI names these executable steps **workflow phases** for users, while the JSON and runtime adapters continue to use the technical `nodes` field.

## Approval Semantics

Runtime adapters must preserve `human_approval` semantics:

- approval is required before downstream implementation work
- allowed actions are `approve` and `reject`
- rejection policy is `cancel`
- rejection must not continue to downstream implementation nodes

## Install

Install the neutral contract itself:

```bash
./install.sh --runtime nunneri-runtime --project --force
```

Install a runtime adapter export:

```bash
./install.sh --runtime langgraph --project --force
./install.sh --runtime crewai --project --force
./install.sh --runtime autogen --project --force
./install.sh --runtime semantic-kernel --project --force
```

No runtime SDK dependencies are installed by this repository.

## Consumer Example

`examples/runtime-contract-consumer/` contains a dependency-free Python example that reads `dist/nunneri-runtime/contract.json`, loads `triage-nine-phase`, and projects it into a CrewAI-style flow shape while preserving approval gates.

`examples/crewai-runtime-runner/` contains the first runnable CrewAI-facing contract harness. It reads `dist/crewai/flows/triage-nine-phase.json`, runs the generated steps, supports approve/reject gate paths, and verifies rejection cancels downstream implementation work. It does not require the CrewAI SDK.

Validate it with:

```bash
python3 scripts/check_runtime_examples.py
python3 scripts/check_crewai_runtime_runner.py
```

## Interactive Demo

Open `guides/runtime-contract-demo.html` for a step-by-step walkthrough covering provider context files, `triage-nine-phase`, `gate_1`, `gate_2`, LangGraph, CrewAI, AutoGen, Semantic Kernel, and the validation checks that keep the exports aligned.

```bash
python3 scripts/check_runtime_contract.py
python3 scripts/check_graph_studio_contract.py
python3 scripts/check_runtime_examples.py
```
