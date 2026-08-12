"""Add module params + _attach_modules call to build_sd1_graph / build_sdxl_graph."""
import pathlib

p = pathlib.Path("src/invokeai_mcp/graphs.py")
c = p.read_text(encoding="utf-8")

MODULE_PARAMS = """    seamless_x: bool = False,
    seamless_y: bool = False,
    control_image_name: str | None = None,
    control_model: dict[str, Any] | None = None,
    control_weight: float = 0.8,
    canny_low: int = 100,
    canny_high: int = 200,
    ip_image_name: str | None = None,
    ip_model: dict[str, Any] | None = None,
    ip_weight: float = 0.7,
"""

ATTACH = """    _attach_modules(
        edges,
        add,
        edge,
        loader=loader,
        denoise=denoise,
        l2i=l2i,
        seamless_x=seamless_x,
        seamless_y=seamless_y,
        control_image_name=control_image_name,
        control_model=control_model,
        control_weight=control_weight,
        canny_low=canny_low,
        canny_high=canny_high,
        ip_image_name=ip_image_name,
        ip_model=ip_model,
        ip_weight=ip_weight,
    )

"""

# sd1 + sdxl: same signature tail - insert params into BOTH
old_sig = "    mask_image_name: str | None = None,\n) -> dict[str, Any]:"
assert c.count(old_sig) == 2, f"signature anchor count: {c.count(old_sig)}"
c = c.replace(old_sig, "    mask_image_name: str | None = None,\n" + MODULE_PARAMS + ") -> dict[str, Any]:")

# insert the attach call before sd1/sdxl final returns (flux excluded: split at flux)
flux_anchor = "# ---------------------------------------------------------------------------\n# FLUX family"
assert flux_anchor in c
head, tail = c.split(flux_anchor, 1)
old_ret = "    edge(denoise, \"latents\", l2i, \"latents\")\n\n    return {\"id\": _uuid(), \"nodes\": nodes, \"edges\": edges}"
assert head.count(old_ret) == 2, f"return anchor count in sd1/sdxl: {head.count(old_ret)}"
head = head.replace(old_ret, "    edge(denoise, \"latents\", l2i, \"latents\")\n\n" + ATTACH + "    return {\"id\": _uuid(), \"nodes\": nodes, \"edges\": edges}")
c = head + flux_anchor + tail

p.write_text(c, encoding="utf-8")
print("builders patched")
