"""Painter catalog + styles x artists cartesian tests."""

from __future__ import annotations

import pathlib

import pytest

import invokeai_mcp.attribution as attribution
import invokeai_mcp.runtime as runtime
from invokeai_mcp.artists import (
    apply_artist,
    get_artist,
    list_artists,
    search_artists,
)


def test_artists_catalog_60():
    artists = list_artists()
    assert len(artists) >= 60, f"got {len(artists)}"
    ids = {a["id"] for a in artists}
    assert "giotto" in ids and "giger" in ids
    for a in artists:
        assert a["id"] and a["name"] and a["prompt"].startswith("in the style of")


def test_get_search_apply():
    giger = get_artist("giger")
    assert giger and "biomechanical" in giger["prompt"]
    assert get_artist("nope") is None
    assert search_artists("impressionist")
    assert apply_artist(giger, "a corridor") == "a corridor, in the style of H.R. Giger, biomechanical nightmare, organic machinery, dark airbrushed alien corridors"


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
    return [
        next(
            n["value"]
            for n in g["nodes"].values()
            if n.get("type") == "string" and isinstance(n.get("value"), str)
        )
        for g in graphs
    ]


async def test_generate_artists_only(fake):
    from invokeai_mcp.tools.generate_tools import invokeai_generate

    result = await invokeai_generate(
        operation="txt2img",
        prompt="a rainy street",
        artists=["van-gogh", "giger"],
        width=512,
        height=512,
    )
    assert result["success"] is True
    assert result["artist_count"] == 2
    assert len(fake.enqueues) == 2
    prompts = await _prompts_of(fake.enqueues)
    assert prompts[0].endswith("in the style of Vincent van Gogh, swirling impasto, electric yellow, cypress spirals, emotional color")
    assert "in the style of H.R. Giger" in prompts[1]


async def test_generate_styles_x_artists_cartesian(fake):
    from invokeai_mcp.tools.generate_tools import invokeai_generate

    result = await invokeai_generate(
        operation="txt2img",
        prompt="a lone detective in the rain",
        styles=["photorealistic", "cinematic"],
        artists=["hopper", "caravaggio"],
        width=512,
        height=512,
    )
    assert result["success"] is True
    assert result["style_count"] == 2
    assert result["artist_count"] == 2
    assert len(fake.enqueues) == 4
    prompts = await _prompts_of(fake.enqueues)
    # painter anchor is LAST in every prompt
    for p in prompts:
        assert "in the style of" in p
        assert p.index("in the style of") > p.index("photorealistic" if "photorealistic" in p else "cinematic")
    # per-item attribution
    attrib = await attribution.session_map()
    per_item = {k: (v["styles"], v["artists"]) for k, v in sorted(attrib.items())}
    assert per_item == {
        "1": (["photorealistic"], ["hopper"]),
        "2": (["photorealistic"], ["caravaggio"]),
        "3": (["cinematic"], ["hopper"]),
        "4": (["cinematic"], ["caravaggio"]),
    }, f"wrong attribution: {per_item}"


async def test_generate_unknown_artist_rejected(fake):
    from invokeai_mcp.tools.generate_tools import invokeai_generate

    result = await invokeai_generate(
        operation="txt2img", prompt="x", artists=["not-a-painter"], width=512, height=512
    )
    assert result["success"] is False
    assert result["error"] == "not_found"
    assert fake.enqueues == []


async def test_artists_list_tool(fake):
    from invokeai_mcp.tools.artist_tools import invokeai_artists

    result = await invokeai_artists(operation="list")
    assert result["success"] is True
    assert result["count"] >= 60

    got = await invokeai_artists(operation="get", artist_id="giger")
    assert got["success"] is True
    assert got["artists"][0]["name"] == "H.R. Giger"

    missing = await invokeai_artists(operation="get", artist_id="bogus")
    assert missing["success"] is False
    assert missing["error"] == "not_found"
