"""Graph builders for InvokeAI v5 queue batches.

Node/edge wiring verified against invoke-ai/InvokeAI main (2026-08)
frontend graph builders (buildSD1Graph / buildSDXLGraph / buildFLUXGraph /
addImageToImage / addInpaint) and invocation schemas.

Supported families:
- sd-1   (main_model_loader + compel)
- sdxl   (sdxl_model_loader + sdxl_compel_prompt)
- flux   (flux_model_loader + flux_text_encoder + flux_denoise + flux_vae_decode)

Each builder emits a full graph dict suitable for
POST /api/v1/queue/{queue_id}/enqueue_batch {"batch": {"graph": ...}}.
"""

from __future__ import annotations

import uuid
from typing import Any

from invokeai_mcp.client import InvokeAIError


def _uuid() -> str:
    return str(uuid.uuid4())


def _image_node(image_name: str) -> dict[str, Any]:
    return {
        "id": _uuid(),
        "type": "image",
        "data": {"image": {"image_name": image_name}},
    }


def _model_field(model: dict[str, Any]) -> dict[str, Any]:
    """ModelIdentifierField - v6 requires key, hash, name, base AND type."""
    return {
        "key": model.get("key"),
        "hash": model.get("hash"),
        "name": model.get("name"),
        "base": model.get("base"),
        "type": model.get("type"),
    }


# ---------------------------------------------------------------------------
# SD 1.5 family
# ---------------------------------------------------------------------------
def build_sd1_graph(
    *,
    model: dict[str, Any],
    positive_prompt: str,
    negative_prompt: str = "",
    width: int = 512,
    height: int = 512,
    steps: int = 30,
    cfg_scale: float = 7.5,
    scheduler: str = "euler",
    seed: int | None = None,
    strength: float | None = None,
    image_name: str | None = None,
    mask_image_name: str | None = None,
) -> dict[str, Any]:
    nodes: dict[str, Any] = {}
    edges: list[dict[str, Any]] = []

    def add(node: dict[str, Any]) -> str:
        """Register a node. v6 uses FLAT node fields - data is merged in."""
        nid = node["id"]
        flat = {"id": nid, "type": node["type"]}
        flat.update(node.get("data") or {})
        nodes[nid] = flat
        return nid

    def edge(src: str, src_field: str, dst: str, dst_field: str) -> None:
        edges.append(
            {
                "source": {"node_id": src, "field": src_field},
                "destination": {"node_id": dst, "field": dst_field},
            }
        )

    loader = add(
        {"id": _uuid(), "type": "main_model_loader", "data": {"model": _model_field(model)}}
    )
    clip_skip = add({"id": _uuid(), "type": "clip_skip", "data": {"clip_skip": -1}})
    pos_string = add({"id": _uuid(), "type": "string", "data": {"value": positive_prompt}})
    pos_cond = add({"id": _uuid(), "type": "compel", "data": {}})
    pos_collect = add({"id": _uuid(), "type": "collect", "data": {}})
    neg_string = add({"id": _uuid(), "type": "string", "data": {"value": negative_prompt}})
    neg_cond = add({"id": _uuid(), "type": "compel", "data": {}})
    neg_collect = add({"id": _uuid(), "type": "collect", "data": {}})
    seed_node = add({"id": _uuid(), "type": "integer", "data": {"value": seed or 0}})
    noise = add(
        {
            "id": _uuid(),
            "type": "noise",
            "data": {"width": width, "height": height, "use_seed": True},
        }
    )
    denoise = add(
        {
            "id": _uuid(),
            "type": "denoise_latents",
            "data": {
                "cfg_scale": cfg_scale,
                "scheduler": scheduler,
                "steps": steps,
                "denoising_start": (1.0 - (strength or 0.75)) if image_name else 0.0,
                "denoising_end": 1.0,
            },
        }
    )
    l2i = add({"id": _uuid(), "type": "l2i", "data": {}})

    edge(loader, "unet", denoise, "unet")
    edge(loader, "clip", clip_skip, "clip")
    edge(clip_skip, "clip", pos_cond, "clip")
    edge(clip_skip, "clip", neg_cond, "clip")
    edge(pos_string, "value", pos_cond, "prompt")
    edge(neg_string, "value", neg_cond, "prompt")
    edge(pos_cond, "conditioning", pos_collect, "item")
    edge(neg_cond, "conditioning", neg_collect, "item")
    edge(pos_collect, "collection", denoise, "positive_conditioning")
    edge(neg_collect, "collection", denoise, "negative_conditioning")
    edge(seed_node, "value", noise, "seed")
    edge(noise, "noise", denoise, "noise")
    edge(loader, "vae", l2i, "vae")

    if image_name is not None:
        img_node = _image_node(image_name)
        img_id = add(img_node)
        i2l = add({"id": _uuid(), "type": "i2l", "data": {}})
        edge(img_id, "image", i2l, "image")
        edge(loader, "vae", i2l, "vae")
        edge(i2l, "latents", denoise, "latents")
        if mask_image_name is not None:
            mask_node = _image_node(mask_image_name)
            mask_id = add(mask_node)
            mask_denoise = add({"id": _uuid(), "type": "create_denoise_mask", "data": {}})
            edge(loader, "vae", mask_denoise, "vae")
            edge(mask_id, "image", mask_denoise, "mask")
            edge(mask_denoise, "mask", denoise, "mask")

    edge(denoise, "latents", l2i, "latents")

    return {"id": _uuid(), "nodes": nodes, "edges": edges}


# ---------------------------------------------------------------------------
# SDXL family
# ---------------------------------------------------------------------------
def build_sdxl_graph(
    *,
    model: dict[str, Any],
    positive_prompt: str,
    negative_prompt: str = "",
    width: int = 1024,
    height: int = 1024,
    steps: int = 30,
    cfg_scale: float = 5.0,
    cfg_rescale_multiplier: float = 0.0,
    scheduler: str = "euler",
    seed: int | None = None,
    strength: float | None = None,
    image_name: str | None = None,
    mask_image_name: str | None = None,
) -> dict[str, Any]:
    nodes: dict[str, Any] = {}
    edges: list[dict[str, Any]] = []

    def add(node: dict[str, Any]) -> str:
        """Register a node. v6 uses FLAT node fields - data is merged in."""
        nid = node["id"]
        flat = {"id": nid, "type": node["type"]}
        flat.update(node.get("data") or {})
        nodes[nid] = flat
        return nid

    def edge(src: str, src_field: str, dst: str, dst_field: str) -> None:
        edges.append(
            {
                "source": {"node_id": src, "field": src_field},
                "destination": {"node_id": dst, "field": dst_field},
            }
        )

    loader = add(
        {"id": _uuid(), "type": "sdxl_model_loader", "data": {"model": _model_field(model)}}
    )
    pos_string = add({"id": _uuid(), "type": "string", "data": {"value": positive_prompt}})
    pos_cond = add({"id": _uuid(), "type": "sdxl_compel_prompt", "data": {}})
    pos_collect = add({"id": _uuid(), "type": "collect", "data": {}})
    neg_string = add({"id": _uuid(), "type": "string", "data": {"value": negative_prompt}})
    neg_cond = add({"id": _uuid(), "type": "sdxl_compel_prompt", "data": {}})
    neg_collect = add({"id": _uuid(), "type": "collect", "data": {}})
    seed_node = add({"id": _uuid(), "type": "integer", "data": {"value": seed or 0}})
    noise = add(
        {
            "id": _uuid(),
            "type": "noise",
            "data": {"width": width, "height": height, "use_seed": True},
        }
    )
    denoise = add(
        {
            "id": _uuid(),
            "type": "denoise_latents",
            "data": {
                "cfg_scale": cfg_scale,
                "cfg_rescale_multiplier": cfg_rescale_multiplier,
                "scheduler": scheduler,
                "steps": steps,
                "denoising_start": (1.0 - (strength or 0.75)) if image_name else 0.0,
                "denoising_end": 1.0,
            },
        }
    )
    l2i = add({"id": _uuid(), "type": "l2i", "data": {}})

    edge(loader, "unet", denoise, "unet")
    edge(loader, "clip", pos_cond, "clip")
    edge(loader, "clip2", pos_cond, "clip2")
    edge(loader, "clip", neg_cond, "clip")
    edge(loader, "clip2", neg_cond, "clip2")
    edge(pos_string, "value", pos_cond, "prompt")
    edge(pos_string, "value", pos_cond, "style")
    edge(neg_string, "value", neg_cond, "prompt")
    edge(neg_string, "value", neg_cond, "style")
    edge(pos_cond, "conditioning", pos_collect, "item")
    edge(neg_cond, "conditioning", neg_collect, "item")
    edge(pos_collect, "collection", denoise, "positive_conditioning")
    edge(neg_collect, "collection", denoise, "negative_conditioning")
    edge(seed_node, "value", noise, "seed")
    edge(noise, "noise", denoise, "noise")
    edge(loader, "vae", l2i, "vae")

    if image_name is not None:
        img_id = add(_image_node(image_name))
        i2l = add({"id": _uuid(), "type": "i2l", "data": {}})
        edge(img_id, "image", i2l, "image")
        edge(loader, "vae", i2l, "vae")
        edge(i2l, "latents", denoise, "latents")
        if mask_image_name is not None:
            mask_id = add(_image_node(mask_image_name))
            mask_denoise = add({"id": _uuid(), "type": "create_denoise_mask", "data": {}})
            edge(loader, "vae", mask_denoise, "vae")
            edge(mask_id, "image", mask_denoise, "mask")
            edge(mask_denoise, "mask", denoise, "mask")

    edge(denoise, "latents", l2i, "latents")

    return {"id": _uuid(), "nodes": nodes, "edges": edges}


# ---------------------------------------------------------------------------
# FLUX family (dev / schnell / kontext share the base wiring)
# ---------------------------------------------------------------------------
def build_flux_graph(
    *,
    model: dict[str, Any],
    positive_prompt: str,
    negative_prompt: str = "",
    width: int = 1024,
    height: int = 1024,
    steps: int = 30,
    cfg_scale: float = 3.5,
    scheduler: str = "euler",
    seed: int | None = None,
    strength: float | None = None,
    image_name: str | None = None,
) -> dict[str, Any]:
    nodes: dict[str, Any] = {}
    edges: list[dict[str, Any]] = []

    def add(node: dict[str, Any]) -> str:
        """Register a node. v6 uses FLAT node fields - data is merged in."""
        nid = node["id"]
        flat = {"id": nid, "type": node["type"]}
        flat.update(node.get("data") or {})
        nodes[nid] = flat
        return nid

    def edge(src: str, src_field: str, dst: str, dst_field: str) -> None:
        edges.append(
            {
                "source": {"node_id": src, "field": src_field},
                "destination": {"node_id": dst, "field": dst_field},
            }
        )

    loader = add(
        {"id": _uuid(), "type": "flux_model_loader", "data": {"model": _model_field(model)}}
    )
    text_encoder = add({"id": _uuid(), "type": "flux_text_encoder", "data": {}})
    pos_string = add({"id": _uuid(), "type": "string", "data": {"value": positive_prompt}})
    pos_cond = add({"id": _uuid(), "type": "flux_compel_prompt", "data": {}})
    pos_collect = add({"id": _uuid(), "type": "collect", "data": {}})
    seed_node = add({"id": _uuid(), "type": "integer", "data": {"value": seed or 0}})
    denoise = add(
        {
            "id": _uuid(),
            "type": "flux_denoise",
            "data": {
                "width": width,
                "height": height,
                "steps": steps,
                "cfg_scale": cfg_scale,
                "scheduler": scheduler,
                "denoising_start": (1.0 - (strength or 0.75)) if image_name else 0.0,
                "denoising_end": 1.0,
            },
        }
    )
    l2i = add({"id": _uuid(), "type": "flux_vae_decode", "data": {}})

    edge(loader, "clip", text_encoder, "clip")
    edge(loader, "t5_encoder", text_encoder, "t5_encoder")
    edge(loader, "max_seq_len", text_encoder, "t5_max_seq_len")
    edge(text_encoder, "clip_embeddings", pos_cond, "clip_embeddings")
    edge(text_encoder, "t5_embeddings", pos_cond, "t5_embeddings")
    edge(pos_string, "value", pos_cond, "prompt")
    edge(pos_cond, "conditioning", pos_collect, "item")
    edge(pos_collect, "collection", denoise, "positive_text_conditioning")
    edge(loader, "transformer", denoise, "transformer")
    edge(loader, "vae", l2i, "vae")
    edge(seed_node, "value", denoise, "seed")

    if image_name is not None:
        img_id = add(_image_node(image_name))
        vae_encode = add({"id": _uuid(), "type": "flux_vae_encode", "data": {}})
        edge(img_id, "image", vae_encode, "image")
        edge(loader, "vae", vae_encode, "vae")
        edge(vae_encode, "latents", denoise, "latents")

    edge(denoise, "latents", l2i, "latents")

    return {"id": _uuid(), "nodes": nodes, "edges": edges}


# ---------------------------------------------------------------------------
# Upscale (RealESRGAN) - no model family dependency
# ---------------------------------------------------------------------------
def build_upscale_graph(
    image_name: str, model_name: str = "RealESRGAN_x4plus.pth"
) -> dict[str, Any]:
    nodes: dict[str, Any] = {}
    edges: list[dict[str, Any]] = []

    def add(node: dict[str, Any]) -> str:
        """Register a node. v6 uses FLAT node fields - data is merged in."""
        nid = node["id"]
        flat = {"id": nid, "type": node["type"]}
        flat.update(node.get("data") or {})
        nodes[nid] = flat
        return nid

    def edge(src: str, src_field: str, dst: str, dst_field: str) -> None:
        edges.append(
            {
                "source": {"node_id": src, "field": src_field},
                "destination": {"node_id": dst, "field": dst_field},
            }
        )

    img_id = add(_image_node(image_name))
    upscale = add({"id": _uuid(), "type": "esrgan", "data": {"model_name": model_name}})
    edge(img_id, "image", upscale, "image")
    return {"id": _uuid(), "nodes": nodes, "edges": edges}


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------
def build_generation_graph(
    *,
    operation: str,
    model: dict[str, Any],
    positive_prompt: str,
    negative_prompt: str = "",
    width: int = 512,
    height: int = 512,
    steps: int = 30,
    cfg_scale: float = 7.5,
    scheduler: str = "euler",
    seed: int | None = None,
    strength: float = 0.75,
    image_name: str | None = None,
    mask_image_name: str | None = None,
) -> dict[str, Any]:
    """Dispatch to the right graph builder for the model's base family."""
    if operation == "upscale":
        if not image_name:
            raise InvokeAIError("upscale requires image_name", error_type="validation")
        return build_upscale_graph(image_name)

    base = (model.get("base") or "").lower()
    kwargs: dict[str, Any] = dict(
        model=model,
        positive_prompt=positive_prompt,
        negative_prompt=negative_prompt,
        width=width,
        height=height,
        steps=steps,
        cfg_scale=cfg_scale,
        scheduler=scheduler,
        seed=seed,
        strength=strength,
        image_name=image_name,
    )
    if operation == "inpaint":
        kwargs["mask_image_name"] = mask_image_name
    if base.startswith("flux"):
        return build_flux_graph(**kwargs)
    if base == "sdxl":
        return build_sdxl_graph(**kwargs)
    if base == "sd-1":
        return build_sd1_graph(**kwargs)
    raise InvokeAIError(
        f"Unsupported model base '{base}' for graph building. Supported: sd-1, sdxl, flux.",
        error_type="unsupported_model",
    )
