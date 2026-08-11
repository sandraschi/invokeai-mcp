"""Prefab UI cards for list/status/stats surfaces (fleet mandate)."""

from __future__ import annotations

from typing import Annotated

from fastmcp import Context
from fastmcp.tools import ToolResult
from prefab_ui import PrefabApp
from prefab_ui.components import Card, CardContent, CardHeader, CardTitle, Div, Heading, Row, Text
from pydantic import Field

from invokeai_mcp.client import InvokeAIError
from invokeai_mcp.runtime import get_client, get_settings
from invokeai_mcp.server import mcp


def _kv(label: str, value: str) -> None:
    with Row(gap=2, justify="between"):
        Text(label, css_class="text-slate-500 text-xs")
        Text(value, css_class="text-slate-200 text-xs font-mono")


def _error_card(message: str, title: str = "Unavailable") -> ToolResult:
    with Card(css_class="max-w-md") as view:
        with CardHeader():
            CardTitle(title)
        with CardContent():
            Text(message)
    return ToolResult(
        content=message, structured_content=PrefabApp(view=view, title=title), is_error=True
    )


@mcp.tool()
async def show_invokeai_dashboard_card(ctx: Context | None = None) -> ToolResult:
    """Show InvokeAI fleet status (version, queue, model counts) as a rich card.

    ## Return Format
    ToolResult with PrefabApp card; plain text fallback in content.

    ## Examples
    show_invokeai_dashboard_card()
    """
    client = get_client()
    settings = get_settings()
    try:
        version = await client.app_version()
        queue = await client.queue_status()
        models = await client.list_models(model_type="main", limit=50)
        with PrefabApp(title="InvokeAI Status") as app:
            Heading("InvokeAI Status")
            _kv("Version", str(version.get("version", "?")))
            _kv("Engine", version.get("app", "invokeai"))
            _kv("Models (main)", str(len(models)))
            _kv("Queue pending", str(queue.get("queued", 0)))
            _kv("In progress", str(queue.get("in_progress", 0)))
            Div()
            Text(f"Running at {settings.invokeai_url}", css_class="text-slate-500 text-xs")
        summary = f"InvokeAI {version.get('version')}: {len(models)} main models, queue {queue.get('queued', 0)} pending."
        return ToolResult(content=summary, structured_content=app)
    except InvokeAIError as exc:
        return _error_card(str(exc))


@mcp.tool()
async def show_invokeai_queue_card(ctx: Context | None = None) -> ToolResult:
    """Show the generation queue status as a rich card.

    ## Return Format
    ToolResult with PrefabApp card; plain text fallback in content.

    ## Examples
    show_invokeai_queue_card()
    """
    client = get_client()
    try:
        status = await client.queue_status()
        with PrefabApp(title="InvokeAI Queue") as app:
            Heading("Queue Status")
            _kv("Queued", str(status.get("queued", 0)))
            _kv("In progress", str(status.get("in_progress", 0)))
            _kv("Completed", str(status.get("completed", 0)))
            _kv("Failed", str(status.get("failed", 0)))
            _kv("Canceled", str(status.get("canceled", 0)))
        summary = f"Queue: {status.get('queued', 0)} queued, {status.get('in_progress', 0)} running, {status.get('failed', 0)} failed."
        return ToolResult(content=summary, structured_content=app)
    except InvokeAIError as exc:
        return _error_card(str(exc))


@mcp.tool()
async def show_invokeai_models_card(
    model_type: Annotated[
        str,
        Field(
            description="Model type to list: main, lora, vae, controlnet, spandrel_image_to_image."
        ),
    ] = "main",
    ctx: Context | None = None,
) -> ToolResult:
    """Show installed models of a type as a rich card.

    ## Return Format
    ToolResult with PrefabApp card; plain text fallback in content.

    ## Examples
    show_invokeai_models_card(model_type="main")
    """
    client = get_client()
    try:
        models = await client.list_models(model_type=model_type, limit=25)
        with PrefabApp(title=f"Models ({model_type})") as app:
            Heading(f"{model_type.capitalize()} models: {len(models)}")
            for m in models[:20]:
                _kv(m.get("name", "?"), m.get("key", "")[:28])
        summary = f"{len(models)} {model_type} models installed."
        return ToolResult(content=summary, structured_content=app)
    except InvokeAIError as exc:
        return _error_card(str(exc))


@mcp.tool()
async def show_invokeai_gallery_card(
    limit: Annotated[int, Field(description="Number of recent images to show.", ge=1, le=12)] = 6,
    ctx: Context | None = None,
) -> ToolResult:
    """Show the most recent gallery images as a rich card.

    ## Return Format
    ToolResult with PrefabApp card; plain text fallback in content.

    ## Examples
    show_invokeai_gallery_card(limit=6)
    """
    client = get_client()
    settings = get_settings()
    try:
        data = await client.gallery_items(limit=limit)
        items = data.get("items", [])
        with PrefabApp(title="Recent Images") as app:
            Heading(f"Recent images: {len(items)}")
            for i in items[:12]:
                name = i.get("image_name", "?")
                _kv(name[:40], f"{settings.api_base}/api/v1/images/i/{name}/full")
        summary = f"{len(items)} recent images (urls in data)."
        return ToolResult(content=summary, structured_content=app)
    except InvokeAIError as exc:
        return _error_card(str(exc))
