"""Franchise preset catalog - recognizable IP style anchors (fan-style).

Each entry: id, name, prompt (the anchor suffix appended LAST - the
strongest visual identity cue). These are style descriptors for personal
creative fun, not official products. Order in a combined prompt:
base -> style -> material -> painter -> franchise.
"""

from __future__ import annotations

import json
import pathlib
from functools import lru_cache
from typing import Any

_DATA = pathlib.Path(__file__).parent / "data" / "franchises.json"

_FRANCHISES: list[tuple[str, str, str]] = [
    ("super-mario", "Super Mario", "bright platformer world, pipes, coins, goombas, cartoon 2.5D"),
    ("zelda", "Zelda", "cel-shaded adventure, lush fields, fantasy ruins, master sword"),
    ("pokemon", "Pokemon", "cute creature battle world, poke ball, tall grass routes"),
    ("minecraft", "Minecraft", "blocky voxel world, cube terrain, pixel blocks"),
    ("animal-crossing", "Animal Crossing", "cozy pastel life sim, cute villagers, island paradise"),
    ("sonic", "Sonic", "fast blue blur, loops and springs, checkered hills"),
    ("hollow-knight", "Hollow Knight", "hand-drawn gothic bug kingdom, muted palette, atmospheric"),
    ("undertale", "Undertale", "retro pixel rpg, quirky characters, pixel charm"),
    ("doom", "Doom", "90s fps hellscape, demons, dark corridors, heavy metal"),
    ("portal", "Portal", "clean test chamber, white panels, orange and blue portals"),
    ("ghibli", "Studio Ghibli", "hand-painted backgrounds, soft light, whimsical worlds"),
    ("shinkai", "Makoto Shinkai", "hyper-detailed skies, lens flare light, emotional scenery"),
    ("disney", "Golden Age Disney", "hand-drawn animation, rounded charm, musical energy"),
    ("pixar", "Pixar", "3d animated film, expressive characters, polished render"),
    ("tim-burton", "Tim Burton", "gothic stop-motion, striped characters, quirky dark whimsy"),
    ("simpsons", "The Simpsons", "flat yellow cartoon, overbite, springfield suburbs"),
    ("marvel", "Marvel", "comic book cinematic, bold heroes, dynamic action panels"),
    ("star-wars", "Star Wars", "sci-fi galaxy, droids, lightsabers, space opera"),
    ("lotr", "Lord of the Rings", "epic high fantasy, middle-earth landscapes, ancient ruins"),
    ("harry-potter", "Harry Potter", "magical school, wands, floating candles, cozy gothic"),
    ("dnd", "Dungeons and Dragons", "classic fantasy adventuring, monster manual creatures"),
    ("warhammer-40k", "Warhammer 40k", "grimdark far future, space marines, gothic machinery"),
    ("mtg", "Magic the Gathering", "painterly fantasy card art, dramatic composition"),
]


def _build() -> list[dict[str, Any]]:
    out = []
    for fid, name, sig in _FRANCHISES:
        out.append(
            {
                "id": fid,
                "name": name,
                "prompt": f"in the style of {name}, {sig}",
            }
        )
    return out


@lru_cache(maxsize=1)
def load_franchises() -> list[dict[str, Any]]:
    if not _DATA.exists():
        _DATA.parent.mkdir(parents=True, exist_ok=True)
        _DATA.write_text(json.dumps(_build(), indent=2), encoding="utf-8")
    return json.loads(_DATA.read_text(encoding="utf-8"))


def list_franchises() -> list[dict[str, Any]]:
    return load_franchises()


def get_franchise(franchise_id: str) -> dict[str, Any] | None:
    for f in load_franchises():
        if f["id"] == franchise_id:
            return f
    return None


def search_franchises(query: str, limit: int = 20) -> list[dict[str, Any]]:
    q = query.lower()
    hits = []
    for f in load_franchises():
        if q in f["id"].lower() or q in f["name"].lower() or q in f["prompt"].lower():
            hits.append(f)
            if len(hits) >= limit:
                break
    return hits


def apply_franchise(franchise: dict[str, Any], prompt: str) -> str:
    """Append the franchise anchor suffix - LAST, the strongest identity cue."""
    suffix = franchise.get("prompt", "").strip()
    if not suffix:
        return prompt.strip()
    return f"{prompt.strip()}, {suffix}"