> **One-liner:** Operations gives teams a provider-neutral way to use AI assets across Claude, Codex, Gemini, and open-source runtimes.

## The Problem Before

Teams duplicated prompts and workflows for each assistant, making quality, approvals, and releases hard to govern.

## The Solution

Canonical assets live once under `assets/` and provider adapters generate the runtime-specific files.

## Command Reference

| Command | What it does | When to use |
| --- | --- | --- |
| `/ingestion-check` | Runs the ingestion-check workflow | Use when the request maps to ingestion-check |
| `/pipeline-health` | Runs the pipeline-health workflow | Use when the request maps to pipeline-health |
| `/release-lookup` | Runs the release-lookup workflow | Use when the request maps to release-lookup |

## How It Works

```text
issue -> canonical asset -> provider adapter -> validation -> release
```

## Real Examples

```text
/ingestion-check orders-topic --provider claude
/pipeline-health prod orders-ingestion --provider codex
/release-lookup payments-api v1.8.0 --provider gemini
```
