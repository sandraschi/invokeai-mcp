# Onboarding - InvokeAI MCP

## What this is for

This MCP server lets Claude, Cursor, and the fleet webapp drive your local
InvokeAI creative engine: text-to-image, image-to-image, masked inpaint, and
4x upscaling with SD1.5, SDXL, Flux, SD3.5, Qwen Image, and more. It does
NOT bundle InvokeAI, its models, or a GPU driver - those live on your machine
and are yours to install once. It also does not replace the InvokeAI canvas
web UI for region-based outpaint workflows.

## Cost and accounts (money / CC)

| Question | Answer |
|----------|--------|
| Do I need an account? | No - InvokeAI is fully local. Optional HuggingFace/Civitai account for gated model downloads. |
| Free tier? | Yes - everything is free and open source (Apache-2.0). |
| Credit card required? | No. |
| Ongoing cost? | Free - only electricity for your GPU. |
| Who bills? | Nobody. |

## Prerequisites outside this repo

- **GPU with 6-12 GB VRAM** recommended (RTX 4090 is excellent). SD1.5 needs
  ~4 GB, SDXL ~8 GB, Flux.1 dev ~12-16 GB.
- **InvokeAI installed** via its launcher (Electron GUI, handles Python +
  CUDA automatically): https://github.com/invoke-ai/launcher/releases/latest
- **~10-30 GB free disk** for model downloads (SDXL ~7 GB, Flux ~12-24 GB).
- Windows 10/11, macOS, or Linux (this machine: Windows 11 + RTX 4090).

## First-timer setup steps

1. Download and run the InvokeAI launcher
   (`Invoke.Community.Edition.Setup.latest.exe`). Pick an install location.
2. In the launcher, click **Install** (or update) to install the InvokeAI
   engine. This downloads the app (a few GB) and prepares the Python env.
3. Start InvokeAI with the launcher. The first start may take a few minutes.
4. When it is running, open the InvokeAI web UI (it opens automatically,
   usually http://127.0.0.1:9090).
5. In the UI: Models tab, Install a model. Recommended starters:
   - `stabilityai/stable-diffusion-xl-base-1.0` (SDXL, 1024x1024)
   - `black-forest-labs/FLUX.1-dev` (best quality, 12+ GB VRAM)
   - `runwayml/stable-diffusion-v1-5` (fastest, 512x512)
6. Keep InvokeAI running (or start it via the launcher before using this MCP).
7. Start the MCP server (INSTALL.md Options A-D) and ask it: "Check the
   InvokeAI health" - it should report reachable.

## Pitfalls (read before you click Generate)

- **InvokeAI must be running.** The MCP bridge connects to
  `http://127.0.0.1:9090`; if the launcher is closed, generation fails with a
  connection error. Start it first.
- **No models = no generation.** The bridge reports an explicit
  "no main models installed" error; it will not pretend to work. Install at
  least one main model in the InvokeAI UI first.
- **VRAM pressure.** Flux models need ~12 GB VRAM. If generation fails with
  CUDA out of memory, switch to SDXL or SD1.5 or lower the resolution.
- **Flux ignores negative prompts** (no negative conditioning in the
  architecture) - SD1.5/SDXL use them normally.
- **Canvas outpaint is not exposed** through this bridge - region editing
  stays in the InvokeAI web UI.
- **First generation is slow** - the model loads into VRAM (10-60s), then
  generation is fast.
- **Don't run two big models at once** - InvokeAI unloads models from VRAM
  between queue items; a failed job can leave the queue paused. Use
  `invokeai_queue(operation="resume")` if the processor paused.

## Sanity check

Onboarding worked when all of these are true:

- `invokeai_system(operation="health")` returns `configured: true`
- The webapp dashboard shows the green "InvokeAI connected" badge and real
  model counts (no MOCK badges)
- `invokeai_models(operation="list")` shows your installed main models
- One dry-run call: `invokeai_generate(operation="txt2img", prompt="test")`
  enqueues an item, and `invokeai_queue(operation="result", item_id=N,
  wait_seconds=120)` returns an output image

## Declared doubles

- Before InvokeAI is reachable, the webapp shows **declared MOCK sample
  content** (badged `[MOCK]`, fake names like "Joe Mocky") that clears once
  the health probe succeeds. This is intentional - see
  [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) "Declared doubles".
- Tools return explicit `connection_error` / `no_model` failures instead of
  fake success. No silent mock paths exist in the MCP tools.
