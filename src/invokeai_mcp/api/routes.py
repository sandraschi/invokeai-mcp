"""REST API layer for the webapp (Starlette, no Pydantic in routes)."""

from __future__ import annotations

from typing import Any

from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse
from starlette.routing import Route

from invokeai_mcp import __version__
from invokeai_mcp.client import InvokeAIError
from invokeai_mcp.runtime import get_client, get_settings, log, query_logs

_SKILL_DIR = __import__("invokeai_mcp").__path__[0] + "/skills"


async def _health(request: Request) -> JSONResponse:
    client = get_client()
    ok = await client.ping()
    return JSONResponse(
        {
            "status": "ok" if ok else "degraded",
            "server": "invokeai-mcp",
            "version": __version__,
            "configured": ok,
            "invokeai_url": get_settings().invokeai_url,
        }
    )


async def _dashboard(request: Request) -> JSONResponse:
    client = get_client()
    try:
        version = await client.app_version()
        queue = await client.queue_status()
        models = await client.list_models(model_type="main", limit=50)
        gallery = await client.gallery_items(limit=6)
        return JSONResponse(
            {
                "configured": True,
                "version": version.get("version", "?"),
                "model_count": len(models),
                "queue": {
                    k: queue.get(k, 0)
                    for k in ("queued", "in_progress", "completed", "failed", "canceled")
                },
                "recent_images": [
                    {
                        "image_name": i.get("image_name"),
                        "url": f"{get_settings().api_base}/api/v1/images/i/{i.get('image_name')}/full",
                        "thumbnail_url": f"{get_settings().api_base}/api/v1/images/i/{i.get('image_name')}/thumbnail",
                    }
                    for i in gallery.get("items", [])
                ],
            }
        )
    except Exception as exc:  # pragma: no cover - degraded path
        log("WARNING", "api", f"dashboard degraded: {exc}")
        return JSONResponse(
            {
                "configured": False,
                "version": None,
                "model_count": 0,
                "queue": {},
                "recent_images": [],
                "error": str(exc),
            }
        )


async def _skills(request: Request) -> JSONResponse:
    from pathlib import Path

    root = Path(_SKILL_DIR)
    skills = []
    if root.exists():
        for d in sorted(root.iterdir()):
            if d.is_dir() and (d / "SKILL.md").exists():
                skills.append({"name": d.name, "uri": f"skill://{d.name}/SKILL.md"})
    return JSONResponse({"skills": skills})


async def _skill_detail(request: Request) -> JSONResponse:
    from pathlib import Path

    name = request.path_params.get("name", "")
    path = Path(_SKILL_DIR) / name / "SKILL.md"
    if not path.exists():
        return JSONResponse({"error": f"skill {name} not found"}, status_code=404)
    return JSONResponse({"name": name, "content": path.read_text(encoding="utf-8")})


async def _tools(request: Request) -> JSONResponse:
    """Dynamic tool list - read from the MCP server's own registry."""
    from invokeai_mcp.server import mcp

    tools = []
    try:
        registered = await mcp.list_tools()
        for tool in registered:
            tools.append({"name": tool.name, "description": (tool.description or "")[:300]})
    except Exception:
        tools = []
    return JSONResponse({"tools": sorted(tools, key=lambda t: t["name"])})


async def _logs(request: Request) -> JSONResponse:
    params = request.query_params
    entries, total = query_logs(
        source=params.get("source"),
        level=params.get("level"),
        search=params.get("search"),
        limit=int(params.get("limit", 50)),
    )
    return JSONResponse({"logs": entries, "count": len(entries), "total": total})


async def _llm_discover(request: Request) -> JSONResponse:
    """Probe local LLM providers (Ollama > LM Studio > vLLM)."""
    import httpx

    providers: list[dict[str, Any]] = []
    probes = [
        ("Ollama", 11434, "/api/tags"),
        ("LM Studio", 1234, "/v1/models"),
        ("vLLM", 8000, "/v1/models"),
    ]
    async with httpx.AsyncClient(timeout=3) as http:
        for name, port, path in probes:
            try:
                resp = await http.get(f"http://127.0.0.1:{port}{path}")
                if resp.status_code == 200:
                    providers.append(
                        {"name": name, "port": port, "base": f"http://127.0.0.1:{port}/v1"}
                    )
            except Exception:
                continue
    return JSONResponse({"providers": providers})


async def _llm_chat(request: Request) -> JSONResponse:
    """Chat proxy to a local LLM (OpenAI-compatible)."""
    import httpx

    body = await request.json()
    provider = body.get("provider", "Ollama")
    model = body.get("model", "")
    messages = body.get("messages", [])
    port = 11434 if provider == "Ollama" else (1234 if provider == "LM Studio" else 8000)
    url = f"http://127.0.0.1:{port}/v1/chat/completions"
    if not model:
        return JSONResponse(
            {"error": "No model selected - pick one in Settings first."}, status_code=400
        )
    try:
        async with httpx.AsyncClient(timeout=180) as http:
            resp = await http.post(
                url,
                json={"model": model, "messages": messages, "stream": False},
            )
            if resp.status_code != 200:
                return JSONResponse(
                    {"error": f"{provider} returned HTTP {resp.status_code}"}, status_code=502
                )
            data = resp.json()
            return JSONResponse({"content": data["choices"][0]["message"]["content"]})
    except httpx.HTTPError as exc:
        return JSONResponse({"error": f"{provider} unreachable: {exc}"}, status_code=502)


async def _invokeai_status(request: Request) -> JSONResponse:
    client = get_client()
    ok = await client.ping()
    data: dict[str, Any] = {"configured": ok, "invokeai_url": get_settings().invokeai_url}
    if ok:
        try:
            version = await client.app_version()
            data["version"] = version.get("version")
            data["models"] = len(await client.list_models(model_type="main", limit=1))
        except Exception:
            pass
    return JSONResponse(data)


async def _invokeai_image(request: Request) -> Response:
    """Proxy engine image bytes same-origin (canvas-safe for outpaint)."""
    client = get_client()
    name = request.path_params.get("name", "")
    try:
        urls = await client.get_image_urls(name)
        full = urls.get("full") or urls.get("url") or urls.get("image_url") or ""
        if not full:
            return JSONResponse({"error": "no url"}, status_code=404)
        url = full if full.startswith("http") else f"{client.settings.api_base}/{full.lstrip('/')}"
        resp = await client._client.get(url)
        if resp.status_code != 200:
            return JSONResponse({"error": f"engine HTTP {resp.status_code}"}, status_code=502)
        return Response(
            content=resp.content, media_type=resp.headers.get("content-type", "image/png")
        )
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=404)


async def _invokeai_plugins(request: Request) -> JSONResponse:
    """Plugins surface: installed node packs + live built-in capability catalog."""
    client = get_client()
    try:
        packs = await client.list_custom_nodes()
        caps = await client.capabilities()
        return JSONResponse({"configured": True, "packs": packs, "capabilities": caps})
    except Exception as exc:  # pragma: no cover - degraded path
        return JSONResponse(
            {"configured": False, "packs": [], "capabilities": {}, "error": str(exc)}
        )


async def _invokeai_plugin_action(request: Request) -> JSONResponse:
    """POST /api/invokeai/plugins/install|reload, DELETE /api/invokeai/plugins/{name}."""
    client = get_client()
    path = request.url.path
    try:
        if path.endswith("/install"):
            body = await request.json()
            result = await client.install_custom_node(body.get("source", ""))
            return JSONResponse({"success": True, "data": result})
        if path.endswith("/reload"):
            await client.reload_custom_nodes()
            return JSONResponse({"success": True, "message": "Custom nodes reloaded."})
        if path.endswith(f"/{request.path_params.get('name', '')}"):
            result = await client.uninstall_custom_node(request.path_params["name"])
            return JSONResponse({"success": True, "data": result})
    except Exception as exc:
        return JSONResponse({"success": False, "error": str(exc)}, status_code=400)
    return JSONResponse({"success": False, "error": "unknown plugin action"}, status_code=400)


async def _invokeai_upload(request: Request) -> JSONResponse:
    """POST /api/invokeai/upload - multipart image upload to the engine gallery."""
    client = get_client()
    form = await request.form()
    upload = form.get("file")
    from starlette.datastructures import UploadFile

    if not isinstance(upload, UploadFile):
        return JSONResponse({"success": False, "error": "missing file field"}, status_code=400)
    data = await upload.read()
    result = await client.upload_image(data, upload.filename or "upload.png")
    return JSONResponse({"success": True, "data": result})


async def _hf_status(request: Request) -> JSONResponse:
    client = get_client()
    try:
        return JSONResponse({"status": await client.hf_status()})
    except Exception as exc:  # pragma: no cover - degraded path
        return JSONResponse({"status": "unknown", "error": str(exc)})


async def _hf_login(request: Request) -> JSONResponse:
    client = get_client()
    try:
        body = await request.json()
        token = (body.get("token") or "").strip()
        if not token or not token.startswith("hf_"):
            return JSONResponse({"success": False, "error": "A valid hf_... token is required."}, status_code=400)
        status = await client.hf_login(token)
        return JSONResponse({"success": True, "status": status})
    except Exception as exc:
        return JSONResponse({"success": False, "error": str(exc)}, status_code=400)


async def _hf_logout(request: Request) -> JSONResponse:
    client = get_client()
    try:
        await client.hf_logout()
        return JSONResponse({"success": True, "status": "invalid"})
    except Exception as exc:
        return JSONResponse({"success": False, "error": str(exc)}, status_code=400)


async def _engine_status(request: Request) -> JSONResponse:
    """Engine lifecycle status: running, pid, version, uptime."""
    client = get_client()
    import subprocess

    running = False
    pid = None
    try:
        version = await client.app_version()
        running = True
    except Exception:
        version = {}
    if running:
        try:
            out = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq invokeai-web.exe", "/FO", "CSV", "/NH"],
                capture_output=True, text=True, timeout=10,
            ).stdout
            if "invokeai-web.exe" in out:
                pid = int(out.split('"')[3])
        except Exception:
            pid = None
    return JSONResponse(
        {
            "running": running,
            "pid": pid,
            "version": version.get("version") if isinstance(version, dict) else None,
            "invokeai_url": get_settings().invokeai_url,
        }
    )


async def _engine_start(request: Request) -> JSONResponse:
    """Spawn the InvokeAI engine (detached, logs to D:\\InvokeAI\\engine.log)."""
    import subprocess

    client = get_client()
    try:
        if await client.ping():
            return JSONResponse({"success": True, "message": "Engine already running."})
        log("INFO", "engine", "starting engine via start-engine.ps1")
        subprocess.Popen(
            [
                "powershell.exe",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                r"D:\InvokeAI\start-engine.ps1",
            ],
            creationflags=0x00000008 | 0x08000000,  # DETACHED_PROCESS | CREATE_NO_WINDOW
        )
        return JSONResponse({"success": True, "message": "Engine starting - health flips when ready."})
    except Exception as exc:
        return JSONResponse({"success": False, "error": str(exc)}, status_code=500)


async def _engine_stop(request: Request) -> JSONResponse:
    """Kill the InvokeAI engine process."""
    import subprocess

    try:
        subprocess.run(["taskkill", "/F", "/IM", "invokeai-web.exe", "/T"], capture_output=True, timeout=30)
        log("WARNING", "engine", "engine stopped")
        return JSONResponse({"success": True, "message": "Engine stopped."})
    except Exception as exc:
        return JSONResponse({"success": False, "error": str(exc)}, status_code=500)


async def _invokeai_models(request: Request) -> JSONResponse:
    """Model list for the webapp Generate/Models pages."""
    client = get_client()
    try:
        models = await client.list_models(model_type="main", limit=100)
        return JSONResponse(
            {
                "configured": True,
                "models": [
                    {
                        "key": m.get("key"),
                        "name": m.get("name"),
                        "base": m.get("base"),
                        "type": m.get("type"),
                    }
                    for m in models
                ],
            }
        )
    except Exception as exc:  # pragma: no cover - degraded path
        return JSONResponse({"configured": False, "models": [], "error": str(exc)})


async def _generate(request: Request) -> JSONResponse:
    """Webapp-friendly generate endpoint (mirrors invokeai_generate)."""
    from invokeai_mcp.tools.generate_tools import invokeai_generate

    body = await request.json()
    result = await invokeai_generate(**body)
    status = 200 if result.get("success") else 400
    return JSONResponse(result, status_code=status)


async def _queue_control(request: Request) -> JSONResponse:
    from invokeai_mcp.tools.queue_tools import invokeai_queue

    body = await request.json()
    result = await invokeai_queue(**body)
    return JSONResponse(result, status_code=200 if result.get("success") else 400)


_DOMAIN_FUNCS = {
    "gallery": ("invokeai_mcp.tools.gallery_tools", "invokeai_gallery"),
    "boards": ("invokeai_mcp.tools.gallery_tools", "invokeai_boards"),
    "models": ("invokeai_mcp.tools.model_tools", "invokeai_models"),
    "workflows": ("invokeai_mcp.tools.workflow_tools", "invokeai_workflows"),
    "system": ("invokeai_mcp.tools.system_tools", "invokeai_system"),
}

_LIST_OPS = {
    "gallery": ("list", {"limit": "limit", "query": "query", "board_id": "board_id"}),
    "boards": ("list", {}),
    "models": ("list", {"model_type": "model_type"}),
    "workflows": ("list", {"limit": "limit"}),
}


async def _invokeai_action(request: Request) -> JSONResponse:
    """POST /api/invokeai/{domain} - passthrough to the matching portmanteau tool."""
    domain = request.path_params.get("domain", "")
    entry = _DOMAIN_FUNCS.get(domain)
    if not entry:
        return JSONResponse({"error": f"unknown domain {domain}"}, status_code=404)
    mod_name, fn_name = entry
    import importlib

    fn = getattr(importlib.import_module(mod_name), fn_name)
    body = await request.json()
    result = await fn(**body)
    return JSONResponse(result, status_code=200 if result.get("success") else 400)


async def _invokeai_list(request: Request) -> JSONResponse:
    """GET /api/invokeai/{domain} - list view for the webapp."""
    domain = request.path_params.get("domain", "")
    if domain not in _LIST_OPS:
        return JSONResponse({"error": f"no list view for {domain}"}, status_code=404)
    op, mapping = _LIST_OPS[domain]
    mod_name, fn_name = _DOMAIN_FUNCS[domain]
    import importlib

    fn = getattr(importlib.import_module(mod_name), fn_name)
    params = request.query_params
    kwargs: dict[str, Any] = {"operation": op}
    for query_key, arg in mapping.items():
        if params.get(query_key):
            value = params.get(query_key, "")
            kwargs[arg] = int(value) if arg == "limit" else value
    result = await fn(**kwargs)
    # GET list endpoints return the payload directly (pages read data.models etc.)
    return JSONResponse(
        result.get("data", result), status_code=200 if result.get("success") else 400
    )


async def _queue_status_rest(request: Request) -> JSONResponse:
    from invokeai_mcp.tools.queue_tools import invokeai_queue

    result = await invokeai_queue(operation="status")
    return JSONResponse(
        result.get("data", {})
        if result.get("success")
        else {"queued": 0, "in_progress": 0, "completed": 0, "failed": 0, "canceled": 0},
        status_code=200 if result.get("success") else 400,
    )


async def _queue_list_rest(request: Request) -> JSONResponse:
    from invokeai_mcp.tools.queue_tools import invokeai_queue

    result = await invokeai_queue(
        operation="list", limit=int(request.query_params.get("limit", 50))
    )
    return JSONResponse(
        result.get("data", result), status_code=200 if result.get("success") else 400
    )


async def _invokeai_styles(request: Request) -> JSONResponse:
    """GET /api/invokeai/styles - style catalog (list, ?query=, ?limit=)."""
    from invokeai_mcp.styles import list_styles, search_styles

    query = request.query_params.get("query")
    limit = min(int(request.query_params.get("limit", 100)), 200)
    if query:
        styles = search_styles(query, limit=limit)
    else:
        styles = list_styles()[:limit]
    return JSONResponse({"styles": styles, "count": len(styles), "total": len(list_styles())})


async def _invokeai_workflow_templates(request: Request) -> JSONResponse:
    """GET /api/invokeai/workflow-templates - editor node templates."""
    from invokeai_mcp.client import InvokeAIError

    try:
        templates = await get_client().node_templates()
        return JSONResponse(
            {"success": True, "templates": templates, "count": len(templates)}
        )
    except InvokeAIError as exc:
        return JSONResponse(
            {"success": False, "templates": {}, "count": 0, "error": exc.message}
        )


async def _gallery_list_rest(request: Request) -> JSONResponse:
    """GET /api/invokeai/gallery - sortable, filterable gallery feed.

    Params: query, sort (created_at|name), order (asc|desc), starred (1),
    board (board_id), style (comma-separated style ids from the catalog),
    limit, offset. Style/starred filtering enriches the page with metadata
    (bounded, parallel).
    """
    import asyncio

    from invokeai_mcp.styles import get_style, match_style_for_prompt

    client = get_client()
    try:
        params = request.query_params
        limit = min(int(params.get("limit", 60)), 200)
        offset = int(params.get("offset", 0))
        sort = params.get("sort", "created_at")
        order = (params.get("order", "desc") or "desc").upper()
        starred_only = params.get("starred") == "1"
        board_id = params.get("board") or None
        search = params.get("query") or None
        style_ids = [s for s in (params.get("style") or "").split(",") if s]

        fetch_limit = max(limit, 300) if (starred_only or style_ids or sort == "name") else limit
        data = await client.list_images(
            limit=fetch_limit,
            offset=offset,
            order_dir=order,
            search_term=search,
            board_id=board_id,
        )
        images = list(data.get("items", data.get("images", [])))
        if not images:
            return JSONResponse({"images": [], "count": 0, "total": 0, "has_more": False})

        # Exact attribution: image.session_id == the queue item's session_id;
        # the registry stores which styles each item ran with.
        from invokeai_mcp.attribution import session_map

        attrib = await session_map()
        session_items = await client.queue_list(limit=1000)
        session_to_item: dict[str, int] = {}
        for it in session_items:
            sid = it.get("session_id")
            iid = it.get("item_id")
            if sid and isinstance(iid, int):
                session_to_item[str(sid)] = iid

        def _styles_for(image: dict) -> list[str]:
            sid = image.get("session_id")
            if not sid:
                return []
            item = session_to_item.get(str(sid))
            if item is None:
                return []
            entry = attrib.get(str(item))
            return list(entry.get("styles", [])) if entry else []

        for image in images:
            image["styles"] = _styles_for(image)

        if starred_only:
            images = [i for i in images if i.get("starred")]

        styles_matched: list[str] = []
        if style_ids:
            style_set = set(style_ids)
            exact: list[dict] = []
            rest: list[dict] = []
            for image in images:
                if any(s in style_set for s in image.get("styles", [])):
                    exact.append(image)
                else:
                    rest.append(image)
            if exact:
                images = exact
                styles_matched = [s for s in style_ids if any(
                    s in img.get("styles", []) for img in images
                )]
            else:
                # fallback: prompt-signature matching for pre-registry images
                styles_map = {sid: get_style(sid) for sid in style_ids}
                valid = {sid: s for sid, s in styles_map.items() if s}

                async def _prompt_of(image: dict) -> str:
                    try:
                        meta = await client.get_image_metadata(image["image_name"])
                        return str(meta.get("positive_prompt") or "")
                    except Exception:
                        return ""

                sem = asyncio.Semaphore(8)

                async def _matched(image: dict) -> bool:
                    async with sem:
                        prompt = await _prompt_of(image)
                    for sid, s in valid.items():
                        if match_style_for_prompt(s, prompt):
                            if sid not in styles_matched:
                                styles_matched.append(sid)
                            return True
                    return False

                results = await asyncio.gather(*(_matched(i) for i in rest))
                images = [i for i, keep in zip(rest, results, strict=True) if keep]

        if sort == "name":
            images.sort(key=lambda i: i.get("image_name", ""), reverse=(order == "DESC"))
        elif sort == "starred":
            images.sort(key=lambda i: bool(i.get("starred")), reverse=True)

        page = images[:limit]
        return JSONResponse(
            {
                "images": page,
                "count": len(page),
                "total": len(images),
                "has_more": len(images) > limit,
                "styles_matched": styles_matched,
            }
        )
    except InvokeAIError as exc:
        return JSONResponse({"error": exc.message, "images": [], "count": 0, "total": 0})


async def _gallery_batch(request: Request) -> JSONResponse:
    """POST /api/invokeai/gallery/batch - {operation, image_names}."""
    from invokeai_mcp.client import InvokeAIError

    body = await request.json()
    operation = body.get("operation")
    names = body.get("image_names") or []
    if not isinstance(names, list) or not names:
        return JSONResponse({"success": False, "error": "image_names required"})
    if operation not in ("delete", "star", "unstar"):
        return JSONResponse({"success": False, "error": f"unknown batch op {operation}"})
    try:
        client = get_client()
        if operation == "delete":
            await client.delete_images(names)
        elif operation == "star":
            await client.star_images(names)
        else:
            await client.unstar_images(names)
        return JSONResponse({"success": True, "operation": operation, "count": len(names)})
    except InvokeAIError as exc:
        return JSONResponse({"success": False, "error": exc.message})


async def _gallery_board(request: Request) -> JSONResponse:
    """POST/DELETE /api/invokeai/gallery/board - {image_names, board_id}."""
    from invokeai_mcp.client import InvokeAIError

    body = await request.json()
    names = body.get("image_names") or []
    board_id = body.get("board_id")
    if not names or not board_id:
        return JSONResponse({"success": False, "error": "image_names + board_id required"})
    try:
        client = get_client()
        if request.method == "DELETE":
            await client.remove_images_from_board(board_id, names)
        else:
            await client.add_images_to_board(board_id, names)
        return JSONResponse({"success": True, "board_id": board_id, "count": len(names)})
    except InvokeAIError as exc:
        return JSONResponse({"success": False, "error": exc.message})


async def _gallery_zip(request: Request) -> Response:
    """POST /api/invokeai/gallery/zip - {image_names} -> zip archive."""
    import io
    import zipfile

    from invokeai_mcp.client import InvokeAIError

    body = await request.json()
    names = body.get("image_names") or []
    if not names:
        return JSONResponse({"success": False, "error": "image_names required"})
    try:
        client = get_client()
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for name in names:
                try:
                    zf.writestr(name, await client.get_image_bytes(name))
                except Exception:
                    continue
        buf.seek(0)
        return StreamingResponse(
            buf,
            media_type="application/zip",
            headers={"Content-Disposition": f'attachment; filename="invokeai-{len(names)}.zip"'},
        )
    except InvokeAIError as exc:
        return JSONResponse({"success": False, "error": exc.message})


async def _boards_rest(request: Request) -> JSONResponse:
    """GET /api/invokeai/boards - board list for filters/assignment."""
    try:
        boards = await get_client().list_boards()
        return JSONResponse({"boards": boards, "count": len(boards)})
    except InvokeAIError as exc:
        return JSONResponse({"boards": [], "count": 0, "error": exc.message})


routes = [
    Route("/api/health", _health),
    Route("/api/dashboard", _dashboard),
    Route("/api/skills", _skills),
    Route("/api/skills/{name}", _skill_detail),
    Route("/api/tools", _tools),
    Route("/api/logs", _logs),
    Route("/api/llm/discover", _llm_discover),
    Route("/api/llm/chat", _llm_chat, methods=["POST"]),
    Route("/api/invokeai/status", _invokeai_status),
    Route("/api/invokeai/models", _invokeai_models),
    Route("/api/invokeai/hf/status", _hf_status),
    Route("/api/invokeai/hf/login", _hf_login, methods=["POST"]),
    Route("/api/invokeai/hf/logout", _hf_logout, methods=["DELETE"]),
    Route("/api/invokeai/engine/status", _engine_status),
    Route("/api/invokeai/engine/start", _engine_start, methods=["POST"]),
    Route("/api/invokeai/engine/stop", _engine_stop, methods=["POST"]),
    Route("/api/invokeai/image/{name}", _invokeai_image),
    Route("/api/invokeai/upload", _invokeai_upload, methods=["POST"]),
    Route("/api/invokeai/plugins", _invokeai_plugins),
    Route("/api/invokeai/plugins/install", _invokeai_plugin_action, methods=["POST"]),
    Route("/api/invokeai/plugins/reload", _invokeai_plugin_action, methods=["POST"]),
    Route("/api/invokeai/plugins/{name}", _invokeai_plugin_action, methods=["DELETE"]),
    Route("/api/invokeai/workflow-templates", _invokeai_workflow_templates),
    Route("/api/invokeai/styles", _invokeai_styles),
    Route("/api/invokeai/gallery/batch", _gallery_batch, methods=["POST"]),
    Route("/api/invokeai/gallery/board", _gallery_board, methods=["POST", "DELETE"]),
    Route("/api/invokeai/gallery/zip", _gallery_zip, methods=["POST"]),
    Route("/api/invokeai/gallery", _gallery_list_rest),
    Route("/api/invokeai/boards", _boards_rest),
    Route("/api/invokeai/queue/status", _queue_status_rest),
    Route("/api/invokeai/queue/list", _queue_list_rest),
    Route("/api/invokeai/generate", _generate, methods=["POST"]),
    Route("/api/invokeai/queue", _queue_control, methods=["POST"]),
    Route("/api/invokeai/{domain}", _invokeai_action, methods=["POST"]),
    Route("/api/invokeai/{domain}", _invokeai_list),
]
