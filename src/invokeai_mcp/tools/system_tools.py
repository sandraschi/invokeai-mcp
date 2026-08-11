"""invokeai_system + invokeai_help + invokeai_shutdown."""

from __future__ import annotations

import asyncio
import os
from typing import Annotated, Literal

from fastmcp import Context
from pydantic import Field

from invokeai_mcp import __version__
from invokeai_mcp.client import InvokeAIError
from invokeai_mcp.runtime import get_client, get_settings, log
from invokeai_mcp.server import mcp

_HELP_INDEX = """## InvokeAI MCP - help index

Bridge between Claude/Cursor/opencode and your local InvokeAI creative engine
(RTX 4090 powered: SDXL, Flux, SD3.5, Qwen Image, and more).

Tools:
- invokeai_generate: txt2img / img2img / inpaint / upscale (enqueues jobs)
- invokeai_queue: status, list, item_status, result, cancel, clear, resume
- invokeai_models: list, install (HF/Civitai), update, delete, installs, stats
- invokeai_gallery: list, search, get, metadata, download, delete, star
- invokeai_boards: list, create, update, delete, add/remove image
- invokeai_workflows: list, get, save, delete
- show_invokeai_*_card: Prefab cards (dashboard, queue, models, gallery)

Workflow: generate -> poll queue -> gallery -> download.

Topics: tools, install, onboarding, api_keys, troubleshooting
"""


@mcp.tool()
async def invokeai_system(
    operation: Annotated[
        Literal["health", "version", "config", "stats"],
        Field(description="System operation to perform."),
    ],
    ctx: Context | None = None,  # noqa: B008
) -> dict:
    """Check InvokeAI connectivity, version, and runtime configuration.

    [RATIONALE]
    System introspection (health, version, config, cache stats) is one domain
    and the standard first call for onboarding and debugging.

    ## Return Format
    {"success": bool, "operation": str, "data": {...}, "message": str,
     "configured": bool}

    ## Examples
    invokeai_system(operation="health")
    invokeai_system(operation="version")

    Notes:
     - health returns configured=false when InvokeAI is not reachable
       (drives the webapp onboarding cue).
    """
    client = get_client()
    settings = get_settings()
    try:
        if operation == "health":
            ok = await client.ping()
            return {
                "success": True,
                "configured": ok,
                "operation": operation,
                "data": {"invokeai_url": settings.invokeai_url, "reachable": ok},
                "message": "InvokeAI reachable."
                if ok
                else f"InvokeAI not reachable at {settings.invokeai_url}.",
            }
        if operation == "version":
            data = await client.app_version()
            return {
                "success": True,
                "operation": operation,
                "data": data,
                "message": f"InvokeAI {data.get('version', 'unknown')}.",
            }
        if operation == "config":
            data = await client.runtime_config()
            return {
                "success": True,
                "operation": operation,
                "data": data,
                "message": "Runtime config.",
            }
        if operation == "stats":
            data = await client.model_stats()
            return {
                "success": True,
                "operation": operation,
                "data": data,
                "message": "Model stats.",
            }
    except InvokeAIError as exc:
        return {
            "success": False,
            "configured": False,
            "error": exc.error_type,
            "message": exc.message,
            "dialogic": {
                "suggestion": "Start InvokeAI (launcher) and complete onboarding before using generation tools.",
                "remediation": "invokeai_system(operation='health')",
            },
        }
    return {"success": False, "error": "validation", "message": f"Unknown operation: {operation}"}


@mcp.tool()
async def invokeai_help(
    topic: Annotated[str | None, Field(description="Help topic, or omit for the index.")] = None,
) -> dict:
    """Get documentation for this server's tools and workflows.

    ## Return Format
    {"success": bool, "help": str}

    ## Examples
    invokeai_help()
    invokeai_help(topic="tools")
    """
    if topic:
        return {
            "success": True,
            "help": f"## InvokeAI MCP - {topic}\n\nSee docs/TOOLS.md and invokeai_help() index for the full tool surface.",
        }
    return {"success": True, "help": _HELP_INDEX}


@mcp.tool()
async def invokeai_shutdown() -> dict:
    """Gracefully shut down this MCP server.

    ## Return Format
    {"success": bool, "message": str}

    ## Examples
    invokeai_shutdown()
    """
    log("INFO", "system", f"shutdown requested (server v{__version__})")
    from invokeai_mcp.runtime import close_client

    await close_client()

    async def _stop() -> None:
        await asyncio.sleep(0.3)
        os._exit(0)

    asyncio.get_event_loop().create_task(_stop())
    return {"success": True, "message": "Shutting down."}
