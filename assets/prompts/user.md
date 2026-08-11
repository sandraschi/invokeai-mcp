# InvokeAI MCP - User Guide

Welcome. This guide teaches you, in plain language, how to get the most out
of the InvokeAI MCP server: what to do the first time you open it, how to
create your first image, how to transform images you already have, how to
repair parts of an image, how to upscale, how to manage the models on your
machine, how to keep your gallery organized, and how to handle the common
problems that come up. The examples are written as natural conversations you
might have with the agent, followed by the exact tool calls the agent should
make.

## Part 1 - The first ten minutes

When you first connect this server, everything is gated on one thing: is
InvokeAI running? InvokeAI is a separate program - an image generation
engine - that runs on your own computer. It is installed with its own
launcher, not with this server. If you have not installed it yet, do this
first:

1. Download the InvokeAI launcher from the InvokeAI GitHub releases page.
   The file is called Invoke.Community.Edition.Setup.latest.exe on Windows.
2. Run the installer. It is an Electron app - after installation, the
   launcher window opens.
3. In the launcher, click Install (or Update) to install the engine itself.
   This downloads a few gigabytes and prepares the Python environment
   automatically. You do not need to install Python or CUDA by hand.
4. Start InvokeAI with the launcher. The first start takes a few minutes
   while it initializes. A browser window opens with the InvokeAI web UI,
   normally at http://127.0.0.1:9090.
5. In the web UI, go to the Models tab and install at least one model. The
   best starting points are: stabilityai/stable-diffusion-xl-base-1.0 for
   high quality 1024x1024 images, or runwayml/stable-diffusion-v1-5 for the
   fastest results at 512x512. If you have a big GPU (12 GB VRAM or more),
   black-forest-labs/FLUX.1-dev gives the best quality.

Now ask the agent: "Check the InvokeAI health." The agent calls
invokeai_system with operation health and reports whether the engine is
reachable. If the answer is yes, your bridge is alive. If the answer is no,
check that the launcher is still running, then retry.

The webapp works the same way: open http://127.0.0.1:11155 and the dashboard
shows a red banner with sample content until the engine responds. Complete
the steps above and the sample content disappears, replaced by live data.

## Part 2 - Your first image

The simplest request: "Generate a picture of a lighthouse at dusk." The
agent will:

1. Optionally check health and list models to confirm a model exists.
2. Call invokeai_generate with operation txt2img, prompt "lighthouse at
   dusk", and default settings.
3. Receive a queue item id.
4. Poll invokeai_queue with operation result and wait_seconds set so the
   image finishes.
5. Show you the result.

What you should know about the default settings: the first main model you
installed is the default model. If you installed SDXL, the default size is
1024x1024 with 30 steps and a CFG scale of 5. If you installed SD1.5, the
default is 512x512 with 30 steps and CFG 7.5. These are sensible starting
points. You can change any of them: "make it 1536 wide", "fewer steps for
speed", "use seed 42", "try the dpmpp_2m_sde scheduler".

A good prompt is one or two sentences describing subject, environment,
lighting, style, and quality: "a weathered lighthouse on a rocky coast at
dusk, dramatic clouds, cinematic lighting, highly detailed, 8k". A negative
prompt helps SD1.5 and SDXL: "blurry, low quality, watermark, text". Flux
ignores negative prompts - its architecture has no negative conditioning,
so do not be surprised when they do nothing.

## Part 3 - Understanding the queue

Every generation job goes through the queue, because the engine can only
process one image at a time on your GPU. When you enqueue, the job is
pending; the engine picks it up, loads the model into VRAM if it is not
already loaded, and runs the denoising steps.

- "Is the queue busy?" invokes invokeai_queue with operation status. The
  result shows how many jobs are queued, in progress, completed, failed,
  and canceled.
- "What's running right now?" invokes invokeai_queue with operation list.
  Each item shows its id, status, batch, and destination.
- "Cancel my last job" cancels the newest item by id.
- "Clear the queue" empties pending work.
- "The queue seems stuck" - after a hard failure the engine pauses its
  processor. Run invokeai_queue with operation resume to restart it. This
  is the most common recovery action.

The first job after a model switch is slow because the engine loads the
model into VRAM. Expect 10 to 60 seconds of loading, then fast generation.
Do not mistake model loading for a hang.

## Part 4 - Transforming an image (img2img)

You have an image and you want a different version of it: repaint it in
another style, change the lighting, make it a watercolor, add elements. This
is img2img. The engine needs the image to exist in its gallery - every
image you generate lives there, and you can also upload images through the
InvokeAI web UI.

The conversation: "Take my last image and turn it into a watercolor
painting." The agent should:

1. List gallery images to find the image_name of your last generation (or
   ask which image you mean).
2. Call invokeai_generate with operation img2img, prompt "watercolor
   painting", image_name set, and strength around 0.6.
3. Poll and present the result.

Strength is the dial that matters here. At 0.3 the engine stays close to
the original, changing details only. At 0.75 it reinterprets strongly. At
0.95 it is nearly a fresh image using the original as inspiration. If the
result looks nothing like your image, lower the strength. If it barely
changed, raise it.

## Part 5 - Repairing a region (inpaint)

Inpaint regenerates only a part of an image. You need two images in the
gallery: the source image and a mask image where white marks the area to
regenerate and black marks everything that must stay untouched. Create the
mask in any image editor (a simple black and white PNG) and upload both
through the InvokeAI web UI or the image upload endpoint.

The conversation: "The face in my portrait came out wrong, fix it with this
mask." The agent should:

1. Confirm both image names from the gallery.
2. Call invokeai_generate with operation inpaint, prompt "correct face,
   natural skin, sharp focus", image_name the portrait, mask_image_name the
   mask, strength 0.5 to 0.7.
3. Poll and present the result.

White in the mask means regenerate; black means preserve. The engine only
denoises the masked region, so the rest of the image stays untouched. This
is the closest the API bridge comes to canvas editing. Full region-based
outpainting (extending the image beyond its borders) needs the interactive
canvas in the InvokeAI web UI - the bridge does not expose it, and the
tools will tell you that honestly if you ask.

## Part 6 - Upscaling

"Upscale my last image 4x" runs the RealESRGAN model on the image. The
agent calls invokeai_generate with operation upscale and the image_name.
RealESRGAN is fast and works on any image. The result is a 4x enlargement
with detail enhancement. For the best final quality, upscale after you are
happy with the composition - upscaling does not change the composition, it
only adds resolution and sharpness.

## Part 7 - Installing and managing models

Models are the brains of the engine. Each model family produces different
styles and capabilities. The agent can manage them for you:

- "What models do I have?" - invokeai_models with operation list and
  model_type main shows your checkpoints. The same call with model_type
  lora, vae, controlnet, or spandrel_image_to_image shows the other
  categories.
- "Install SDXL base from HuggingFace" - invokeai_models with operation
  install and source stabilityai/stable-diffusion-xl-base-1.0. The install
  runs in the background; "how is my model install going?" polls operation
  installs.
- "Remove the old model" - invokeai_models with operation delete and the
  model key. Be careful: this deletes the files.
- "Rename my model" - invokeai_models with operation update, the key, and
  config {"name": "New Name"}.

Where do models come from? HuggingFace repo ids work directly
(stabilityai/stable-diffusion-xl-base-1.0, black-forest-labs/FLUX.1-dev,
runwayml/stable-diffusion-v1-5). Civitai model page URLs work too, and so
do local paths on the machine running the engine. Gated repositories need a
login or token: configure INVOKEAI_ACCESS_TOKEN in the environment, or log
into HuggingFace inside the InvokeAI web UI.

Model tips: SD1.5 is small, fast, and forgiving on modest GPUs; its
community LoRA library is huge. SDXL is the quality workhorse at 1024x1024
with strong text rendering. Flux is the current state of the art for
photorealism and text, but it is heavy (12-16 GB VRAM) and slow. For
iterating quickly on ideas, use SD1.5; for final pieces, use SDXL or Flux.

## Part 8 - The gallery and boards

Every generated image lands in the gallery, and everything there is
searchable by the prompt that created it.

- "Show me my recent images" - invokeai_gallery with operation list.
- "Find the image of the lighthouse" - invokeai_gallery with operation
  search and query "lighthouse". The search matches prompt metadata.
- "Download the lighthouse image" - invokeai_gallery with operation
  download and the image_name. The file lands in the download directory and
  the agent reports the local path.
- "Star my favorites" - invokeai_gallery with operation star and the
  image_name; "unstar" reverses it.
- "Delete this image" - invokeai_gallery with operation delete. This
  removes it from the engine's storage.

Boards are folders for images. "Make a board called Concept Art" creates
one; "put these three images on it" assigns them with add_image; "rename it
to Refined" updates; "delete the board" removes it (images stay in the
gallery). Boards make long projects navigable - one board per project, one
per style experiment, one per client.

## Part 9 - Workflows

InvokeAI workflows are saved node graphs. The bridge manages the library:
"list my workflows", "show me the workflow named X" (get returns the full
JSON), "save this workflow" (paste the JSON), "delete workflow X". Running
a stored workflow graph is done through generation enqueue, not through
this library portmanteau. The webapp Workflows page has a JSON editor for
viewing and editing saved graphs.

## Part 10 - Batch generation

One prompt, several images: pass runs to invokeai_generate. "Generate four
variations of a dragon logo" enqueues one batch of four. The result
contains all four queue item ids; polling any of them waits for the batch.
Use this to give the user options: four seeds, pick the winner, upscale it.

## Part 11 - Troubleshooting conversations

"Everything says InvokeAI is offline." The launcher is not running, or the
engine crashed. Start the launcher, wait for the web UI, re-check health.

"The model list is empty." You installed the bridge but no models. Open the
InvokeAI web UI, Models tab, install something. The bridge will then see it
immediately.

"Generation failed with out of memory." The model needs more VRAM than
available, or another model is still loaded. Switch to a smaller family
(SDXL instead of Flux, SD1.5 instead of SDXL), reduce width and height, or
wait for the queue to idle and retry.

"I can't find a model key." Model keys are exact identifiers. Run
invokeai_models with operation list and copy the key verbatim; the name
also works if you match it exactly.

"The install never finishes." Large downloads take minutes; poll installs
for progress. If it is stuck on a gated repo, configure the token or log in
via the engine UI.

"Canceled jobs still show in the queue." They stay listed for audit with
status canceled; clear the queue to tidy up.

"Flux ignored my negative prompt." Expected behavior - Flux has no negative
conditioning. Use SD1.5 or SDXL if negatives matter to you.

## Part 12 - Webapp walkthrough

If you prefer a browser over chat, the webapp on port 11155 covers
everything: the Dashboard gives you the live health pill and KPIs; Generate
has the full parameter form with operation tabs and inline result polling;
Gallery is a searchable grid with hover actions; Models has type tabs and
an install box; Queue shows live counts and item controls; Boards, Inbox,
Tools, Skills, Chat, Settings, Help, and Logs round out the surface. The
Chat page uses a local LLM (Ollama, LM Studio, or vLLM) detected on the
standard ports - pick the provider and model in Settings first. Everything
talks to the same backend and the same engine, so state is shared between
the webapp and the chat.

## Part 13 - Cost and privacy

Everything runs locally on your GPU. There are no subscriptions, no API
keys for generation, no cloud round trips. Model downloads come from
HuggingFace or Civitai and are free unless the repository is gated (then
you log in with your own account). The only cost is electricity. Your
images, prompts, and seeds never leave your machine unless you choose to
share them.

## Part 14 - Glossary

Batch - one enqueue request; a batch with runs N produces N images. CFG
scale - how strongly the image follows the prompt; too high produces
distorted contrast, too low ignores the prompt. Checkpoint - a full model
(sometimes called a main model). Denoise - the iterative refinement loop
that turns noise into an image. Gallery - the searchable store of every
image the engine produced. LoRA - a small fine-tune applied on top of a
checkpoint for style or subject control. Mask - a black and white image
that selects a region for inpaint. Scheduler - the sampling algorithm;
different schedulers trade speed against quality. Seed - the random start
of a generation; same seed and settings reproduce the same image. Strength
- how much an img2img or inpaint transformation changes the source.
Upscale - increase resolution with detail enhancement. VAE - the
encoder/decoder between pixels and latent space; most models bundle one.

## Part 15 - Style workflows in depth

Style transfer is the most common creative loop, and the strength dial is
its heart. Start with a strong reinterpretation and dial back until the
result matches your intent:

Conversation: "I want a film noir version of my city photo."
1. The agent lists gallery images and finds the city photo image_name.
2. It calls invokeai_generate with operation img2img, prompt "film noir
   style, hard shadows, high contrast, 1940s detective movie, rain-slicked
   streets", image_name set, strength 0.65.
3. The first result is presented. If it is too literal, the agent raises
   strength to 0.8 and retries. If it has drifted too far (wrong geometry,
   warped signs), it lowers to 0.45 and retries.

A strong prompt does the heavy lifting; strength only controls how much of
the original survives. For style changes that should preserve composition
exactly (line art to color, day to night), keep strength between 0.4 and
0.6. For reinterpretation that should feel like a new image, 0.7 to 0.85.

You can also chain transformations: generate a base, img2img it into a
style, then upscale the winner. The gallery keeps every intermediate, so
the chain is always resumable.

## Part 16 - Seed exploration

Seeds make generation reproducible and explorable. The conversation: "Same
prompt, but show me four different takes." The agent calls invokeai_generate
with runs 4 and no seed - four random seeds. "Now give me more like the
second one" means: find the seed of the second image from its metadata
(invokeai_gallery operation metadata returns the seed) and regenerate with
that seed and a slightly varied prompt. Metadata recall is one of the
strongest features of the engine - every image remembers exactly how it was
made, and the bridge can read that back.

## Part 17 - The complete creative pipeline

The production flow this server is built for:

1. Ideate: batch txt2img with several prompts and runs, at SD1.5 speeds.
2. Select: search the gallery for the candidate set, star the favorites.
3. Refine: img2img the favorites toward the final direction, one style at
   a time.
4. Repair: inpaint any defects with masks.
5. Finalize: upscale the winner 4x.
6. Organize: create a board for the project, add the final image, export
   via download.

At every step the agent knows the exact image names, so nothing needs
re-uploading. This loop is the same whether you drive it from chat or from
the webapp.

## Part 18 - Model comparison dialogue

"How does SDXL compare to Flux for my logo?" A good agent response: both
are installed (or propose installing Flux). SDXL renders text well at
1024x1024 and is fast; Flux is slower and heavier but best-in-class for
photorealism and typography. The agent then generates the same prompt on
both models with identical seeds and settings, presents the pair, and lets
you pick. Model A/B testing is two enqueue calls and one comparison.

To run the comparison: invokeai_models list to get both keys, then two
invokeai_generate calls with the same prompt and seed but different
model_key values, then present both results. The metadata of each image
records which model produced it, so the comparison is auditable later.

## Part 19 - Working with LoRAs

LoRA models modify the style or subject of a checkpoint. Install one like
any other model: invokeai_models with operation install and a Civitai LoRA
URL or HuggingFace LoRA repo id, then check it appears under model_type
lora. The bridge's generate flow currently applies the default main model;
LoRA composition through the API graph is a planned extension, and until it
ships, apply LoRAs through the InvokeAI web UI where the model manager and
workflow editor support them natively. The bridge will always report what
it can and cannot do - no silent gaps.

## Part 20 - Frequent questions

Why is my first image slow? The model loads into VRAM on first use.
Subsequent jobs are fast until the model is evicted.

Why did my job fail after I switched models? The engine may need to free
VRAM; the failed job left the processor paused. Resume the queue and retry.

Can I run two generations at once? The engine serializes jobs on one GPU;
your jobs queue up and run in order. Batch with runs if you want several at
once - they share the same model load.

Where do downloaded files go? To the INVOKEAI_DOWNLOAD_DIR directory
(default data/downloads under the repo). The agent reports the absolute
path of every download.

Can the bridge generate video? The engine supports Wan video models, and
the client has the video endpoints, but the tools do not expose video
generation yet. Ask the agent for the current tool list to see what is
available.

Is anything uploaded to the cloud? No. Generation, upscaling, and storage
are all local. Model downloads pull from HuggingFace and Civitai; that is
the only network traffic.

What happens if I run the webapp and the chat at the same time? They share
the same backend and the same queue, so jobs and gallery state are
identical in both. Enqueue from chat, watch it progress in the webapp
Queue page, grab the result from the gallery.

How do I start over? Clear the queue, delete unwanted images from the
gallery, and remove models you no longer need. The engine's own storage is
the source of truth; the bridge never holds state of its own beyond the
log ring buffer.

## Part 21 - Error messages decoded

Every failure the bridge returns carries three parts: a short error code,
a human-readable message, and a remediation hint. Learn to read the codes:

connection_error means the engine is unreachable - start the launcher.
http_error means the engine answered with an error status; the message
includes the engine's own text, which is usually precise about what
rejected the request (unknown node type, invalid field, missing model).
no_model means no main model is installed - install one first. not_found
means a model key, image name, or workflow id does not exist - list first,
then retry with an exact identifier. validation means an argument is
missing or out of range - the message names the argument. unsupported_model
means the model's base family has no graph builder - sd-1, sdxl, and flux
are supported. job_failed means the queue item ended failed; the message
usually contains the engine's error text and the remediation often points
at resuming the queue after clearing the cause.

The dialogic block always suggests the concrete next call. When in doubt,
run the remediation - it is the shortest path back to a working state.

## Part 22 - Quick reference cheat sheet

The most useful calls, grouped:

Health and orientation: invokeai_system(operation="health");
invokeai_models(operation="list", model_type="main"); invokeai_help().

Generate: invokeai_generate(operation="txt2img", prompt="...");
invokeai_generate(operation="img2img", prompt="...", image_name="...",
strength=0.6); invokeai_generate(operation="inpaint", prompt="...",
image_name="...", mask_image_name="..."); invokeai_generate(operation=
"upscale", image_name="..."); invokeai_generate(operation="txt2img",
prompt="...", runs=4, seed=12345).

Queue: invokeai_queue(operation="status"); invokeai_queue(operation="list",
limit=10); invokeai_queue(operation="result", item_id=123,
wait_seconds=120, download_image=true); invokeai_queue(operation="cancel",
item_id=123); invokeai_queue(operation="cancel_batch",
batch_ids=["..."]); invokeai_queue(operation="clear");
invokeai_queue(operation="resume"); invokeai_queue(operation="pause").

Models: invokeai_models(operation="install", source=
"stabilityai/stable-diffusion-xl-base-1.0", config={"name":"SDXL Base"});
invokeai_models(operation="installs"); invokeai_models(operation="delete",
key="..."); invokeai_models(operation="update", key="...",
config={"name":"New Name"}); invokeai_models(operation="stats").

Gallery and boards: invokeai_gallery(operation="list", limit=20);
invokeai_gallery(operation="search", query="lighthouse");
invokeai_gallery(operation="metadata", image_name="...");
invokeai_gallery(operation="download", image_name="...");
invokeai_gallery(operation="star", image_name="...");
invokeai_boards(operation="create", board_name="Concept Art");
invokeai_boards(operation="add_image", board_id="...",
image_names=["a.png","b.png"]).

Workflows: invokeai_workflows(operation="list");
invokeai_workflows(operation="get", workflow_id="...");
invokeai_workflows(operation="save", workflow_json="...");
invokeai_workflows(operation="delete", workflow_id="...").

Cards and system: show_invokeai_dashboard_card();
show_invokeai_queue_card(); show_invokeai_models_card();
show_invokeai_gallery_card(); invokeai_system(operation="version");
invokeai_system(operation="config"); invokeai_shutdown().

Keep this sheet handy. Every command in it works against a healthy local
engine, and the parameter reference in the system prompt gives the full
contract for each argument.

## Part 23 - Example dialogues for the agent

Dialogue one - the user says: "Make me a poster background, dark space
nebula, then I will add text in Photoshop." Agent plan: check health, list
main models, pick the best family (SDXL for quality at 1024x1536
portrait), enqueue txt2img with runs 3, poll, present three candidates,
offer to upscale the chosen one, and on request download it to disk.

Dialogue two - the user says: "My product photo has a bad reflection,
there is a mask in my gallery called fix.png." Agent plan: confirm the
product image name and the mask name via gallery list, enqueue inpaint
with prompt "remove reflection, clean glass surface", strength 0.6, poll,
present the repaired image, and compare side by side with the original via
their URLs.

Dialogue three - the user says: "Install DreamShaper and make an anime
version of my cat photo." Agent plan: install from the Civitai source the
user provides (or suggest the HuggingFace mirror), poll installs until the
model is ready, then img2img the cat photo with strength 0.55 and prompt
describing the anime style, using the newly installed model as model_key.

Dialogue four - the user says: "Everything is broken." Agent plan: run
health, then queue status, then models list. Report exactly what is
reachable and what is not, give the recovery steps in order (start engine,
resume queue, install model), and only then retry the original request.

Dialogue five - the user says: "Which of these two styles do you like for
the logo, and can you give me a clean version of the winner?" Agent plan:
run the two style generations (or reuse existing gallery images by name),
present both, let the user choose, then upscale and download the winner,
and optionally star it and file it into a logo board.

## Part 24 - Making the most of the webapp

The webapp is not just a mirror of the tools - a few things are faster in
the browser. The Generate page keeps your settings sticky while you tweak
prompts, which is the fastest way to iterate on a concept. The Gallery
lightbox shows the full-resolution image and its metadata in one click.
The Queue page auto-refreshes every five seconds, so you can watch a batch
progress while you think about the next prompt. The Logs page is where the
backend tells you what it is doing - if a tool call misbehaves, the log
entry usually explains why. The Chat page is the place for open-ended
creative direction: describe what you want, and the local LLM will turn it
into prompts and settings you can copy to Generate, or the agent can run
the generation directly. Remember that the webapp and the chat agent share
one engine and one queue, so nothing is lost switching between them.

## Part 25 - A final word on creative iteration

The best results come from iterating, and iteration is cheap here. Do not
chase the perfect prompt on the first try - generate three or four
variations, pick the direction, refine with img2img, repair with inpaint,
and finalize with upscale. Every step is one or two tool calls, and every
intermediate is preserved in the gallery for comparison. The engine is
local, the GPU is yours, and the only limit is how many variations you
want to look at. Enjoy the loop, and let the agent handle the plumbing.



