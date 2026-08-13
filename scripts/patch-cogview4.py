"""Add CogView4 graph builder + dispatch (LLM-based transformer family)."""
import pathlib

p = pathlib.Path("src/invokeai_mcp/graphs.py")
c = p.read_text(encoding="utf-8")

builder = '''

# ---------------------------------------------------------------------------
# CogView4 family (LLM-based: GLM text encoder, transformer denoise)
# ---------------------------------------------------------------------------
def build_cogview4_graph(
    *,
    model: dict[str, Any],
    positive_prompt: str,
    negative_prompt: str = "",
    width: int = 1024,
    height: int = 1024,
    steps: int = 40,
    cfg_scale: float = 1.0,
    scheduler: str = "euler",
    seed: int | None = None,
    strength: float | None = None,
    image_name: str | None = None,
) -> dict[str, Any]:
    """CogView4 txt2img/img2img graph (verified vs engine 6.13.7 nodes)."""
    nodes: dict[str, Any] = {}
    edges: list[dict[str, Any]] = []

    def add(node: dict[str, Any]) -> str:
        nid = node["id"]
        flat = {"id": nid, "type": node["type"]}
        flat.update(node.get("data") or {})
        nodes[nid] = flat
        return nid

    def edge(src: str, src_field: str, dst: str, dst_field: str) -> None:
        edges.append(
            {
                "source": {"node_id": src, "field": src_field},
                "destination": {"node_id": dst, "field": dst_field},
            }
        )

    loader = add({"id": _uuid(), "type": "cogview4_model_loader", "data": {"model": _model_field(model)}})
    pos_string = add({"id": _uuid(), "type": "string", "data": {"value": positive_prompt}})
    pos_cond = add({"id": _uuid(), "type": "cogview4_text_encoder", "data": {}})
    neg_string = add({"id": _uuid(), "type": "string", "data": {"value": negative_prompt}})
    neg_cond = add({"id": _uuid(), "type": "cogview4_text_encoder", "data": {}})
    seed_node = add({"id": _uuid(), "type": "integer", "data": {"value": seed or 0}})
    denoise = add(
        {
            "id": _uuid(),
            "type": "cogview4_denoise",
            "data": {
                "steps": steps,
                "cfg_scale": cfg_scale,
                "denoising_start": (1.0 - (strength or 0.75)) if image_name else 0.0,
                "denoising_end": 1.0,
            },
        }
    )
    l2i = add({"id": _uuid(), "type": "cogview4_l2i", "data": {}})

    edge(loader, "transformer", denoise, "transformer")
    edge(loader, "glm_encoder", pos_cond, "glm_encoder")
    edge(loader, "glm_encoder", neg_cond, "glm_encoder")
    edge(loader, "vae", l2i, "vae")
    edge(pos_string, "value", pos_cond, "prompt")
    edge(neg_string, "value", neg_cond, "prompt")
    edge(pos_cond, "conditioning", denoise, "positive_conditioning")
    edge(neg_cond, "conditioning", denoise, "negative_conditioning")
    edge(seed_node, "value", denoise, "seed")
    edge(denoise, "latents", l2i, "latents")

    if image_name is not None:
        img_id = add(_image_node(image_name))
        i2l = add({"id": _uuid(), "type": "cogview4_i2l", "data": {}})
        edge(img_id, "image", i2l, "image")
        edge(loader, "vae", i2l, "vae")
        edge(i2l, "latents", denoise, "latents")

    _attach_metadata(
        edges,
        add,
        edge,
        l2i=l2i,
        seed_node=seed_node,
        pos_string=pos_string,
        neg_string=neg_string,
        model=model,
        generation_mode="cogview4_txt2img" if image_name is None else "cogview4_img2img",
        width=width,
        height=height,
        steps=steps,
        cfg_scale=cfg_scale,
        scheduler=scheduler,
        strength=strength,
        init_image=image_name,
    )

    return {"id": _uuid(), "nodes": nodes, "edges": edges}
'''

anchor = "# ---------------------------------------------------------------------------\n# Upscale (RealESRGAN)"
assert anchor in c
c = c.replace(anchor, builder.strip() + "\n\n\n" + anchor, 1)

# dispatch
old = '    if base.startswith("flux"):\n        return build_flux_graph(**kwargs)  # type: ignore[arg-type]'
new = '    if base.startswith("flux"):\n        return build_flux_graph(**kwargs)  # type: ignore[arg-type]\n    if base == "cogview4":\n        return build_cogview4_graph(**kwargs)  # type: ignore[arg-type]'
assert old in c
c = c.replace(old, new)

p.write_text(c, encoding="utf-8")
print("cogview4 builder added")
