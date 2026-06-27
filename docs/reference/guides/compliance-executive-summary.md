> **One-liner:** Compliance gives teams a provider-neutral way to use AI assets across Claude, Codex, Gemini, and open-source runtimes.

## The Problem Before

Teams duplicated prompts and workflows for each assistant, making quality, approvals, and releases hard to govern.

## The Solution

Canonical assets live once under `assets/` and provider adapters generate the runtime-specific files.

## Command Reference

| Command | What it does | When to use |
| --- | --- | --- |
| `/exception-handling` | Runs the exception-handling workflow | Use when the request maps to exception-handling |
| `/nfr-readiness` | Runs the nfr-readiness workflow | Use when the request maps to nfr-readiness |
| `/check-logging` | Runs the check-logging workflow | Use when the request maps to check-logging |

## How It Works

```text
issue -> canonical asset -> provider adapter -> validation -> release
```

## Real Examples

```text
/exception-handling services/checkout --provider claude
/nfr-readiness services/reporting --provider codex
/check-logging src/payments --provider claude
```
