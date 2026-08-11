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
    """Pick the requested model or the first main model."""
    if not client.models_cache:
        await client.refresh_models()
    if model_key:
        for m in client.models_cache.get("main", []):
            if m.get("key") == model_key or m.get("name", "").lower() == model_key.lower():
                return m
        raise InvokeAIError(
            f"Model '{model_key}' not found. Use invokeai_models list to see keys.",
            error_type="not_found",
        )
    mains = client.models_cache.get("main", [])
    if not mains:
        raise InvokeAIError(
            "No main models installed. Install one via invokeai_models (e.g. SDXL or Flux) first.",
            error_type="no_model",
        )
    return mains[0]


@mcp.tool()
async def invokeai_generate(
    operation: Annotated[
        Literal["txt2img", "img2img", "inpaint", "upscale"],
        Field(description="Generation operation to run."),
    ],
    prompt: Annotated[str, Field(description="Positive prompt describing the desired image.")],
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

    try:
        model = await _resolve_model(client, model_key)
        graph = build_generation_graph(
            operation=operation,
            model=model,
            positive_prompt=prompt,
            negative_prompt=negative_prompt or "",
            width=width,
            height=height,
            steps=steps,
            cfg_scale=cfg_scale,
            scheduler=scheduler,
            seed=seed,
            strength=strength,
            image_name=image_name,
            mask_image_name=mask_image_name,
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
