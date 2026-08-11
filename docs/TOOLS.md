# InvokeAI MCP - Tool Reference

## invokeai_generate

Generate images through InvokeAI. One portmanteau, four operations.

| Operation | Requires | Notes |
|-----------|----------|-------|
| `txt2img` | prompt | Text to fresh image |
| `img2img` | prompt + image_name | Transform existing image, `strength` controls intensity |
| `inpaint` | prompt + image_name + mask_image_name | Regenerate masked region (white = regenerate) |
| `upscale` | image_name | RealESRGAN 4x upscale |

Common parameters: `model_key`, `negative_prompt`, `width`, `height`,
`steps`, `cfg_scale`, `scheduler` (euler, euler_a, dpmpp_2m, dpmpp_2m_sde,
dpmpp_3m_sde, dpmpp_sde, ddim, unipc), `seed`, `strength`, `runs`.

Model base auto-selects the graph family: `sd-1`, `sdxl`, `flux`. Unsupported
bases return an explicit `unsupported_model` error.

```python
invokeai_generate(operation="txt2img", prompt="neon cyberpunk city at night, rain")
invokeai_generate(operation="img2img", prompt="make it a watercolor", image_name="abc123.png", strength=0.6)
invokeai_generate(operation="upscale", image_name="abc123.png")
```

Returns: `queue_item_id`, `batch_id` - poll with invokeai_queue.

## invokeai_queue

| Operation | Args | Notes |
|-----------|------|-------|
| `status` | - | queued/in_progress/completed/failed/canceled counts |
| `list` | limit, status_filter | Recent queue items |
| `item_status` | item_id | Single item state |
| `result` | item_id, wait_seconds, download_image | Poll to completion, return output URLs (optionally save locally) |
| `cancel` | item_id | Cancel one item |
| `cancel_batch` | batch_ids | Cancel a batch |
| `clear` | - | Clear queue |
| `resume` / `pause` | - | Processor control |

```python
invokeai_queue(operation="result", item_id=42, wait_seconds=120, download_image=True)
```

## invokeai_models

| Operation | Notes |
|-----------|-------|
| `list` | model_type (main/lora/vae/controlnet/embedding/spandrel_image_to_image), search, limit |
| `get` | key |
| `install` | source (HF repo id, Civitai URL, local path) + optional config {name, type, base} |
| `installs` | async install job progress |
| `update` | key + config |
| `delete` | key |
| `stats` | model manager stats |

```python
invokeai_models(operation="install", source="stabilityai/stable-diffusion-xl-base-1.0", config={"name": "SDXL Base"})
```

## invokeai_gallery

| Operation | Notes |
|-----------|-------|
| `list` | board_id / starred / limit / offset filters |
| `search` | query on prompt metadata |
| `get` | image_name |
| `metadata` | image_name (prompt, seed, settings) |
| `download` | image_name - saves to download dir, returns local path |
| `delete` | image_name |
| `star` / `unstar` | image_name |

## invokeai_boards

`list`, `get`, `create` (board_name), `update`, `delete`, `add_image`
(board_id + image_names), `remove_image`.

## invokeai_workflows

`list`, `get` (workflow_id), `save` (workflow_json - full workflow object),
`delete`.

## Prefab cards (chat UI)

`show_invokeai_dashboard_card`, `show_invokeai_queue_card`,
`show_invokeai_models_card`, `show_invokeai_gallery_card` - rich in-chat
cards for list/status surfaces.

## System

`invokeai_system(operation=health|version|config|stats)`, `invokeai_help(topic)`,
`invokeai_shutdown`.

## Honesty contract

- `outpaint` and region canvas editing are NOT exposed - they need the
  InvokeAI canvas UI. No stub exists.
- All failures return structured `{success: false, error, message, dialogic}`
  with remediation hints. No fake success paths.
