"""Fix seamless img2img vae reroute (must not mutate the loader->seamless edge)."""
import pathlib

p = pathlib.Path("src/invokeai_mcp/graphs.py")
c = p.read_text(encoding="utf-8")

old = """        if control_image_name is None:
            # img2img i2l vae edge also reroutes through seamless
            for e in edges:
                if e["destination"]["field"] == "vae" and e["destination"]["node_id"] != l2i:
                    e["source"] = {"node_id": seamless, "field": "vae"}"""
new = """        if control_image_name is None:
            # img2img i2l vae edge also reroutes through seamless (never self-loop)
            for e in edges:
                if (
                    e["destination"]["field"] == "vae"
                    and e["destination"]["node_id"] not in (l2i, seamless)
                ):
                    e["source"] = {"node_id": seamless, "field": "vae"}"""
assert old in c
c = c.replace(old, new)
p.write_text(c, encoding="utf-8")
print("seamless reroute fixed")
