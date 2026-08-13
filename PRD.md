# PRD — invokeai-mcp

## Product

InvokeAI MCP bridge: Claude/Cursor/opencode + fleet webapp drive a local
InvokeAI creative engine (SD1.5/SDXL/Flux/SD3.5/Qwen Image) on the user's GPU.

## Goals (v0.1)

1. Full generation loop in chat: txt2img, img2img, masked inpaint, 4x upscale,
   outpaint, ControlNet (canny), IP-Adapter, seamless tiling (all live-verified
   against InvokeAI 6.13.7 except controlnet/ipadapter which need their models)
2. Queue lifecycle: status, list, result polling, cancel, clear, resume
3. Model management: list, install (HF/Civitai/local), delete, stats
4. Gallery + boards: search, download, star, organize
5. Workflow library CRUD
6. SOTA webapp (catch-them-all pages) with declared MOCK-until-onboarded UX;
   Generate page: 8 mode tabs, 60-style/24-material catalog, batch generation
   with live progress, AI prompt refiner; Plugins page (node packs + catalog);
   engine lifecycle control; HuggingFace token login; CogView4 support
7. MCPB + dual transport (stdio/HTTP) + Prefab cards

## Non-goals (v0.1)

- Canvas region outpaint (InvokeAI web UI only) - explicit, no stub
- ControlNet/Adapters/Refiner graph wiring (later)
- Video generation (Wan) - API client has endpoints; tools come later
- Tauri/NSIS installer (release tier T2; native later if used)

## Success metrics

- `just ci` green, assfix-zero on first assess
- Generation round-trip via chat: enqueue -> poll -> image URL
- Webapp onboarding: MOCK -> connected flip without reload hacks

## Ports

11154 backend / 11155 frontend (registry updated 2026-08-11).
