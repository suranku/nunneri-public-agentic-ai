# Graph Studio

Graph Studio is the browser-based UI for running AI agents, inspecting execution state in real time,
and reviewing run history. It is served by the Nunneri API server at `/ui`.

## Prerequisites

| Requirement | Default |
|---|---|
| API server running | `http://localhost:8000` |
| Ollama running | `http://localhost:11434` |
| At least one Ollama model pulled | `ollama pull mistral` |
| PostgreSQL | `postgresql://nunneri:nunneri@localhost:5432/nunneri` |

See [api-server.md](api-server.md) for setup instructions.

---

## Opening the Studio

Navigate to `http://localhost:8000/ui`.

The header shows:
- **Ollama ✓ · N models** — Ollama is reachable and the model count is shown. Red means Ollama is offline.
- **Queue badge** — appears yellow when Ollama slots are busy, red when requests are waiting.

---

## Selecting an Agent or Command

The left panel lists all available agents and commands loaded from `dist/langgraph/manifests/`.

- **Agents** run multi-phase agentic workflows (intake → analysis → gate → output).
- **Commands** run targeted single-purpose workflows (dispatch → execute → summarize).

Click any item to select it. The graph canvas updates to show the node layout for that agent.

---

## Running an Agent

1. Select an agent or command from the left panel.
2. (Optional) Enter a local path or git URL in the **Project Path** field. The server will inject the
   repository structure and key files as context for the LLM.
3. Type your message in the input field and press **Enter** or click **▶ Run**.

The graph canvas activates and nodes light up as execution progresses:

| Colour | Meaning |
|---|---|
| Blue pulse | Node is active (LLM call in progress) |
| Green | Node completed |
| Diamond / teal | Gate node passed |
| Red | Node errored |

The **Transcript** panel below the canvas shows token-by-token output as each node produces it.

### Queue position

If Ollama is busy, a **Queued** banner appears in the transcript showing your position and estimated wait.

### Routing rules

If a routing rule matched on a node, a `⤳ Rule match: from → to` line appears and the target node briefly flashes cyan.

### Context trimming

If older messages were dropped to fit within the model's context window, a yellow warning appears in the transcript.

---

## Thread History

Every run is attached to a **thread** — a persistent conversation context. The left panel's
**Threads** tab lists all threads, most recent first.

Click a thread to:
- Restore the graph view with node completion states from the last run.
- Show the run output and error details in the transcript.
- See the full run ID and model in the transcript header (click either to copy to clipboard).

Thread IDs are shown in full and are click-to-copy for debugging and support.

### Run status indicators

| Indicator | Meaning |
|---|---|
| `✓ Run complete` | The run finished successfully. |
| `Waiting for approval` | The graph is paused at a human approval gate and is waiting for Approve or Reject. |
| `✕ Run rejected` | A human rejected a gate; downstream execution was cancelled. |
| `✕ Run failed` + error detail | The run errored. The exact exception is shown in red. |
| `⚠ Run appears stuck` | Status is still "running" but started more than 2 minutes ago — the server or browser disconnected mid-run. |

Stuck runs are automatically closed with `status=error` on the next server restart if they are older than 1 hour.

### Approval gates

Human approval nodes are real LangGraph interrupts, not visual markers. When a run reaches a gate, Graph Studio shows an approval card in the transcript and keeps downstream nodes pending.

Available actions:

| Action | Result |
|---|---|
| Approve and resume | Calls `POST /threads/{thread_id}/gates/{gate_id}/approve`, then streams the resumed run from the same checkpoint. |
| Reject and stop | Calls `POST /threads/{thread_id}/gates/{gate_id}/reject`, marks the gate rejected, and prevents downstream work. |

The legacy trace fallback is simulated only. It can show where a gate would occur, but it cannot approve or resume because no durable checkpoint exists for that path.

---

## Node Configuration

Click any node in the graph to open the **Node Config** tab on the right panel.

| Field | Purpose |
|---|---|
| System Prompt | Override the global agent system prompt for this node only. |
| Classification Labels | Comma-separated labels; the LLM is instructed to classify output into one of these. |
| Routing Rules | Conditions that determine which node the graph routes to after this node exits. |
| Notes | Free-text notes for your team (not sent to the LLM). |

### Routing rules

Each rule has a condition, a match value, and a target node ID:

| Condition | Matches when |
|---|---|
| `contains` | Output contains the value (case-insensitive). |
| `starts_with` | Output starts with the value. |
| `ends_with` | Output ends with the value. |
| `regex` | Output matches the regular expression. |
| `always` | Always routes to this target (use as a default/fallback). |

Rules are evaluated in priority order (lowest number first). The first match wins.
Click **Save** to persist. Node configs are stored in PostgreSQL and applied to every run of that agent.

---

## Stopping a Run

Click **■ Stop** to abort the current run. Runs that do not complete within **10 minutes** are
aborted automatically and a timeout message appears in the transcript.

---

## State Inspector

The right panel **State** tab shows:

| Field | Value |
|---|---|
| Thread | Current thread UUID (click to copy) |
| Phase | Last node that ran |
| Output | Tail of the last node's output |
| Checkpoints | Phase breadcrumb trail for the current run |

---

## Errors and Debugging

If a run errors, the transcript shows a red block with the exception class and message, for example:

```
✕ Error
TimeoutError: Ollama queue timeout after 300s (0 still waiting, 2 active)
```

The same detail is stored on the run record in PostgreSQL and is shown when you reload the thread
from history. To query it directly:

```sql
SELECT id, agent, status, error_detail, started_at
FROM nunneri_runs
WHERE status = 'error'
ORDER BY started_at DESC
LIMIT 10;
```

Common errors:

| Error | Likely cause |
|---|---|
| `TimeoutError: Ollama queue timeout` | Too many concurrent runs; increase `OLLAMA_MAX_CONCURRENT` or wait. |
| `ConnectionRefusedError` connecting to Ollama | Ollama is not running. Start it with `ollama serve`. |
| `model not found` from Ollama | The selected model has not been pulled. Run `ollama pull <model>`. |
| `asyncio.CancelledError` | The browser disconnected mid-run. The run will be marked error on the next server start. |
