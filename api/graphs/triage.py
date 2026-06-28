"""Nine-phase triage LangGraph built from triage-nine-phase.json."""
from __future__ import annotations

import json
from pathlib import Path

from langgraph.graph import END, StateGraph

from . import base as _base
from .base import AgentState, cancelled_node, make_gate_node, make_ollama_node, route_after_gate

_GRAPH_JSON = Path(__file__).resolve().parents[2] / "dist/langgraph/graphs/triage-nine-phase.json"


def build_triage_graph():
    data = json.loads(_GRAPH_JSON.read_text(encoding="utf-8"))
    nodes = data["nodes"]
    edges = data["edges"]

    builder = StateGraph(AgentState)
    for n in nodes:
        ntype = n.get("type", "work")
        if ntype == "work":
            builder.add_node(n["id"], make_ollama_node(n["id"], n["label"]))
        else:
            builder.add_node(n["id"], make_gate_node(n["id"]))
    builder.add_node("__cancelled__", cancelled_node)

    first_node = nodes[0]["id"]
    builder.set_entry_point(first_node)

    node_ids = {n["id"] for n in nodes}
    gate_edges: dict[str, str] = {}
    for edge in edges:
        src, dst = edge["from"], edge["to"]
        src_node = next((n for n in nodes if n["id"] == src), {})
        if src_node.get("type") == "human_approval":
            gate_edges[src] = dst
            continue
        if src in node_ids and dst in node_ids:
            builder.add_edge(src, dst)

    for gate_id, next_node in gate_edges.items():
        builder.add_conditional_edges(
            gate_id,
            route_after_gate(next_node),
            {next_node: next_node, "__cancelled__": "__cancelled__"},
        )

    last_node = nodes[-1]["id"]
    builder.add_edge(last_node, END)
    builder.add_edge("__cancelled__", END)

    return builder.compile(checkpointer=_base.checkpointer)
