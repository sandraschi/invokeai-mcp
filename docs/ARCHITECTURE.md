# InvokeAI MCP - Architecture

## System context

```
Claude Desktop / Cursor / opencode (stdio)          Browser (webapp)
        |                                                    |
        v                                                    v
invokeai-mcp (FastMCP 3.4 + Starlette, port 11154)           |
  - /mcp  : MCP streamable HTTP transport                    |
  - /api/*: REST for the webapp (health, skills, tools,      |
            logs, llm proxy, dashboard, generate, queue)     |
        |                                                    |
        +--------------------+-------------------------------+
                             v
              InvokeAI engine (port 9090, owned by InvokeAI)
                REST API v1/v2 - queue, models, gallery,
                boards, images, workflows, videos
```

Ports: backend 11154, frontend 11155 (fleet registry), InvokeAI itself runs
on 9090. CORS on the outer Starlette app covers both `/api/*` and the mounted
`/mcp` app (fleet CORS standard, Tauri origins + Tailscale/LAN regex).

## Source layout

| Path | Role |
|------|------|
| `src/invokeai_mcp/server.py` | FastMCP instance, Starlette app, dual transport, skill resource |
| `src/invokeai_mcp/client.py` | Typed InvokeAI REST client (all 23 router surfaces used) |
| `src/invokeai_mcp/graphs.py` | Graph builders: SD1.5 / SDXL / FLUX txt2img+img2img+inpaint, ESRGAN upscale |
| `src/invokeai_mcp/runtime.py` | Client singleton + ring-buffer logs |
| `src/invokeai_mcp/tools/` | 7 portmanteaus + 4 Prefab cards + help/shutdown |
| `src/invokeai_mcp/api/routes.py` | Starlette REST routes for the webapp |
| `src/invokeai_mcp/skills/` | SKILL.md files (exposed as `skill://` resources) |
| `webapp/` | Vite React + Tailwind dark SOTA webapp |

## Graph building

Graphs are constructed per model family because node types differ:

| Family | Loader | Conditioning | Denoise | Decode |
|--------|--------|--------------|---------|--------|
| sd-1 | main_model_loader + clip_skip | compel | denoise_latents | l2i |
| sdxl | sdxl_model_loader | sdxl_compel_prompt (clip+clip2) | denoise_latents | l2i |
| flux | flux_model_loader + flux_text_encoder | flux_compel_prompt | flux_denoise | flux_vae_decode |

Wiring verified against invoke-ai/InvokeAI `main` frontend graph builders
(2026-08) and live-tested against **InvokeAI 6.13.7**. v6 specifics the
client handles: nodes are FLAT (fields at node level, no `data` wrapper);
list endpoints use trailing slashes (`/api/v2/models/`); enqueue returns
`item_ids` + `batch`; `ModelIdentifierField` requires key/hash/name/base/type
(the list endpoint omits hash - the client fetches the full record);
`vae_loader` needs a `vae_model` value so the graphs wire the main loader's
`vae` output directly; queue status is nested under `queue`; there is no
`/sessions/.../result` endpoint - outputs are correlated via
images-by-`session_id`.
img2img adds `image -> image_to_latents -> denoise.latents` with
`denoising_start = 1 - strength`; inpaint adds `create_denoise_mask` into
`denoise.mask`. Upscale uses the `esrgan` node (RealESRGAN).

## Queue flow

```
invokeai_generate -> build graph -> POST /v1/queue/{qid}/enqueue_batch
  -> {queue_item_ids} -> invokeai_queue result (poll) -> session result
  -> output image URLs -> download_image -> local file
```

## Onboarding detection

`/api/health` and `invokeai_system(health)` probe
`GET /api/v1/app/version` on the InvokeAI host. `configured: false` drives
the webapp MOCK-until-onboarded UI and the red under-hero CTA.

## Declared doubles

- Webapp MOCK sample data (badged) until InvokeAI is reachable - declared in
  `webapp/src/lib/mockOnboarding.ts` and docs/ONBOARDING.md.
- No other fake paths: all tools return real API results or explicit errors.
