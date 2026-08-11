"""Generate assets/prompts/examples.json - 100+ tool-call mappings."""
import json
from pathlib import Path

examples = []


def add(name, desc, prompt, tool, args):
    examples.append(
        {"name": name, "description": desc, "prompt": prompt, "tool": tool, "arguments": args}
    )


# invokeai_generate: txt2img
for i, (topic, p) in enumerate(
    [
        ("lighthouse", "Generate a picture of a lighthouse at dusk"),
        ("cyberpunk", "Create a neon cyberpunk city at night with rain"),
        ("watercolor", "Paint a watercolor scene of a mountain lake"),
        ("steampunk", "Generate a steampunk robot portrait with dramatic lighting"),
        ("space", "Make a dark space nebula poster background"),
        ("dragon-logo", "Generate four variations of a dragon logo"),
        ("portrait", "Create a cinematic portrait of an old fisherman"),
        ("architecture", "Render a brutalist concrete building at sunrise"),
        ("product", "Generate a product shot of a ceramic teapot on slate"),
        ("book-cover", "Design a fantasy book cover with a glowing forest"),
        ("isometric", "Make an isometric illustration of a cozy coffee shop"),
        ("pixel", "Generate a pixel art village at night"),
        ("car", "Render a 1960s sports car in a desert"),
        ("food", "Create an editorial food photo of ramen with steam"),
        ("garden", "Paint a japanese garden in autumn, koi pond"),
    ]
):
    add(f"txt2img-{i}", f"txt2img: {topic}", p, "invokeai_generate", {"operation": "txt2img", "prompt": p})

add("txt2img-settings", "txt2img with explicit size/steps/cfg",
    "Generate a wide banner of a space station, 1536x512, 40 steps",
    "invokeai_generate", {"operation": "txt2img", "prompt": "space station orbital sunrise",
                          "width": 1536, "height": 512, "steps": 40, "cfg_scale": 6.0})
add("txt2img-seed", "txt2img with fixed seed",
    "Regenerate my dragon image with seed 42",
    "invokeai_generate", {"operation": "txt2img", "prompt": "dragon logo, dark background", "seed": 42})
add("txt2img-runs", "txt2img batch of 4",
    "Give me four different takes of a nebula",
    "invokeai_generate", {"operation": "txt2img", "prompt": "colorful nebula", "runs": 4})
add("txt2img-scheduler", "txt2img with dpmpp scheduler",
    "Render a lighthouse using the dpmpp_2m_sde scheduler",
    "invokeai_generate", {"operation": "txt2img", "prompt": "lighthouse at dusk", "scheduler": "dpmpp_2m_sde"})
add("txt2img-negative", "txt2img with negative prompt",
    "Generate a clean logo without text or watermark",
    "invokeai_generate", {"operation": "txt2img", "prompt": "minimalist gear logo",
                          "negative_prompt": "text, watermark, blurry"})
add("txt2img-model", "txt2img on a specific model",
    "Use my FLUX model to create a photo-real feline portrait",
    "invokeai_generate", {"operation": "txt2img", "prompt": "photorealistic tabby portrait", "model_key": "flux"})

# invokeai_generate: img2img
add("img2img-watercolor", "img2img style transfer",
    "Turn my last image into a watercolor painting",
    "invokeai_generate", {"operation": "img2img", "prompt": "watercolor painting",
                          "image_name": "abc123.png", "strength": 0.6})
add("img2img-noir", "img2img film noir",
    "Make my city photo film noir style",
    "invokeai_generate", {"operation": "img2img", "prompt": "film noir, hard shadows, high contrast",
                          "image_name": "city.png", "strength": 0.65})
add("img2img-anime", "img2img anime version",
    "Make an anime version of my pet photo",
    "invokeai_generate", {"operation": "img2img", "prompt": "anime style, vibrant colors",
                          "image_name": "pet.png", "strength": 0.55})
add("img2img-day-night", "img2img day to night",
    "Convert my street photo to night with neon lights",
    "invokeai_generate", {"operation": "img2img", "prompt": "night scene, neon lights",
                          "image_name": "street.png", "strength": 0.5})
add("img2img-subtle", "img2img subtle change",
    "Slightly enhance the lighting of my portrait",
    "invokeai_generate", {"operation": "img2img", "prompt": "better lighting, natural",
                          "image_name": "portrait.png", "strength": 0.3})

# invokeai_generate: inpaint
add("inpaint-face", "inpaint fix face",
    "Fix the face in my portrait using the mask fix.png",
    "invokeai_generate", {"operation": "inpaint", "prompt": "correct face, natural skin",
                          "image_name": "portrait.png", "mask_image_name": "fix.png", "strength": 0.6})
add("inpaint-reflection", "inpaint remove reflection",
    "Remove the bad reflection from my product photo",
    "invokeai_generate", {"operation": "inpaint", "prompt": "remove reflection, clean glass",
                          "image_name": "product.png", "mask_image_name": "mask.png", "strength": 0.6})
add("inpaint-object", "inpaint remove object",
    "Remove the person from the background of my photo",
    "invokeai_generate", {"operation": "inpaint", "prompt": "empty background",
                          "image_name": "scene.png", "mask_image_name": "person-mask.png", "strength": 0.7})

# invokeai_generate: upscale
add("upscale-4x", "upscale image 4x",
    "Upscale my last image 4x",
    "invokeai_generate", {"operation": "upscale", "image_name": "abc123.png"})
add("upscale-poster", "upscale for print",
    "Upscale the poster background for print",
    "invokeai_generate", {"operation": "upscale", "image_name": "nebula.png"})

# invokeai_queue
add("queue-status", "queue status", "Is the queue busy?", "invokeai_queue", {"operation": "status"})
add("queue-list", "queue recent items", "What is running right now?",
    "invokeai_queue", {"operation": "list", "limit": 10})
add("queue-list-completed", "queue completed filter", "Show my completed jobs",
    "invokeai_queue", {"operation": "list", "status_filter": "completed", "limit": 20})
add("queue-item-status", "queue item status", "What is the status of item 42?",
    "invokeai_queue", {"operation": "item_status", "item_id": 42})
add("queue-result", "queue result with wait", "Wait for my generation and show it",
    "invokeai_queue", {"operation": "result", "item_id": 42, "wait_seconds": 120})
add("queue-result-download", "queue result download",
    "Generate an image and save it to disk",
    "invokeai_queue", {"operation": "result", "item_id": 42, "wait_seconds": 180, "download_image": True})
add("queue-cancel", "queue cancel item", "Cancel my last job",
    "invokeai_queue", {"operation": "cancel", "item_id": 43})
add("queue-cancel-batch", "queue cancel batch", "Cancel the batch I just enqueued",
    "invokeai_queue", {"operation": "cancel_batch", "batch_ids": ["batch-uuid"]})
add("queue-clear", "queue clear", "Clear the queue", "invokeai_queue", {"operation": "clear"})
add("queue-resume", "queue resume", "The queue seems stuck, resume it",
    "invokeai_queue", {"operation": "resume"})
add("queue-pause", "queue pause", "Pause the queue while I think",
    "invokeai_queue", {"operation": "pause"})

# invokeai_models
add("models-list-main", "list main models", "What models do I have installed?",
    "invokeai_models", {"operation": "list", "model_type": "main"})
add("models-list-lora", "list loras", "Show my LoRA models",
    "invokeai_models", {"operation": "list", "model_type": "lora"})
add("models-list-search", "search models", "Find the model with flux in the name",
    "invokeai_models", {"operation": "list", "model_type": "main", "search": "flux"})
add("models-install-sdxl", "install SDXL",
    "Install SDXL base from HuggingFace",
    "invokeai_models", {"operation": "install", "source": "stabilityai/stable-diffusion-xl-base-1.0",
                        "config": {"name": "SDXL Base"}})
add("models-install-flux", "install Flux dev", "Install FLUX.1 dev",
    "invokeai_models", {"operation": "install", "source": "black-forest-labs/FLUX.1-dev"})
add("models-install-sd15", "install SD1.5", "Install the fast SD1.5 model",
    "invokeai_models", {"operation": "install", "source": "runwayml/stable-diffusion-v1-5"})
add("models-install-civitai", "install from civitai",
    "Install this Civitai model: https://civitai.com/models/4384",
    "invokeai_models", {"operation": "install", "source": "https://civitai.com/models/4384"})
add("models-installs", "poll install jobs", "How is my model install going?",
    "invokeai_models", {"operation": "installs"})
add("models-get", "get model by key", "Show me details of model m1",
    "invokeai_models", {"operation": "get", "key": "m1"})
add("models-update", "rename model", "Rename my model to DreamShaper",
    "invokeai_models", {"operation": "update", "key": "m1", "config": {"name": "DreamShaper"}})
add("models-delete", "delete model", "Remove the old SD1.5 model",
    "invokeai_models", {"operation": "delete", "key": "sd15-old"})
add("models-stats", "model stats", "Show model manager stats",
    "invokeai_models", {"operation": "stats"})

# invokeai_gallery
add("gallery-list", "gallery recent", "Show me my recent images",
    "invokeai_gallery", {"operation": "list", "limit": 20})
add("gallery-search", "gallery search", "Find the image of the lighthouse",
    "invokeai_gallery", {"operation": "search", "query": "lighthouse"})
add("gallery-get", "gallery get image", "Get details for image abc123.png",
    "invokeai_gallery", {"operation": "get", "image_name": "abc123.png"})
add("gallery-metadata", "gallery metadata", "What settings made this image?",
    "invokeai_gallery", {"operation": "metadata", "image_name": "abc123.png"})
add("gallery-download", "gallery download", "Download the lighthouse image",
    "invokeai_gallery", {"operation": "download", "image_name": "abc123.png"})
add("gallery-star", "gallery star", "Star my favorite images",
    "invokeai_gallery", {"operation": "star", "image_name": "abc123.png"})
add("gallery-unstar", "gallery unstar", "Unstar this image",
    "invokeai_gallery", {"operation": "unstar", "image_name": "abc123.png"})
add("gallery-delete", "gallery delete", "Delete this image",
    "invokeai_gallery", {"operation": "delete", "image_name": "abc123.png"})
add("gallery-starred", "gallery starred filter", "Show my starred images",
    "invokeai_gallery", {"operation": "list", "starred": True, "limit": 50})
add("gallery-board-filter", "gallery by board", "Show images in the Concept Art board",
    "invokeai_gallery", {"operation": "list", "board_id": "board-uuid", "limit": 30})

# invokeai_boards
add("boards-list", "list boards", "What boards do I have?", "invokeai_boards", {"operation": "list"})
add("boards-create", "create board", "Make a board called Concept Art",
    "invokeai_boards", {"operation": "create", "board_name": "Concept Art"})
add("boards-update", "rename board", "Rename that board to Refined",
    "invokeai_boards", {"operation": "update", "board_id": "board-uuid", "board_name": "Refined"})
add("boards-delete", "delete board", "Delete the old board",
    "invokeai_boards", {"operation": "delete", "board_id": "board-uuid"})
add("boards-add-image", "add image to board",
    "Put these three images on the Concept Art board",
    "invokeai_boards", {"operation": "add_image", "board_id": "board-uuid",
                        "image_names": ["a.png", "b.png", "c.png"]})
add("boards-remove-image", "remove image from board",
    "Take this image off the board",
    "invokeai_boards", {"operation": "remove_image", "board_id": "board-uuid", "image_names": ["a.png"]})

# invokeai_workflows
add("workflows-list", "list workflows", "List my saved workflows",
    "invokeai_workflows", {"operation": "list"})
add("workflows-get", "get workflow", "Show me the workflow named Upscale XL",
    "invokeai_workflows", {"operation": "get", "workflow_id": "wf-uuid"})
add("workflows-save", "save workflow", "Save this workflow JSON",
    "invokeai_workflows", {"operation": "save", "workflow_json": '{"nodes": {}}'})
add("workflows-delete", "delete workflow", "Delete the old workflow",
    "invokeai_workflows", {"operation": "delete", "workflow_id": "wf-uuid"})

# invokeai_system
add("system-health", "health check", "Check the InvokeAI health",
    "invokeai_system", {"operation": "health"})
add("system-version", "version check", "What version of InvokeAI is running?",
    "invokeai_system", {"operation": "version"})
add("system-config", "runtime config", "Show the engine runtime config",
    "invokeai_system", {"operation": "config"})
add("system-stats", "system stats", "Show engine model stats",
    "invokeai_system", {"operation": "stats"})

# cards
add("card-dashboard", "dashboard card", "Show the InvokeAI status card",
    "show_invokeai_dashboard_card", {})
add("card-queue", "queue card", "Show me the queue as a card",
    "show_invokeai_queue_card", {})
add("card-models", "models card", "Show my models as a card",
    "show_invokeai_models_card", {"model_type": "main"})
add("card-gallery", "gallery card", "Show recent images as a card",
    "show_invokeai_gallery_card", {"limit": 6})

# help
add("help-index", "help index", "What can this server do?", "invokeai_help", {})
add("help-tools", "help tools topic", "Explain the tools", "invokeai_help", {"topic": "tools"})
add("help-install", "help install topic", "How do I install models?",
    "invokeai_help", {"topic": "install"})

# multi-step workflow examples
add("workflow-banner", "full banner workflow",
    "Create a wide cyberpunk banner, then upscale it",
    "invokeai_generate", {"operation": "txt2img", "prompt": "cyberpunk city wide banner",
                          "width": 1536, "height": 512})
add("workflow-pick-upscale", "pick and upscale",
    "Pick the best of my four dragons and upscale it",
    "invokeai_gallery", {"operation": "search", "query": "dragon"})
add("workflow-organize", "organize batch",
    "Star the good results and put them on a board",
    "invokeai_boards", {"operation": "add_image", "board_id": "board-uuid",
                        "image_names": ["d1.png", "d2.png"]})
add("workflow-cleanup", "cleanup", "Delete the failed experiment images",
    "invokeai_gallery", {"operation": "delete", "image_name": "exp1.png"})
add("workflow-inspect", "inspect before reuse",
    "What prompt and seed made this image?",
    "invokeai_gallery", {"operation": "metadata", "image_name": "abc123.png"})

# extra txt2img topics
for i, (topic, p) in enumerate(
    [
        ("neon-sign", "Generate a neon sign in a rainy alley"),
        ("vintage-poster", "Create a vintage travel poster of Vienna"),
        ("macro", "Generate a macro photo of a dragonfly on a leaf"),
        ("fantasy-map", "Draw a fantasy world map with parchment texture"),
        ("abstract", "Create an abstract gradient artwork with gold accents"),
        ("character", "Design a sci-fi bounty hunter character sheet"),
        ("lowpoly", "Render a low-poly fox in a forest"),
        ("minimal", "Make a minimal geometric sun poster"),
        ("spaceship", "Generate a detailed spaceship hangar interior"),
        ("texture", "Create a seamless stone wall texture"),
    ]
):
    add(f"txt2img-extra-{i}", f"txt2img extra: {topic}", p, "invokeai_generate",
        {"operation": "txt2img", "prompt": p})

# extra img2img / inpaint / upscale variants
add("img2img-colorize", "img2img colorize sketch",
    "Colorize my pencil sketch",
    "invokeai_generate", {"operation": "img2img", "prompt": "vibrant colors, detailed",
                          "image_name": "sketch.png", "strength": 0.7})
add("img2img-restyle", "img2img restyle logo",
    "Restyle my logo in flat design",
    "invokeai_generate", {"operation": "img2img", "prompt": "flat design, clean shapes",
                          "image_name": "logo.png", "strength": 0.6})
add("inpaint-text", "inpaint fix text",
    "Fix the misspelled text on my sign with mask text.png",
    "invokeai_generate", {"operation": "inpaint", "prompt": "correct text spelling",
                          "image_name": "sign.png", "mask_image_name": "text.png", "strength": 0.5})
add("upscale-thumb", "upscale small image",
    "Upscale the thumbnail for my profile",
    "invokeai_generate", {"operation": "upscale", "image_name": "thumb.png"})

# extra queue / gallery / boards / workflows / system variants
add("queue-list-inprogress", "queue in progress filter",
    "What is the engine working on right now?",
    "invokeai_queue", {"operation": "list", "status_filter": "in_progress", "limit": 10})
add("queue-delete-item", "queue delete item",
    "Remove the stuck item 77 from the queue",
    "invokeai_queue", {"operation": "cancel", "item_id": 77})
add("gallery-board-images", "gallery board images",
    "List images on the client board",
    "invokeai_gallery", {"operation": "list", "board_id": "client-board", "limit": 40})
add("gallery-rename-check", "gallery metadata check",
    "Which scheduler did I use for the nebula image?",
    "invokeai_gallery", {"operation": "metadata", "image_name": "nebula.png"})
add("boards-get", "board detail",
    "Show me the contents info of the Concept Art board",
    "invokeai_boards", {"operation": "get", "board_id": "board-uuid"})
add("workflows-count", "workflow count",
    "How many workflows do I have saved?",
    "invokeai_workflows", {"operation": "list", "limit": 100})
add("system-health-then-generate", "health before generate",
    "Check the engine then generate a test image",
    "invokeai_system", {"operation": "health"})
add("card-models-lora", "lora models card",
    "Show my LoRAs as a card",
    "show_invokeai_models_card", {"model_type": "lora"})
add("help-troubleshooting", "help troubleshooting topic",
    "How do I fix connection errors?",
    "invokeai_help", {"topic": "troubleshooting"})
add("help-api-keys", "help api keys topic",
    "Do I need any API keys?",
    "invokeai_help", {"topic": "api_keys"})

out = Path("assets/prompts/examples.json")
out.write_text(json.dumps(examples, indent=2, ensure_ascii=False), encoding="utf-8")
print("examples written:", len(examples))