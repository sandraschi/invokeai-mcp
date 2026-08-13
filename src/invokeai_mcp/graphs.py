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


def _attach_metadata(
    edges: list[dict[str, Any]],
    add,
    edge,
    *,
    l2i: str,
    seed_node: str | None,
    pos_string: str | None,
    neg_string: str | None,
    model: dict[str, Any],
    generation_mode: str,
    width: int,
    height: int,
    steps: int,
    cfg_scale: float,
    scheduler: str,
    cfg_rescale_multiplier: float | None = None,
    strength: float | None = None,
    init_image: str | None = None,
    seamless_x: bool = False,
    seamless_y: bool = False,
) -> None:
    """Attach a core_metadata node so generated PNGs embed prompt + parameters."""
    data: dict[str, Any] = {
        "generation_mode": generation_mode,
        "width": width,
        "height": height,
        "steps": steps,
        "cfg_scale": cfg_scale,
        "scheduler": scheduler,
        "model": _model_field(model),
        "rand_device": "cuda",
        "seamless_x": seamless_x,
        "seamless_y": seamless_y,
    }
    if cfg_rescale_multiplier is not None:
        data["cfg_rescale_multiplier"] = cfg_rescale_multiplier
    if strength is not None:
        data["strength"] = strength
    if init_image is not None:
        data["init_image"] = init_image
    meta = add({"id": _uuid(), "type": "core_metadata", "data": data})
    if seed_node is not None:
        edge(seed_node, "value", meta, "seed")
    if pos_string is not None:
        edge(pos_string, "value", meta, "positive_prompt")
    if neg_string is not None:
        edge(neg_string, "value", meta, "negative_prompt")
    edge(meta, "metadata", l2i, "metadata")


def _attach_modules(
    edges: list[dict[str, Any]],
    add,
    edge,
    *,
    loader: str,
    denoise: str,
    l2i: str,
    seamless_x: bool = False,
    seamless_y: bool = False,
    control_image_name: str | None = None,
    control_model: dict[str, Any] | None = None,
    control_weight: float = 0.8,
    canny_low: int = 100,
    canny_high: int = 200,
    ip_image_name: str | None = None,
    ip_model: dict[str, Any] | None = None,
    ip_weight: float = 0.7,
) -> None:
    """Attach optional generation modules to a base sd1/sdxl graph.

    - seamless: reroutes loader.unet/vae through the seamless node (tiling).
    - controlnet: canny edge detection -> controlnet node -> denoise.control.
    - ip_adapter: reference image -> ip_adapter node -> denoise.ip_adapter.
    """
    if seamless_x or seamless_y:
        seamless = add(
            {
                "id": _uuid(),
                "type": "seamless",
                "data": {"seamless_x": seamless_x, "seamless_y": seamless_y},
            }
        )
        # reroute the unet/vae chain through the seamless node
        edges[:] = [
            e
            for e in edges
            if not (e["source"]["node_id"] == loader and e["source"]["field"] in ("unet", "vae"))
        ]
        edge(loader, "unet", seamless, "unet")
        edge(loader, "vae", seamless, "vae")
        edge(seamless, "unet", denoise, "unet")
        edge(seamless, "vae", l2i, "vae")
        if control_image_name is None:
            # img2img i2l vae edge also reroutes through seamless (never self-loop)
            for e in edges:
                if e["destination"]["field"] == "vae" and e["destination"]["node_id"] not in (
                    l2i,
                    seamless,
                ):
                    e["source"] = {"node_id": seamless, "field": "vae"}

    if control_image_name and control_model:
        ctrl_img = add(_image_node(control_image_name))
        canny = add(
            {
                "id": _uuid(),
                "type": "canny_edge_detection",
                "data": {"low_threshold": canny_low, "high_threshold": canny_high},
            }
        )
        controlnet = add(
            {
                "id": _uuid(),
                "type": "controlnet",
                "data": {
                    "control_model": _model_field(control_model),
                    "control_weight": control_weight,
                    "control_mode": "balanced",
                    "resize_mode": "resize",
                    "begin_step_percent": 0.0,
                    "end_step_percent": 1.0,
                },
            }
        )
        edge(ctrl_img, "image", canny, "image")
        edge(canny, "image", controlnet, "image")
        edge(controlnet, "control", denoise, "control")

    if ip_image_name and ip_model:
        ip_img = add(_image_node(ip_image_name))
        ip_adapter = add(
            {
                "id": _uuid(),
                "type": "ip_adapter",
                "data": {
                    "ip_adapter_model": _model_field(ip_model),
                    "weight": ip_weight,
                    "method": "full",
                    "begin_step_percent": 0.0,
                    "end_step_percent": 1.0,
                },
            }
        )
        edge(ip_img, "image", ip_adapter, "image")
        edge(ip_adapter, "ip_adapter", denoise, "ip_adapter")


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
    seamless_x: bool = False,
    seamless_y: bool = False,
    control_image_name: str | None = None,
    control_model: dict[str, Any] | None = None,
    control_weight: float = 0.8,
    canny_low: int = 100,
    canny_high: int = 200,
    ip_image_name: str | None = None,
    ip_model: dict[str, Any] | None = None,
    ip_weight: float = 0.7,
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
            "data": {"width": width, "height": height, "use_seed": True, "use_cpu": False},
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
    l2i = add({"id": _uuid(), "type": "l2i", "data": {"fp32": True}})

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
            edge(mask_denoise, "denoise_mask", denoise, "denoise_mask")

    edge(denoise, "latents", l2i, "latents")

    _attach_modules(
        edges,
        add,
        edge,
        loader=loader,
        denoise=denoise,
        l2i=l2i,
        seamless_x=seamless_x,
        seamless_y=seamless_y,
        control_image_name=control_image_name,
        control_model=control_model,
        control_weight=control_weight,
        canny_low=canny_low,
        canny_high=canny_high,
        ip_image_name=ip_image_name,
        ip_model=ip_model,
        ip_weight=ip_weight,
    )
    _attach_metadata(
        edges,
        add,
        edge,
        l2i=l2i,
        seed_node=seed_node,
        pos_string=pos_string,
        neg_string=neg_string,
        model=model,
        generation_mode="txt2img" if image_name is None else ("img2img" if mask_image_name is None else "inpaint"),
        width=width,
        height=height,
        steps=steps,
        cfg_scale=cfg_scale,
        scheduler=scheduler,
        strength=strength,
        init_image=image_name,
        seamless_x=seamless_x,
        seamless_y=seamless_y,
    )

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
    cfg_rescale_multiplier: float | None = None,
    scheduler: str = "euler",
    seed: int | None = None,
    strength: float | None = None,
    image_name: str | None = None,
    mask_image_name: str | None = None,
    seamless_x: bool = False,
    seamless_y: bool = False,
    control_image_name: str | None = None,
    control_model: dict[str, Any] | None = None,
    control_weight: float = 0.8,
    canny_low: int = 100,
    canny_high: int = 200,
    ip_image_name: str | None = None,
    ip_model: dict[str, Any] | None = None,
    ip_weight: float = 0.7,
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
            "data": {"width": width, "height": height, "use_seed": True, "use_cpu": False},
        }
    )
    denoise = add(
        {
            "id": _uuid(),
            "type": "denoise_latents",
            "data": {
                "cfg_scale": cfg_scale,
                "cfg_rescale_multiplier": cfg_rescale_multiplier if cfg_rescale_multiplier is not None else 0.7,
                "scheduler": scheduler,
                "steps": steps,
                "denoising_start": (1.0 - (strength or 0.75)) if image_name else 0.0,
                "denoising_end": 1.0,
            },
        }
    )
    l2i = add({"id": _uuid(), "type": "l2i", "data": {"fp32": True}})

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
            edge(mask_denoise, "denoise_mask", denoise, "denoise_mask")

    edge(denoise, "latents", l2i, "latents")

    _attach_modules(
        edges,
        add,
        edge,
        loader=loader,
        denoise=denoise,
        l2i=l2i,
        seamless_x=seamless_x,
        seamless_y=seamless_y,
        control_image_name=control_image_name,
        control_model=control_model,
        control_weight=control_weight,
        canny_low=canny_low,
        canny_high=canny_high,
        ip_image_name=ip_image_name,
        ip_model=ip_model,
        ip_weight=ip_weight,
    )
    _attach_metadata(
        edges,
        add,
        edge,
        l2i=l2i,
        seed_node=seed_node,
        pos_string=pos_string,
        neg_string=neg_string,
        model=model,
        generation_mode="sdxl_txt2img" if image_name is None else ("sdxl_img2img" if mask_image_name is None else "sdxl_inpaint"),
        width=width,
        height=height,
        steps=steps,
        cfg_scale=cfg_scale,
        scheduler=scheduler,
        cfg_rescale_multiplier=cfg_rescale_multiplier,
        strength=strength,
        init_image=image_name,
        seamless_x=seamless_x,
        seamless_y=seamless_y,
    )

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
    _attach_metadata(
        edges,
        add,
        edge,
        l2i=l2i,
        seed_node=seed_node,
        pos_string=pos_string,
        neg_string=None,
        model=model,
        generation_mode="flux_txt2img" if image_name is None else "flux_img2img",
        width=width,
        height=height,
        steps=steps,
        cfg_scale=cfg_scale,
        scheduler=scheduler,
        strength=strength,
        init_image=image_name,
    )

    return {"id": _uuid(), "nodes": nodes, "edges": edges}


# ---------------------------------------------------------------------------
# CogView4 family (LLM-based: GLM text encoder, transformer denoise)
# ---------------------------------------------------------------------------
def build_cogview4_graph(
    *,
    model: dict[str, Any],
    positive_prompt: str,
    negative_prompt: str = "",
    width: int = 1024,
    height: int = 1024,
    steps: int = 40,
    cfg_scale: float = 1.0,
    scheduler: str = "euler",
    seed: int | None = None,
    strength: float | None = None,
    image_name: str | None = None,
) -> dict[str, Any]:
    """CogView4 txt2img/img2img graph (verified vs engine 6.13.7 nodes)."""
    nodes: dict[str, Any] = {}
    edges: list[dict[str, Any]] = []

    def add(node: dict[str, Any]) -> str:
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

    loader = add({"id": _uuid(), "type": "cogview4_model_loader", "data": {"model": _model_field(model)}})
    pos_string = add({"id": _uuid(), "type": "string", "data": {"value": positive_prompt}})
    pos_cond = add({"id": _uuid(), "type": "cogview4_text_encoder", "data": {}})
    neg_string = add({"id": _uuid(), "type": "string", "data": {"value": negative_prompt}})
    neg_cond = add({"id": _uuid(), "type": "cogview4_text_encoder", "data": {}})
    seed_node = add({"id": _uuid(), "type": "integer", "data": {"value": seed or 0}})
    denoise = add(
        {
            "id": _uuid(),
            "type": "cogview4_denoise",
            "data": {
                "steps": steps,
                "cfg_scale": cfg_scale,
                "denoising_start": (1.0 - (strength or 0.75)) if image_name else 0.0,
                "denoising_end": 1.0,
            },
        }
    )
    l2i = add({"id": _uuid(), "type": "cogview4_l2i", "data": {}})

    edge(loader, "transformer", denoise, "transformer")
    edge(loader, "glm_encoder", pos_cond, "glm_encoder")
    edge(loader, "glm_encoder", neg_cond, "glm_encoder")
    edge(loader, "vae", l2i, "vae")
    edge(pos_string, "value", pos_cond, "prompt")
    edge(neg_string, "value", neg_cond, "prompt")
    edge(pos_cond, "conditioning", denoise, "positive_conditioning")
    edge(neg_cond, "conditioning", denoise, "negative_conditioning")
    edge(seed_node, "value", denoise, "seed")
    edge(denoise, "latents", l2i, "latents")

    if image_name is not None:
        img_id = add(_image_node(image_name))
        i2l = add({"id": _uuid(), "type": "cogview4_i2l", "data": {}})
        edge(img_id, "image", i2l, "image")
        edge(loader, "vae", i2l, "vae")
        edge(i2l, "latents", denoise, "latents")

    _attach_metadata(
        edges,
        add,
        edge,
        l2i=l2i,
        seed_node=seed_node,
        pos_string=pos_string,
        neg_string=neg_string,
        model=model,
        generation_mode="cogview4_txt2img" if image_name is None else "cogview4_img2img",
        width=width,
        height=height,
        steps=steps,
        cfg_scale=cfg_scale,
        scheduler=scheduler,
        strength=strength,
        init_image=image_name,
    )

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
    seamless_x: bool = False,
    seamless_y: bool = False,
    control_image_name: str | None = None,
    control_model: dict[str, Any] | None = None,
    control_weight: float = 0.8,
    canny_low: int = 100,
    canny_high: int = 200,
    ip_image_name: str | None = None,
    ip_model: dict[str, Any] | None = None,
    ip_weight: float = 0.7,
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
    modules = dict(
        seamless_x=seamless_x,
        seamless_y=seamless_y,
        control_image_name=control_image_name,
        control_model=control_model,
        control_weight=control_weight,
        canny_low=canny_low,
        canny_high=canny_high,
        ip_image_name=ip_image_name,
        ip_model=ip_model,
        ip_weight=ip_weight,
    )
    if base.startswith("flux"):
        return build_flux_graph(**kwargs)  # type: ignore[arg-type]
    if base == "cogview4":
        return build_cogview4_graph(**kwargs)  # type: ignore[arg-type]
    if base == "sdxl":
        return build_sdxl_graph(**kwargs, **modules)  # type: ignore[arg-type]
    if base == "sd-1":
        return build_sd1_graph(**kwargs, **modules)  # type: ignore[arg-type]
    raise InvokeAIError(
        f"Unsupported model base '{base}' for graph building. Supported: sd-1, sdxl, flux.",
        error_type="unsupported_model",
    )
