"""invokeai_models - model manager: list, install, update, delete."""

from __future__ import annotations

from typing import Annotated, Literal

from fastmcp import Context
from pydantic import Field

from invokeai_mcp.client import InvokeAIError
from invokeai_mcp.runtime import get_client, log
from invokeai_mcp.server import mcp


@mcp.tool()
async def invokeai_models(
    operation: Annotated[
        Literal["list", "get", "install", "update", "delete", "installs", "stats"],
        Field(description="Model manager operation to perform."),
    ],
    model_type: Annotated[
        str | None,
        Field(
            description="Filter by model type: main, lora, vae, controlnet, embedding, spandrel_image_to_image."
        ),
    ] = None,
    search: Annotated[str | None, Field(description="Search filter on model name.")] = None,
    key: Annotated[
        str | None, Field(description="Model key (required for get, update, delete).")
    ] = None,
    source: Annotated[
        str | None,
        Field(
            description="Install source: HF repo id, Civitai URL, or local path (required for install)."
        ),
    ] = None,
    config: Annotated[
        dict | None, Field(description="Install config overrides: {name, type, base, description}.")
    ] = None,
    limit: Annotated[int, Field(description="Max models to return.", ge=1, le=200)] = 100,
    ctx: Context | None = None,  # noqa: B008
) -> dict:
    """Manage installed models in the local InvokeAI instance.

    [RATIONALE]
    Model lifecycle (discovery, install from HF/Civitai, config, removal) is a
    single domain with a shared record store, so all operations live under
    this portmanteau.

    Sources accepted by install: HuggingFace repo ids (e.g.
    "stabilityai/stable-diffusion-xl-base-1.0"), Civitai model URLs, or local
    paths. Install runs asynchronously; poll with operation='installs'.

    ## Return Format
    {"success": bool, "operation": str, "data": {...}, "message": str}

    ## Examples
    invokeai_models(operation="list", model_type="main")
    invokeai_models(operation="install", source="stabilityai/stable-diffusion-xl-base-1.0", config={"name": "SDXL Base"})
    invokeai_models(operation="delete", key="sdxl-main")

    Notes:
     - model_type values follow InvokeAI taxonomy (main, lora, vae, ...).
     - Install may download multiple GB; check operation='installs' for progress.
    """
    client = get_client()
    try:
        if operation == "list":
            models = await client.list_models(
                model_type=model_type or "main", search=search, limit=limit
            )
            if search and not models:
                models = await client.list_models(model_type=model_type or "main", limit=limit)
                models = [m for m in models if search.lower() in (m.get("name") or "").lower()]
            client.models_cache = {"main": [m for m in models if m.get("type") == "main"]}
            return {
                "success": True,
                "operation": operation,
                "data": {"models": models, "count": len(models)},
                "message": f"{len(models)} model(s).",
            }
        if operation == "get":
            if not key:
                return _missing("key", operation)
            data = await client.get_model(key)
            return {
                "success": True,
                "operation": operation,
                "data": data,
                "message": f"Model {key}.",
            }
        if operation == "install":
            if not source:
                return _missing("source", operation)
            data = await client.install_model(source, config=config or {})
            log("INFO", "models", f"install started: {source} -> {data.get('id')}")
            return {
                "success": True,
                "operation": operation,
                "data": data,
                "message": f"Install started ({data.get('id')}). Poll with invokeai_models(operation='installs').",
            }
        if operation == "installs":
            jobs = await client.list_model_installs()
            return {
                "success": True,
                "operation": operation,
                "data": {"jobs": jobs, "count": len(jobs)},
                "message": f"{len(jobs)} install job(s).",
            }
        if operation == "update":
            if not key:
                return _missing("key", operation)
            data = await client.update_model(key, config or {})
            return {
                "success": True,
                "operation": operation,
                "data": data,
                "message": f"Model {key} updated.",
            }
        if operation == "delete":
            if not key:
                return _missing("key", operation)
            await client.delete_model(key)
            log("WARNING", "models", f"deleted model {key}")
            return {"success": True, "operation": operation, "message": f"Model {key} deleted."}
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
            "error": exc.error_type,
            "message": exc.message,
            "dialogic": {
                "suggestion": "Model manager API unreachable or invalid source.",
                "remediation": "invokeai_system(operation='health')",
            },
        }
    return {"success": False, "error": "validation", "message": f"Unknown operation: {operation}"}


def _missing(arg: str, op: str) -> dict:
    return {
        "success": False,
        "error": "validation",
        "message": f"Missing required argument '{arg}' for {op}.",
        "dialogic": {
            "suggestion": "Provide the missing argument.",
            "remediation": f"invokeai_models(operation='{op}', {arg}=...)",
        },
    }
