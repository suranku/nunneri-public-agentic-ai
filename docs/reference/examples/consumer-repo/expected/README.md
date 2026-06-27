# Expected Install Artifacts

These files document the key artifacts a consumer repository should see after installing Nunneri AI Assets.

The full generated provider and runtime payload is intentionally not duplicated here. The authoritative outputs are generated under `dist/` and verified by `scripts/check_consumer_install.py`.

## Context-Only Claude Install

```text
CLAUDE.md
.ai-assets-version
```

## Full Claude Install

```text
CLAUDE.md
.claude/.ai-assets-version
.claude/agents/python-triage-specialist.md
.claude/commands/triage.md
```

## Codex and Gemini Context Files

```text
AGENTS.md
GEMINI.md
```

## LangGraph Runtime Install

```text
.langgraph/.ai-assets-version
.langgraph/context/repo-agent-instructions.json
.langgraph/graphs/triage-nine-phase.json
.langgraph/manifests/agents/python-triage-specialist.json
```
