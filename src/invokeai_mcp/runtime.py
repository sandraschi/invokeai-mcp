"""Shared runtime state: InvokeAI client singleton + ring-buffer log."""

from __future__ import annotations

import logging
import threading
import time
from collections import deque
from typing import Any

from invokeai_mcp.client import InvokeAIClient
from invokeai_mcp.config import Settings

_client: InvokeAIClient | None = None
_client_lock = threading.Lock()
_settings: Settings | None = None

_RING_MAX = 500
_ring: deque[dict[str, Any]] = deque(maxlen=_RING_MAX)
_ring_lock = threading.Lock()


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def get_client() -> InvokeAIClient:
    global _client
    with _client_lock:
        if _client is None:
            _client = InvokeAIClient(get_settings())
        return _client


async def close_client() -> None:
    global _client
    with _client_lock:
        if _client is not None:
            await _client.close()
            _client = None


def log(level: str, source: str, message: str) -> None:
    """Append to the ring buffer (for /api/logs) and stderr."""
    entry = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "level": level.upper(),
        "source": source,
        "message": message,
    }
    with _ring_lock:
        _ring.append(entry)
    getattr(logging.getLogger(source), level.lower(), logging.info)(message)


def query_logs(
    *,
    source: str | None = None,
    level: str | None = None,
    search: str | None = None,
    limit: int = 50,
) -> tuple[list[dict[str, Any]], int]:
    with _ring_lock:
        entries = list(_ring)
    if source:
        entries = [e for e in entries if e["source"] == source]
    if level:
        entries = [e for e in entries if e["level"] == level.upper()]
    if search:
        needle = search.lower()
        entries = [e for e in entries if needle in e["message"].lower()]
    total = len(entries)
    return entries[-limit:], total
