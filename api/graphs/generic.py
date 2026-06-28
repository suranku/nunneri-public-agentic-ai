"""Generic 4-node agent graph and 3-node command graph."""
from __future__ import annotations

from langgraph.graph import END, StateGraph

from . import base as _base
from .base import AgentState, cancelled_node, make_gate_node, make_ollama_node, route_after_gate

_AGENT_NODES = [
    {"id": "intake",    "label": "Intake",    "type": "work"},
    {"id": "analysis",  "label": "Analysis",  "type": "work"},
    {"id": "gate_1",    "label": "Review Gate", "type": "human_approval"},
    {"id": "output",    "label": "Output",    "type": "work"},
]

_COMMAND_NODES = [
    {"id": "dispatch",  "label": "Dispatch",  "type": "work"},
    {"id": "execute",   "label": "Execute",   "type": "work"},
    {"id": "summarize", "label": "Summarize", "type": "work"},
]


def _build_from_nodes(node_list: list[dict]):
    builder = StateGraph(AgentState)
    for n in node_list:
        if n["type"] == "work":
            builder.add_node(n["id"], make_ollama_node(n["id"], n["label"]))
        else:
            builder.add_node(n["id"], make_gate_node(n["id"]))
    builder.add_node("__cancelled__", cancelled_node)

    builder.set_entry_point(node_list[0]["id"])
    for i in range(len(node_list) - 1):
        current = node_list[i]
        nxt = node_list[i + 1]["id"]
        if current["type"] == "human_approval":
            builder.add_conditional_edges(
                current["id"],
                route_after_gate(nxt),
                {nxt: nxt, "__cancelled__": "__cancelled__"},
            )
        else:
            builder.add_edge(current["id"], nxt)
    builder.add_edge(node_list[-1]["id"], END)
    builder.add_edge("__cancelled__", END)

    return builder.compile(checkpointer=_base.checkpointer)


def build_generic_agent_graph():
    return _build_from_nodes(_AGENT_NODES)


def build_generic_command_graph():
    return _build_from_nodes(_COMMAND_NODES)
