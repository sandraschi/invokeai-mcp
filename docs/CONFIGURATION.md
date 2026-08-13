# InvokeAI MCP - Configuration

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `INVOKEAI_URL` | `http://127.0.0.1:9090` | Base URL of the running InvokeAI instance |
| `INVOKEAI_QUEUE_ID` | `default` | InvokeAI queue id used for enqueue/control |
| `INVOKEAI_DOWNLOAD_DIR` | `<repo>/data/downloads` | Where `download` operations save files |
| `INVOKEAI_MCP_PORT` | `11154` | Backend HTTP port (REST + MCP `/mcp`) |
| `INVOKEAI_FRONTEND_PORT` | `11155` | Vite dev port for the webapp |
| `INVOKEAI_ACCESS_TOKEN` | *(empty)* | Token passed to InvokeAI for gated model sources |
| `INVOKEAI_TIMEOUT` | `120` | HTTP request timeout in seconds |

## Setting Variables

Copy `.env.example` to `.env` in the repo root, or set them in
`claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "invokeai": {
      "command": "uv",
      "args": ["--directory", "C:\\path\\to\\invokeai-mcp", "run", "invokeai-mcp"],
      "env": {
        "INVOKEAI_URL": "http://127.0.0.1:9090"
      }
    }
  }
}
```

## Ports

| Port | Service | Registry |
|------|---------|----------|
| 11154 | invokeai-mcp backend (REST `/api/*`, MCP `/mcp`) | [WEBAPP_PORTS.md](../../../mcp-central-docs/operations/WEBAPP_PORTS.md) |
| 11155 | webapp frontend (Vite dev) | same |
| 9090 | InvokeAI engine (owned by InvokeAI, not this repo) | n/a |

## Engine-side tuning (invokeai.yaml)

The InvokeAI engine reads `D:\InvokeAI\invokeai.yaml` (or the install root).
The fleet-tested profile on Goliath (RTX 4090 with desktop apps resident):

```yaml
max_cache_vram_gb: 8
precision: float16
```

Without the VRAM cap the engine assumes it owns all 24 GB and OOMs during
generation when other apps (Discord, Notion, Edge, Steam) hold ~11 GB.

## HuggingFace integration

Two ways to authenticate with HuggingFace for gated model downloads:

| Method | Where | Persists |
|--------|-------|----------|
| **Engine login** | Settings page > HuggingFace (or Models > HuggingFace tab) - token field | Engine HF cache (recommended; enables gated repos) |
| `INVOKEAI_ACCESS_TOKEN` | `.env` / mcpServers env | Env only; passed per-install as Bearer |

Token: create at https://huggingface.co/settings/tokens (read scope is enough).
Gated repos (FLUX.1-dev/schnell, SD3.5, many community checkpoints) additionally
require accepting the repo license once in the browser on huggingface.co.

REST surface: `GET /api/invokeai/hf/status`, `POST /api/invokeai/hf/login` `{token}`,
`DELETE /api/invokeai/hf/logout` - mirrored as Settings > HuggingFace and the
Models page HuggingFace tab.

## Queue destination

Enqueued batches carry `destination: "mcp"` (or `"webapp"` for UI-triggered
generation) so results are easy to distinguish in the InvokeAI queue.
