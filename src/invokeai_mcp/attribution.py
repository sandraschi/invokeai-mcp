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
    styles: list[str] | None = None,
    artists: list[str] | None = None,
    franchises: list[str] | None = None,
    model_key: str | None = None,
    prompt: str = "",
) -> None:
    """Associate queue items with the styles/painters/franchises that produced them."""
    if not item_ids:
        return
    async with _lock:
        data = _load()
        entries = data["entries"]
        now = time.time()
        for item_id in item_ids:
            entries[str(item_id)] = {
                "styles": list(styles or []),
                "artists": list(artists or []),
                "franchises": list(franchises or []),
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


def prompt_slug(prompt: str, max_words: int = 5, max_len: int = 24) -> str:
    """Short human slug from the first words of a prompt (display names).

    'Philip Marlowe, a lone detective...' -> 'philip-marlowe-a-lone'
    """
    words = []
    for token in prompt.lower().replace(",", " ").split():
        clean = "".join(ch for ch in token if ch.isalnum())
        if clean and clean not in ("a", "an", "the", "in", "of", "on", "at", "with"):
            words.append(clean)
        if len(words) >= max_words:
            break
    if not words:
        return "image"
    slug = "-".join(words)
    return slug[:max_len].rstrip("-")


def short_id(image_name: str, length: int = 8) -> str:
    """Terse id suffix: uuid.png -> first 8 chars of the uuid."""
    stem = image_name.rsplit(".", 1)[0]
    return stem[:length]
