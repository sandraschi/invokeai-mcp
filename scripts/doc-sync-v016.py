"""Doc sync for v0.1.6 (styles tools)."""
import pathlib

c = pathlib.Path("CHANGELOG.md").read_text(encoding="utf-8")
c = c.replace(
    "## [0.1.5] - 2026-08-12",
    """## [0.1.6] - 2026-08-12

### Added
- invokeai_styles tool (list/get/search) - style catalog moved into the
  backend as single source of truth (data/styles.json, 69 presets)
- invokeai_generate styles=[...] + style_cfg params: multi-style batches
  enqueue one item per style (prompt suffix + style cfg/steps)
- GET /api/invokeai/styles; Generate page now fetches the live catalog
  with the bundled presets.ts as offline fallback

## [0.1.5] - 2026-08-12""",
)
pathlib.Path("CHANGELOG.md").write_text(c, encoding="utf-8")

l = pathlib.Path("llms-full.txt").read_text(encoding="utf-8")
l = l.replace(
    "## v0.1.5 additions",
    """## v0.1.6 additions

Styles are backend-owned (data/styles.json, 69 presets): invokeai_styles
(operation=list|get|search, style_id/query/limit) lists presets with
id/name/prompt/negative/cfg/steps. Pass ids to
invokeai_generate(styles=["photorealistic","watercolor"], style_cfg=true)
for a multi-style batch - one item per style, style prompt appended,
style cfg/steps applied unless style_cfg=false. REST: GET /api/invokeai/styles.

## v0.1.5 additions""",
)
pathlib.Path("llms-full.txt").write_text(l, encoding="utf-8")

a = pathlib.Path("AGENTS.md").read_text(encoding="utf-8")
a = a.replace(
    "invokeai_workflows, invokeai_system",
    "invokeai_styles (list/get/search), invokeai_workflows, invokeai_system",
)
a = a.replace(
    "controlnet/ip-adapter modules + cogview4 family - outpaint via webapp pad+mask),",
    "controlnet/ip-adapter modules + cogview4 family + styles=[...] multi-style batches - outpaint via webapp pad+mask),",
)
pathlib.Path("AGENTS.md").write_text(a, encoding="utf-8")
print("docs updated")
