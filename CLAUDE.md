# invokeai-mcp — Claude Code context

## Session context (InvokeAI MCP)

You have access to the local InvokeAI creative engine: image generation
(txt2img/img2img/inpaint/upscale), queue control, model management,
gallery/board organization, and workflow library management.

**Before starting work:**
1. Check engine health: `invokeai_system(operation="health")` - if
   `configured` is false, InvokeAI is not running; tell the user, don't
   pretend generation works.
2. Check installed models: `invokeai_models(operation="list", model_type="main")`
   - the first entry is the default generation model.

**At end of work, save outputs:**
- Download generated images locally:
  `invokeai_queue(operation="result", item_id=..., download_image=true)`
- Organize favorites into boards:
  `invokeai_boards(operation="add_image", board_id=..., image_names=[...])`

**Workflow:** generate -> poll queue (result, wait_seconds) -> gallery -> download.

**Pitfalls:** flux ignores negative prompts; outpaint is canvas-only (web UI);
first generation is slow (model load); VRAM errors -> use SDXL/SD1.5 or lower
resolution.
