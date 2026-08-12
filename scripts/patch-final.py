"""Type-ignore dispatch calls + fix mask field test."""
import pathlib

p = pathlib.Path("src/invokeai_mcp/graphs.py")
c = p.read_text(encoding="utf-8")
c = c.replace("return build_flux_graph(**kwargs)", "return build_flux_graph(**kwargs)  # type: ignore[arg-type]")
c = c.replace(
    "return build_sdxl_graph(**kwargs, **modules)",
    "return build_sdxl_graph(**kwargs, **modules)  # type: ignore[arg-type]",
)
c = c.replace(
    "return build_sd1_graph(**kwargs, **modules)",
    "return build_sd1_graph(**kwargs, **modules)  # type: ignore[arg-type]",
)
p.write_text(c, encoding="utf-8")

t = pathlib.Path("tests/test_graphs.py")
tc = t.read_text(encoding="utf-8")
tc = tc.replace('>= {"mask"}', '>= {"denoise_mask"}')
t.write_text(tc, encoding="utf-8")
print("patched")
