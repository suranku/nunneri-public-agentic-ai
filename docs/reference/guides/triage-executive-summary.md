> **One-liner:** Triage gives teams a provider-neutral nine-phase workflow for moving from symptom to evidence, approved fix plan, validation, and release impact.

## The Problem Before

Teams duplicated triage prompts for each assistant, mixed diagnosis with implementation, and often skipped approval gates before edits or release actions.

## The Solution

Canonical triage assets define one stable nine-phase workflow. Claude, Codex, Gemini, and open-source adapters receive generated copies from the same source of truth.

## Command Reference

| Command | What it does | When to use |
| --- | --- | --- |
| `/triage` | Runs bug triage from intake through RCA and approval gates | Use for application bugs or unclear symptoms |
| `/prodops-triage` | Classifies incidents and determines whether a runbook or defect is needed | Use for production incidents or environment-specific failures |
| `/devhub-fix` | Fixes a governance finding with test-first validation and approval gates | Use when DevHub or governance JSON identifies a remediable issue |

## How It Works

```text
1 intake
  -> 2 context load
  -> 3 classification
  -> 4 evidence collection
  -> 5 root cause analysis
  -> 6 gate 1: RCA and fix plan approval
  -> 7 test-first fix
  -> 8 validation
  -> 9 gate 2: summary and release impact
```

Post-triage actions such as commit, push, PR creation, release tagging, and publishing require explicit human confirmation.

## Real Examples

```text
/triage NUN-1024 "Checkout API returns 500 after deploy" --provider claude
/prodops-triage INC-204 prod "Kafka consumer lag exceeded threshold" --provider codex
/devhub-fix '{"finding":"missing correlation id","repo":"payments-api"}' --provider gemini
```
