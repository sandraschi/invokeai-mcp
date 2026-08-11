"""invokeai_workflows - workflow CRUD against the InvokeAI workflow store."""

from __future__ import annotations

import json
from typing import Annotated, Literal

from fastmcp import Context
from pydantic import Field

from invokeai_mcp.client import InvokeAIError
from invokeai_mcp.runtime import get_client, log
from invokeai_mcp.server import mcp


@mcp.tool()
async def invokeai_workflows(
    operation: Annotated[
        Literal["list", "get", "save", "delete"],
        Field(description="Workflow operation to perform."),
    ],
    workflow_id: Annotated[
        str | None, Field(description="Workflow id (required for get, delete).")
    ] = None,
    workflow_json: Annotated[
        str | None, Field(description="Raw workflow JSON string (required for save).")
    ] = None,
    limit: Annotated[int, Field(description="Max workflows to list.", ge=1, le=100)] = 50,
    offset: Annotated[int, Field(description="Pagination offset.", ge=0)] = 0,
    ctx: Context | None = None,  # noqa: B008
) -> dict:
    """Manage InvokeAI node workflows (list, get, save, delete).

    [RATIONALE]
    Workflows are stored artifacts in a single store; CRUD plus export share
    this portmanteau. Running a workflow graph goes through invokeai_generate
    or a raw enqueue - this tool manages the stored workflow library.

    ## Return Format
    {"success": bool, "operation": str, "data": {...}, "message": str}

    ## Examples
    invokeai_workflows(operation="list")
    invokeai_workflows(operation="get", workflow_id="wf-uuid")
    invokeai_workflows(operation="save", workflow_json='{"nodes": {...}}')

    Notes:
     - workflow_json must be a full InvokeAI workflow object (id, nodes, edges).
     - Save with an existing id updates; without one, creates.
    """
    client = get_client()
    try:
        if operation == "list":
            workflows = await client.list_workflows(limit=limit, offset=offset)
            return {
                "success": True,
                "operation": operation,
                "data": {"workflows": workflows, "count": len(workflows)},
                "message": f"{len(workflows)} workflow(s).",
            }
        if operation == "get":
            if not workflow_id:
                return _missing("workflow_id", operation)
            data = await client.get_workflow(workflow_id)
            return {
                "success": True,
                "operation": operation,
                "data": data,
                "message": f"Workflow {workflow_id}.",
            }
        if operation == "save":
            if not workflow_json:
                return _missing("workflow_json", operation)
            try:
                parsed = json.loads(workflow_json)
            except json.JSONDecodeError as exc:
                return {
                    "success": False,
                    "error": "validation",
                    "message": f"workflow_json is not valid JSON: {exc}",
                }
            data = await client.save_workflow(parsed)
            log("INFO", "workflows", f"saved workflow {data.get('id')}")
            return {
                "success": True,
                "operation": operation,
                "data": data,
                "message": f"Workflow saved ({data.get('id')}).",
            }
        if operation == "delete":
            if not workflow_id:
                return _missing("workflow_id", operation)
            await client.delete_workflow(workflow_id)
            log("WARNING", "workflows", f"deleted workflow {workflow_id}")
            return {
                "success": True,
                "operation": operation,
                "message": f"Workflow {workflow_id} deleted.",
            }
    except InvokeAIError as exc:
        return {
            "success": False,
            "error": exc.error_type,
            "message": exc.message,
            "dialogic": {
                "suggestion": "Workflow API unreachable.",
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
            "remediation": f"invokeai_workflows(operation='{op}', {arg}=...)",
        },
    }
