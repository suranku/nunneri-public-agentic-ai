"""Graph registry: lazily builds and caches compiled LangGraph instances."""
from __future__ import annotations

from .generic import build_generic_agent_graph, build_generic_command_graph
from .triage import build_triage_graph

_cache: dict[str, object] = {}


def get_graph(category: str, is_command: bool):
    key = f"{category}:{'cmd' if is_command else 'agent'}"
    if key not in _cache:
        if is_command:
            _cache[key] = build_generic_command_graph()
        elif category == "triage":
            _cache[key] = build_triage_graph()
        else:
            _cache[key] = build_generic_agent_graph()
    return _cache[key]
