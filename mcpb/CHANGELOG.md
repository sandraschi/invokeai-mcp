# Changelog

## [0.1.11] - 2026-08-12

### Added
- invokeai_franchises tool + 23 fan-style franchise presets (Super Mario,
  Zelda, Pokemon, Minecraft, Ghibli, Shinkai, Disney, Pixar, Tim Burton,
  Simpsons, Marvel, Star Wars, LotR, Harry Potter, D&D, Warhammer 40k,
  MTG, Doom, Portal, Sonic, Hollow Knight, Undertale, Animal Crossing)
  - fan-style descriptors for personal creative use
- invokeai_generate franchises=[...] param; appended LAST (strongest
  identity cue): base -> style -> material -> painter -> franchise;
  styles x artists x franchises cartesian (capped 100)
- Attribution records franchises; gallery franchise filter + chips
  (fuchsia); REST /api/invokeai/franchises; Generate page 4th checkbox
  group; Gallery filter dropdown
- Fixed duplicated name in anchors ("in the style of Super Mario, super
  mario style..." -> clean signature)

## [0.1.10] - 2026-08-12

### Changed
- Generate page: styles/materials/painters checkbox panels moved into a
  collapsible "Batch presets" card (hidden by default, selection count in
  the header); batch action button lives in its own always-visible card

## [0.1.9] - 2026-08-12

### Added
- invokeai_artists tool + 60-painter catalog (Giotto to Giger) with
  curated one-line signatures; painters anchor the prompt LAST
  (base -> style -> material -> painter = strongest cue)
- invokeai_generate artists=[...] param; styles x artists cartesian
  (capped 100); per-item attribution now records styles + artists
- Gallery: painter filter (exact + fallback) and painter chips
- Fixed broken images: engine returns RELATIVE image urls - feed now
  normalizes to absolute (browser was 404ing against the webapp origin)
- display_name: prompt-slug + short id (marlowe-in-rain-2774b797)
  instead of the raw uuid; Generate page painter checkboxes (search,
  select-all) cross-batched with styles x materials

## [0.1.8] - 2026-08-12

### Added
- Exact per-image style attribution: enqueue-time registry
  (data/attribution.json, item_id -> styles), joined through
  image.session_id == queue item session_id
- Gallery feed returns per-image styles[]; style filter matches exactly,
  falling back to prompt-signature matching for pre-registry images
- Style chips on gallery tiles + lightbox (up to 3, +N overflow)
- Fixed per-item attribution bug (was recording the full style set on
  every job of a batch)

## [0.1.7] - 2026-08-12

### Added
- Gallery: sorting (created_at/name/starred, asc/desc), filters (starred,
  board, style from the catalog, prompt search) via dedicated REST feed
- Batch ops: multi-select mode, select-page, batch star/unstar/delete,
  zip export (backend streams a real archive), move-to-board
- invokeai_gallery batch ops: batch_delete/batch_star/batch_unstar/
  board_add/board_remove (MCP parity)
- GET /api/invokeai/boards; client.list_boards v6 "all" param fix
- Style matching for gallery filtering (match_style_for_prompt)

## [0.1.6] - 2026-08-12

### Added
- invokeai_styles tool (list/get/search) - style catalog moved into the
  backend as single source of truth (data/styles.json, 69 presets)
- invokeai_generate styles=[...] + style_cfg params: multi-style batches
  enqueue one item per style (prompt suffix + style cfg/steps)
- GET /api/invokeai/styles; Generate page now fetches the live catalog
  with the bundled presets.ts as offline fallback

## [0.1.5] - 2026-08-12

### Added
- CogView4-6B graph builder + install (Apache-2.0, no token) - live-verified
- Engine lifecycle control: Settings > Engine control (start/stop/status,
  canvas UI link); REST /api/invokeai/engine/status|start|stop
- HuggingFace token login: Settings + Models HF tab (engine-stored token,
  gated repos installable); REST /api/invokeai/hf/status|login|logout
- Models page horizontal tabs: Local | HuggingFace
- Model catalog documented in README (2026 generation, VRAM/license/fit)
- models_dir moved to N:\InvokeAI-models (715 GB free); Juggernaut XL v9
  default (2023 SDXL base removed)
- Generate: model-aware defaults (flux -> 4 steps / cfg 1.0)

## [0.1.4] - 2026-08-12

### Added
- Generation metadata embedded in output PNGs (core_metadata node: prompt,
  seed, steps, cfg, scheduler, model, size, mode) - verified in-file

### Fixed
- Image quality: GPU noise (was CPU RNG), SDXL cfg_rescale 0.7 (was 0 -
  the muddy/oversaturated SDXL failure mode), default steps 35, scheduler
  dpmpp_2m_sde; Juggernaut XL v9 installed as the structural-quality SDXL
  checkpoint (SDXL base 1.0 is a 2023 model - malformed geometry is model-level)

## [0.1.3] - 2026-08-12

### Fixed
- Black output images (SDXL fp16 VAE decode) - l2i nodes now decode in fp32;
  verified pixel brightness 0 -> 152/255 on live generation
- Gallery/queue list envelope unwrap (empty lists)

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
