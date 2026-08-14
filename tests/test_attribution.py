"""Exact style attribution tests."""

from __future__ import annotations

import pathlib

import pytest

import invokeai_mcp.attribution as attribution


@pytest.fixture
def registry(tmp_path, monkeypatch):
    monkeypatch.setattr(attribution, "_REGISTRY", pathlib.Path(tmp_path) / "attribution.json")
    return tmp_path


async def test_record_and_read(registry):
    await attribution.record_items([101, 102], styles=["photorealistic", "watercolor"], model_key="m1", prompt="p")
    entry = await attribution.get_attribution(101)
    assert entry["styles"] == ["photorealistic", "watercolor"]
    assert entry["model_key"] == "m1"
    assert entry["prompt"] == "p"
    smap = await attribution.session_map()
    assert set(smap.keys()) == {"101", "102"}


async def test_record_empty_noop(registry):
    await attribution.record_items([], styles=["x"])
    assert await attribution.session_map() == {}


async def test_cap_prunes_oldest(registry):
    for i in range(2050):
        await attribution.record_items([i], styles=["s"], prompt="p")
    smap = await attribution.session_map()
    assert len(smap) <= 2000
    assert "0" not in smap


async def test_overwrite(registry):
    await attribution.record_items([5], styles=["a"])
    await attribution.record_items([5], styles=["b"])
    assert (await attribution.get_attribution(5))["styles"] == ["b"]
