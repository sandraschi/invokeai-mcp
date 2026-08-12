# invokeai-mcp — Agent Guide

Fleet MCP server (Creative / Image Generation). Wraps the local InvokeAI
engine (port 9090). Ports **11154** (backend) / **11155** (frontend).

## Overview

FastMCP 3.4+ bridge: generate (txt2img/img2img/inpaint/upscale), queue,
models, gallery, boards, workflows + SOTA dark webapp. Onboarding required
(InvokeAI must be installed + running + models installed) - MOCK-until-onboarded UI.

## Standards

- FastMCP 3.4.4+ portmanteau + skills (`skill://` resource) + Prefab cards
- Dual transport: stdio (default) + HTTP `--mode http` (MCP `/mcp`, REST `/api/*`)
- Starlette 1.0 REST (no Pydantic in routes), fleet CORS on outer app
- MCPB: `just mcpb-pack` (wipe+recopy src -> mcpb/src, 3-4-100 verified)
- Onboarding: `docs/ONBOARDING.md` + red under-hero CTA + MOCK badges
- No GitHub Actions while private; local `just ci` is the gate

## Key files

| Path | Role |
|------|------|
| `src/invokeai_mcp/server.py` | FastMCP + Starlette app, dual transport |
| `src/invokeai_mcp/client.py` | Typed InvokeAI REST client |
| `src/invokeai_mcp/graphs.py` | Graph builders (sd1/sdxl/flux, inpaint, esrgan upscale) |
| `src/invokeai_mcp/tools/` | 7 portmanteaus + 4 Prefab cards + help/shutdown |
| `src/invokeai_mcp/api/routes.py` | REST routes (health, dashboard, skills, tools, logs, llm, generate, queue) |
| `src/invokeai_mcp/skills/invokeai-expert/` | SKILL.md |
| `webapp/` | Vite React + Tailwind dark UI + Playwright e2e |

## Quick ref

```powershell
.\start.ps1
uv run pytest tests/ -q
cd webapp; bun run dev
just mcpb-pack
```

## Tool surface (portmanteau)

invokeai_generate (txt2img/img2img/inpaint/upscale/outpaint + seamless/
controlnet/ip-adapter modules - outpaint via webapp pad+mask, API inpaint), invokeai_queue
(status/list/item_status/result/cancel/clear/resume/pause), invokeai_models
(list/get/install/installs/update/delete/stats), invokeai_gallery
(list/search/get/metadata/download/delete/star/unstar), invokeai_boards,
invokeai_workflows, invokeai_system (health/version/config/stats), 4 Prefab
cards, invokeai_help, invokeai_shutdown.

## Honesty

- `outpaint` / canvas regions are NOT exposed (InvokeAI canvas UI only) -
  no stub.
- All tool failures return `{success: false, error, message, dialogic}`.
- Webapp mock data is declared (mockOnboarding.ts) and badged `[MOCK]`.
