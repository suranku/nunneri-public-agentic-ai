> **One-liner:** Ingestion Pipeline gives teams a provider-neutral way to use AI assets across Claude, Codex, Gemini, and open-source runtimes.

## The Problem Before

Teams duplicated prompts and workflows for each assistant, making quality, approvals, and releases hard to govern.

## The Solution

Canonical assets live once under `assets/` and provider adapters generate the runtime-specific files.

## Command Reference

| Command | What it does | When to use |
| --- | --- | --- |
| `/ingestion-check` | Runs the ingestion-check workflow | Use when the request maps to ingestion-check |
| `/pipeline-health` | Runs the pipeline-health workflow | Use when the request maps to pipeline-health |

## How It Works

```text
issue -> canonical asset -> provider adapter -> validation -> release
```

## Real Examples

```text
/ingestion-check sample-input --provider claude
/pipeline-health sample-input --provider claude
```
