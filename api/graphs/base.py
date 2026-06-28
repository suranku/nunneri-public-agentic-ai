"""Shared state, checkpointer, and Ollama node factory for all LangGraph graphs."""
from __future__ import annotations

import os
import re
from typing import Annotated, Any, TypedDict

import httpx
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph.message import add_messages
from langgraph.types import interrupt

import ollama_queue

OLLAMA_BASE = "http://localhost:11434"

# Maximum estimated tokens to send to Ollama per call.
# Rough estimate: 1 token ≈ 4 chars. 6000 tokens ≈ 24 KB of text.
MAX_CONTEXT_TOKENS: int = int(os.environ.get("OLLAMA_MAX_CONTEXT_TOKENS", "6000"))

# Set by main.py lifespan via the AsyncPostgresSaver context manager.
checkpointer = None


# ---------------------------------------------------------------------------
# Message trimming — keeps context within model limits
# ---------------------------------------------------------------------------

def _est_tokens(m: BaseMessage) -> int:
    """Rough token estimate: 1 token per 4 characters, minimum 1."""
    return max(1, len(str(m.content)) // 4)


def trim_messages(
    messages: list[BaseMessage],
    max_tokens: int = MAX_CONTEXT_TOKENS,
) -> tuple[list[BaseMessage], int]:
    """Trim message history to fit within max_tokens.

    Strategy:
    - Always keep the first message (original user intent as anchor).
    - Fill backwards from the most recent message until the budget runs out.
    - Insert a synthetic notice if any messages were dropped.

    Returns (trimmed_messages, n_dropped).
    """
    if not messages:
        return messages, 0

    anchor = messages[0]
    rest = messages[1:]

    budget = max_tokens - _est_tokens(anchor)
    kept: list[BaseMessage] = []
    for m in reversed(rest):
        cost = _est_tokens(m)
        if budget - cost < 0:
            break
        kept.insert(0, m)
        budget -= cost

    dropped = len(rest) - len(kept)
    if dropped > 0:
        notice = HumanMessage(
            content=f"[{dropped} earlier message(s) trimmed — context window limit reached]"
        )
        return [anchor, notice] + kept, dropped
    return [anchor] + kept, 0


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    phase: str
    node_output: str
    project_context: str
    route_to: str       # set by a node when a routing rule matches; "" = follow default edges
    context_trimmed: int  # number of messages dropped in last Ollama call
    gate_decision: dict[str, Any]


# ---------------------------------------------------------------------------
# Routing rule evaluation
# ---------------------------------------------------------------------------

def evaluate_routing_rules(text: str, rules: list[dict]) -> str | None:
    """Match routing rules against node output text. Returns target node_id or None."""
    for rule in sorted(rules, key=lambda r: r.get("priority", 0)):
        cond = rule.get("condition", "contains")
        val = rule.get("value", "")
        target = rule.get("target_node", "").strip()
        if not target:
            continue
        t = text.lower()
        v = val.lower()
        if cond == "always":
            return target
        elif cond == "contains" and v and v in t:
            return target
        elif cond == "starts_with" and v and t.startswith(v):
            return target
        elif cond == "ends_with" and v and t.endswith(v):
            return target
        elif cond == "regex" and val:
            try:
                if re.search(val, text, re.IGNORECASE):
                    return target
            except re.error:
                pass
    return None


# ---------------------------------------------------------------------------
# Ollama call — queue-aware, context-trimmed
# ---------------------------------------------------------------------------

async def _call_ollama(
    model: str, system: str, messages: list[BaseMessage]
) -> tuple[str, int]:
    """Call Ollama. Returns (response_text, messages_dropped_count)."""
    trimmed, dropped = trim_messages(messages)

    ollama_msgs = [{"role": "system", "content": system}]
    for m in trimmed:
        role = "user" if isinstance(m, HumanMessage) else "assistant"
        ollama_msgs.append({"role": role, "content": str(m.content)})

    async with ollama_queue.slot():
        async with httpx.AsyncClient(timeout=120.0) as client:
            r = await client.post(
                f"{OLLAMA_BASE}/api/chat",
                json={"model": model, "messages": ollama_msgs, "stream": False},
            )
            r.raise_for_status()
            return r.json()["message"]["content"], dropped


# ---------------------------------------------------------------------------
# Node factories
# ---------------------------------------------------------------------------

def make_ollama_node(node_id: str, phase_label: str):
    """Return an async node function that calls Ollama for the given phase."""
    async def _node(state: AgentState, config: RunnableConfig) -> dict:
        cfg = config.get("configurable", {})
        model = cfg.get("model", "mistral")
        base_system = cfg.get("system_prompt", "")
        ctx = state.get("project_context", "")

        # Per-node config overrides the global agent system prompt when set.
        node_cfgs: dict = cfg.get("node_configs", {})
        node_cfg: dict = node_cfgs.get(node_id, {})
        if node_cfg.get("system_prompt"):
            base_system = node_cfg["system_prompt"]

        system = (f"{ctx}\n\n---\n\n{base_system}" if ctx else base_system)
        system += f"\n\n## Current Phase: {phase_label}"

        labels: list = node_cfg.get("classification_labels", [])
        if labels:
            system += (
                "\n\n## Output Classification\n"
                "Your response must classify into one of: " + ", ".join(labels)
            )

        text, dropped = await _call_ollama(model, system, state["messages"])

        # Evaluate routing rules against this node's output.
        rules: list = node_cfg.get("routing_rules", [])
        matched_route = evaluate_routing_rules(text, rules) if rules else None

        return {
            "messages": [AIMessage(content=text)],
            "phase": node_id,
            "node_output": text,
            "route_to": matched_route or "",
            "context_trimmed": dropped,
        }
    _node.__name__ = node_id
    return _node


def make_gate_node(node_id: str):
    """Pause graph execution until an explicit human approval decision resumes it."""
    async def _gate(state: AgentState, config: RunnableConfig) -> dict:
        payload = {
            "type": "approval_gate",
            "gate_id": node_id,
            "question": f"Approve {node_id.replace('_', ' ')} and continue?",
            "phase": state.get("phase", ""),
            "node_output": state.get("node_output", ""),
            "allowed_actions": ["approve", "reject"],
        }
        decision = interrupt(payload)
        if not isinstance(decision, dict):
            decision = {"approved": bool(decision)}

        approved = bool(decision.get("approved"))
        return {
            "phase": node_id,
            "node_output": "[approved]" if approved else "[rejected]",
            "route_to": "" if approved else "__cancelled__",
            "context_trimmed": 0,
            "gate_decision": {
                "gate_id": node_id,
                "approved": approved,
                "reason": decision.get("reason", ""),
                "reviewer": decision.get("reviewer", ""),
                "decided_at": decision.get("decided_at", ""),
            },
        }
    _gate.__name__ = node_id
    return _gate


async def cancelled_node(state: AgentState, config: RunnableConfig) -> dict:
    """Terminal node used when a human rejects an approval gate."""
    return {
        "phase": "cancelled",
        "node_output": "[cancelled by human approval gate]",
        "route_to": "__cancelled__",
        "context_trimmed": 0,
    }


def route_after_gate(next_node: str):
    """Return a conditional-edge selector for a gate node."""
    def _route(state: AgentState) -> str:
        if state.get("route_to") == "__cancelled__":
            return "__cancelled__"
        return next_node
    return _route
