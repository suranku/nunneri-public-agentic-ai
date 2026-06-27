> **One-liner:** Schema and Lineage gives teams a provider-neutral way to use AI assets across Claude, Codex, Gemini, and open-source runtimes.

## The Problem Before

Teams duplicated prompts and workflows for each assistant, making quality, approvals, and releases hard to govern.

## The Solution

Canonical assets live once under `assets/` and provider adapters generate the runtime-specific files.

## Command Reference

| Command | What it does | When to use |
| --- | --- | --- |
| `/schema-drift` | Runs the schema-drift workflow | Use when the request maps to schema-drift |
| `/impact-analysis` | Runs the impact-analysis workflow | Use when the request maps to impact-analysis |
| `/column-trace` | Runs the column-trace workflow | Use when the request maps to column-trace |

## How It Works

```text
issue -> canonical asset -> provider adapter -> validation -> release
```

## Real Examples

```text
/schema-drift sample-input --provider claude
/impact-analysis sample-input --provider claude
/column-trace sample-input --provider claude
```
