# Nunneri Runtime Contract

The Nunneri Runtime Contract is the provider- and framework-neutral export layer between canonical assets and runtime adapters.

Authors edit `assets/`. The build step generates `dist/nunneri-runtime/` first, then derives runtime-specific exports for LangGraph, CrewAI, Microsoft AutoGen, and Microsoft Semantic Kernel.

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
