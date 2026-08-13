"""Model-aware generation defaults: flux -> 4 steps / cfg 1.0."""
import pathlib

p = pathlib.Path("webapp/src/pages/GeneratePage.tsx")
c = p.read_text(encoding="utf-8")

old = """              <div>
                <label className={labelCls}>Model</label>
                <select value={modelKey} onChange={(e) => setModelKey(e.target.value)} className={inputCls} data-testid="model-select">"""
new = """              <div>
                <label className={labelCls}>Model</label>
                <select
                  value={modelKey}
                  onChange={(e) => {
                    const key = e.target.value;
                    setModelKey(key);
                    const m = models.find((x) => x.key === key);
                    if (m?.base === "flux") {
                      setSteps(4);
                      setCfg(1);
                      setScheduler("euler");
                    } else if (m?.base === "sdxl") {
                      setSteps(35);
                      setCfg(5);
                    }
                  }}
                  className={inputCls}
                  data-testid="model-select"
                >"""
print("model select occurrences:", c.count(old))
assert c.count(old) == 1
c = c.replace(old, new)
p.write_text(c, encoding="utf-8")

ch = pathlib.Path("CHANGELOG.md")
cc = ch.read_text(encoding="utf-8")
cc = cc.replace(
    "checkpoint (SDXL base 1.0 is a 2023 model - malformed geometry is model-level)",
    "checkpoint (SDXL base 1.0 is a 2023 model - malformed geometry is model-level);\n  FLUX.1 Schnell as the default model (4-step, Apache-2.0, structural quality),\n  webapp auto-applies 4 steps / cfg 1.0 when a flux model is selected",
)
ch.write_text(cc, encoding="utf-8")
print("done")
