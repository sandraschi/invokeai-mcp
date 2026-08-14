"""invokeai_gallery + invokeai_boards - image and board management."""

from __future__ import annotations

from typing import Annotated, Literal

from fastmcp import Context
from pydantic import Field

from invokeai_mcp.client import InvokeAIError
from invokeai_mcp.runtime import get_client, get_settings, log
from invokeai_mcp.server import mcp


@mcp.tool()
async def invokeai_gallery(
    operation: Annotated[
        Literal[
            "list",
            "search",
            "get",
            "metadata",
            "download",
            "delete",
            "star",
            "unstar",
            "batch_delete",
            "batch_star",
            "batch_unstar",
            "board_add",
            "board_remove",
        ],
        Field(description="Gallery operation to perform."),
    ],
    image_name: Annotated[
        str | None,
        Field(
            description="InvokeAI image_name (required for get, metadata, download, delete, star, unstar)."
        ),
    ] = None,
    image_names: Annotated[
        list[str] | None,
        Field(
            description="Image list (required for batch_delete, batch_star, batch_unstar, board_add, board_remove)."
        ),
    ] = None,
    board_id: Annotated[
        str | None,
        Field(description="Board id (filter for list; target for board_add/board_remove)."),
    ] = None,
    query: Annotated[
        str | None, Field(description="Search text for operation='search' (prompt metadata).")
    ] = None,
    starred: Annotated[bool | None, Field(description="Filter to starred images only.")] = None,
    limit: Annotated[int, Field(description="Max images.", ge=1, le=100)] = 30,
    offset: Annotated[int, Field(description="Pagination offset.", ge=0)] = 0,
    ctx: Context | None = None,  # noqa: B008
) -> dict:
    """Browse, search, download, and manage generated images.

    [RATIONALE]
    The gallery is a single searchable feed (gallery endpoint) with per-image
    actions; one portmanteau keeps discovery and mutation together.

    ## Return Format
    {"success": bool, "operation": str, "data": {...}, "message": str,
     "images": [{"image_name", "url", "thumbnail_url", "width", "height"}]}

    ## Examples
    invokeai_gallery(operation="list", limit=20)
    invokeai_gallery(operation="search", query="cyberpunk")
    invokeai_gallery(operation="download", image_name="abc123.png")
    invokeai_gallery(operation="batch_star", image_names=["a.png", "b.png"])
    invokeai_gallery(operation="board_add", image_names=["a.png"], board_id="board-uuid")

    Notes:
     - URLs returned are absolute (InvokeAI host), usable in chat/browser.
    """
    client = get_client()
    settings = get_settings()
    try:
        if operation in ("list", "search"):
            params: dict = {"limit": limit, "offset": offset}
            if board_id:
                params["board_id"] = board_id
            if starred is not None:
                params["is_starred"] = starred
            if operation == "search" and query:
                params["search"] = query
            data = await client.gallery_items(**params)
            items = data.get("items", [])
            images = [
                {
                    "image_name": i.get("image_name"),
                    "url": f"{settings.api_base}/api/v1/images/i/{i.get('image_name')}/full",
                    "thumbnail_url": f"{settings.api_base}/api/v1/images/i/{i.get('image_name')}/thumbnail",
                    "width": i.get("width"),
                    "height": i.get("height"),
                    "starred": i.get("is_starred", False),
                    "board_id": i.get("board_id"),
                }
                for i in items
            ]
            return {
                "success": True,
                "operation": operation,
                "data": {"images": images, "count": len(images), "total": data.get("total")},
                "message": f"{len(images)} image(s).",
            }
        if operation == "get":
            if not image_name:
                return _missing("image_name", operation)
            data = await client.get_image(image_name)
            return {
                "success": True,
                "operation": operation,
                "data": data,
                "message": f"Image {image_name}.",
            }
        if operation == "metadata":
            if not image_name:
                return _missing("image_name", operation)
            data = await client.get_image_metadata(image_name)
            return {
                "success": True,
                "operation": operation,
                "data": data,
                "message": f"Metadata for {image_name} (prompt, seed, settings).",
            }
        if operation == "download":
            if not image_name:
                return _missing("image_name", operation)
            dest = settings.download_dir / image_name
            dest.parent.mkdir(parents=True, exist_ok=True)
            await client.download_image(image_name, dest)
            return {
                "success": True,
                "operation": operation,
                "data": {"local_path": str(dest)},
                "message": f"Downloaded to {dest}.",
            }
        if operation == "delete":
            if not image_name:
                return _missing("image_name", operation)
            await client.delete_image(image_name)
            log("WARNING", "gallery", f"deleted image {image_name}")
            return {
                "success": True,
                "operation": operation,
                "message": f"Image {image_name} deleted.",
            }
        if operation in ("star", "unstar"):
            if not image_name:
                return _missing("image_name", operation)
            if operation == "star":
                await client.star_images([image_name])
            else:
                await client.unstar_images([image_name])
            return {
                "success": True,
                "operation": operation,
                "message": f"Image {image_name} {operation}ed.",
            }
        if operation in ("batch_delete", "batch_star", "batch_unstar"):
            names = image_names or []
            if not names:
                return _missing("image_names", operation)
            if operation == "batch_delete":
                await client.delete_images(names)
            elif operation == "batch_star":
                await client.star_images(names)
            else:
                await client.unstar_images(names)
            log("WARNING", "gallery", f"{operation} on {len(names)} images")
            return {
                "success": True,
                "operation": operation,
                "count": len(names),
                "message": f"{operation} applied to {len(names)} images.",
            }
        if operation in ("board_add", "board_remove"):
            names = image_names or []
            if not names or not board_id:
                return _missing("image_names + board_id", operation)
            if operation == "board_add":
                await client.add_images_to_board(board_id, names)
            else:
                await client.remove_images_from_board(board_id, names)
            return {
                "success": True,
                "operation": operation,
                "board_id": board_id,
                "count": len(names),
                "message": f"{len(names)} image(s) {operation.replace('board_', '')} to board {board_id}.",
            }
    except InvokeAIError as exc:
        return {
            "success": False,
            "error": exc.error_type,
            "message": exc.message,
            "dialogic": {
                "suggestion": "Gallery API unreachable.",
                "remediation": "invokeai_system(operation='health')",
            },
        }
    return {"success": False, "error": "validation", "message": f"Unknown operation: {operation}"}


@mcp.tool()
async def invokeai_boards(
    operation: Annotated[
        Literal["list", "get", "create", "update", "delete", "add_image", "remove_image"],
        Field(description="Board operation to perform."),
    ],
    board_id: Annotated[
        str | None,
        Field(description="Board id (required for get, update, delete, add_image, remove_image)."),
    ] = None,
    board_name: Annotated[
        str | None, Field(description="Board name (required for create, update).")
    ] = None,
    image_names: Annotated[
        list[str] | None,
        Field(description="Image names to assign/remove (add_image, remove_image)."),
    ] = None,
    ctx: Context | None = None,  # noqa: B008
) -> dict:
    """Manage boards (collections of generated images).

    [RATIONALE]
    Boards are the primary organization surface of the InvokeAI gallery; all
    board operations share one record store and one portmanteau.

    ## Return Format
    {"success": bool, "operation": str, "data": {...}, "message": str}

    ## Examples
    invokeai_boards(operation="list")
    invokeai_boards(operation="create", board_name="Concept art")
    invokeai_boards(operation="add_image", board_id="board-uuid", image_names=["abc123.png"])

    Notes:
     - Board ids come from invokeai_boards(operation='list').
    """
    client = get_client()
    try:
        if operation == "list":
            boards = await client.list_boards()
            return {
                "success": True,
                "operation": operation,
                "data": {"boards": boards, "count": len(boards)},
                "message": f"{len(boards)} board(s).",
            }
        if operation == "get":
            if not board_id:
                return _missing("board_id", operation)
            data = await client.get_board(board_id)
            return {
                "success": True,
                "operation": operation,
                "data": data,
                "message": f"Board {board_id}.",
            }
        if operation == "create":
            if not board_name:
                return _missing("board_name", operation)
            data = await client.create_board(board_name)
            log("INFO", "boards", f"created board {board_name}")
            return {
                "success": True,
                "operation": operation,
                "data": data,
                "message": f"Board '{board_name}' created.",
            }
        if operation == "update":
            if not board_id or not board_name:
                return _missing("board_id + board_name", operation)
            data = await client.update_board(board_id, board_name)
            return {
                "success": True,
                "operation": operation,
                "data": data,
                "message": f"Board {board_id} updated.",
            }
        if operation == "delete":
            if not board_id:
                return _missing("board_id", operation)
            await client.delete_board(board_id)
            log("WARNING", "boards", f"deleted board {board_id}")
            return {
                "success": True,
                "operation": operation,
                "message": f"Board {board_id} deleted.",
            }
        if operation in ("add_image", "remove_image"):
            if not board_id or not image_names:
                return _missing("board_id + image_names", operation)
            if operation == "add_image":
                await client.add_images_to_board(board_id, image_names)
            else:
                await client.remove_images_from_board(board_id, image_names)
            return {
                "success": True,
                "operation": operation,
                "message": f"{len(image_names)} image(s) {'added to' if operation == 'add_image' else 'removed from'} board {board_id}.",
            }
    except InvokeAIError as exc:
        return {
            "success": False,
            "error": exc.error_type,
            "message": exc.message,
            "dialogic": {
                "suggestion": "Boards API unreachable.",
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
            "remediation": f"invokeai_{op.split('_')[0]}(operation='{op}', {arg}=...)",
        },
    }
