#!/usr/bin/env python3
from __future__ import annotations

import asyncio
import json
import logging
import re
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
_log = logging.getLogger("nunneri.api")

# Ensure api/ itself is on sys.path so 'graphs' resolves when uvicorn
# imports this file as 'api.main' from the repo root.
_api_dir = Path(__file__).parent
if str(_api_dir) not in sys.path:
    sys.path.insert(0, str(_api_dir))

import httpx
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse, RedirectResponse, StreamingResponse
from langchain_core.messages import HumanMessage
from langgraph.types import Command
from pydantic import BaseModel, Field

import auth as _auth
import db as _db
import ollama_queue
from graphs import get_graph
from models import Membership, NodeConfig, Org, Project, RoutingRule, Run, RunNode, Team, Thread, User

# ---------------------------------------------------------------------------
# Project context constants
# ---------------------------------------------------------------------------

SKIP_DIRS = {".git", "node_modules", "__pycache__", "dist", "venv", ".venv",
             ".mypy_cache", ".pytest_cache", ".tox", "build", "target", ".idea", ".vscode"}
KEY_FILES = [
    "README.md", "README.rst",
    "pyproject.toml", "setup.py", "setup.cfg", "requirements.txt", "requirements-dev.txt",
    "package.json", "package-lock.json",
    "go.mod", "go.sum",
    "pom.xml", "build.gradle", "build.gradle.kts",
    "Makefile", "Dockerfile", ".env.example", "docker-compose.yml",
    "CLAUDE.md", "AGENTS.md", "GEMINI.md",
]
MAX_FILE_BYTES  = 4 * 1024       # 4 KB per file
MAX_TOTAL_BYTES = 20 * 1024      # 20 KB total context

ROOT = Path(__file__).resolve().parents[1]
AGENTS_DIR = ROOT / "dist/langgraph/manifests/agents"
COMMANDS_DIR = ROOT / "dist/langgraph/manifests/commands"
GRAPHS_DIR = ROOT / "dist/langgraph/graphs"
UI_FILE = Path(__file__).parent / "ui.html"
DOCS_DIR = ROOT / "docs"
PORTAL_FILE = DOCS_DIR / "index.html"
OLLAMA_BASE = "http://localhost:11434"
DEFAULT_MODEL = "mistral"

# Characters of Ollama output before advancing to the next work node.
# Only advances at sentence/paragraph boundaries to avoid mid-sentence phase tags.
CHARS_PER_WORK_NODE = 300

_SENTENCE_END = frozenset({'.', '!', '?', '\n'})

# Remote context cache: url -> (context_str, included_files, fetched_at)
_remote_ctx_cache: dict[str, tuple[str, list[str], float]] = {}
REMOTE_CTX_TTL = 600  # seconds; re-clone after 10 min

_GIT_URL_RE = re.compile(r'^(https?://|git@|git\+ssh://|ssh://)\S+')

# ---------------------------------------------------------------------------
# Generic graph node templates
# ---------------------------------------------------------------------------

GENERIC_AGENT_NODES = [
    {"id": "intake", "label": "Intake", "phase": 1, "type": "work"},
    {"id": "analysis", "label": "Analysis", "phase": 2, "type": "work"},
    {"id": "gate_1", "label": "Review Gate", "phase": 3, "type": "human_approval", "approval_checkpoint": True},
    {"id": "output", "label": "Output", "phase": 4, "type": "work"},
]

GENERIC_COMMAND_NODES = [
    {"id": "dispatch", "label": "Dispatch", "phase": 1, "type": "work"},
    {"id": "execute", "label": "Execute", "phase": 2, "type": "work"},
    {"id": "summarize", "label": "Summarize", "phase": 3, "type": "work"},
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    import graphs.base as _base
    from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
    _log.info("Starting up — connecting to PostgreSQL checkpointer")
    async with AsyncPostgresSaver.from_conn_string(_db.DATABASE_URL) as cp:
        await cp.setup()
        _base.checkpointer = cp
        await _db.init_db()
        _log.info("Startup complete — DB ready, checkpointer active")
        yield
    _log.info("Shutdown complete")


app = FastAPI(title="Nunneri Agent API", version="0.1.0", lifespan=lifespan)


# ---------------------------------------------------------------------------
# Manifest and graph loading
# ---------------------------------------------------------------------------

def load_all(directory: Path) -> dict[str, dict]:
    result: dict[str, dict] = {}
    for path in sorted(directory.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        result[data["name"]] = data
    return result


def agent_system_prompt(manifest: dict) -> str:
    return manifest.get("node", {}).get("body", "")


def command_system_prompt(manifest: dict) -> str:
    return manifest.get("entrypoint", {}).get("body", "")


def load_graph_nodes(manifest: dict, is_command: bool = False) -> list[dict]:
    """Return the LangGraph node list appropriate for this agent/command."""
    category = manifest.get("category", "")
    if category == "triage" and not is_command:
        graph_path = GRAPHS_DIR / "triage-nine-phase.json"
        if graph_path.exists():
            graph = json.loads(graph_path.read_text(encoding="utf-8"))
            return graph.get("nodes", GENERIC_AGENT_NODES)
    return GENERIC_COMMAND_NODES if is_command else GENERIC_AGENT_NODES


def resolve_manifest(agent_name: str) -> tuple[dict, bool]:
    manifests = load_all(AGENTS_DIR)
    is_command = False
    if agent_name not in manifests:
        manifests = load_all(COMMANDS_DIR)
        is_command = True
    if agent_name not in manifests:
        raise HTTPException(status_code=404, detail=f"Agent or command '{agent_name}' not found")
    return manifests[agent_name], is_command


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Project context gathering
# ---------------------------------------------------------------------------

def _tree_lines(root: Path, prefix: str = "", depth: int = 2) -> list[str]:
    if depth < 0:
        return []
    lines = []
    try:
        children = sorted(root.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
    except PermissionError:
        return []
    for child in children:
        if child.name in SKIP_DIRS:
            continue
        lines.append(f"{prefix}{child.name}{'/' if child.is_dir() else ''}")
        if child.is_dir():
            lines.extend(_tree_lines(child, prefix + "  ", depth - 1))
    return lines


def gather_project_context(path: Path) -> tuple[str, list[str]]:
    """Return (formatted_context_block, list_of_file_names_included)."""
    tree = "\n".join(_tree_lines(path)) or "(empty)"
    sections = [f"## Project Context: {path}\n\n### Directory Structure\n{tree}"]
    included: list[str] = []
    total = 0

    for name in KEY_FILES:
        f = path / name
        if not f.exists():
            continue
        raw = f.read_bytes()[:MAX_FILE_BYTES]
        text = raw.decode("utf-8", errors="replace")
        total += len(text)
        sections.append(f"### {name}\n```\n{text}\n```")
        included.append(name)
        if total >= MAX_TOTAL_BYTES:
            break

    return "\n\n".join(sections), included


def is_remote_url(path: str) -> bool:
    return bool(_GIT_URL_RE.match(path))


async def gather_remote_context(url: str) -> tuple[str, list[str]]:
    """Clone a git repo to a temp dir, gather context, clean up. Results cached for REMOTE_CTX_TTL seconds."""
    now = time.time()
    if url in _remote_ctx_cache:
        ctx, included, ts = _remote_ctx_cache[url]
        if now - ts < REMOTE_CTX_TTL:
            return ctx, included

    tmpdir = tempfile.mkdtemp(prefix="nunneri_remote_")
    try:
        proc = await asyncio.create_subprocess_exec(
            "git", "clone", "--depth=1", "--single-branch", url, tmpdir,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await asyncio.wait_for(proc.communicate(), timeout=120)
        if proc.returncode != 0:
            msg = stderr.decode(errors="replace")[:300]
            raise ValueError(f"git clone failed: {msg}")
        ctx, included = gather_project_context(Path(tmpdir))
        _remote_ctx_cache[url] = (ctx, included, now)
        return ctx, included
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


async def inject_project_context(system_prompt: str, project_path: str | None) -> str:
    if not project_path:
        return system_prompt
    try:
        if is_remote_url(project_path):
            ctx, _ = await gather_remote_context(project_path)
        else:
            p = Path(project_path).expanduser().resolve()
            if not p.is_dir():
                return system_prompt
            ctx, _ = gather_project_context(p)
    except Exception:
        return system_prompt
    return f"{ctx}\n\n---\n\n{system_prompt}"


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------

class Message(BaseModel):
    role: str
    content: str


class InvokeRequest(BaseModel):
    message: str
    model: str = Field(DEFAULT_MODEL, description="Ollama model name, e.g. mistral, llama3, phi3")
    history: list[Message] = Field(default_factory=list)
    stream: bool = Field(False)
    project_path: str | None = Field(None, description="Absolute path or git URL for project context")
    custom_nodes: list[dict] | None = Field(None, description="Custom graph nodes overriding manifest defaults")


class InvokeResponse(BaseModel):
    response: str
    name: str
    model: str


class GraphRunRequest(BaseModel):
    message: str
    model: str = Field(DEFAULT_MODEL)
    project_path: str | None = Field(None)
    thread_id: str | None = Field(None)
    project_id: str | None = Field(None, description="Nunneri project UUID for scoping")


class GateDecisionRequest(BaseModel):
    reason: str | None = Field(None, description="Optional human approval or rejection reason")


class RunCancelRequest(BaseModel):
    reason: str | None = Field(None, description="Optional cancellation reason")


# ---------------------------------------------------------------------------
# Ollama helpers
# ---------------------------------------------------------------------------

def _build_messages(system: str, history: list[Message], user_message: str) -> list[dict]:
    msgs: list[dict] = [{"role": "system", "content": system}]
    msgs.extend({"role": m.role, "content": m.content} for m in history)
    msgs.append({"role": "user", "content": user_message})
    return msgs


async def _ollama_invoke(model: str, system: str, history: list[Message], message: str) -> str:
    msgs = _build_messages(system, history, message)
    async with ollama_queue.slot():
        async with httpx.AsyncClient(timeout=120.0) as client:
            r = await client.post(
                f"{OLLAMA_BASE}/api/chat",
                json={"model": model, "messages": msgs, "stream": False},
            )
            if r.status_code != 200:
                raise HTTPException(status_code=502, detail=f"Ollama error {r.status_code}: {r.text}")
            return r.json()["message"]["content"]


async def _ollama_stream(model: str, system: str, history: list[Message], message: str):
    msgs = _build_messages(system, history, message)
    async with ollama_queue.slot():
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                f"{OLLAMA_BASE}/api/chat",
                json={"model": model, "messages": msgs, "stream": True},
            ) as r:
                if r.status_code != 200:
                    raise HTTPException(status_code=502, detail=f"Ollama stream error {r.status_code}")
                async for line in r.aiter_lines():
                    if not line:
                        continue
                    chunk = json.loads(line)
                    token = chunk.get("message", {}).get("content", "")
                    if token:
                        yield token
                    if chunk.get("done"):
                        break


# ---------------------------------------------------------------------------
# Graph-traced SSE streaming
# ---------------------------------------------------------------------------

def _sse(data: dict) -> str:
    return f"data: {json.dumps(data)}\n\n"


def _ntype(n: dict) -> str:
    """Normalize node type from either 'type' or 'node_type' key."""
    return n.get("type") or n.get("node_type", "work")


def _jsonable(value):
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    return str(value)


def _interrupt_value(obj):
    if obj is None:
        return None
    value = getattr(obj, "value", None)
    if value is not None:
        return _jsonable(value)
    if isinstance(obj, dict):
        if "value" in obj:
            return _jsonable(obj["value"])
        if obj.get("type") == "approval_gate" or ("gate_id" in obj and "allowed_actions" in obj):
            return _jsonable(obj)
    return None


def _extract_interrupt_payload(container):
    if container is None:
        return None
    if isinstance(container, dict):
        for key in ("__interrupt__", "interrupts"):
            if key in container:
                payload = _extract_interrupt_payload(container[key])
                if payload:
                    return payload
        for value in container.values():
            payload = _extract_interrupt_payload(value)
            if payload:
                return payload
    elif isinstance(container, (list, tuple)):
        for item in container:
            payload = _extract_interrupt_payload(item)
            if payload:
                return payload
    else:
        payload = _interrupt_value(container)
        if payload:
            return payload
    return None


async def _pending_interrupt_payload(graph, config: dict) -> dict | None:
    """Inspect the latest checkpoint for a pending interrupt payload."""
    try:
        snapshot = await graph.aget_state(config)
    except Exception:
        return None
    for task in getattr(snapshot, "tasks", ()) or ():
        payload = _extract_interrupt_payload(getattr(task, "interrupts", None))
        if payload:
            return payload
    return _extract_interrupt_payload(getattr(snapshot, "interrupts", None))


async def _graph_trace_stream(system_prompt: str, nodes: list[dict], model: str, message: str):
    """Yield SSE strings that advance through LangGraph nodes as Ollama produces output."""
    yield _sse({"type": "graph_start", "nodes": [
        {"id": n["id"], "label": n["label"], "phase": n.get("phase", 1), "node_type": _ntype(n)}
        for n in nodes
    ]})

    node_ptr = 0
    chars = 0

    yield _sse({"type": "node_enter", "id": nodes[0]["id"], "label": nodes[0]["label"],
                "node_type": _ntype(nodes[0])})

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                f"{OLLAMA_BASE}/api/chat",
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": message},
                    ],
                    "stream": True,
                },
            ) as r:
                if r.status_code != 200:
                    yield _sse({"type": "error", "detail": f"Ollama returned {r.status_code}"})
                    return

                async for line in r.aiter_lines():
                    if not line:
                        continue
                    chunk = json.loads(line)
                    token = chunk.get("message", {}).get("content", "")

                    if token:
                        yield _sse({"type": "token", "id": nodes[node_ptr]["id"], "content": token})
                        chars += len(token)

                        # Only advance at sentence/paragraph boundaries to prevent mid-sentence phase tags.
                        if token[-1] in _SENTENCE_END:
                            while chars >= CHARS_PER_WORK_NODE and node_ptr < len(nodes) - 1:
                                chars -= CHARS_PER_WORK_NODE
                                yield _sse({"type": "node_exit", "id": nodes[node_ptr]["id"]})
                                node_ptr += 1

                                while node_ptr < len(nodes) and _ntype(nodes[node_ptr]) == "human_approval":
                                    gate = nodes[node_ptr]
                                    yield _sse({"type": "node_enter", "id": gate["id"], "label": gate["label"],
                                                "node_type": "human_approval"})
                                    yield _sse({
                                        "type": "gate_waiting",
                                        "id": gate["id"],
                                        "simulated": True,
                                        "payload": {
                                            "gate_id": gate["id"],
                                            "question": "Simulated trace stopped at this approval gate. Use /graphs/{agent}/run for resumable approvals.",
                                            "allowed_actions": [],
                                        },
                                    })
                                    return

                                if node_ptr < len(nodes):
                                    n = nodes[node_ptr]
                                    yield _sse({"type": "node_enter", "id": n["id"], "label": n["label"],
                                                "node_type": _ntype(n)})

                    if chunk.get("done"):
                        break
    except Exception as exc:
        yield _sse({"type": "error", "detail": str(exc)})
    finally:
        # Clamp node_ptr: gate advancement can push it past the end of the list.
        safe_ptr = min(node_ptr, len(nodes) - 1)
        yield _sse({"type": "node_exit", "id": nodes[safe_ptr]["id"]})
        yield _sse({"type": "graph_done"})


async def _traced_with_history(gen, run_meta: dict):
    """Wrap a _graph_trace_stream generator, saving the run to history on graph_done."""
    output_parts: list[str] = []
    async for chunk in gen:
        yield chunk
        if chunk.startswith("data: "):
            try:
                ev = json.loads(chunk[6:])
                t = ev.get("type")
                if t == "token":
                    output_parts.append(ev.get("content", ""))
                elif t == "graph_done":
                    run_meta["output"] = "".join(output_parts)
                    run_meta["status"] = "done"
                    run_meta["duration_s"] = round(time.time() - run_meta["started_at"], 1)
            except Exception:
                pass


# ---------------------------------------------------------------------------
# Real LangGraph SSE streaming
# ---------------------------------------------------------------------------

async def _langgraph_sse(graph, graph_input, config: dict,
                          thread_id: str, graph_node_defs: list[dict], run: Run):
    """Execute real LangGraph graph, persist state to DB, and yield SSE events."""
    import logging as _logging
    _log = _logging.getLogger("nunneri.sse")

    node_ids = {n["id"] for n in graph_node_defs}
    existing_nodes = await _db.list_run_nodes(run.id)
    run_nodes: dict[str, RunNode] = {n.node_id: n for n in existing_nodes}
    output_parts: list[str] = []
    def_map = {n["id"]: n for n in graph_node_defs}
    _error_detail: str | None = None
    _paused_payload: dict | None = None
    _run_status = "running" if run.status == "waiting_approval" else run.status

    # Emit queue position before starting if Ollama is busy.
    qs = ollama_queue.stats()
    if qs["active"] >= qs["max_concurrent"] or qs["waiting"] > 0:
        pos = ollama_queue.queue_position()
        yield _sse({
            "type": "queued",
            "position": pos,
            "active": qs["active"],
            "waiting": qs["waiting"],
            "avg_wait_s": qs["avg_wait_s"],
            "message": f"Waiting for Ollama — {pos - 1} request(s) ahead",
        })

    yield _sse({"type": "graph_start", "thread_id": thread_id, "nodes": [
        {"id": n["id"], "label": n["label"], "phase": n.get("phase", 1),
         "node_type": n.get("type", "work")}
        for n in graph_node_defs
    ], "run_id": run.id})

    try:
        async for event in graph.astream_events(graph_input, config, version="v2"):
            ev_type = event["event"]
            ev_name = event.get("name", "")
            ev_data = event.get("data", {})

            payload = _extract_interrupt_payload(ev_data)
            if payload:
                _paused_payload = payload

            if ev_name not in node_ids:
                continue
            if ev_type not in ("on_chain_start", "on_chain_end"):
                continue

            nd = def_map.get(ev_name, {})
            node_type = nd.get("type") or nd.get("node_type", "work")

            if ev_type == "on_chain_start":
                rn = run_nodes.get(ev_name)
                if rn:
                    rn.status = "active"
                    rn.entered_at = rn.entered_at or time.time()
                    rn.exited_at = None
                else:
                    rn = RunNode(
                        run_id=run.id,
                        node_id=ev_name,
                        label=nd.get("label", ev_name),
                        phase=nd.get("phase"),
                        node_type=node_type,
                        status="active",
                        entered_at=time.time(),
                    )
                run_nodes[ev_name] = rn
                await _db.upsert_run_node(rn)
                yield _sse({"type": "node_enter", "id": ev_name})

            elif ev_type == "on_chain_end":
                output = ev_data.get("output", {})
                node_out = ""
                if isinstance(output, dict):
                    node_out = output.get("node_output", "")
                    if not node_out:
                        msgs = output.get("messages", [])
                        if msgs:
                            last = msgs[-1]
                            node_out = last.content if hasattr(last, "content") else str(last)

                if node_out:
                    words = node_out.split()
                    for i in range(0, len(words), 8):
                        chunk = " ".join(words[i:i + 8])
                        chunk += " " if i + 8 < len(words) else "\n"
                        yield _sse({"type": "token", "id": ev_name, "content": chunk})
                        output_parts.append(chunk)
                        await asyncio.sleep(0.03)

                is_gate = ev_name.startswith("gate_")
                phase_val = output.get("phase", ev_name) if isinstance(output, dict) else ev_name
                decision = output.get("gate_decision", {}) if isinstance(output, dict) else {}
                route_to = output.get("route_to", "") if isinstance(output, dict) else ""
                rejected_gate = bool(is_gate and (route_to == "__cancelled__" or decision.get("approved") is False))
                final_status = "rejected" if rejected_gate else "approved" if is_gate else "done"

                # Routing rule match — tell the UI which node output routed to.
                if route_to:
                    yield _sse({"type": "route_match", "from": ev_name, "to": route_to,
                                "message": f"Routing rule matched: {ev_name} → {route_to}"})

                # Context trimming notice.
                trimmed_count = output.get("context_trimmed", 0) if isinstance(output, dict) else 0
                if trimmed_count:
                    yield _sse({"type": "context_trimmed", "node": ev_name,
                                "dropped": trimmed_count,
                                "message": f"{trimmed_count} earlier message(s) dropped to fit context window"})

                # Update run node in DB.
                rn = run_nodes.get(ev_name)
                if rn:
                    rn.status = final_status
                    rn.output = node_out[:2000] if node_out else None
                    rn.exited_at = time.time()
                    await _db.upsert_run_node(rn)

                if is_gate:
                    if rejected_gate:
                        _run_status = "rejected"
                        yield _sse({"type": "gate_rejected", "id": ev_name, "decision": decision})
                    else:
                        yield _sse({"type": "gate_approved", "id": ev_name, "decision": decision})
                yield _sse({"type": "node_exit", "id": ev_name, "state": {
                    "phase": phase_val,
                    "node_output": node_out[:500],
                    "route_to": route_to,
                }})

        if not _paused_payload:
            _paused_payload = await _pending_interrupt_payload(graph, config)

        if _paused_payload:
            gate_id = str(_paused_payload.get("gate_id") or _paused_payload.get("id") or "")
            if gate_id and gate_id in node_ids:
                nd = def_map.get(gate_id, {})
                rn = run_nodes.get(gate_id)
                if not rn:
                    rn = RunNode(
                        run_id=run.id,
                        node_id=gate_id,
                        label=nd.get("label", gate_id),
                        phase=nd.get("phase"),
                        node_type=nd.get("type", "human_approval"),
                        entered_at=time.time(),
                    )
                    run_nodes[gate_id] = rn
                rn.status = "waiting_approval"
                rn.output = json.dumps(_paused_payload, ensure_ascii=False)[:2000]
                rn.exited_at = None
                await _db.upsert_run_node(rn)
                run.status = "waiting_approval"
                _run_status = "waiting_approval"
                yield _sse({
                    "type": "gate_waiting",
                    "id": gate_id,
                    "payload": _paused_payload,
                    "thread_id": thread_id,
                    "run_id": run.id,
                })

    except Exception as exc:
        _paused_payload = _paused_payload or await _pending_interrupt_payload(graph, config)
        if _paused_payload:
            gate_id = str(_paused_payload.get("gate_id") or _paused_payload.get("id") or "")
            nd = def_map.get(gate_id, {})
            rn = run_nodes.get(gate_id)
            if gate_id and gate_id in node_ids:
                if not rn:
                    rn = RunNode(
                        run_id=run.id,
                        node_id=gate_id,
                        label=nd.get("label", gate_id),
                        phase=nd.get("phase"),
                        node_type=nd.get("type", "human_approval"),
                        entered_at=time.time(),
                    )
                    run_nodes[gate_id] = rn
                rn.status = "waiting_approval"
                rn.output = json.dumps(_paused_payload, ensure_ascii=False)[:2000]
                rn.exited_at = None
                await _db.upsert_run_node(rn)
                run.status = "waiting_approval"
                _run_status = "waiting_approval"
                yield _sse({
                    "type": "gate_waiting",
                    "id": gate_id,
                    "payload": _paused_payload,
                    "thread_id": thread_id,
                    "run_id": run.id,
                })
        else:
            _error_detail = f"{type(exc).__name__}: {exc}"
            _log.error("run %s failed at graph execution: %s", run.id, _error_detail, exc_info=True)
            run.status = "error"
            yield _sse({"type": "error", "detail": _error_detail})

    finally:
        full_output = "".join(output_parts)
        duration = round(time.time() - run.started_at, 1)
        if run.status == "error":
            status = "error"
        elif _run_status == "waiting_approval":
            status = "waiting_approval"
        elif _run_status == "rejected":
            status = "rejected"
        else:
            status = "done"
        await _db.finish_run(run.id, full_output, duration, status, error_detail=_error_detail)
        await _db.update_thread(run.thread_id, run.agent, run.model, run.message)
        if status == "waiting_approval":
            return
        if status == "rejected":
            yield _sse({"type": "run_rejected", "thread_id": thread_id, "run_id": run.id})
        else:
            yield _sse({"type": "run_done", "thread_id": thread_id, "run_id": run.id})


# ---------------------------------------------------------------------------
# Thread endpoints
# ---------------------------------------------------------------------------

@app.post("/threads", tags=["threads"])
async def create_thread(
    project_id: str | None = None,
    user: User = Depends(_auth.get_current_user),
):
    if project_id:
        await _auth.require_project_role(project_id, "member", user)
    t = Thread(project_id=project_id)
    await _db.insert_thread(t)
    return t.model_dump()


@app.get("/threads", tags=["threads"])
async def list_threads_endpoint(
    project_id: str | None = None,
    user: User = Depends(_auth.get_current_user),
):
    if project_id:
        await _auth.require_project_role(project_id, "viewer", user)
    threads = await _db.list_threads(project_id=project_id)
    return {"threads": [t.model_dump() for t in threads]}


@app.delete("/threads/{thread_id}", tags=["threads"])
async def delete_thread(
    thread_id: str,
    user: User = Depends(_auth.get_current_user),
):
    await _db.delete_thread(thread_id)
    return {"deleted": thread_id}


@app.get("/threads/{thread_id}/state", tags=["threads"])
async def get_thread_state(thread_id: str, agent: str, is_command: bool = False):
    manifests = load_all(COMMANDS_DIR if is_command else AGENTS_DIR)
    if agent not in manifests:
        raise HTTPException(status_code=404, detail=f"Agent '{agent}' not found")
    category = manifests[agent].get("category", "")
    graph = get_graph(category, is_command)
    config = {"configurable": {"thread_id": thread_id}}
    try:
        state = await graph.aget_state(config)
        return {
            "thread_id": thread_id,
            "values": {k: v for k, v in (state.values or {}).items() if k != "messages"},
            "next": list(state.next),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/threads/{thread_id}/history", tags=["threads"])
async def get_thread_history(thread_id: str, agent: str, is_command: bool = False):
    manifests = load_all(COMMANDS_DIR if is_command else AGENTS_DIR)
    if agent not in manifests:
        raise HTTPException(status_code=404, detail=f"Agent '{agent}' not found")
    category = manifests[agent].get("category", "")
    graph = get_graph(category, is_command)
    config = {"configurable": {"thread_id": thread_id}}
    try:
        checkpoints = []
        async for snapshot in graph.aget_state_history(config):
            checkpoints.append({
                "step": snapshot.metadata.get("step", 0),
                "source": snapshot.metadata.get("source", ""),
                "next": list(snapshot.next),
                "phase": (snapshot.values or {}).get("phase", ""),
            })
        return {"thread_id": thread_id, "checkpoints": checkpoints}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/threads/{thread_id}/runs", tags=["threads"])
async def get_thread_runs(thread_id: str):
    runs = await _db.list_runs(thread_id=thread_id)
    return {"thread_id": thread_id, "runs": [r.model_dump(exclude={"nodes"}) for r in runs]}


# ---------------------------------------------------------------------------
# Real LangGraph graph run endpoint
# ---------------------------------------------------------------------------

@app.post("/graphs/{agent_name}/run", tags=["graphs"])
async def run_graph(
    agent_name: str,
    req: GraphRunRequest,
    user: User = Depends(_auth.get_current_user),
):
    """Run an agent through its real LangGraph graph with SSE streaming."""
    _log.info("graph_run start agent=%s model=%s thread=%s user=%s",
              agent_name, req.model, req.thread_id, user.id)

    if req.project_id:
        await _auth.require_project_role(req.project_id, "member", user)

    is_command = False
    manifests = load_all(AGENTS_DIR)
    if agent_name not in manifests:
        manifests = load_all(COMMANDS_DIR)
        is_command = True
    if agent_name not in manifests:
        _log.warning("graph_run 404 agent=%s", agent_name)
        raise HTTPException(status_code=404, detail=f"Agent or command '{agent_name}' not found")

    manifest = manifests[agent_name]
    category = manifest.get("category", "")
    system = await inject_project_context(
        agent_system_prompt(manifest) if not is_command else command_system_prompt(manifest),
        req.project_path,
    )

    # Ensure thread exists in DB.
    thread_id = req.thread_id or str(uuid.uuid4())
    await _db.insert_thread(Thread(
        id=thread_id,
        project_id=req.project_id,
        agent=agent_name,
        model=req.model,
        last_message=req.message[:200],
    ))

    graph = get_graph(category, is_command)
    graph_node_defs = load_graph_nodes(manifest, is_command)

    # Load per-node configs and pass them so nodes can override the global prompt.
    node_cfgs = await _db.list_node_configs(agent_name)
    node_cfg_map = {nc.node_id: nc.model_dump() for nc in node_cfgs}

    config = {"configurable": {
        "thread_id": thread_id,
        "model": req.model,
        "system_prompt": system,
        "node_configs": node_cfg_map,
    }}
    initial_state = {
        "messages": [HumanMessage(content=req.message)],
        "phase": "",
        "node_output": "",
        "project_context": "",
        "route_to": "",
        "context_trimmed": 0,
        "gate_decision": {},
    }

    run = Run(
        thread_id=thread_id,
        project_id=req.project_id,
        agent=agent_name,
        kind="command" if is_command else "agent",
        model=req.model,
        project_path=req.project_path,
        message=req.message,
        system_prompt=system,
        status="running",
    )
    await _db.insert_run(run)

    return StreamingResponse(
        _langgraph_sse(graph, initial_state, config, thread_id, graph_node_defs, run),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


async def _resume_gate_stream(
    thread_id: str,
    gate_id: str,
    approved: bool,
    body: GateDecisionRequest,
    user: User,
):
    run = await _db.latest_waiting_run(thread_id, gate_id)
    if not run:
        raise HTTPException(
            status_code=404,
            detail=f"No pending approval gate '{gate_id}' found for thread '{thread_id}'",
        )
    if run.project_id:
        await _auth.require_project_role(run.project_id, "member", user)

    manifest, is_command = resolve_manifest(run.agent)
    category = manifest.get("category", "")
    graph = get_graph(category, is_command)
    graph_node_defs = load_graph_nodes(manifest, is_command)
    if gate_id not in {n["id"] for n in graph_node_defs if n.get("type") == "human_approval"}:
        raise HTTPException(status_code=404, detail=f"Gate '{gate_id}' is not part of run agent '{run.agent}'")

    node_cfgs = await _db.list_node_configs(run.agent)
    node_cfg_map = {nc.node_id: nc.model_dump() for nc in node_cfgs}
    config = {"configurable": {
        "thread_id": thread_id,
        "model": run.model,
        "system_prompt": run.system_prompt or "",
        "node_configs": node_cfg_map,
    }}
    decision = {
        "approved": approved,
        "gate_id": gate_id,
        "reason": body.reason or "",
        "reviewer": user.email,
        "decided_at": time.time(),
    }
    return StreamingResponse(
        _langgraph_sse(graph, Command(resume=decision), config, thread_id, graph_node_defs, run),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.post("/threads/{thread_id}/gates/{gate_id}/approve", tags=["graphs"])
async def approve_gate(
    thread_id: str,
    gate_id: str,
    body: GateDecisionRequest | None = None,
    user: User = Depends(_auth.get_current_user),
):
    """Approve a pending LangGraph interrupt gate and resume the same thread checkpoint."""
    return await _resume_gate_stream(thread_id, gate_id, True, body or GateDecisionRequest(), user)


@app.post("/threads/{thread_id}/gates/{gate_id}/reject", tags=["graphs"])
async def reject_gate(
    thread_id: str,
    gate_id: str,
    body: GateDecisionRequest | None = None,
    user: User = Depends(_auth.get_current_user),
):
    """Reject a pending LangGraph interrupt gate and cancel downstream execution."""
    return await _resume_gate_stream(thread_id, gate_id, False, body or GateDecisionRequest(), user)


# ---------------------------------------------------------------------------
# Node configuration endpoints
# ---------------------------------------------------------------------------

class NodeConfigBody(BaseModel):
    label: str | None = None
    system_prompt: str | None = None
    routing_rules: list[dict] = Field(default_factory=list)
    classification_labels: list[str] = Field(default_factory=list)
    notes: str | None = None


@app.get("/agents/{agent_name}/nodes/configs", tags=["node-config"])
async def list_agent_node_configs(agent_name: str):
    """Return all saved node configurations for an agent."""
    configs = await _db.list_node_configs(agent_name)
    return {"agent": agent_name, "configs": [c.model_dump() for c in configs]}


@app.get("/agents/{agent_name}/nodes/{node_id}/config", tags=["node-config"])
async def get_agent_node_config(agent_name: str, node_id: str):
    """Return the saved config for one node, or 404 if not yet configured."""
    nc = await _db.get_node_config(agent_name, node_id)
    if not nc:
        raise HTTPException(status_code=404, detail="No config saved for this node yet")
    return nc.model_dump()


@app.put("/agents/{agent_name}/nodes/{node_id}/config", tags=["node-config"])
async def save_agent_node_config(agent_name: str, node_id: str, body: NodeConfigBody):
    """Create or update the configuration for a specific node."""
    import time as _time
    nc = NodeConfig(
        agent_name=agent_name,
        node_id=node_id,
        label=body.label,
        system_prompt=body.system_prompt,
        routing_rules=[RoutingRule(**r) for r in body.routing_rules],
        classification_labels=body.classification_labels,
        notes=body.notes,
        updated_at=_time.time(),
    )
    saved = await _db.upsert_node_config(nc)
    return saved.model_dump()


@app.delete("/agents/{agent_name}/nodes/{node_id}/config", tags=["node-config"])
async def delete_agent_node_config(agent_name: str, node_id: str):
    await _db.delete_node_config(agent_name, node_id)
    return {"deleted": node_id}


# ---------------------------------------------------------------------------
# Auth endpoints (OIDC Authorization Code flow)
# ---------------------------------------------------------------------------

@app.get("/auth/login", tags=["auth"], include_in_schema=_auth.AUTH_ENABLED)
async def auth_login():
    """Redirect browser to OIDC provider for login."""
    if not _auth.AUTH_ENABLED:
        raise HTTPException(status_code=400, detail="Auth is disabled (AUTH_ENABLED=false)")
    url = await _auth.oidc_login_url()
    return RedirectResponse(url)


@app.get("/auth/callback", tags=["auth"], include_in_schema=_auth.AUTH_ENABLED)
async def auth_callback(code: str, state: str):
    """Handle OIDC provider callback, issue session token, redirect to UI."""
    if not _auth.AUTH_ENABLED:
        raise HTTPException(status_code=400, detail="Auth is disabled")
    user, session_jwt = await _auth.oidc_callback(code, state)
    return RedirectResponse(f"/ui#token={session_jwt}")


@app.get("/auth/me", tags=["auth"])
async def auth_me(user: User = Depends(_auth.get_current_user)):
    return user.model_dump(exclude={"created_at"})


@app.post("/auth/logout", tags=["auth"])
async def auth_logout():
    """Client-side: discard the session JWT. Server has no session state to clear."""
    return {"detail": "Logged out — discard your session token"}


# ---------------------------------------------------------------------------
# Org endpoints
# ---------------------------------------------------------------------------

class OrgCreate(BaseModel):
    name: str
    slug: str


@app.post("/orgs", tags=["orgs"])
async def create_org(
    body: OrgCreate,
    user: User = Depends(_auth.get_current_user),
):
    org = await _db.insert_org(Org(name=body.name, slug=body.slug))
    # Creator gets admin role.
    await _db.upsert_membership(
        Membership(scope_type="org", scope_id=org.id, user_id=user.id, role="admin")
    )
    return org.model_dump()


@app.get("/orgs", tags=["orgs"])
async def list_orgs(user: User = Depends(_auth.get_current_user)):
    orgs = await _db.list_orgs(user.id)
    return {"orgs": [o.model_dump() for o in orgs]}


@app.get("/orgs/{org_id}", tags=["orgs"])
async def get_org(org_id: str, user: User = Depends(_auth.get_current_user)):
    await _auth.require_org_role(org_id, "viewer", user)
    org = await _db.get_org(org_id)
    if not org:
        raise HTTPException(404, "Org not found")
    return org.model_dump()


@app.delete("/orgs/{org_id}", tags=["orgs"])
async def delete_org(org_id: str, user: User = Depends(_auth.get_current_user)):
    await _auth.require_org_role(org_id, "admin", user)
    await _db.delete_org(org_id)
    return {"deleted": org_id}


@app.get("/orgs/{org_id}/members", tags=["orgs"])
async def list_org_members(org_id: str, user: User = Depends(_auth.get_current_user)):
    await _auth.require_org_role(org_id, "viewer", user)
    return {"members": await _db.list_members("org", org_id)}


class MemberAdd(BaseModel):
    user_id: str
    role: str = "member"


@app.post("/orgs/{org_id}/members", tags=["orgs"])
async def add_org_member(
    org_id: str,
    body: MemberAdd,
    user: User = Depends(_auth.get_current_user),
):
    await _auth.require_org_role(org_id, "admin", user)
    m = await _db.upsert_membership(
        Membership(scope_type="org", scope_id=org_id, user_id=body.user_id, role=body.role)
    )
    return m.model_dump()


@app.delete("/orgs/{org_id}/members/{user_id}", tags=["orgs"])
async def remove_org_member(
    org_id: str,
    user_id: str,
    user: User = Depends(_auth.get_current_user),
):
    await _auth.require_org_role(org_id, "admin", user)
    await _db.delete_membership("org", org_id, user_id)
    return {"removed": user_id}


# ---------------------------------------------------------------------------
# Team endpoints
# ---------------------------------------------------------------------------

class TeamCreate(BaseModel):
    name: str
    slug: str


@app.post("/orgs/{org_id}/teams", tags=["teams"])
async def create_team(
    org_id: str,
    body: TeamCreate,
    user: User = Depends(_auth.get_current_user),
):
    await _auth.require_org_role(org_id, "member", user)
    team = await _db.insert_team(Team(org_id=org_id, name=body.name, slug=body.slug))
    await _db.upsert_membership(
        Membership(scope_type="team", scope_id=team.id, user_id=user.id, role="admin")
    )
    return team.model_dump()


@app.get("/orgs/{org_id}/teams", tags=["teams"])
async def list_teams(org_id: str, user: User = Depends(_auth.get_current_user)):
    await _auth.require_org_role(org_id, "viewer", user)
    teams = await _db.list_teams(org_id)
    return {"teams": [t.model_dump() for t in teams]}


@app.delete("/orgs/{org_id}/teams/{team_id}", tags=["teams"])
async def delete_team(
    org_id: str,
    team_id: str,
    user: User = Depends(_auth.get_current_user),
):
    await _auth.require_team_role(team_id, "admin", user)
    await _db.delete_team(team_id)
    return {"deleted": team_id}


@app.get("/teams/{team_id}/members", tags=["teams"])
async def list_team_members(team_id: str, user: User = Depends(_auth.get_current_user)):
    await _auth.require_team_role(team_id, "viewer", user)
    return {"members": await _db.list_members("team", team_id)}


@app.post("/teams/{team_id}/members", tags=["teams"])
async def add_team_member(
    team_id: str,
    body: MemberAdd,
    user: User = Depends(_auth.get_current_user),
):
    await _auth.require_team_role(team_id, "admin", user)
    m = await _db.upsert_membership(
        Membership(scope_type="team", scope_id=team_id, user_id=body.user_id, role=body.role)
    )
    return m.model_dump()


@app.delete("/teams/{team_id}/members/{user_id}", tags=["teams"])
async def remove_team_member(
    team_id: str,
    user_id: str,
    user: User = Depends(_auth.get_current_user),
):
    await _auth.require_team_role(team_id, "admin", user)
    await _db.delete_membership("team", team_id, user_id)
    return {"removed": user_id}


# ---------------------------------------------------------------------------
# Project endpoints
# ---------------------------------------------------------------------------

class ProjectCreate(BaseModel):
    name: str
    slug: str
    description: str | None = None


@app.post("/teams/{team_id}/projects", tags=["projects"])
async def create_project(
    team_id: str,
    body: ProjectCreate,
    user: User = Depends(_auth.get_current_user),
):
    await _auth.require_team_role(team_id, "member", user)
    team = await _db.get_team(team_id)
    if not team:
        raise HTTPException(404, "Team not found")
    project = await _db.insert_project(Project(
        team_id=team_id,
        org_id=team.org_id,
        name=body.name,
        slug=body.slug,
        description=body.description,
    ))
    await _db.upsert_membership(
        Membership(scope_type="project", scope_id=project.id, user_id=user.id, role="owner")
    )
    return project.model_dump()


@app.get("/teams/{team_id}/projects", tags=["projects"])
async def list_projects(team_id: str, user: User = Depends(_auth.get_current_user)):
    await _auth.require_team_role(team_id, "viewer", user)
    projects = await _db.list_projects(team_id)
    return {"projects": [p.model_dump() for p in projects]}


@app.get("/projects/{project_id}", tags=["projects"])
async def get_project(project_id: str, user: User = Depends(_auth.get_current_user)):
    await _auth.require_project_role(project_id, "viewer", user)
    p = await _db.get_project(project_id)
    if not p:
        raise HTTPException(404, "Project not found")
    return p.model_dump()


@app.delete("/projects/{project_id}", tags=["projects"])
async def delete_project(project_id: str, user: User = Depends(_auth.get_current_user)):
    await _auth.require_project_role(project_id, "owner", user)
    await _db.delete_project(project_id)
    return {"deleted": project_id}


@app.get("/projects/{project_id}/members", tags=["projects"])
async def list_project_members(
    project_id: str,
    user: User = Depends(_auth.get_current_user),
):
    await _auth.require_project_role(project_id, "viewer", user)
    return {"members": await _db.list_members("project", project_id)}


@app.post("/projects/{project_id}/members", tags=["projects"])
async def add_project_member(
    project_id: str,
    body: MemberAdd,
    user: User = Depends(_auth.get_current_user),
):
    await _auth.require_project_role(project_id, "owner", user)
    m = await _db.upsert_membership(
        Membership(scope_type="project", scope_id=project_id, user_id=body.user_id, role=body.role)
    )
    return m.model_dump()


@app.delete("/projects/{project_id}/members/{user_id}", tags=["projects"])
async def remove_project_member(
    project_id: str,
    user_id: str,
    user: User = Depends(_auth.get_current_user),
):
    await _auth.require_project_role(project_id, "owner", user)
    await _db.delete_membership("project", project_id, user_id)
    return {"removed": user_id}


# ---------------------------------------------------------------------------
# Project context preview endpoint
# ---------------------------------------------------------------------------

@app.get("/browse", tags=["meta"])
def browse_local():
    """Open a native OS folder picker and return the selected path (macOS only)."""
    if sys.platform != "darwin":
        raise HTTPException(status_code=501, detail="Native folder browser only supported on macOS")
    try:
        result = subprocess.run(
            ["osascript",
             "-e", 'choose folder with prompt "Select project directory"',
             "-e", "POSIX path of result"],
            capture_output=True, text=True, timeout=60,
        )
        if result.returncode != 0:
            raise HTTPException(status_code=400, detail="No folder selected")
        return {"path": result.stdout.strip()}
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="Folder picker timed out")
    except FileNotFoundError:
        raise HTTPException(status_code=501, detail="osascript not available")


@app.get("/project/context", tags=["meta"])
async def preview_project_context(path: str):
    """Preview what project context will be sent to the agent. Accepts local paths or git URLs."""
    if is_remote_url(path):
        try:
            ctx, included = await gather_remote_context(path)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        return {
            "path": path,
            "files_included": included,
            "remote": True,
            "context_chars": len(ctx),
        }
    p = Path(path).expanduser().resolve()
    if not p.exists():
        raise HTTPException(status_code=404, detail=f"Path does not exist: {path}")
    if not p.is_dir():
        raise HTTPException(status_code=400, detail=f"Not a directory: {path}")
    ctx, included = gather_project_context(p)
    return {
        "path": str(p),
        "files_included": included,
        "remote": False,
        "tree": "\n".join(_tree_lines(p)),
        "context_chars": len(ctx),
    }


# ---------------------------------------------------------------------------
# Run history endpoints
# ---------------------------------------------------------------------------

@app.get("/runs", tags=["meta"])
async def list_runs_endpoint(
    project_id: str | None = None,
    user: User = Depends(_auth.get_current_user),
):
    """Return the last 50 completed runs (without full output)."""
    if project_id:
        await _auth.require_project_role(project_id, "viewer", user)
    runs = await _db.list_runs(project_id=project_id)
    return {"runs": [r.model_dump(exclude={"nodes", "output", "system_prompt"}) for r in runs]}


@app.get("/runs/{run_id}", tags=["meta"])
async def get_run_endpoint(
    run_id: str,
    user: User = Depends(_auth.get_current_user),
):
    """Return a single run including full output and per-node state."""
    r = await _db.get_run(run_id)
    if not r:
        raise HTTPException(status_code=404, detail="Run not found")
    if r.project_id:
        await _auth.require_project_role(r.project_id, "viewer", user)
    return r.model_dump()


@app.get("/runs/{run_id}/nodes", tags=["meta"])
async def get_run_nodes(
    run_id: str,
    user: User = Depends(_auth.get_current_user),
):
    """Return per-node execution records for a run."""
    r = await _db.get_run(run_id)
    if not r:
        raise HTTPException(status_code=404, detail="Run not found")
    if r.project_id:
        await _auth.require_project_role(r.project_id, "viewer", user)
    nodes = await _db.list_run_nodes(run_id)
    return {"run_id": run_id, "nodes": [n.model_dump() for n in nodes]}


@app.post("/runs/{run_id}/cancel", tags=["meta"])
async def cancel_run_endpoint(
    run_id: str,
    body: RunCancelRequest | None = None,
    user: User = Depends(_auth.get_current_user),
):
    """Cancel a running or approval-waiting run and close pending node records."""
    r = await _db.get_run(run_id)
    if not r:
        raise HTTPException(status_code=404, detail="Run not found")
    if r.project_id:
        await _auth.require_project_role(r.project_id, "member", user)
    if r.status not in ("running", "waiting_approval"):
        return {"run": r.model_dump(), "cancelled": False, "message": f"Run is already {r.status}"}
    updated = await _db.cancel_run(run_id, (body.reason if body else None) or f"Cancelled by {user.email}")
    return {"run": updated.model_dump() if updated else None, "cancelled": True}


# ---------------------------------------------------------------------------
# Portal (home) + UI + static docs assets
# ---------------------------------------------------------------------------

@app.get("/", include_in_schema=False)
@app.get("/index.html", include_in_schema=False)
def serve_portal():
    if not PORTAL_FILE.exists():
        raise HTTPException(status_code=404, detail="docs/index.html not found")
    return FileResponse(PORTAL_FILE, media_type="text/html")


@app.get("/assets/{filename:path}", include_in_schema=False)
def serve_docs_asset(filename: str):
    p = DOCS_DIR / "assets" / filename
    if not p.exists() or not p.is_file():
        raise HTTPException(status_code=404, detail=f"Asset not found: {filename}")
    return FileResponse(p)


@app.get("/reference/{path:path}", include_in_schema=False)
def serve_reference(path: str):
    p = DOCS_DIR / "reference" / path
    if not p.exists() or not p.is_file():
        raise HTTPException(status_code=404, detail=f"Not found: {path}")
    return FileResponse(p)


@app.get("/ui", include_in_schema=False)
def serve_ui():
    if not UI_FILE.exists():
        raise HTTPException(status_code=404, detail="ui.html not found — run from the repo root")
    return FileResponse(UI_FILE, media_type="text/html")


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/queue/status", tags=["meta"])
async def queue_status():
    """Live Ollama queue stats — active calls, waiters, average wait time."""
    return ollama_queue.stats()


@app.post("/queue/reset", tags=["meta"])
async def reset_queue(
    body: RunCancelRequest | None = None,
    user: User = Depends(_auth.get_current_user),
):
    """Reset stale in-memory Ollama queue counters without touching persisted runs."""
    reason = (body.reason if body else None) or f"Manual queue reset by {user.email}"
    return ollama_queue.reset_stale(reason)


@app.get("/health", tags=["meta"])
async def health():
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(f"{OLLAMA_BASE}/api/tags")
            models = [m["name"] for m in r.json().get("models", [])]
            ollama_ok = True
    except Exception:
        models = []
        ollama_ok = False
    return {
        "status": "ok",
        "ollama": ollama_ok,
        "ollama_url": OLLAMA_BASE,
        "available_models": models,
        "agents": len(list(AGENTS_DIR.glob("*.json"))),
        "commands": len(list(COMMANDS_DIR.glob("*.json"))),
    }


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------

@app.get("/agents", tags=["agents"])
def list_agents():
    return {
        "agents": [
            {"name": v["name"], "description": v["description"], "category": v.get("category")}
            for v in load_all(AGENTS_DIR).values()
        ]
    }


@app.get("/agents/{name}", tags=["agents"])
def get_agent(name: str):
    agents = load_all(AGENTS_DIR)
    if name not in agents:
        raise HTTPException(status_code=404, detail=f"Agent '{name}' not found")
    m = agents[name]
    return {
        "name": m["name"],
        "description": m["description"],
        "category": m.get("category"),
        "source": m.get("source"),
        "system_prompt": agent_system_prompt(m),
    }


@app.post("/agents/{name}/invoke", tags=["agents"])
async def invoke_agent(name: str, req: InvokeRequest):
    agents = load_all(AGENTS_DIR)
    if name not in agents:
        raise HTTPException(status_code=404, detail=f"Agent '{name}' not found")
    system = await inject_project_context(agent_system_prompt(agents[name]), req.project_path)
    if req.stream:
        return StreamingResponse(
            _ollama_stream(req.model, system, req.history, req.message),
            media_type="text/plain",
        )
    response = await _ollama_invoke(req.model, system, req.history, req.message)
    return InvokeResponse(response=response, name=name, model=req.model)


@app.post("/agents/{name}/invoke/trace", tags=["agents"])
async def invoke_agent_trace(name: str, req: InvokeRequest):
    """Graph-traced invocation: SSE stream showing live LangGraph node progression."""
    agents = load_all(AGENTS_DIR)
    if name not in agents:
        raise HTTPException(status_code=404, detail=f"Agent '{name}' not found")
    manifest = agents[name]
    system = await inject_project_context(agent_system_prompt(manifest), req.project_path)
    nodes = req.custom_nodes or load_graph_nodes(manifest, is_command=False)
    run_meta = {
        "id": str(uuid.uuid4()),
        "started_at": time.time(),
        "agent": name,
        "kind": "agent",
        "model": req.model,
        "project_path": req.project_path,
        "message": req.message,
        "output": "",
        "status": "running",
        "duration_s": 0,
    }
    return StreamingResponse(
        _traced_with_history(_graph_trace_stream(system, nodes, req.model, req.message), run_meta),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

@app.get("/commands", tags=["commands"])
def list_commands():
    return {
        "commands": [
            {"name": v["name"], "description": v["description"], "category": v.get("category")}
            for v in load_all(COMMANDS_DIR).values()
        ]
    }


@app.get("/commands/{name}", tags=["commands"])
def get_command(name: str):
    commands = load_all(COMMANDS_DIR)
    if name not in commands:
        raise HTTPException(status_code=404, detail=f"Command '{name}' not found")
    m = commands[name]
    return {
        "name": m["name"],
        "description": m["description"],
        "category": m.get("category"),
        "source": m.get("source"),
        "system_prompt": command_system_prompt(m),
    }


@app.post("/commands/{name}/invoke", tags=["commands"])
async def invoke_command(name: str, req: InvokeRequest):
    commands = load_all(COMMANDS_DIR)
    if name not in commands:
        raise HTTPException(status_code=404, detail=f"Command '{name}' not found")
    system = await inject_project_context(command_system_prompt(commands[name]), req.project_path)
    if req.stream:
        return StreamingResponse(
            _ollama_stream(req.model, system, req.history, req.message),
            media_type="text/plain",
        )
    response = await _ollama_invoke(req.model, system, req.history, req.message)
    return InvokeResponse(response=response, name=name, model=req.model)


@app.post("/commands/{name}/invoke/trace", tags=["commands"])
async def invoke_command_trace(name: str, req: InvokeRequest):
    """Graph-traced command invocation."""
    commands = load_all(COMMANDS_DIR)
    if name not in commands:
        raise HTTPException(status_code=404, detail=f"Command '{name}' not found")
    manifest = commands[name]
    system = await inject_project_context(command_system_prompt(manifest), req.project_path)
    nodes = req.custom_nodes or load_graph_nodes(manifest, is_command=True)
    run_meta = {
        "id": str(uuid.uuid4()),
        "started_at": time.time(),
        "agent": name,
        "kind": "command",
        "model": req.model,
        "project_path": req.project_path,
        "message": req.message,
        "output": "",
        "status": "running",
        "duration_s": 0,
    }
    return StreamingResponse(
        _traced_with_history(_graph_trace_stream(system, nodes, req.model, req.message), run_meta),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
