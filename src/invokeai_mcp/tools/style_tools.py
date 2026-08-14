"""invokeai_styles - style catalog lookups for the generate portmanteau."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import Field

from invokeai_mcp.server import mcp
from invokeai_mcp.styles import (
    community_styles,
    get_style,
    list_styles,
    load_community,
    search_styles,
)


@mcp.tool()
async def invokeai_styles(
    operation: Annotated[
        Literal["list", "get", "search", "community"],
        Field(description="Style catalog operation to perform."),
    ],
    style_id: Annotated[
        str | None, Field(description="Style id (required for get).")
    ] = None,
    query: Annotated[
        str | None, Field(description="Free-text search across style ids, names, and prompts.")
    ] = None,
    limit: Annotated[int, Field(description="Max styles to return.", ge=1, le=300)] = 50,
) -> dict:
    """Look up generation style presets (photography, art, anime, etc.).

    [RATIONALE]
    Styles are curated prompt/parameter presets shared by the webapp and
    the MCP surface; a single catalog tool keeps agents from hardcoding
    prompts and enables multi-style batches via invokeai_generate(styles=...).

    ## Return Format
    {"success": bool, "operation": str, "styles": [...], "count": int}

    ## Examples
    invokeai_styles(operation="list")
    invokeai_styles(operation="get", style_id="photorealistic")
    invokeai_styles(operation="search", query="watercolor")
    invokeai_styles(operation="community", query="neon")

    Notes:
     - Pass style ids to invokeai_generate(styles=[...]) for a batch; each
       style appends its prompt suffix and applies its cfg/steps when
       style_cfg=True.
     - operation="community" lists styles imported from A1111 community
       packs (data/community_styles.json, 1300+); get() resolves both.
    """
    if operation == "get":
        if not style_id:
            return {
                "success": False,
                "error": "validation",
                "message": "Missing required argument 'style_id' for get.",
            }
        style = get_style(style_id)
        if not style:
            return {
                "success": False,
                "error": "not_found",
                "message": f"Unknown style '{style_id}'. Use list to see valid ids.",
            }
        return {"success": True, "operation": operation, "styles": [style], "count": 1}
    if operation == "search":
        if not query:
            return {
                "success": False,
                "error": "validation",
                "message": "Missing required argument 'query' for search.",
            }
        hits = search_styles(query, limit=limit)
        return {"success": True, "operation": operation, "styles": hits, "count": len(hits)}
    if operation == "community":
        hits = community_styles(query, limit=limit)
        return {
            "success": True,
            "operation": operation,
            "styles": hits,
            "count": len(hits),
            "total": len(load_community()),
        }
    styles = list_styles()
    return {
        "success": True,
        "operation": operation,
        "styles": styles[:limit],
        "count": min(len(styles), limit),
        "total": len(styles),
    }
