# Consumer Repository Example

This fixture shows how a normal GitHub repository can consume Nunneri AI Assets without becoming tied to one AI provider.

## What This Example Proves

- Provider context files install at the consumer repository root.
- Provider assets install under provider directories such as `.claude/`, `.codex/`, and `.gemini/`.
- LangGraph runtime exports install under `.langgraph/`.
- Dry runs show planned writes without modifying the consumer repository.
- Existing root context files are skipped unless `--force` is used.

## Preview a Context-Only Install

```bash
./install.sh --provider claude --project --context-only --dry-run
```

Expected output includes:

```text
Would install CLAUDE.md (root-context)
Would write version metadata to .ai-assets-version
```

## Install Claude Context Only

```bash
./install.sh --provider claude --project --context-only --force --skip-build
```

Expected consumer files:

```text
CLAUDE.md
.ai-assets-version
```

## Install Full Claude Assets

```bash
./install.sh --provider claude --project --force --skip-build
```

Expected consumer files:

```text
CLAUDE.md
.claude/.ai-assets-version
.claude/agents/python-triage-specialist.md
.claude/commands/triage.md
```

## Install Codex or Gemini

```bash
./install.sh --provider codex --project --force --skip-build
./install.sh --provider gemini --project --force --skip-build
```

Expected root context files:

```text
AGENTS.md
GEMINI.md
```

## Install LangGraph Runtime Exports

```bash
./install.sh --runtime langgraph --project --force --skip-build
```

Expected consumer files:

```text
.langgraph/.ai-assets-version
.langgraph/context/repo-agent-instructions.json
.langgraph/graphs/triage-nine-phase.json
.langgraph/manifests/agents/python-triage-specialist.json
```

## Automated Verification

Run the smoke check from the asset repository root:

```bash
python3 scripts/check_consumer_install.py
```

The check stages a temporary consumer repository, runs the installer in dry-run, context-only, full provider, LangGraph, and existing-file scenarios, and verifies the expected files.
