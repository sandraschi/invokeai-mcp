"""Style catalog - the single source of truth for generation presets.

Extracted from webapp/src/lib/presets.ts (regenerate with
scripts/extract-styles.py after editing presets there). Each entry:
id, name, prompt (suffix), negative, cfg, steps.
"""

from __future__ import annotations

import json
import pathlib
from functools import lru_cache
from typing import Any

_DATA = pathlib.Path(__file__).parent / "data" / "styles.json"


@lru_cache(maxsize=1)
def load_styles() -> list[dict[str, Any]]:
    if not _DATA.exists():
        return []
    return json.loads(_DATA.read_text(encoding="utf-8"))


def list_styles() -> list[dict[str, Any]]:
    """All style presets (id, name, prompt, negative, cfg, steps)."""
    return load_styles()


def get_style(style_id: str) -> dict[str, Any] | None:
    for s in load_styles():
        if s["id"] == style_id:
            return s
    return None


def search_styles(query: str, limit: int = 20) -> list[dict[str, Any]]:
    q = query.lower()
    hits = []
    for s in load_styles():
        if q in s["id"].lower() or q in s["name"].lower() or q in s["prompt"].lower():
            hits.append(s)
            if len(hits) >= limit:
                break
    return hits


def apply_style(style: dict[str, Any], prompt: str) -> str:
    """Append the style's prompt suffix to the base prompt (webapp parity)."""
    suffix = style.get("prompt", "").strip()
    if not suffix:
        return prompt.strip()
    return f"{prompt.strip()}, {suffix}"


def match_style_for_prompt(style: dict[str, Any], prompt: str) -> bool:
    """Did this style's suffix get applied to this prompt?

    The batch appends style.prompt to the base prompt, so a style matches
    when its name or the first token of its suffix appears in the prompt.
    """
    p = prompt.lower()
    name = style.get("name", "").lower()
    if name and name in p:
        return True
    suffix = style.get("prompt", "").strip().lower()
    if not suffix:
        return False
    first_token = suffix.split(",")[0].strip()
    return len(first_token) >= 3 and first_token in p
