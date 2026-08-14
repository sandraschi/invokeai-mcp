"""invokeai_generate - txt2img, img2img, inpaint, upscale graph enqueue."""

from __future__ import annotations

import random
from typing import Annotated, Any, Literal

from fastmcp import Context
from pydantic import Field

from invokeai_mcp.client import InvokeAIClient, InvokeAIError
from invokeai_mcp.graphs import build_generation_graph
from invokeai_mcp.runtime import get_client, get_settings, log
from invokeai_mcp.server import mcp

_SCHEDULERS = Literal[
    "euler", "euler_a", "dpmpp_2m", "dpmpp_2m_sde", "dpmpp_3m_sde", "dpmpp_sde", "ddim", "unipc"
]


def _random_seed() -> int:
    """Cryptographically random seed - None used to collapse to the graph
    default (0), which made every batch job start from identical noise."""
    return random.SystemRandom().randint(0, 0xFFFF_FFFF)


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
    styles: Annotated[
        list[str] | None,
        Field(
            description="Style ids from invokeai_styles list. Each style appends its "
            "prompt suffix and enqueues one item (multi-style batch). "
            "style_cfg=False keeps the explicit steps/cfg_scale for every item."
        ),
    ] = None,
    style_cfg: Annotated[
        bool,
        Field(description="Apply each style's cfg/steps when styles are used (default true)."),
    ] = True,
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

    style_set: list[dict] | None = None
    if styles:
        from invokeai_mcp.styles import get_style

        style_set = []
        for sid in styles:
            s = get_style(sid)
            if not s:
                return {
                    "success": False,
                    "error": "not_found",
                    "message": f"Unknown style '{sid}'. Use invokeai_styles(operation='list') for valid ids.",
                }
            style_set.append(s)

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

        from invokeai_mcp.styles import apply_style

        jobs: list[dict] = [{"prompt": prompt, "negative": negative_prompt, "steps": steps, "cfg": cfg_scale}]
        if style_set:
            jobs = []
            for s in style_set:
                job: dict = {
                    "prompt": apply_style(s, prompt),
                    "negative": negative_prompt if negative_prompt is not None else s.get("negative") or "",
                }
                if style_cfg:
                    job["steps"] = int(s.get("steps") or steps)
                    job["cfg"] = float(s.get("cfg") or cfg_scale)
                else:
                    job["steps"] = steps
                    job["cfg"] = cfg_scale
                jobs.append(job)

        items: list[int] = []
        batch_ids: list[str] = []
        queue_id = settings.queue_id
        if style_set:
            style_ids_for_jobs = [[s["id"]] for s in style_set]
        else:
            style_ids_for_jobs = [[] for _ in jobs]
        for job, job_style_ids in zip(jobs, style_ids_for_jobs, strict=True):
            job_seed = seed if seed is not None else _random_seed()
            graph = build_generation_graph(
                operation=operation,
                model=model,
                positive_prompt=job["prompt"],
                negative_prompt=job["negative"],
                width=eff_width,
                height=eff_height,
                steps=job["steps"],
                cfg_scale=job["cfg"],
                scheduler=scheduler,
                seed=job_seed,
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
            if result.get("queue_id"):
                queue_id = result.get("queue_id")
            job_items_raw = result.get("queue_item_ids") or result.get("queue_item_id")
            if isinstance(job_items_raw, int):
                job_items: list[Any] = [job_items_raw]
            elif isinstance(job_items_raw, list):
                job_items = job_items_raw
            else:
                job_items = []
            if job_items:
                items.extend(job_items)
            bid = result.get("batch_id")
            if bid:
                batch_ids.append(str(bid))
            from invokeai_mcp.attribution import record_items

            await record_items(
                [int(i) for i in job_items if isinstance(i, int)],
                styles=job_style_ids,
                model_key=model.get("key") if model else None,
                prompt=job["prompt"],
            )
        first = items[0] if items else None
        log(
            "INFO", "generate", f"{operation} enqueued: {len(items)} item(s) batch={batch_ids[0] if batch_ids else None}"
        )
        return {
            "success": True,
            "queue_item_id": first,
            "queue_item_ids": items,
            "batch_id": batch_ids[0] if batch_ids else None,
            "batch_ids": batch_ids,
            "queue_id": queue_id,
            "style_count": len(style_set) if style_set else None,
            "message": f"{operation} job enqueued ({len(items)} item(s), first {first}). Poll with invokeai_queue(operation='item_status').",
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
