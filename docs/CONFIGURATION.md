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

## Queue destination

Enqueued batches carry `destination: "mcp"` (or `"webapp"` for UI-triggered
generation) so results are easy to distinguish in the InvokeAI queue.
