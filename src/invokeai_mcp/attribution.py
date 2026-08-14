"""Exact per-image style attribution registry.

The backend knows which queue item carried which styles at enqueue time;
images link back to their queue item through session_id. This module
persists item_id -> {styles, model_key, prompt} so the gallery can
attribute images exactly instead of guessing from prompt text.
"""

from __future__ import annotations

import asyncio
import json
import pathlib
import time
from typing import Any

_REGISTRY: pathlib.Path = pathlib.Path(__file__).parent / "data" / "attribution.json"
_MAX_ENTRIES = 2000
_lock = asyncio.Lock()


def _load() -> dict[str, Any]:
    if not _REGISTRY.exists():
        return {"entries": {}}
    try:
        return json.loads(_REGISTRY.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"entries": {}}


def _save(data: dict[str, Any]) -> None:
    _REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    _REGISTRY.write_text(json.dumps(data, indent=2), encoding="utf-8")


async def record_items(
    item_ids: list[int],
    styles: list[str],
    model_key: str | None = None,
    prompt: str = "",
) -> None:
    """Associate queue items with the styles that produced them."""
    if not item_ids:
        return
    async with _lock:
        data = _load()
        entries = data["entries"]
        now = time.time()
        for item_id in item_ids:
            entries[str(item_id)] = {
                "styles": styles,
                "model_key": model_key,
                "prompt": prompt[:2000],
                "ts": now,
            }
        # prune oldest beyond the cap
        if len(entries) > _MAX_ENTRIES:
            ordered = sorted(entries.items(), key=lambda kv: kv[1].get("ts", 0))
            for k, _ in ordered[: len(entries) - _MAX_ENTRIES]:
                entries.pop(k, None)
        _save(data)


async def get_attribution(item_id: int | str) -> dict[str, Any] | None:
    async with _lock:
        return _load()["entries"].get(str(item_id))


async def session_map() -> dict[str, dict[str, Any]]:
    """item_id -> attribution entry, loaded once per call."""
    async with _lock:
        return dict(_load()["entries"])
