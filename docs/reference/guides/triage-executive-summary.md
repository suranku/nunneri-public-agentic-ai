> **One-liner:** Triage gives teams a provider-neutral way to use AI assets across Claude, Codex, Gemini, and open-source runtimes.

## The Problem Before

Teams duplicated prompts and workflows for each assistant, making quality, approvals, and releases hard to govern.

## The Solution

Canonical assets live once under `assets/` and provider adapters generate the runtime-specific files.

## Command Reference

| Command | What it does | When to use |
| --- | --- | --- |
| `/triage` | Runs the triage workflow | Use when the request maps to triage |
| `/prodops-triage` | Runs the prodops-triage workflow | Use when the request maps to prodops-triage |
| `/devhub-fix` | Runs the devhub-fix workflow | Use when the request maps to devhub-fix |

## How It Works

```text
issue -> canonical asset -> provider adapter -> validation -> release
```

## Real Examples

```text
/triage sample-input --provider claude
/prodops-triage sample-input --provider claude
/devhub-fix sample-input --provider claude
```
