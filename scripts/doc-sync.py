"""Doc sync pass for invokeai-mcp v0.1.5."""
import pathlib

root = pathlib.Path(".")

# ---------- CHANGELOG ----------
p = pathlib.Path("CHANGELOG.md")
c = p.read_text(encoding="utf-8")
c = c.replace(
    "## [0.1.4] - 2026-08-12",
    """## [0.1.5] - 2026-08-12

### Added
- CogView4-6B graph builder + install (Apache-2.0, no token) - live-verified
- Engine lifecycle control: Settings > Engine control (start/stop/status,
  canvas UI link); REST /api/invokeai/engine/status|start|stop
- HuggingFace token login: Settings + Models HF tab (engine-stored token,
  gated repos installable); REST /api/invokeai/hf/status|login|logout
- Models page horizontal tabs: Local | HuggingFace
- Model catalog documented in README (2026 generation, VRAM/license/fit)
- models_dir moved to N:\\InvokeAI-models (715 GB free); Juggernaut XL v9
  default (2023 SDXL base removed)
- Generate: model-aware defaults (flux -> 4 steps / cfg 1.0)

## [0.1.4] - 2026-08-12""",
)
p.write_text(c, encoding="utf-8")

# ---------- PRD ----------
p = pathlib.Path("PRD.md")
c = p.read_text(encoding="utf-8")
c = c.replace(
    "6. SOTA webapp (catch-them-all pages) with declared MOCK-until-onboarded UX;\n   Generate page: 8 mode tabs, 60-style/24-material catalog, batch generation\n   with live progress, AI prompt refiner; Plugins page (node packs + catalog)",
    "6. SOTA webapp (catch-them-all pages) with declared MOCK-until-onboarded UX;\n   Generate page: 8 mode tabs, 60-style/24-material catalog, batch generation\n   with live progress, AI prompt refiner; Plugins page (node packs + catalog);\n   engine lifecycle control; HuggingFace token login; CogView4 support",
)
p.write_text(c, encoding="utf-8")

# ---------- AGENTS.md ----------
p = pathlib.Path("AGENTS.md")
c = p.read_text(encoding="utf-8")
c = c.replace(
    "| `src/invokeai_mcp/api/routes.py` | REST routes (health, dashboard, skills, tools, logs, llm, generate, queue) |",
    "| `src/invokeai_mcp/api/routes.py` | REST routes (health, dashboard, skills, tools, logs, llm, generate, queue, upload, image proxy, plugins, hf login, engine control) |",
)
c = c.replace(
    "invokeai_generate (txt2img/img2img/inpaint/upscale/outpaint + seamless/\ncontrolnet/ip-adapter modules - outpaint via webapp pad+mask, API inpaint),",
    "invokeai_generate (txt2img/img2img/inpaint/upscale/outpaint + seamless/\ncontrolnet/ip-adapter modules + cogview4 family - outpaint via webapp pad+mask),\nengine control (Settings) + HF token login (Settings + Models HF tab),",
)
p.write_text(c, encoding="utf-8")

# ---------- CONFIGURATION.md: engine control + models_dir ----------
p = pathlib.Path("docs/CONFIGURATION.md")
c = p.read_text(encoding="utf-8")
c = c.replace(
    "## Engine-side tuning (invokeai.yaml)",
    "## Engine process control\n\nThe engine is a separate process (invokeai-web). Control it from the webapp\nSettings > Engine control (start/stop/status), or REST:\n\n- `GET  /api/invokeai/engine/status` - running, pid, version\n- `POST /api/invokeai/engine/start` - spawn detached (logs to D:\\InvokeAI\\engine.log)\n- `POST /api/invokeai/engine/stop` - kill the engine process\n\n## Models location\n\nModels live on **N:\\InvokeAI-models** (engine `models_dir` in invokeai.yaml) -\n715 GB free; D: holds only the install. Move the dir + update `models_dir`\nwhen relocating.\n\n## Engine-side tuning (invokeai.yaml)",
)
p.write_text(c, encoding="utf-8")

print("repo docs updated")
