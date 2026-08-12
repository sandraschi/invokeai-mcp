# Changelog

## [0.1.2] - 2026-08-12

### Added
- Generate page: 8 horizontal mode tabs (txt2img, img2img, inpaint, outpaint,
  upscale, controlnet, ip-adapter, seamless) with image/mask uploads
- 60-style catalog + 24 materials (stained glass, tilt-shift, disco, super
  mario, ukiyo-e, art nouveau, vaporwave, ...) with select-all batch generation
  and live per-item progress bar
- Outpaint via client-side pad + border-mask inpaint (canvas-safe image proxy)
- Plugins page: custom node pack install/uninstall/reload (git) + live
  built-in capability catalog (19 categories, 253 nodes from the engine spec)
- AI prompt refiner wired to local LLM with style/material context
- Live-verified modes: txt2img, img2img, inpaint, upscale, seamless

## [0.1.1] - 2026-08-12

Live-verified against InvokeAI 6.13.7.

### Fixed
- v6 API alignment: flat graph node fields (no `data` wrapper), trailing
  slashes on list endpoints, `item_ids`/`batch` in enqueue response,
  `ModelIdentifierField` requires base+type, vae wired from main loader
  (vae_loader needs a vae_model value), queue status unwrap, results via
  images-by-session (v6 has no /sessions/.../result endpoint)
- Engine install path: manual `invokeai-web` install (launcher GUI has a
  uv-managed-Python lock collision with the fleet); engine VRAM capped via
  invokeai.yaml (`max_cache_vram_gb: 8`, `precision: float16`) so desktop
  apps + engine coexist on the 4090

### Added
- Onboarding completed on Goliath: InvokeAI 6.13.7 + SDXL base installed
- README Preview screenshots (live data) via `just screenshots`

## [0.1.0] - 2026-08-11

Initial release.

### Added
- FastMCP 3.4.4+ server, dual transport (stdio + HTTP `/mcp`, `/api/*`)
- Tool surface: invokeai_generate (txt2img/img2img/inpaint/upscale),
  invokeai_queue, invokeai_models, invokeai_gallery, invokeai_boards,
  invokeai_workflows, invokeai_system, 4 Prefab cards, help, shutdown
- Graph builders verified against InvokeAI main (sd-1 / sdxl / flux families)
- Starlette REST API: health, dashboard, skills, tools, logs, LLM proxy,
  generate/queue endpoints (fleet CORS, Tauri + Tailscale origins)
- SOTA webapp (React/Vite/Tailwind/Zustand/Bun): Dashboard, Generate,
  Gallery, Models, Queue, Boards, Workflows, Inbox, Tools, Skills, Chat,
  Settings, Help, Logs
- Onboarding: docs/ONBOARDING.md, red under-hero CTA, MOCK-until-onboarded
- Skills (skill:// resource), docs stack, llms.txt pair, glama.json, manifest
- MCPB packaging with 3-4-100 prompts + wipe+recopy pack script
- Tests: client (respx), graphs (invariants), tools (fake client), Playwright e2e
- CI workflow (Windows-only, lightweight) + local `just ci`
