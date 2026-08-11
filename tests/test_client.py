"""Tests for the InvokeAI HTTP client (mocked transport via respx)."""

from __future__ import annotations

import httpx
import pytest
import respx

from invokeai_mcp.client import InvokeAIClient, InvokeAIError
from invokeai_mcp.config import Settings


@pytest.fixture
def settings(tmp_path) -> Settings:
    return Settings(invokeai_url="http://fake.invokeai:9090", download_dir=tmp_path / "dl")


@pytest.fixture
def client(settings):
    with respx.mock(assert_all_mocked=True) as router:
        http = httpx.AsyncClient(base_url="http://fake.invokeai:9090")
        c = InvokeAIClient(settings, client=http)
        yield c, router


async def test_app_version_ok(client):
    c, router = client
    router.get("http://fake.invokeai:9090/api/v1/app/version").respond(
        json={"version": "5.7.0", "app": "InvokeAI"}
    )
    data = await c.app_version()
    assert data["version"] == "5.7.0"


async def test_connection_error_is_wrapped(client):
    c, router = client
    router.get("http://fake.invokeai:9090/api/v1/app/version").side_effect = httpx.ConnectError(
        "refused"
    )
    with pytest.raises(InvokeAIError) as exc:
        await c.app_version()
    assert exc.value.error_type == "connection_error"


async def test_http_error_is_wrapped(client):
    c, router = client
    router.get("http://fake.invokeai:9090/api/v1/app/version").respond(status_code=500, text="boom")
    with pytest.raises(InvokeAIError) as exc:
        await c.app_version()
    assert exc.value.status == 500


async def test_enqueue_batch_payload(client):
    c, router = client
    router.post("http://fake.invokeai:9090/api/v1/queue/default/enqueue_batch").respond(
        json={"batch_id": "b1", "queue_item_ids": [42], "queue_id": "default"}
    )
    graph = {"id": "g1", "nodes": {}, "edges": []}
    data = await c.enqueue_batch(graph, runs=2, destination="mcp")
    assert data["queue_item_ids"] == [42]
    req = router.calls.last.request
    body = req.read().decode()
    assert '"runs":2' in body
    assert '"destination":"mcp"' in body
    assert '"graph"' in body


async def test_list_models_passthrough(client):
    c, router = client
    router.get("http://fake.invokeai:9090/api/v2/models/").respond(
        json={"models": [{"key": "k1", "name": "SDXL Base", "type": "main", "base": "sdxl"}]}
    )
    models = await c.list_models(model_type="main")
    assert models[0]["key"] == "k1"


async def test_install_model_sends_config_body(client):
    c, router = client
    router.post("http://fake.invokeai:9090/api/v2/models/install").respond(
        json={"id": "job1", "status": "running"}
    )
    data = await c.install_model("hf/repo", config={"name": "Custom"})
    assert data["id"] == "job1"
    req = router.calls.last.request
    assert "source=hf%2Frepo" in str(req.url)
    assert '"name":"Custom"' in req.read().decode()


async def test_download_image_writes_file(client, tmp_path):
    c, router = client
    router.get("http://fake.invokeai:9090/api/v1/images/i/img1.png/urls").respond(
        json={"full": "/api/v1/images/i/img1.png/full"}
    )
    router.get("http://fake.invokeai:9090/api/v1/images/i/img1.png/full").respond(
        content=b"PNGDATA"
    )
    dest = tmp_path / "img1.png"
    await c.download_image("img1.png", dest)
    assert dest.read_bytes() == b"PNGDATA"


async def test_gallery_items_sends_filters(client):
    c, router = client
    router.get("http://fake.invokeai:9090/api/v1/images/").respond(
        json={"items": [{"image_name": "a.png", "session_id": "s1"}], "total": 1}
    )
    data = await c.gallery_items(limit=10, board_id="b1", search="cat")
    req = str(router.calls.last.request.url)
    assert "limit=10" in req and "board_id=b1" in req and "search_term=cat" in req
    assert data["items"][0]["image_name"] == "a.png"


async def test_enqueue_batch_v6_response(client):
    c, router = client
    router.post("http://fake.invokeai:9090/api/v1/queue/default/enqueue_batch").respond(
        json={
            "queue_id": "default",
            "enqueued": 1,
            "requested": 1,
            "batch": {"batch_id": "b9"},
            "priority": 0,
            "item_ids": [7],
        }
    )
    data = await c.enqueue_batch({"id": "g1", "nodes": {}, "edges": []}, runs=1)
    assert data["queue_item_ids"] == [7]
    assert data["batch_id"] == "b9"


async def test_images_by_session(client):
    c, router = client
    router.get("http://fake.invokeai:9090/api/v1/images/").respond(
        json={
            "items": [
                {"image_name": "a.png", "session_id": "s1"},
                {"image_name": "b.png", "session_id": "s2"},
            ],
            "total": 2,
        }
    )
    images = await c.images_by_session("s2")
    assert [i["image_name"] for i in images] == ["b.png"]
