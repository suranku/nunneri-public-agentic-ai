> **One-liner:** Developer Tools gives teams a provider-neutral way to use AI assets across Claude, Codex, Gemini, and open-source runtimes.

## The Problem Before

Teams duplicated prompts and workflows for each assistant, making quality, approvals, and releases hard to govern.

## The Solution

Canonical assets live once under `assets/` and provider adapters generate the runtime-specific files.

## Command Reference

| Command | What it does | When to use |
| --- | --- | --- |
| `/devhub-fix` | Runs the devhub-fix workflow | Use when the request maps to devhub-fix |
| `/generate-agent-context` | Runs the generate-agent-context workflow | Use when the request maps to generate-agent-context |

## How It Works

```text
issue -> canonical asset -> provider adapter -> validation -> release
```

## Real Examples

```text
/devhub-fix '{"finding":"missing correlation id","repo":"payments-api"}' --provider gemini
/generate-agent-context . --provider codex
```
