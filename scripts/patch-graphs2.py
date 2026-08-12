"""Patch graphs.py: wire loader.vae directly to l2i/i2l/mask nodes (v6 requires vae_model value on vae_loader)."""
import pathlib

p = pathlib.Path("src/invokeai_mcp/graphs.py")
c = p.read_text(encoding="utf-8")

# sd1 builder
c = c.replace(
    '    l2i = add({"id": _uuid(), "type": "l2i", "data": {}})\n'
    '    vae_loader = add({"id": _uuid(), "type": "vae_loader", "data": {}})\n',
    '    l2i = add({"id": _uuid(), "type": "l2i", "data": {}})\n',
)
c = c.replace(
    '    edge(noise, "noise", denoise, "noise")\n'
    '    edge(vae_loader, "vae", l2i, "vae")\n',
    '    edge(noise, "noise", denoise, "noise")\n'
    '    edge(loader, "vae", l2i, "vae")\n',
)
c = c.replace(
    '        edge(img_id, "image", i2l, "image")\n'
    '        edge(vae_loader, "vae", i2l, "vae")\n',
    '        edge(img_id, "image", i2l, "image")\n'
    '        edge(loader, "vae", i2l, "vae")\n',
)
c = c.replace(
    '            edge(vae_loader, "vae", mask_denoise, "vae")\n',
    '            edge(loader, "vae", mask_denoise, "vae")\n',
)

# sdxl builder
c = c.replace(
    '    l2i = add({"id": _uuid(), "type": "l2i", "data": {}})\n'
    '    vae_loader = add({"id": _uuid(), "type": "vae_loader", "data": {}})\n'
    '\n'
    '    edge(loader, "unet", denoise, "unet")\n'
    '    edge(loader, "clip", pos_cond, "clip")',
    '    l2i = add({"id": _uuid(), "type": "l2i", "data": {}})\n'
    '\n'
    '    edge(loader, "unet", denoise, "unet")\n'
    '    edge(loader, "clip", pos_cond, "clip")',
)
c = c.replace(
    '    edge(noise, "noise", denoise, "noise")\n'
    '    edge(vae_loader, "vae", l2i, "vae")\n',
    '    edge(noise, "noise", denoise, "noise")\n'
    '    edge(loader, "vae", l2i, "vae")\n',
)
c = c.replace(
    '        edge(img_id, "image", i2l, "image")\n'
    '        edge(vae_loader, "vae", i2l, "vae")\n',
    '        edge(img_id, "image", i2l, "image")\n'
    '        edge(loader, "vae", i2l, "vae")\n',
)
c = c.replace(
    '            edge(vae_loader, "vae", mask_denoise, "vae")\n',
    '            edge(loader, "vae", mask_denoise, "vae")\n',
)

p.write_text(c, encoding="utf-8")
print("vae_loader nodes remaining:", c.count('"vae_loader"'))
print("loader->vae edges:", c.count('edge(loader, "vae"'))
