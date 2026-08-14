"""invokeai_artists - painter catalog (Giotto to Giger) for style anchoring."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import Field

from invokeai_mcp.artists import get_artist, list_artists, search_artists
from invokeai_mcp.server import mcp


@mcp.tool()
async def invokeai_artists(
    operation: Annotated[
        Literal["list", "get", "search"],
        Field(description="Painter catalog operation to perform."),
    ],
    artist_id: Annotated[
        str | None, Field(description="Painter id (required for get).")
    ] = None,
    query: Annotated[
        str | None, Field(description="Free-text search across painter ids, names, signatures.")
    ] = None,
    limit: Annotated[int, Field(description="Max painters to return.", ge=1, le=100)] = 60,
) -> dict:
    """Look up the 60-painter catalog (Giotto to Giger) for style anchoring.

    [RATIONALE]
    Painter presets are a curated, shared catalog - one tool keeps agents
    from hardcoding "in the style of X" and enables batches via
    invokeai_generate(artists=[...]).

    ## Return Format
    {"success": bool, "operation": str, "artists": [...], "count": int, "total": int}

    ## Examples
    invokeai_artists(operation="list")
    invokeai_artists(operation="get", artist_id="giger")
    invokeai_artists(operation="search", query="impressionist")

    Notes:
     - Painter anchors are appended LAST in the prompt (strongest cue):
       base -> style -> material -> painter.
    """
    if operation == "get":
        if not artist_id:
            return {
                "success": False,
                "error": "validation",
                "message": "Missing required argument 'artist_id' for get.",
            }
        artist = get_artist(artist_id)
        if not artist:
            return {
                "success": False,
                "error": "not_found",
                "message": f"Unknown painter '{artist_id}'. Use list to see valid ids.",
            }
        return {"success": True, "operation": operation, "artists": [artist], "count": 1}
    if operation == "search":
        if not query:
            return {
                "success": False,
                "error": "validation",
                "message": "Missing required argument 'query' for search.",
            }
        hits = search_artists(query, limit=limit)
        return {"success": True, "operation": operation, "artists": hits, "count": len(hits)}
    artists = list_artists()
    return {
        "success": True,
        "operation": operation,
        "artists": artists[:limit],
        "count": min(len(artists), limit),
        "total": len(artists),
    }
