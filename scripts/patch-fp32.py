"""Fix black SDXL output: fp32 VAE decode on l2i nodes."""
import pathlib

p = pathlib.Path("src/invokeai_mcp/graphs.py")
c = p.read_text(encoding="utf-8")
old = 'l2i = add({"id": _uuid(), "type": "l2i", "data": {}})'
new = 'l2i = add({"id": _uuid(), "type": "l2i", "data": {"fp32": True}})'
print("occurrences:", c.count(old))
c = c.replace(old, new)
p.write_text(c, encoding="utf-8")
print("done")
