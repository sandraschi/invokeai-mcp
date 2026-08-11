# Changelog

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
