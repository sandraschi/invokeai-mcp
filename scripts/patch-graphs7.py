"""Fix denoise mask input field name (denoise_mask in v6)."""
import pathlib

p = pathlib.Path("src/invokeai_mcp/graphs.py")
c = p.read_text(encoding="utf-8")
old = 'edge(mask_denoise, "denoise_mask", denoise, "mask")'
new = 'edge(mask_denoise, "denoise_mask", denoise, "denoise_mask")'
print("occurrences:", c.count(old))
c = c.replace(old, new)
p.write_text(c, encoding="utf-8")
print("done")
