"""Tool-level tests with a mocked InvokeAI client."""

from __future__ import annotations

import pytest

import invokeai_mcp.runtime as runtime
from invokeai_mcp.client import InvokeAIError


class FakeClient:
    """Minimal stand-in for InvokeAIClient."""

    def __init__(self):
        self.models_cache = {}
        self.calls = []

    async def refresh_models(self):
        self.models_cache = {
            "main": [{"key": "m1", "name": "SDXL", "type": "main", "base": "sdxl"}]
        }
        return self.models_cache

    async def list_models(self, **kw):
        return [{"key": "m1", "name": "SDXL", "type": "main", "base": "sdxl"}]

    async def enqueue_batch(self, graph, runs=1, destination="mcp"):
        self.calls.append(("enqueue", graph, runs))
        return {"batch_id": "b1", "queue_item_ids": [7], "queue_id": "default"}

    async def queue_status(self):
        return {"queued": 2, "in_progress": 1, "completed": 5, "failed": 0, "canceled": 0}

    async def queue_item(self, item_id):
        return {"id": item_id, "status": "completed", "session_id": "s1"}

    async def session_result(self, session_id, item_id):
        return {"items": [{"outputs": [{"image": {"image_name": "out.png"}}]}]}

    async def app_version(self):
        return {"version": "5.7.0", "app": "InvokeAI"}

    async def ping(self):
        return True


@pytest.fixture
def fake(monkeypatch):
    fc = FakeClient()
    monkeypatch.setattr(runtime, "_client", fc)
    return fc


async def test_generate_txt2img_enqueues(fake):
    from invokeai_mcp.tools.generate_tools import invokeai_generate

    result = await invokeai_generate(operation="txt2img", prompt="a red car")
    assert result["success"] is True
    assert result["queue_item_id"] == 7
    assert fake.calls[0][1]["nodes"]  # graph has nodes


async def test_generate_img2img_requires_image(fake):
    from invokeai_mcp.tools.generate_tools import invokeai_generate

    result = await invokeai_generate(operation="img2img", prompt="x")
    assert result["success"] is False
    assert result["error"] == "validation"


async def test_queue_result_returns_outputs(fake):
    from invokeai_mcp.tools.queue_tools import invokeai_queue

    result = await invokeai_queue(operation="result", item_id=7)
    assert result["success"] is True
    assert result["data"]["outputs"][0]["image_name"] == "out.png"


async def test_queue_status(fake):
    from invokeai_mcp.tools.queue_tools import invokeai_queue

    result = await invokeai_queue(operation="status")
    assert result["data"]["queued"] == 2


async def test_models_list(fake):
    from invokeai_mcp.tools.model_tools import invokeai_models

    result = await invokeai_models(operation="list")
    assert result["success"] is True
    assert result["data"]["count"] == 1


async def test_system_health_configured(fake):
    from invokeai_mcp.tools.system_tools import invokeai_system

    result = await invokeai_system(operation="health")
    assert result["configured"] is True


async def test_error_dialogic_on_failure(fake, monkeypatch):
    async def boom(*args, **kwargs):
        raise InvokeAIError("engine down", error_type="connection_error")

    monkeypatch.setattr(fake, "ping", boom)
    from invokeai_mcp.tools.system_tools import invokeai_system

    result = await invokeai_system(operation="health")
    assert result["success"] is False
    assert result["configured"] is False
    assert result["dialogic"]["remediation"]


async def test_help_index(fake):
    from invokeai_mcp.tools.system_tools import invokeai_help

    result = await invokeai_help()
    assert "invokeai_generate" in result["help"]
