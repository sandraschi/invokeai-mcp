"""invokeai_generate - txt2img, img2img, inpaint, upscale graph enqueue."""

from __future__ import annotations

from typing import Annotated, Literal

from fastmcp import Context
from pydantic import Field

from invokeai_mcp.client import InvokeAIClient, InvokeAIError
from invokeai_mcp.graphs import build_generation_graph
from invokeai_mcp.runtime import get_client, get_settings, log
from invokeai_mcp.server import mcp

_SCHEDULERS = Literal[
    "euler", "euler_a", "dpmpp_2m", "dpmpp_2m_sde", "dpmpp_3m_sde", "dpmpp_sde", "ddim", "unipc"
]


async def _resolve_model(client: InvokeAIClient, model_key: str | None) -> dict:
    """Pick the requested model or the first main model, enriched with the
    full record (the list endpoint omits the hash the graph loader needs)."""
    if not client.models_cache:
        await client.refresh_models()
    if model_key:
        match = None
        for m in client.models_cache.get("main", []):
            if m.get("key") == model_key or m.get("name", "").lower() == model_key.lower():
                match = m
                break
        if not match:
            raise InvokeAIError(
                f"Model '{model_key}' not found. Use invokeai_models list to see keys.",
                error_type="not_found",
            )
    else:
        mains = client.models_cache.get("main", [])
        if not mains:
            raise InvokeAIError(
                "No main models installed. Install one via invokeai_models (e.g. SDXL or Flux) first.",
                error_type="no_model",
            )
        match = mains[0]
    try:
        return await client.get_model(match["key"])
    except InvokeAIError:
        return match


@mcp.tool()
async def invokeai_generate(
    operation: Annotated[
        Literal["txt2img", "img2img", "inpaint", "upscale"],
        Field(description="Generation operation to run."),
    ],
    prompt: Annotated[
        str,
        Field(description="Positive prompt describing the desired image (not needed for upscale)."),
    ] = "",
    negative_prompt: Annotated[
        str | None, Field(description="Elements to avoid in the image.")
    ] = None,
    model_key: Annotated[
        str | None,
        Field(description="Model key or name from invokeai_models. Defaults to first main model."),
    ] = None,
    image_name: Annotated[
        str | None,
        Field(description="Source image for img2img / inpaint / upscale (InvokeAI image_name)."),
    ] = None,
    mask_image_name: Annotated[
        str | None, Field(description="Mask image for inpaint (white = regenerate region).")
    ] = None,
    width: Annotated[int, Field(description="Image width in pixels.", ge=64, le=2048)] = 512,
    height: Annotated[int, Field(description="Image height in pixels.", ge=64, le=2048)] = 512,
    steps: Annotated[int, Field(description="Denoising steps (1-150).", ge=1, le=150)] = 30,
    cfg_scale: Annotated[
        float, Field(description="Prompt guidance scale (1.0-20.0).", ge=1.0, le=20.0)
    ] = 7.5,
    scheduler: Annotated[_SCHEDULERS, Field(description="Sampling scheduler.")] = "euler",
    seed: Annotated[
        int | None, Field(description="Random seed for reproducibility. Omit for a random seed.")
    ] = None,
    strength: Annotated[
        float,
        Field(description="img2img/inpaint transformation strength (0.0-1.0).", ge=0.0, le=1.0),
    ] = 0.75,
    seamless_x: Annotated[bool, Field(description="Seamless tiling along X (textures).")] = False,
    seamless_y: Annotated[bool, Field(description="Seamless tiling along Y (textures).")] = False,
    control_image_name: Annotated[
        str | None,
        Field(description="Control image for ControlNet (canny edge detection is applied)."),
    ] = None,
    control_model: Annotated[
        dict | None,
        Field(description="ControlNet model record (type=controlnet) from invokeai_models list."),
    ] = None,
    control_weight: Annotated[
        float, Field(description="ControlNet influence (0.0-1.0).", ge=0.0, le=1.0)
    ] = 0.8,
    canny_low: Annotated[int, Field(description="Canny low threshold.", ge=0, le=255)] = 100,
    canny_high: Annotated[int, Field(description="Canny high threshold.", ge=0, le=255)] = 200,
    ip_image_name: Annotated[
        str | None, Field(description="Reference image for IP-Adapter style transfer.")
    ] = None,
    ip_model: Annotated[
        dict | None,
        Field(description="IP-Adapter model record (type=ip_adapter) from invokeai_models list."),
    ] = None,
    ip_weight: Annotated[
        float, Field(description="IP-Adapter influence (0.0-1.0).", ge=0.0, le=1.0)
    ] = 0.7,
    runs: Annotated[int, Field(description="Number of images to generate (1-8).", ge=1, le=8)] = 1,
    ctx: Context | None = None,  # noqa: B008
) -> dict:
    """Generate images through the local InvokeAI creative engine.

    [RATIONALE]
    All generation paths share one enqueue flow (graph build -> queue batch),
    so they live under a single portmanteau with an operation discriminator
    instead of four near-identical tools.

    - txt2img: text prompt to a fresh image.
    - img2img: transform an existing image (needs image_name, uses strength).
    - inpaint: regenerate a masked region (needs image_name + mask_image_name).
    - upscale: RealESRGAN 4x upscale of an existing image (needs image_name).

    The job is enqueued and runs asynchronously; poll completion with
    invokeai_queue(operation="item_status" or "result").

    ## Return Format
    {"success": bool, "queue_item_id": int, "batch_id": str, "message": str,
     "poll": {"tool": "invokeai_queue", "args": {...}}}

    ## Examples
    invokeai_generate(operation="txt2img", prompt="neon cyberpunk city at night, rain")
    invokeai_generate(operation="img2img", prompt="make it a watercolor painting", image_name="abc123.png", strength=0.6)
    invokeai_generate(operation="upscale", image_name="abc123.png")

    Notes:
     - InvokeAI must be running (onboarding) and a main model installed.
     - Model base determines graph family: sd-1, sdxl, flux.
    """
    client = get_client()
    settings = get_settings()
    if operation in ("img2img", "inpaint", "upscale") and not image_name:
        return {
            "success": False,
            "error": "validation",
            "message": f"{operation} requires image_name (an InvokeAI image from the gallery).",
        }
    if operation in ("txt2img", "img2img", "inpaint") and not prompt.strip():
        return {
            "success": False,
            "error": "validation",
            "message": f"{operation} requires a prompt.",
        }

    try:
        model = await _resolve_model(client, model_key)
        eff_width, eff_height = width, height
        if image_name:
            # image-based modes: noise/latents must match the source image size
            try:
                dto = await client.get_image(image_name)
                if dto.get("width") and dto.get("height"):
                    eff_width, eff_height = int(dto["width"]), int(dto["height"])
            except InvokeAIError:
                pass
        graph = build_generation_graph(
            operation=operation,
            model=model,
            positive_prompt=prompt,
            negative_prompt=negative_prompt or "",
            width=eff_width,
            height=eff_height,
            steps=steps,
            cfg_scale=cfg_scale,
            scheduler=scheduler,
            seed=seed,
            strength=strength,
            image_name=image_name,
            mask_image_name=mask_image_name,
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
        result = await client.enqueue_batch(graph, runs=runs, destination="mcp")
        queue_id = result.get("queue_id") or settings.queue_id
        items = result.get("queue_item_ids") or result.get("queue_item_id") or []
        if isinstance(items, int):
            items = [items]
        first = items[0] if items else None
        log(
            "INFO", "generate", f"{operation} enqueued: batch={result.get('batch_id')} item={first}"
        )
        return {
            "success": True,
            "queue_item_id": first,
            "queue_item_ids": items,
            "batch_id": result.get("batch_id"),
            "queue_id": queue_id,
            "message": f"{operation} job enqueued (item {first}). Poll with invokeai_queue(operation='item_status').",
            "poll": {
                "tool": "invokeai_queue",
                "args": {"operation": "item_status", "item_id": first},
            },
        }
    except InvokeAIError as exc:
        return {
            "success": False,
            "error": exc.error_type,
            "message": exc.message,
            "dialogic": {
                "suggestion": "Verify InvokeAI is running and reachable, then retry.",
                "remediation": "invokeai_system(operation='health')",
            },
        }
