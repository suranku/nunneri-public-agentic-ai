# CrewAI Runtime Runner Example

This example is the first runnable CrewAI-facing adapter harness for the Nunneri Runtime Contract.

It reads generated files from:

```text
dist/nunneri-runtime/workflows/triage-nine-phase.json
dist/crewai/flows/triage-nine-phase.json
```

Then it executes the flow shape deterministically without installing the CrewAI SDK. This keeps the repository dependency-free while proving that the CrewAI export preserves:

- ordered workflow steps
- `human_input` approval gates
- approve/reject actions
- cancellation on rejection
- no downstream implementation work after rejection

Run an all-approved flow:

```bash
python3 examples/crewai-runtime-runner/run_crewai_contract.py --auto-approve
```

Run a rejection path:

```bash
python3 examples/crewai-runtime-runner/run_crewai_contract.py --reject-gate gate_1
```

This is not a CrewAI SDK application yet. It is the contract runner that a later SDK-backed implementation should match.
