"""Add core_metadata node (embedded PNG metadata) to sd1/sdxl/flux builders."""
import pathlib

p = pathlib.Path("src/invokeai_mcp/graphs.py")
c = p.read_text(encoding="utf-8")

helper = '''

def _attach_metadata(
    edges: list[dict[str, Any]],
    add,
    edge,
    *,
    l2i: str,
    seed_node: str | None,
    pos_string: str | None,
    neg_string: str | None,
    model: dict[str, Any],
    generation_mode: str,
    width: int,
    height: int,
    steps: int,
    cfg_scale: float,
    scheduler: str,
    cfg_rescale_multiplier: float | None = None,
    strength: float | None = None,
    init_image: str | None = None,
    seamless_x: bool = False,
    seamless_y: bool = False,
) -> None:
    """Attach a core_metadata node so generated PNGs embed prompt + parameters."""
    data: dict[str, Any] = {
        "generation_mode": generation_mode,
        "width": width,
        "height": height,
        "steps": steps,
        "cfg_scale": cfg_scale,
        "scheduler": scheduler,
        "model": _model_field(model),
        "rand_device": "cuda",
        "seamless_x": seamless_x,
        "seamless_y": seamless_y,
    }
    if cfg_rescale_multiplier is not None:
        data["cfg_rescale_multiplier"] = cfg_rescale_multiplier
    if strength is not None:
        data["strength"] = strength
    if init_image is not None:
        data["init_image"] = init_image
    meta = add({"id": _uuid(), "type": "core_metadata", "data": data})
    if seed_node is not None:
        edge(seed_node, "value", meta, "seed")
    if pos_string is not None:
        edge(pos_string, "value", meta, "positive_prompt")
    if neg_string is not None:
        edge(neg_string, "value", meta, "negative_prompt")
    edge(meta, "metadata", l2i, "metadata")
'''

anchor = "def _attach_modules("
assert anchor in c
c = c.replace(anchor, helper.strip() + "\n\n\n" + anchor, 1)

# sd1 first (file order), sdxl second - identical tails, replace sequentially
old_tail = """        ip_model=ip_model,
        ip_weight=ip_weight,
    )

    return {"id": _uuid(), "nodes": nodes, "edges": edges}"""
assert c.count(old_tail) == 2, f"tail count: {c.count(old_tail)}"
c = c.replace(
    old_tail,
    """        ip_model=ip_model,
        ip_weight=ip_weight,
    )
    _attach_metadata(
        edges,
        add,
        edge,
        l2i=l2i,
        seed_node=seed_node,
        pos_string=pos_string,
        neg_string=neg_string,
        model=model,
        generation_mode="txt2img" if image_name is None else ("img2img" if mask_image_name is None else "inpaint"),
        width=width,
        height=height,
        steps=steps,
        cfg_scale=cfg_scale,
        scheduler=scheduler,
        strength=strength,
        init_image=image_name,
        seamless_x=seamless_x,
        seamless_y=seamless_y,
    )

    return {"id": _uuid(), "nodes": nodes, "edges": edges}""",
    1,
)
c = c.replace(
    old_tail,
    """        ip_model=ip_model,
        ip_weight=ip_weight,
    )
    _attach_metadata(
        edges,
        add,
        edge,
        l2i=l2i,
        seed_node=seed_node,
        pos_string=pos_string,
        neg_string=neg_string,
        model=model,
        generation_mode="sdxl_txt2img" if image_name is None else ("sdxl_img2img" if mask_image_name is None else "sdxl_inpaint"),
        width=width,
        height=height,
        steps=steps,
        cfg_scale=cfg_scale,
        scheduler=scheduler,
        cfg_rescale_multiplier=cfg_rescale_multiplier,
        strength=strength,
        init_image=image_name,
        seamless_x=seamless_x,
        seamless_y=seamless_y,
    )

    return {"id": _uuid(), "nodes": nodes, "edges": edges}""",
    1,
)

# flux: insert before its return
old_flux = "    edge(denoise, \"latents\", l2i, \"latents\")\n\n    return {\"id\": _uuid(), \"nodes\": nodes, \"edges\": edges}"
assert c.count(old_flux) == 1, f"flux anchor: {c.count(old_flux)}"
new_flux = """    edge(denoise, "latents", l2i, "latents")
    _attach_metadata(
        edges,
        add,
        edge,
        l2i=l2i,
        seed_node=seed_node,
        pos_string=pos_string,
        neg_string=None,
        model=model,
        generation_mode="flux_txt2img" if image_name is None else "flux_img2img",
        width=width,
        height=height,
        steps=steps,
        cfg_scale=cfg_scale,
        scheduler=scheduler,
        strength=strength,
        init_image=image_name,
    )

    return {"id": _uuid(), "nodes": nodes, "edges": edges}"""
c = c.replace(old_flux, new_flux)

p.write_text(c, encoding="utf-8")
print("metadata nodes attached")
