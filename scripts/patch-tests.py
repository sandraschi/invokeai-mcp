"""Fix tests for flat-node graph access + FakeClient.get_model."""
import pathlib

p = pathlib.Path("tests/test_graphs.py")
c = p.read_text(encoding="utf-8")
c = c.replace('denoise["data"]["denoising_start"]', 'denoise["denoising_start"]')
c = c.replace('denoise["data"]["denoising_end"]', 'denoise["denoising_end"]')
c = c.replace('esrgan["data"]["model_name"]', 'esrgan["model_name"]')
p.write_text(c, encoding="utf-8")

p2 = pathlib.Path("tests/test_tools.py")
c2 = p2.read_text(encoding="utf-8")
old = '    async def enqueue_batch(self, graph, runs=1, destination="mcp"):'
new = (
    '    async def get_model(self, key):\n'
    '        return {"key": key, "name": "SDXL", "base": "sdxl", "type": "main", "hash": "h"}\n'
    "\n"
    '    async def enqueue_batch(self, graph, runs=1, destination="mcp"):'
)
assert old in c2
c2 = c2.replace(old, new)
p2.write_text(c2, encoding="utf-8")
print("patched")
