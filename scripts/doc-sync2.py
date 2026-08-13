"""Add v0.1.5 additions to llms-full.txt."""
import pathlib

p = pathlib.Path("llms-full.txt")
c = p.read_text(encoding="utf-8")

addition = """
## v0.1.5 additions

Model families: sd-1, sdxl, flux, cogview4 (CogView4-6B, Apache-2.0, no HF
token - GLM text encoder + transformer denoise nodes). sd-3, qwen-image,
z-image, flux2 builders are follow-up work; the engine supports them natively.

Engine control (webapp Settings > Engine control, REST):
- GET  /api/invokeai/engine/status - running/pid/version
- POST /api/invokeai/engine/start - spawn detached (logs D:\\InvokeAI\\engine.log)
- POST /api/invokeai/engine/stop

HuggingFace login (gated repos, e.g. official FLUX.1):
- GET  /api/invokeai/hf/status - valid | invalid | unknown
- POST /api/invokeai/hf/login  {token: hf_...}
- DELETE /api/invokeai/hf/logout
Token is stored by the engine (HF cache). UI: Settings > HuggingFace and the
Models page HuggingFace tab. Accept gated licenses once on huggingface.co.

Models directory: N:\\InvokeAI-models (engine models_dir in invokeai.yaml).

Model catalog (2026): FLUX.1 dev/schnell + FLUX.2 (gated), SD 3.5 large/medium
(license+token), SDXL/Juggernaut (open, default), CogView4-6B (Apache-2.0),
Z-Image turbo/base (permissive), Qwen-Image 20B (Apache-2.0, needs ~20 GB
fp8 - heavy for a 24 GB GPU with desktop apps), SD 1.5 (legacy).
"""
c = c.rstrip() + "\n" + addition
p.write_text(c, encoding="utf-8")
print("llms-full updated, lines:", len(c.splitlines()))
