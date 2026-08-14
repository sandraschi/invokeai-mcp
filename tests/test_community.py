"""Community style pack tests."""

from __future__ import annotations

import pathlib

import pytest

import invokeai_mcp.attribution as attribution
import invokeai_mcp.runtime as runtime
from invokeai_mcp.styles import community_styles, get_style, load_community


def test_community_catalog_loaded():
    entries = load_community()
    assert len(entries) >= 1000, f"expected the A1111 packs, got {len(entries)}"
    for e in entries:
        assert e["id"] and e["name"] and e["prompt"] and e["source"]


def test_community_search_and_get_fallback():
    hits = community_styles("neon", limit=10)
    assert hits, "expected neon matches in the community pack"
    first = hits[0]
    assert get_style(first["id"]) is not None  # get() resolves community ids
    # ids are namespaced - no collision with curated styles
    curated = {s["id"] for s in __import__("invokeai_mcp.styles", fromlist=["list_styles"]).list_styles()}
    assert first["id"] not in curated


def test_community_explicit_filter():
    entries = load_community()
    for e in entries:
        low = (e["name"] + " " + e["prompt"]).lower()
        for tok in ("nsfw", "porn", "hentai", "bdsm", "fuck"):
            assert tok not in low, f"explicit token {tok} leaked into {e['id']}"


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


async def test_generate_with_community_style(fake):
    from invokeai_mcp.tools.generate_tools import invokeai_generate

    community = community_styles("neonpunk", limit=1)
    assert community
    result = await invokeai_generate(
        operation="txt2img",
        prompt="a lone detective in the rain",
        styles=[community[0]["id"]],
        width=512,
        height=512,
    )
    assert result["success"] is True
    assert result["style_count"] == 1
    prompt = next(
        n["value"]
        for g in fake.enqueues
        for n in g["nodes"].values()
        if n.get("type") == "string" and isinstance(n.get("value"), str)
    )
    assert "a lone detective in the rain" in prompt
    assert "vaporwave" in prompt.lower() or "neon" in prompt.lower()


async def test_styles_community_tool_op(fake):
    from invokeai_mcp.tools.style_tools import invokeai_styles

    result = await invokeai_styles(operation="community", query="origami")
    assert result["success"] is True
    assert result["count"] >= 1
    assert result["total"] >= 1000

    all_res = await invokeai_styles(operation="community")
    assert all_res["count"] > 0
