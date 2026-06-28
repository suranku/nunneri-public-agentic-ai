"""Ollama concurrency queue — limits simultaneous LLM calls and tracks fairness.

Configuration via environment variables:
  OLLAMA_MAX_CONCURRENT  — max parallel Ollama calls (default: 2)
  OLLAMA_QUEUE_TIMEOUT_S — seconds to wait before giving up (default: 300)
"""
from __future__ import annotations

import asyncio
import os
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass, field

MAX_CONCURRENT: int = int(os.environ.get("OLLAMA_MAX_CONCURRENT", "2"))
QUEUE_TIMEOUT_S: float = float(os.environ.get("OLLAMA_QUEUE_TIMEOUT_S", "300"))

# ---------------------------------------------------------------------------
# Internal state — all mutations are protected by asyncio (single event loop)
# ---------------------------------------------------------------------------

_sem: asyncio.Semaphore | None = None   # initialised on first use (or explicitly)
_active: int = 0
_waiting: int = 0
_total_queued: int = 0      # monotonic counter: total calls ever queued
_total_completed: int = 0   # monotonic counter: total calls ever completed
_wait_times: list[float] = []   # rolling window of recent wait durations (last 50)


def _get_sem() -> asyncio.Semaphore:
    global _sem
    if _sem is None:
        _sem = asyncio.Semaphore(MAX_CONCURRENT)
    return _sem


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def stats() -> dict:
    """Snapshot of queue state — safe to call from any async context."""
    avg_wait = sum(_wait_times) / len(_wait_times) if _wait_times else 0.0
    return {
        "active": _active,
        "waiting": _waiting,
        "max_concurrent": MAX_CONCURRENT,
        "queue_depth": _waiting,        # alias used by UI
        "avg_wait_s": round(avg_wait, 1),
        "total_queued": _total_queued,
        "total_completed": _total_completed,
    }


@asynccontextmanager
async def slot(timeout: float = QUEUE_TIMEOUT_S):
    """Async context manager: acquire an Ollama slot, yield, release.

    Raises asyncio.TimeoutError if the wait exceeds `timeout` seconds.

    Usage:
        async with ollama_queue.slot():
            result = await call_ollama(...)
    """
    global _active, _waiting, _total_queued, _total_completed

    _waiting += 1
    _total_queued += 1
    enqueued_at = time.monotonic()

    try:
        await asyncio.wait_for(_get_sem().acquire(), timeout=timeout)
    except asyncio.TimeoutError:
        _waiting -= 1
        raise asyncio.TimeoutError(
            f"Ollama queue timeout after {timeout:.0f}s "
            f"({_waiting} still waiting, {_active} active)"
        )

    _waiting -= 1
    _active += 1
    wait_s = time.monotonic() - enqueued_at
    _wait_times.append(wait_s)
    if len(_wait_times) > 50:
        _wait_times.pop(0)

    try:
        yield wait_s   # caller can use actual wait time for logging / SSE
    finally:
        _active -= 1
        _total_completed += 1
        _get_sem().release()


def queue_position() -> int:
    """Approximate position a new caller would be at if it joined right now."""
    return _waiting + 1 if _waiting > 0 or _active >= MAX_CONCURRENT else 0
