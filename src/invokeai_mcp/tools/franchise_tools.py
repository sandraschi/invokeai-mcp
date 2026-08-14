"""invokeai_franchises - fan-style IP preset catalog (Mario, Ghibli, 40k...)."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import Field

from invokeai_mcp.franchises import (
    get_franchise,
    list_franchises,
    search_franchises,
)
from invokeai_mcp.server import mcp


@mcp.tool()
async def invokeai_franchises(
    operation: Annotated[
        Literal["list", "get", "search"],
        Field(description="Franchise preset operation to perform."),
    ],
    franchise_id: Annotated[
        str | None, Field(description="Franchise id (required for get).")
    ] = None,
    query: Annotated[
        str | None, Field(description="Free-text search across franchise ids, names, signatures.")
    ] = None,
    limit: Annotated[int, Field(description="Max franchises to return.", ge=1, le=100)] = 30,
) -> dict:
    """Look up the fan-style franchise preset catalog (Mario, Pokemon, Ghibli,
    Warhammer 40k, Disney, ...) for style anchoring.

    [RATIONALE]
    Franchise presets are a curated, shared catalog - one tool keeps agents
    from hardcoding "in the style of X" and enables batches via
    invokeai_generate(franchises=[...]).

    ## Return Format
    {"success": bool, "operation": str, "franchises": [...], "count": int, "total": int}

    ## Examples
    invokeai_franchises(operation="list")
    invokeai_franchises(operation="get", franchise_id="super-mario")
    invokeai_franchises(operation="search", query="ghibli")

    Notes:
     - Franchise anchors are appended LAST in the prompt (strongest cue):
       base -> style -> material -> painter -> franchise.
     - These are fan-style descriptors for personal creative use, not
       official products.
    """
    if operation == "get":
        if not franchise_id:
            return {
                "success": False,
                "error": "validation",
                "message": "Missing required argument 'franchise_id' for get.",
            }
        franchise = get_franchise(franchise_id)
        if not franchise:
            return {
                "success": False,
                "error": "not_found",
                "message": f"Unknown franchise '{franchise_id}'. Use list to see valid ids.",
            }
        return {"success": True, "operation": operation, "franchises": [franchise], "count": 1}
    if operation == "search":
        if not query:
            return {
                "success": False,
                "error": "validation",
                "message": "Missing required argument 'query' for search.",
            }
        hits = search_franchises(query, limit=limit)
        return {"success": True, "operation": operation, "franchises": hits, "count": len(hits)}
    franchises = list_franchises()
    return {
        "success": True,
        "operation": operation,
        "franchises": franchises[:limit],
        "count": min(len(franchises), limit),
        "total": len(franchises),
    }
