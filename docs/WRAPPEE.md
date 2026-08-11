# InvokeAI - the wrapped host application

## What it is

**InvokeAI** is a leading open-source creative engine for Stable Diffusion and
related models. It provides an industry-leading web UI (Unified Canvas,
node workflows, boards/gallery), a model manager, and a REST API. It is the
foundation of several commercial products but is itself free and
Apache-2.0 licensed.

This repo (`invokeai-mcp`) bridges AI coding agents and the fleet webapp to a
locally running InvokeAI instance over its REST API.

## Official links

| Resource | URL |
|----------|-----|
| GitHub | https://github.com/invoke-ai/InvokeAI (27.8k stars) |
| Launcher (install) | https://github.com/invoke-ai/launcher/releases/latest |
| Documentation | https://invoke.ai |
| FAQ / troubleshooting | https://invoke.ai/troubleshooting/faq/ |
| Discord | https://discord.gg/ZmtBAhwWhy |
| Weblate (translations) | https://hosted.weblate.org/engage/invokeai/ |

## Community / disambiguation

- "Invoke" / "InvokeAI" are the same project (recently renamed in marketing
  materials). No unrelated product with this name - nothing to confuse here.
- Not to be confused with ComfyUI (node-based, different engine) or
  Automatic1111 (SD WebUI) - all three are separate Stable Diffusion UIs.
  InvokeAI is the canvas-first, product-grade option.

## Model sources

- HuggingFace: https://huggingface.co (official Stability AI models:
  `stabilityai/stable-diffusion-xl-base-1.0`)
- Civitai: https://civitai.com (community models and LoRAs)

## Installation (summary)

Download the launcher EXE, install, then install the engine and models from
inside the launcher/UI. Full steps: [docs/ONBOARDING.md](docs/ONBOARDING.md).
