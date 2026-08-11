"""invokeai_queue - queue status, listing, control, and result retrieval."""

from __future__ import annotations

import time
from typing import Annotated, Literal

from fastmcp import Context
from pydantic import Field

from invokeai_mcp.client import InvokeAIError
from invokeai_mcp.runtime import get_client, get_settings
from invokeai_mcp.server import mcp


@mcp.tool()
async def invokeai_queue(
    operation: Annotated[
        Literal[
            "status",
            "list",
            "item_status",
            "result",
            "cancel",
            "cancel_batch",
            "clear",
            "resume",
            "pause",
        ],
        Field(description="Queue operation to perform."),
    ],
    item_id: Annotated[
        int | None, Field(description="Queue item id (required for item_status, result, cancel).")
    ] = None,
    batch_ids: Annotated[
        list[str] | None, Field(description="Batch ids to cancel (cancel_batch).")
    ] = None,
    limit: Annotated[int, Field(description="Max items to list.", ge=1, le=100)] = 20,
    status_filter: Annotated[
        str | None,
        Field(
            description="Filter list by status (pending, in_progress, completed, failed, canceled)."
        ),
    ] = None,
    download_image: Annotated[
        bool,
        Field(
            description="For 'result': save the output image to the local download dir and return its path."
        ),
    ] = False,
    wait_seconds: Annotated[
        int | None,
        Field(
            description="For 'result': poll until the item completes (max seconds), then return outputs."
        ),
    ] = None,
    ctx: Context | None = None,  # noqa: B008
) -> dict:
    """Manage the InvokeAI generation queue and retrieve results.

    [RATIONALE]
    Queue lifecycle (inspect, control, and harvest outputs) is one domain, so
    all operations share this portmanteau. 'result' is the natural partner of
    invokeai_generate: it polls an item to completion and returns the output
    image URLs (or downloads the file locally).

    ## Return Format
    {"success": bool, "operation": str, "data": {...}, "message": str}

    ## Examples
    invokeai_queue(operation="status")
    invokeai_queue(operation="list", status_filter="completed", limit=10)
    invokeai_queue(operation="result", item_id=123, wait_seconds=120, download_image=True)
    invokeai_queue(operation="cancel_batch", batch_ids=["batch-uuid"])

    Notes:
     - result polls every 3s up to wait_seconds; use wait_seconds for synchronous flows.
     - Without wait_seconds, result returns the current item state immediately.
    """
    client = get_client()
    settings = get_settings()
    try:
        if operation == "status":
            data = await client.queue_status()
            return {
                "success": True,
                "operation": operation,
                "data": data,
                "message": f"Queue: {data.get('queued', 0)} queued, {data.get('in_progress', 0)} in progress.",
            }
        if operation == "list":
            items = await client.queue_list(limit=limit)
            if status_filter:
                items = [
                    i for i in items if (i.get("status") or "").lower() == status_filter.lower()
                ]
            return {
                "success": True,
                "operation": operation,
                "data": {"items": items, "count": len(items)},
                "message": f"{len(items)} queue items.",
            }
        if operation == "item_status":
            if item_id is None:
                return _missing(item_id, "item_status")
            data = await client.queue_item(item_id)
            status = data.get("status", "unknown")
            return {
                "success": True,
                "operation": operation,
                "data": data,
                "message": f"Item {item_id}: {status}.",
            }
        if operation == "result":
            if item_id is None:
                return _missing(item_id, "result")
            data = await client.queue_item(item_id)
            if wait_seconds and (data.get("status") not in ("completed", "failed", "canceled")):
                deadline = time.time() + wait_seconds
                while time.time() < deadline:
                    time.sleep(3)
                    data = await client.queue_item(item_id)
                    if data.get("status") in ("completed", "failed", "canceled"):
                        break
            status = data.get("status", "unknown")
            outputs = []
            session = data.get("session_id")
            if status == "completed" and session:
                result = await client.session_result(session, item_id)
                outputs = _extract_images(result)
            payload: dict = {"item": data, "status": status, "outputs": outputs}
            if download_image and outputs:
                saved = []
                for out in outputs[:1]:
                    name = out.get("image_name") or out.get("image_name")
                    if not name:
                        continue
                    dest = settings.download_dir / name
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    await client.download_image(name, dest)
                    out["local_path"] = str(dest)
                    saved.append(str(dest))
                payload["local_paths"] = saved
                message = f"Item {item_id}: {status}. Saved to {saved}"
            else:
                message = f"Item {item_id}: {status}." + (
                    f" {len(outputs)} output image(s)." if outputs else ""
                )
            return {
                "success": status != "failed",
                "operation": operation,
                "data": payload,
                "message": message,
            }
        if operation == "cancel":
            if item_id is None:
                return _missing(item_id, "cancel")
            await client.queue_cancel(item_id)
            return {
                "success": True,
                "operation": operation,
                "message": f"Cancelled item {item_id}.",
            }
        if operation == "cancel_batch":
            if not batch_ids:
                return _missing(batch_ids, "cancel_batch")
            await client.queue_cancel_batch(batch_ids)
            return {
                "success": True,
                "operation": operation,
                "message": f"Cancelled batches {batch_ids}.",
            }
        if operation == "clear":
            await client.queue_clear()
            return {"success": True, "operation": operation, "message": "Queue cleared."}
        if operation == "resume":
            await client.queue_resume()
            return {"success": True, "operation": operation, "message": "Queue processor resumed."}
        if operation == "pause":
            await client.queue_pause()
            return {"success": True, "operation": operation, "message": "Queue processor paused."}
    except InvokeAIError as exc:
        return {
            "success": False,
            "error": exc.error_type,
            "message": exc.message,
            "dialogic": {
                "suggestion": "InvokeAI queue API unreachable.",
                "remediation": "invokeai_system(operation='health')",
            },
        }
    return {"success": False, "error": "validation", "message": f"Unknown operation: {operation}"}


def _missing(value: object, op: str) -> dict:
    return {
        "success": False,
        "error": "validation",
        "message": f"Missing required argument for {op}.",
        "dialogic": {
            "suggestion": "Pass the required id argument.",
            "remediation": f"invokeai_queue(operation='{op}', ...)",
        },
    }


def _extract_images(result: dict) -> list[dict]:
    """Walk a session result envelope for output images."""
    images: list[dict] = []
    for item in result.get("items", []):
        outputs = item.get("outputs") or item.get("result", {}).get("outputs") or []
        for out in outputs:
            if isinstance(out, dict):
                if "image" in out:
                    images.append({"image_name": out["image"]["image_name"]})
                elif out.get("type") == "image_output" and out.get("image"):
                    images.append({"image_name": out["image"]["image_name"]})
    return images
