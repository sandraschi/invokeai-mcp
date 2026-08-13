"""Quality fixes: GPU noise (use_cpu=False) + SDXL cfg_rescale 0.7."""
import pathlib

p = pathlib.Path("src/invokeai_mcp/graphs.py")
c = p.read_text(encoding="utf-8")

# noise nodes: explicit GPU noise (v6 defaults to CPU RNG)
old_noise = '"data": {"width": width, "height": height, "use_seed": True}'
new_noise = '"data": {"width": width, "height": height, "use_seed": True, "use_cpu": False}'
print("noise occurrences:", c.count(old_noise))
c = c.replace(old_noise, new_noise)

# sdxl: cfg_rescale_multiplier default 0.7 (frontend default - prevents muddy SDXL)
old_sdxl = '"cfg_scale": cfg_scale,\n                "cfg_rescale_multiplier": cfg_rescale_multiplier,'
new_sdxl = '"cfg_scale": cfg_scale,\n                "cfg_rescale_multiplier": cfg_rescale_multiplier if cfg_rescale_multiplier is not None else 0.7,'
print("sdxl rescale anchor:", c.count(old_sdxl))
c = c.replace(old_sdxl, new_sdxl)

# sdxl signature default for cfg_rescale_multiplier
old_sig = "    cfg_rescale_multiplier: float = 0.0,"
new_sig = "    cfg_rescale_multiplier: float | None = None,"
print("sig anchor:", c.count(old_sig))
c = c.replace(old_sig, new_sig)

p.write_text(c, encoding="utf-8")
print("quality patches applied")
