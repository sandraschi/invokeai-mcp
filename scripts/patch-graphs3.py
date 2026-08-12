"""Add module support (seamless/controlnet/ip_adapter) to sd1/sdxl graph builders."""
import pathlib

p = pathlib.Path("src/invokeai_mcp/graphs.py")
c = p.read_text(encoding="utf-8")

# 1. Add the shared module-attach helper after _model_field
helper = '''

def _attach_modules(
    edges: list[dict[str, Any]],
    add,
    edge,
    *,
    loader: str,
    denoise: str,
    l2i: str,
    seamless_x: bool = False,
    seamless_y: bool = False,
    control_image_name: str | None = None,
    control_model: dict[str, Any] | None = None,
    control_weight: float = 0.8,
    canny_low: int = 100,
    canny_high: int = 200,
    ip_image_name: str | None = None,
    ip_model: dict[str, Any] | None = None,
    ip_weight: float = 0.7,
) -> None:
    """Attach optional generation modules to a base sd1/sdxl graph.

    - seamless: reroutes loader.unet/vae through the seamless node (tiling).
    - controlnet: canny edge detection -> controlnet node -> denoise.control.
    - ip_adapter: reference image -> ip_adapter node -> denoise.ip_adapter.
    """
    if seamless_x or seamless_y:
        seamless = add(
            {
                "id": _uuid(),
                "type": "seamless",
                "data": {"seamless_x": seamless_x, "seamless_y": seamless_y},
            }
        )
        # reroute the unet/vae chain through the seamless node
        edges[:] = [
            e
            for e in edges
            if not (
                e["source"]["node_id"] == loader
                and e["source"]["field"] in ("unet", "vae")
            )
        ]
        edge(loader, "unet", seamless, "unet")
        edge(loader, "vae", seamless, "vae")
        edge(seamless, "unet", denoise, "unet")
        edge(seamless, "vae", l2i, "vae")
        if control_image_name is None:
            # img2img i2l vae edge also reroutes through seamless
            for e in edges:
                if e["destination"]["field"] == "vae" and e["destination"]["node_id"] != l2i:
                    e["source"] = {"node_id": seamless, "field": "vae"}

    if control_image_name and control_model:
        ctrl_img = add(_image_node(control_image_name))
        canny = add(
            {
                "id": _uuid(),
                "type": "canny_edge_detection",
                "data": {"low_threshold": canny_low, "high_threshold": canny_high},
            }
        )
        controlnet = add(
            {
                "id": _uuid(),
                "type": "controlnet",
                "data": {
                    "control_model": _model_field(control_model),
                    "control_weight": control_weight,
                    "control_mode": "balanced",
                    "resize_mode": "resize",
                    "begin_step_percent": 0.0,
                    "end_step_percent": 1.0,
                },
            }
        )
        edge(ctrl_img, "image", canny, "image")
        edge(canny, "image", controlnet, "image")
        edge(controlnet, "control", denoise, "control")

    if ip_image_name and ip_model:
        ip_img = add(_image_node(ip_image_name))
        ip_adapter = add(
            {
                "id": _uuid(),
                "type": "ip_adapter",
                "data": {
                    "ip_adapter_model": _model_field(ip_model),
                    "weight": ip_weight,
                    "method": "full",
                    "begin_step_percent": 0.0,
                    "end_step_percent": 1.0,
                },
            }
        )
        edge(ip_img, "image", ip_adapter, "image")
        edge(ip_adapter, "ip_adapter", denoise, "ip_adapter")
'''

anchor = "def _image_node(image_name: str) -> dict[str, Any]:"
assert anchor in c
c = c.replace(anchor, helper.strip() + "\n\n\n" + anchor, 1)

p.write_text(c, encoding="utf-8")
print("helper added")
