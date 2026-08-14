"""Franchise catalog + multi-dimension cartesian tests."""

from __future__ import annotations

import pathlib

import pytest

import invokeai_mcp.attribution as attribution
import invokeai_mcp.runtime as runtime
from invokeai_mcp.franchises import (
    apply_franchise,
    get_franchise,
    list_franchises,
    search_franchises,
)


def test_franchises_catalog():
    franchises = list_franchises()
    assert len(franchises) >= 20
    ids = {f["id"] for f in franchises}
    assert "super-mario" in ids and "ghibli" in ids and "warhammer-40k" in ids
    for f in franchises:
        assert f["id"] and f["name"] and f["prompt"].startswith("in the style of")


def test_get_search_apply():
    mario = get_franchise("super-mario")
    assert mario and "platformer" in mario["prompt"]
    assert get_franchise("nope") is None
    assert search_franchises("ghibli")
    assert apply_franchise(mario, "a funeral procession") == (
        "a funeral procession, in the style of Super Mario, bright platformer world, "
        "pipes, coins, goombas, cartoon 2.5D"
    )


class FakeClient:
    def __init__(self):
        self.models_cache = {
            "main": [{"key": "m1", "name": "SDXL", "type": "main", "base": "sdxl"}]
        }
        self.enqueues = []

    async def refresh_models(self):
        return self.models_cache

    async def get_model(self, key):
        return {"key": key, "base": "sdxl", "type": "main", "hash": "h"}

    async def enqueue_batch(self, graph, runs=1, destination="mcp"):
        self.enqueues.append(graph)
        n = len(self.enqueues)
        return {"batch_id": f"b{n}", "queue_item_ids": [n], "queue_id": "default"}


@pytest.fixture
def fake(monkeypatch, tmp_path):
    fc = FakeClient()
    monkeypatch.setattr(runtime, "_client", fc)
    monkeypatch.setattr(attribution, "_REGISTRY", pathlib.Path(tmp_path) / "attribution.json")
    return fc


async def _prompts_of(graphs):
    out = []
    for g in graphs:
        strings = [
            n["value"]
            for n in g["nodes"].values()
            if n.get("type") == "string" and isinstance(n.get("value"), str)
        ]
        positive = next((s for s in strings if "in the style of" in s or s.startswith("a kindergarten")), strings[0] if strings else "")
        out.append(positive)
    return out


async def test_generate_franchise_only(fake):
    from invokeai_mcp.tools.generate_tools import invokeai_generate

    result = await invokeai_generate(
        operation="txt2img",
        prompt="a funeral procession",
        franchises=["super-mario"],
        width=512,
        height=512,
    )
    assert result["success"] is True
    assert result["franchise_count"] == 1
    prompts = await _prompts_of(fake.enqueues)
    assert prompts[0].endswith("in the style of Super Mario, bright platformer world, pipes, coins, goombas, cartoon 2.5D")


async def test_generate_all_dims_cartesian(fake):
    from invokeai_mcp.tools.generate_tools import invokeai_generate

    result = await invokeai_generate(
        operation="txt2img",
        prompt="a kindergarten scene",
        styles=["cinematic"],
        artists=["klimt"],
        franchises=["ghibli", "pokemon"],
        width=512,
        height=512,
    )
    assert result["success"] is True
    assert result["style_count"] == 1
    assert result["artist_count"] == 1
    assert result["franchise_count"] == 2
    assert len(fake.enqueues) == 2
    prompts = await _prompts_of(fake.enqueues)
    assert "in the style of Studio Ghibli" in prompts[0]
    assert "in the style of Pokemon" in prompts[1]
    for p in prompts:
        # franchise is LAST, after painter and style
        assert p.index("in the style of Gustav Klimt") > p.index("cinematic")
    assert prompts[0].index("in the style of Studio Ghibli") > prompts[0].index("in the style of Gustav Klimt")
    attrib = await attribution.session_map()
    per_item = {k: (v["styles"], v["artists"], v["franchises"]) for k, v in sorted(attrib.items())}
    assert per_item == {
        "1": (["cinematic"], ["klimt"], ["ghibli"]),
        "2": (["cinematic"], ["klimt"], ["pokemon"]),
    }, f"wrong attribution: {per_item}"


async def test_generate_unknown_franchise_rejected(fake):
    from invokeai_mcp.tools.generate_tools import invokeai_generate

    result = await invokeai_generate(
        operation="txt2img", prompt="x", franchises=["not-a-franchise"], width=512, height=512
    )
    assert result["success"] is False
    assert result["error"] == "not_found"
    assert fake.enqueues == []


async def test_franchises_list_tool(fake):
    from invokeai_mcp.tools.franchise_tools import invokeai_franchises

    result = await invokeai_franchises(operation="list")
    assert result["success"] is True
    assert result["count"] >= 20

    got = await invokeai_franchises(operation="get", franchise_id="ghibli")
    assert got["success"] is True
    assert got["franchises"][0]["name"] == "Studio Ghibli"

    missing = await invokeai_franchises(operation="get", franchise_id="bogus")
    assert missing["success"] is False
    assert missing["error"] == "not_found"

    hit = await invokeai_franchises(operation="search", query="mario")
    assert hit["success"] is True
    assert hit["count"] >= 1
