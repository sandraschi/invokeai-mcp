"""HTTP client for the InvokeAI v5 REST API.

Endpoint inventory verified against invoke-ai/InvokeAI main (2026-08):
  app_info      /api/v1/app/version, /api/v1/app/runtime_config, ...
  session_queue /api/v1/queue/{queue_id}/... (enqueue_batch, list, status, cancel, clear, resume)
  model_manager /api/v2/models/... (list, install, update, delete, convert, merge, stats)
  gallery       /api/v1/gallery/items/ (searchable image feed)
  boards        /api/v1/boards, /api/v1/board_images
  images        /api/v1/images/... (upload, get, delete, star, urls, metadata)
  workflows     /api/v1/workflows/... (CRUD + export)
  videos        /api/v1/videos/... (Wan video outputs)
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from invokeai_mcp.config import Settings

logger = logging.getLogger("invokeai_mcp.client")


class InvokeAIError(Exception):
    """Raised when InvokeAI returns an error or is unreachable."""

    def __init__(
        self, message: str, *, error_type: str = "invokeai_error", status: int | None = None
    ):
        super().__init__(message)
        self.message = message
        self.error_type = error_type
        self.status = status


class InvokeAIClient:
    """Thin, typed wrapper over the InvokeAI REST API."""

    def __init__(self, settings: Settings | None = None, client: httpx.AsyncClient | None = None):
        self.settings = settings or Settings()
        self._client = client or httpx.AsyncClient(
            base_url=self.settings.api_base, timeout=self.settings.request_timeout
        )
        self.models_cache: dict[str, list[dict[str, Any]]] = {}

    async def refresh_models(self) -> dict[str, list[dict[str, Any]]]:
        """Load the main-model list into the cache (used by generate dispatch)."""
        models = await self.list_models()
        self.models_cache = {"main": [m for m in models if m.get("type") == "main"]}
        return self.models_cache

    @property
    def headers(self) -> dict[str, str]:
        h = {"Accept": "application/json"}
        if self.settings.access_token:
            h["Authorization"] = f"Bearer {self.settings.access_token}"
        return h

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any | None = None,
        data: Any | None = None,
        files: Any | None = None,
        allow_error: bool = False,
    ) -> Any:
        if path.startswith("http") or path.startswith("/api") or path.startswith("/openapi"):
            url = path
        else:
            url = f"/api{path}"
        try:
            resp = await self._client.request(
                method, url, params=params, json=json, data=data, files=files, headers=self.headers
            )
        except httpx.HTTPError as exc:
            raise InvokeAIError(
                f"InvokeAI unreachable at {self.settings.api_base}: {exc}",
                error_type="connection_error",
            ) from exc
        if resp.status_code >= 400 and not allow_error:
            raise InvokeAIError(
                f"InvokeAI {method} {path} -> HTTP {resp.status_code}: {resp.text[:400]}",
                error_type="http_error",
                status=resp.status_code,
            )
        if resp.status_code in (204, 202) or not resp.content:
            return None
        try:
            return resp.json()
        except ValueError:
            return resp.text

    # ------------------------------------------------------------------ app
    async def app_version(self) -> dict[str, Any]:
        return await self._request("GET", "/v1/app/version")

    async def runtime_config(self) -> dict[str, Any]:
        return await self._request("GET", "/v1/app/runtime_config")

    async def ping(self) -> bool:
        try:
            await self.app_version()
            return True
        except InvokeAIError:
            return False

    # ----------------------------------------------------------------- queue
    async def enqueue_batch(
        self,
        graph: dict[str, Any],
        *,
        runs: int = 1,
        queue_id: str | None = None,
        destination: str = "webapp",
        prepend: bool = False,
    ) -> dict[str, Any]:
        batch = {
            "batch_id": graph.get("id", ""),
            "destination": destination,
            "graph": graph,
            "runs": runs,
        }
        data = await self._request(
            "POST",
            f"/v1/queue/{queue_id or self.settings.queue_id}/enqueue_batch",
            params={"prepend": str(prepend).lower()},
            json={"batch": batch},
        )
        # v6 returns {queue_id, enqueued, requested, batch, priority, item_ids}
        batch_meta = data.get("batch") or {}
        return {
            "queue_id": data.get("queue_id") or queue_id or self.settings.queue_id,
            "batch_id": data.get("batch_id") or batch_meta.get("batch_id") or batch_meta.get("id"),
            "queue_item_ids": data.get("item_ids") or data.get("queue_item_ids") or [],
        }

    async def queue_status(self, queue_id: str | None = None) -> dict[str, Any]:
        data = await self._request("GET", f"/v1/queue/{queue_id or self.settings.queue_id}/status")
        if isinstance(data, dict) and "queue" in data:
            return data["queue"]
        return data or {}

    async def queue_list(
        self, limit: int = 20, queue_id: str | None = None
    ) -> list[dict[str, Any]]:
        data = await self._request(
            "GET",
            f"/v1/queue/{queue_id or self.settings.queue_id}/list_all",
            params={"limit": limit},
        )
        if isinstance(data, dict):
            return data.get("items", data.get("queue", []))
        return data or []

    async def queue_item(self, item_id: int, queue_id: str | None = None) -> dict[str, Any]:
        return await self._request(
            "GET", f"/v1/queue/{queue_id or self.settings.queue_id}/i/{item_id}"
        )

    async def queue_clear(self, queue_id: str | None = None) -> None:
        await self._request("PUT", f"/v1/queue/{queue_id or self.settings.queue_id}/clear")

    async def queue_cancel(self, item_id: int, queue_id: str | None = None) -> None:
        await self._request(
            "PUT", f"/v1/queue/{queue_id or self.settings.queue_id}/i/{item_id}/cancel"
        )

    async def queue_cancel_batch(self, batch_ids: list[str], queue_id: str | None = None) -> None:
        await self._request(
            "PUT",
            f"/v1/queue/{queue_id or self.settings.queue_id}/cancel_by_batch_ids",
            json={"batch_ids": batch_ids},
        )

    async def queue_resume(self, queue_id: str | None = None) -> None:
        await self._request(
            "PUT", f"/v1/queue/{queue_id or self.settings.queue_id}/processor/resume"
        )

    async def queue_pause(self, queue_id: str | None = None) -> None:
        await self._request(
            "PUT", f"/v1/queue/{queue_id or self.settings.queue_id}/processor/pause"
        )

    async def queue_delete_item(self, item_id: int, queue_id: str | None = None) -> None:
        await self._request("DELETE", f"/v1/queue/{queue_id or self.settings.queue_id}/i/{item_id}")

    async def images_by_session(self, session_id: str, limit: int = 10) -> list[dict[str, Any]]:
        """v6 result lookup: images carry session_id; filter the recent feed."""
        data = await self.gallery_items(limit=limit)
        return [i for i in data.get("items", []) if i.get("session_id") == session_id]

    async def session_result(self, session_id: str, item_id: int) -> dict[str, Any]:
        images = await self.images_by_session(session_id)
        return {
            "items": [{"outputs": [{"image": {"image_name": i.get("image_name")}}]} for i in images]
        }

    # ----------------------------------------------------------------- models
    async def list_models(self, **params: Any) -> list[dict[str, Any]]:
        """List models. v6 accepts base_models/model_type/model_name/model_format;
        search and limit are applied client-side (the API has no search param)."""
        allowed = {
            k: v
            for k, v in params.items()
            if k in ("base_models", "model_type", "model_name", "model_format") and v
        }
        data = await self._request("GET", "/v2/models/", params=allowed or None)
        if isinstance(data, dict):
            models = data.get("models", data.get("items", []))
        else:
            models = data or []
        search = params.get("search")
        if search:
            needle = str(search).lower()
            models = [
                m
                for m in models
                if needle in (m.get("name") or "").lower() or needle in (m.get("key") or "").lower()
            ]
        limit = params.get("limit")
        if limit:
            models = models[: int(limit)]
        return models

    async def get_model(self, key: str) -> dict[str, Any]:
        return await self._request("GET", f"/v2/models/i/{key}")

    async def install_model(
        self, source: str, *, config: dict[str, Any] | None = None, inplace: bool = False
    ) -> dict[str, Any]:
        return await self._request(
            "POST",
            "/v2/models/install",
            params={"source": source, "inplace": str(inplace).lower()},
            json=config or {},
        )

    async def update_model(self, key: str, config: dict[str, Any]) -> dict[str, Any]:
        return await self._request("PATCH", f"/v2/models/i/{key}", json=config)

    async def delete_model(self, key: str) -> None:
        await self._request("DELETE", f"/v2/models/i/{key}")

    async def list_model_installs(self) -> list[dict[str, Any]]:
        data = await self._request("GET", "/v2/models/install")
        if isinstance(data, dict):
            return data.get("jobs", data.get("items", []))
        return data or []

    async def model_stats(self) -> dict[str, Any]:
        return await self._request("GET", "/v2/models/stats")

    # ----------------------------------------------------------------- gallery
    async def gallery_items(
        self, limit: int = 50, offset: int = 0, **filters: Any
    ) -> dict[str, Any]:
        """Image feed. v6 endpoint: /api/v1/images/ with search_term/board_id."""
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if filters.get("board_id"):
            params["board_id"] = filters["board_id"]
        if filters.get("starred") is not None:
            params["starred_first"] = filters["starred"]
        if filters.get("search"):
            params["search_term"] = filters["search"]
        data = await self._request("GET", "/v1/images/", params=params)
        if isinstance(data, dict):
            items = data.get("images", data.get("items", []))
            return {"items": items, "total": data.get("total", len(items))}
        return {"items": data or [], "total": len(data or [])}

    # ----------------------------------------------------------------- images
    async def list_images(self, limit: int = 50, offset: int = 0, **params: Any) -> dict[str, Any]:
        query = {"limit": limit, "offset": offset, **{k: v for k, v in params.items() if v}}
        return await self._request("GET", "/v1/images/", params=query)

    async def get_image(self, image_name: str) -> dict[str, Any]:
        return await self._request("GET", f"/v1/images/i/{image_name}")

    async def get_image_urls(self, image_name: str) -> dict[str, Any]:
        return await self._request("GET", f"/v1/images/i/{image_name}/urls")

    async def get_image_metadata(self, image_name: str) -> dict[str, Any]:
        return await self._request("GET", f"/v1/images/i/{image_name}/metadata")

    async def delete_image(self, image_name: str) -> None:
        await self._request("DELETE", f"/v1/images/i/{image_name}")

    async def delete_images(self, image_names: list[str]) -> None:
        await self._request("POST", "/v1/images/delete", json={"image_names": image_names})

    async def star_images(self, image_names: list[str]) -> None:
        await self._request("POST", "/v1/images/star", json={"image_names": image_names})

    async def unstar_images(self, image_names: list[str]) -> None:
        await self._request("POST", "/v1/images/unstar", json={"image_names": image_names})

    async def download_image(self, image_name: str, dest: Any) -> None:
        urls = await self.get_image_urls(image_name)
        full_url = urls.get("full", urls.get("url", ""))
        if not full_url:
            raise InvokeAIError(f"No download URL for image {image_name}", error_type="not_found")
        url = full_url if full_url.startswith("http") else f"{self.settings.api_base}{full_url}"
        async with self._client.stream("GET", url) as resp:
            resp.raise_for_status()
            with open(dest, "wb") as fh:
                async for chunk in resp.aiter_bytes():
                    fh.write(chunk)

    # ----------------------------------------------------------------- boards
    async def list_boards(self) -> list[dict[str, Any]]:
        data = await self._request("GET", "/v1/boards/")
        if isinstance(data, dict):
            return data.get("boards", [])
        return data or []

    async def get_board(self, board_id: str) -> dict[str, Any]:
        return await self._request("GET", f"/v1/boards/{board_id}")

    async def create_board(self, board_name: str) -> dict[str, Any]:
        return await self._request("POST", "/v1/boards", json={"board_name": board_name})

    async def update_board(self, board_id: str, board_name: str) -> dict[str, Any]:
        return await self._request(
            "PATCH", f"/v1/boards/{board_id}", json={"board_name": board_name}
        )

    async def delete_board(self, board_id: str) -> None:
        await self._request("DELETE", f"/v1/boards/{board_id}")

    async def add_images_to_board(self, board_id: str, image_names: list[str]) -> None:
        await self._request(
            "POST", "/v1/board_images", json={"board_id": board_id, "image_names": image_names}
        )

    async def remove_images_from_board(self, board_id: str, image_names: list[str]) -> None:
        await self._request(
            "DELETE", "/v1/board_images", json={"board_id": board_id, "image_names": image_names}
        )

    # --------------------------------------------------------------- workflows
    async def list_workflows(self, limit: int = 50, offset: int = 0) -> list[dict[str, Any]]:
        data = await self._request(
            "GET", "/v1/workflows/", params={"limit": limit, "offset": offset}
        )
        if isinstance(data, dict):
            return data.get("items", data.get("workflows", []))
        return data or []

    async def get_workflow(self, workflow_id: str) -> dict[str, Any]:
        return await self._request("GET", f"/v1/workflows/i/{workflow_id}")

    async def save_workflow(self, workflow: dict[str, Any]) -> dict[str, Any]:
        wid = workflow.get("id")
        if wid:
            return await self._request("PATCH", f"/v1/workflows/i/{wid}", json=workflow)
        return await self._request("POST", "/v1/workflows", json=workflow)

    async def delete_workflow(self, workflow_id: str) -> None:
        await self._request("DELETE", f"/v1/workflows/i/{workflow_id}")

    # ------------------------------------------------------------- custom nodes
    async def list_custom_nodes(self) -> list[dict[str, Any]]:
        data = await self._request("GET", "/v2/custom_nodes/")
        if isinstance(data, dict):
            return data.get("node_packs", [])
        return data or []

    async def install_custom_node(self, source: str) -> dict[str, Any]:
        return await self._request("POST", "/v2/custom_nodes/install", json={"source": source})

    async def uninstall_custom_node(self, pack_name: str) -> dict[str, Any]:
        return await self._request("DELETE", f"/v2/custom_nodes/{pack_name}")

    async def reload_custom_nodes(self) -> None:
        await self._request("POST", "/v2/custom_nodes/reload")

    async def capabilities(self) -> dict[str, Any]:
        """Live capability catalog derived from the engine's OpenAPI spec."""
        data = await self._request("GET", "/openapi.json", allow_error=True)
        if not isinstance(data, dict):
            return {}
        cats: dict[str, dict[str, Any]] = {}
        schemas = data.get("components", {}).get("schemas", {})
        for name, schema in schemas.items():
            if schema.get("class") != "invocation" or not schema.get("category"):
                continue
            cat = schema["category"]
            entry = cats.setdefault(cat, {"count": 0, "nodes": []})
            entry["count"] += 1
            if len(entry["nodes"]) < 5:
                entry["nodes"].append(name)
        return cats

    async def upload_image(self, file_bytes: bytes, filename: str) -> dict[str, Any]:
        """Upload an image to the engine gallery (multipart)."""
        files = {"file": (filename, file_bytes, "image/png")}
        return await self._request(
            "POST",
            "/v1/images/upload",
            params={"image_category": "general", "is_intermediate": "false"},
            files=files,
        )

    async def close(self) -> None:
        await self._client.aclose()


def url_for_image(settings: Settings, image_name: str) -> str:
    """Absolute URL to the full-size image (usable from the webapp)."""
    return f"{settings.api_base}/api/v1/images/i/{image_name}/full"


def url_for_thumbnail(settings: Settings, image_name: str) -> str:
    return f"{settings.api_base}/api/v1/images/i/{image_name}/thumbnail"
