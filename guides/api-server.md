# API Server

The Nunneri API server (`api/`) is a FastAPI application that serves the Graph Studio UI, runs
LangGraph agent workflows, and persists all state to PostgreSQL.

## Architecture

```
Browser (ui.html)
   │  SSE streaming + REST
   ▼
FastAPI  (api/main.py)          port 8000
   ├─ LangGraph graphs          api/graphs/
   ├─ PostgreSQL checkpointer   langgraph-checkpoint-postgres
   ├─ Ollama queue              api/ollama_queue.py
   ├─ Auth (OIDC optional)      api/auth.py
   └─ DB CRUD                   api/db.py
         │
         ▼
PostgreSQL                      port 5432
Ollama                          port 11434
```

## Prerequisites

- Python 3.11+
- Docker (for PostgreSQL) or a running PostgreSQL 14+ instance
- [Ollama](https://ollama.com) installed and running locally
- At least one model pulled: `ollama pull mistral`

## Setup

### 1. Start PostgreSQL

```bash
cd api
docker compose up -d
```

This starts `postgres:16-alpine` with:
- user/password: `nunneri/nunneri`
- database: `nunneri`
- port: `5432`
- data volume: `pg_data` (persists across restarts)

### 2. Install Python dependencies

```bash
cd api
pip install -r requirements.txt
```

Key packages:

| Package | Purpose |
|---|---|
| `fastapi`, `uvicorn[standard]` | HTTP server and SSE streaming |
| `langgraph>=0.2` | Stateful agent graph execution |
| `langgraph-checkpoint-postgres` | PostgreSQL-backed checkpointer |
| `psycopg[binary,pool]>=3.1` | Async PostgreSQL driver |
| `langchain-core` | Message types used in graph state |
| `httpx` | Async HTTP client for Ollama and cloud LLM APIs |
| `PyJWT[cryptography]` | OIDC token validation and session JWTs |

### 3. Start the server

From the repository root:

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

On startup the server:
1. Connects to PostgreSQL and sets up the `AsyncPostgresSaver` LangGraph checkpointer.
2. Runs `init_db()` — creates all tables if they don't exist and adds any new columns via `ALTER TABLE ... ADD COLUMN IF NOT EXISTS`.
3. Closes any runs left in `status=running` that are older than 1 hour (orphaned by a previous crash).

Open `http://localhost:8000` for the portal or `http://localhost:8000/ui` for the Graph Studio.

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `postgresql://nunneri:nunneri@localhost:5432/nunneri` | PostgreSQL connection string |
| `OLLAMA_BASE` | `http://localhost:11434` | Ollama base URL |
| `OLLAMA_MAX_CONCURRENT` | `2` | Max parallel Ollama calls (semaphore slots) |
| `OLLAMA_QUEUE_TIMEOUT_S` | `300` | Seconds to wait for a queue slot before aborting |
| `OLLAMA_MAX_CONTEXT_TOKENS` | `6000` | Estimated token budget per Ollama call |
| `AUTH_ENABLED` | `true` | Set to `false` to disable auth (dev mode — all requests run as anonymous admin) |
| `OIDC_ISSUER_URL` | — | OIDC provider discovery URL, e.g. `https://keycloak.example.com/realms/nunneri` |
| `OIDC_CLIENT_ID` | `nunneri` | OIDC client ID |
| `OIDC_CLIENT_SECRET` | — | OIDC client secret |
| `OIDC_REDIRECT_URI` | `http://localhost:8000/auth/callback` | OAuth2 callback URL |
| `SESSION_SECRET` | `change-me-in-production` | HS256 secret for internal session JWTs |
| `SESSION_TTL_S` | `86400` | Session JWT lifetime in seconds |
| `GEMINI_API_KEY` | — | Google AI Studio key (enables `gemini:*` models) |
| `ANTHROPIC_API_KEY` | — | Anthropic key (enables `claude:*` models) |

### Minimal dev `.env`

```bash
DATABASE_URL=postgresql://nunneri:nunneri@localhost:5432/nunneri
AUTH_ENABLED=false
```

## Authentication

When `AUTH_ENABLED=false` (default for local dev), all requests are accepted as an anonymous admin
user. No OIDC provider is needed.

When `AUTH_ENABLED=true`, set the OIDC variables and configure your provider (Keycloak, Okta, or
Azure AD) with:
- Grant type: Authorization Code
- Redirect URI: `$OIDC_REDIRECT_URI`
- Scopes: `openid profile email`

Users log in via `GET /auth/login` → provider → `GET /auth/callback` → session JWT → `/ui`.

## Multi-Tenant Hierarchy

```
Organisation
  └─ Team
       └─ Project
            └─ Thread
                 └─ Run
```

RBAC roles per scope: `admin > owner > member > viewer`.

Org admins manage teams. Team admins manage projects. Project owners manage members.
With `AUTH_ENABLED=false` the hierarchy still exists in the DB but all access checks pass.

## LLM Providers

| Model prefix | Provider | Required env var |
|---|---|---|
| `mistral`, `phi3`, etc. (no prefix) | Local Ollama | — |
| `ollama:mistral` | Local Ollama | — |
| `gemini:gemini-2.0-flash` | Google Generative AI | `GEMINI_API_KEY` |
| `claude:claude-sonnet-4-6` | Anthropic | `ANTHROPIC_API_KEY` |

Ollama calls are throttled through the concurrency queue. Cloud provider calls bypass the queue
(rate limiting is handled by their APIs).

## Key API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Ollama status, available models, agent/command count |
| `GET` | `/models` | All models grouped by provider with configured status |
| `GET` | `/queue/status` | Live Ollama queue stats |
| `GET` | `/agents` | List all agents |
| `GET` | `/commands` | List all commands |
| `POST` | `/graphs/{agent}/run` | Run an agent via SSE streaming |
| `POST` | `/threads/{id}/gates/{gate}/approve` | Approve a pending LangGraph gate and resume the checkpoint |
| `POST` | `/threads/{id}/gates/{gate}/reject` | Reject a pending LangGraph gate and stop downstream execution |
| `GET/POST/DELETE` | `/threads` | Thread management |
| `GET` | `/threads/{id}/runs` | Run history for a thread |
| `GET` | `/runs/{id}` | Full run detail including per-node state |
| `PUT` | `/agents/{agent}/nodes/{node}/config` | Save node configuration |
| `GET/POST/DELETE` | `/orgs`, `/teams`, `/projects` | Tenant management |
| `GET` | `/auth/login` | Redirect to OIDC provider |
| `GET` | `/auth/me` | Current user info |
| `GET` | `/ui` | Graph Studio HTML |
| `GET` | `/` | Developer portal HTML |

Full interactive docs: `http://localhost:8000/docs`

## Human Approval Gates

LangGraph gates are human-blocking in the runtime server. Gate nodes call LangGraph `interrupt()` with a JSON payload and rely on the PostgreSQL checkpointer to persist the paused state.

SSE event flow:

```text
node_enter gate_1
gate_waiting gate_1
```

At that point the stream stops without `run_done`, `nunneri_runs.status` is `waiting_approval`, and the matching `nunneri_run_nodes.status` is `waiting_approval`.

To continue:

```bash
curl -X POST http://localhost:8000/threads/<thread-id>/gates/gate_1/approve \
  -H 'Content-Type: application/json' \
  -d '{"reason":"Reviewed in Graph Studio"}'
```

Approval resumes the same checkpoint and emits `gate_approved` before continuing downstream. Rejection resumes with `approved=false`, emits `gate_rejected` and `run_rejected`, and routes to a terminal cancellation node so downstream work is not executed.

## Logging

The server logs to stdout in the format:

```
2026-06-27T14:30:00 INFO nunneri.api graph_run start agent=triage-go model=mistral thread=abc123 user=anon
2026-06-27T14:30:45 ERROR nunneri.sse run abc-def failed: TimeoutError: Ollama queue timeout ...
```

Logger names:
- `nunneri.api` — request-level events (startup, graph run start, 404s)
- `nunneri.sse` — SSE stream errors with full tracebacks

To increase verbosity: set `LOG_LEVEL=DEBUG` or pass `--log-level debug` to uvicorn.

## Adding a New Agent

1. Create `assets/agents/<name>.md` following the frontmatter schema in `assets/agents/`.
2. Run `python3 scripts/build_adapters.py` to generate `dist/langgraph/manifests/agents/<name>.json`.
3. Restart the server — the new agent appears immediately in the UI.

For a custom node layout (not the default 4-node agent graph), create a graph JSON under
`dist/langgraph/graphs/` and reference it via the agent manifest's `category` field.

## Database Schema

Tables are created by `init_db()` on startup. Key tables:

| Table | Contents |
|---|---|
| `nunneri_threads` | Thread metadata (agent, model, last message) |
| `nunneri_runs` | Run records including output, status, error\_detail |
| `nunneri_run_nodes` | Per-node execution state for each run |
| `nunneri_node_configs` | Per-node LLM/routing configuration |
| `nunneri_users` | Users from OIDC |
| `nunneri_orgs` / `nunneri_teams` / `nunneri_projects` | Tenant hierarchy |
| `nunneri_memberships` | RBAC role assignments |
| `langgraph_checkpoints` | LangGraph thread state (managed by the checkpointer) |

## Troubleshooting

**Server won't start — `checkpointer setup failed`**  
PostgreSQL is not running. Start it: `cd api && docker compose up -d`.

**Ollama offline badge in UI**  
Ollama is not running. Start it: `ollama serve`.

**Run stuck at first node**  
The previous SSE connection dropped without cleanup. The run will be auto-closed on next restart.
To close it manually:
```sql
UPDATE nunneri_runs SET status='error' WHERE status='running';
UPDATE nunneri_run_nodes SET status='error', exited_at=extract(epoch from now())
  WHERE run_id IN (SELECT id FROM nunneri_runs WHERE status='error') AND exited_at IS NULL;
```

**`model not found` error**  
Pull the model: `ollama pull <model-name>`.
