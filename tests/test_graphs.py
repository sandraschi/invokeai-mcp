"""Graph builder tests - structural invariants per model family."""

from __future__ import annotations

import pytest

from invokeai_mcp.client import InvokeAIError
from invokeai_mcp.graphs import (
    build_flux_graph,
    build_generation_graph,
    build_sd1_graph,
    build_sdxl_graph,
    build_upscale_graph,
)

MODEL = {"key": "k1", "hash": "h1", "name": "Test Model"}


def _node_types(graph) -> set[str]:
    return {n["type"] for n in graph["nodes"].values()}


def _edges(graph) -> list[tuple[str, str, str, str]]:
    return [
        (
            e["source"]["node_id"],
            e["source"]["field"],
            e["destination"]["node_id"],
            e["destination"]["field"],
        )
        for e in graph["edges"]
    ]


def _edge_fields(graph, target_type: str) -> set[str]:
    """Fields on nodes of target_type that are destinations of edges."""
    ids = {nid for nid, n in graph["nodes"].items() if n["type"] == target_type}
    return {e[3] for e in _edges(graph) if e[2] in ids}


def test_sd1_graph_has_required_node_types():
    g = build_sd1_graph(model=MODEL, positive_prompt="cat", width=512, height=512)
    types = _node_types(g)
    assert {
        "main_model_loader",
        "compel",
        "noise",
        "denoise_latents",
        "l2i",
        "collect",
    } <= types


def test_sd1_denoise_receives_conditioning_and_noise():
    g = build_sd1_graph(model=MODEL, positive_prompt="cat", negative_prompt="dog")
    fields = _edge_fields(g, "denoise_latents")
    assert {"positive_conditioning", "negative_conditioning", "noise", "unet"} <= fields


def test_sdxl_graph_uses_sdxl_nodes():
    g = build_sdxl_graph(model=MODEL, positive_prompt="cat", width=1024, height=1024)
    types = _node_types(g)
    assert "sdxl_model_loader" in types and "sdxl_compel_prompt" in types
    assert _edge_fields(g, "denoise_latents") >= {"positive_conditioning", "negative_conditioning"}


def test_sdxl_compel_gets_clip_and_clip2():
    g = build_sdxl_graph(model=MODEL, positive_prompt="cat")
    fields = _edge_fields(g, "sdxl_compel_prompt")
    assert {"clip", "clip2", "prompt", "style"} <= fields


def test_flux_graph_uses_flux_nodes():
    g = build_flux_graph(model=MODEL, positive_prompt="cat", width=1024, height=1024)
    types = _node_types(g)
    assert "flux_model_loader" in types
    assert "flux_text_encoder" in types
    assert "flux_denoise" in types
    assert "flux_vae_decode" in types
    denoise_fields = _edge_fields(g, "flux_denoise")
    assert {"transformer", "positive_text_conditioning", "seed"} <= denoise_fields


def test_img2img_adds_image_and_i2l():
    g = build_sd1_graph(model=MODEL, positive_prompt="cat", image_name="src.png", strength=0.6)
    types = _node_types(g)
    assert "image" in types and "i2l" in types
    assert _edge_fields(g, "i2l") >= {"image"}
    denoise = next(n for n in g["nodes"].values() if n["type"] == "denoise_latents")
    assert denoise["denoising_start"] == pytest.approx(0.4)


def test_inpaint_adds_mask_path():
    g = build_sdxl_graph(
        model=MODEL, positive_prompt="cat", image_name="src.png", mask_image_name="mask.png"
    )
    types = _node_types(g)
    assert "create_denoise_mask" in types
    assert _edge_fields(g, "denoise_latents") >= {"denoise_mask"}


def test_txt2img_denoising_starts_at_zero():
    g = build_sd1_graph(model=MODEL, positive_prompt="cat")
    denoise = next(n for n in g["nodes"].values() if n["type"] == "denoise_latents")
    assert denoise["denoising_start"] == 0.0
    assert denoise["denoising_end"] == 1.0


def test_upscale_graph():
    g = build_upscale_graph("src.png")
    types = _node_types(g)
    assert "esrgan" in types and "image" in types
    esrgan = next(n for n in g["nodes"].values() if n["type"] == "esrgan")
    assert esrgan["model_name"] == "RealESRGAN_x4plus.pth"


def test_dispatch_by_base():
    for base, expected in (
        ("sd-1", "main_model_loader"),
        ("sdxl", "sdxl_model_loader"),
        ("flux", "flux_model_loader"),
    ):
        g = build_generation_graph(
            operation="txt2img", model={**MODEL, "base": base}, positive_prompt="cat"
        )
        assert expected in _node_types(g)


def test_dispatch_rejects_unknown_base():
    with pytest.raises(InvokeAIError):
        build_generation_graph(
            operation="txt2img", model={**MODEL, "base": "unknown"}, positive_prompt="cat"
        )


def test_dispatch_upscale_requires_image():
    with pytest.raises(InvokeAIError):
        build_generation_graph(operation="upscale", model=MODEL, positive_prompt="")


def test_all_node_ids_unique_and_edges_reference_existing():
    g = build_sdxl_graph(
        model=MODEL, positive_prompt="cat", image_name="src.png", mask_image_name="m.png"
    )
    ids = set(g["nodes"].keys())
    assert len(ids) == len(g["nodes"])
    for e in g["edges"]:
        assert e["source"]["node_id"] in ids
        assert e["destination"]["node_id"] in ids
