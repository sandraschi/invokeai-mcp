"""Style catalog + multi-style batch tests."""

from __future__ import annotations

import pytest

import invokeai_mcp.runtime as runtime
from invokeai_mcp.styles import apply_style, get_style, list_styles, search_styles


def test_styles_catalog_nonempty():
    styles = list_styles()
    assert len(styles) >= 60
    ids = {s["id"] for s in styles}
    assert "photorealistic" in ids
    for s in styles:
        assert s["id"] and s["name"] and s["prompt"]


def test_get_style_known_and_unknown():
    assert get_style("photorealistic") is not None
    assert get_style("no-such-style") is None


def test_search_styles():
    hits = search_styles("watercolor")
    assert hits, "expected at least one watercolor style"
    assert all("watercolor" in s["id"] + s["name"] + s["prompt"] for s in hits)


def test_apply_style_suffix():
    style = {"id": "x", "name": "X", "prompt": "oil painting, canvas texture"}
    assert apply_style(style, "a boat") == "a boat, oil painting, canvas texture"
    assert apply_style({"id": "y", "prompt": ""}, "a boat") == "a boat"


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
    import invokeai_mcp.attribution as attribution

    monkeypatch.setattr(attribution, "_REGISTRY", tmp_path / "attribution.json")
    return fc


async def test_generate_multi_style_enqueues_one_per_style(fake):
    from invokeai_mcp.tools.generate_tools import invokeai_generate

    result = await invokeai_generate(
        operation="txt2img",
        prompt="a lone detective in the rain",
        styles=["photorealistic", "watercolor", "film-noir"],
        width=512,
        height=512,
    )
    assert result["success"] is True
    assert result["style_count"] == 3
    assert len(result["queue_item_ids"]) == 3
    assert len(fake.enqueues) == 3
    prompts = [
        next(
            n["value"]
            for n in g["nodes"].values()
            if n.get("type") == "string" and isinstance(n.get("value"), str)
        )
        for g in fake.enqueues
    ]
    assert prompts[0].startswith("a lone detective in the rain, photorealistic")
    assert "watercolor" in prompts[1]

    from invokeai_mcp.attribution import session_map

    attrib = await session_map()
    per_item = {k: a["styles"] for k, a in sorted(attrib.items())}
    assert per_item == {
        "1": ["photorealistic"],
        "2": ["watercolor"],
        "3": ["film-noir"],
    }, f"per-item attribution wrong: {per_item}"


async def test_generate_multi_style_random_seeds(fake):
    """seed=None must roll a fresh random seed per job (was 0 for all)."""
    from invokeai_mcp.tools.generate_tools import invokeai_generate

    result = await invokeai_generate(
        operation="txt2img",
        prompt="a boat",
        styles=["photorealistic", "watercolor", "film-noir"],
        width=512,
        height=512,
    )
    assert result["success"] is True
    seeds = []
    for g in fake.enqueues:
        for n in g["nodes"].values():
            if n.get("type") == "integer" and isinstance(n.get("value"), int) and n["value"] > 0:
                seeds.append(n["value"])
    assert len(seeds) == 3, f"expected 3 seed nodes, got {seeds}"
    assert len(set(seeds)) == 3, f"seeds must differ per job, got {seeds}"


async def test_generate_explicit_seed_shared_across_styles(fake):
    from invokeai_mcp.tools.generate_tools import invokeai_generate

    result = await invokeai_generate(
        operation="txt2img",
        prompt="a boat",
        styles=["photorealistic", "watercolor"],
        width=512,
        height=512,
        seed=12345,
    )
    assert result["success"] is True
    seeds = [
        n["value"]
        for g in fake.enqueues
        for n in g["nodes"].values()
        if n.get("type") == "integer" and n.get("value") == 12345
    ]
    assert len(seeds) == 2


async def test_generate_unknown_style_rejected(fake):
    from invokeai_mcp.tools.generate_tools import invokeai_generate

    result = await invokeai_generate(
        operation="txt2img", prompt="x", styles=["not-a-style"], width=512, height=512
    )
    assert result["success"] is False
    assert result["error"] == "not_found"
    assert fake.enqueues == []


async def test_styles_list_tool(fake):
    from invokeai_mcp.tools.style_tools import invokeai_styles

    result = await invokeai_styles(operation="list", limit=100)
    assert result["success"] is True
    assert result["count"] >= 60

    got = await invokeai_styles(operation="get", style_id="photorealistic")
    assert got["success"] is True
    assert got["styles"][0]["id"] == "photorealistic"

    missing = await invokeai_styles(operation="get", style_id="bogus")
    assert missing["success"] is False
    assert missing["error"] == "not_found"

    hit = await invokeai_styles(operation="search", query="watercolor")
    assert hit["success"] is True
    assert hit["count"] >= 1
