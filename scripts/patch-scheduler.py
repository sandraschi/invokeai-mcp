"""Webapp scheduler default -> dpmpp_2m_sde + changelog note."""
import pathlib

p = pathlib.Path("webapp/src/pages/GeneratePage.tsx")
c = p.read_text(encoding="utf-8")
old = 'const [scheduler, setScheduler] = useState("euler");'
new = 'const [scheduler, setScheduler] = useState("dpmpp_2m_sde");'
print("scheduler default occurrences:", c.count(old))
c = c.replace(old, new)
p.write_text(c, encoding="utf-8")

ch = pathlib.Path("CHANGELOG.md")
cc = ch.read_text(encoding="utf-8")
cc = cc.replace(
    "the muddy/oversaturated SDXL failure mode), default steps 35",
    "the muddy/oversaturated SDXL failure mode), default steps 35, scheduler\n  dpmpp_2m_sde; Juggernaut XL v9 installed as the structural-quality SDXL\n  checkpoint (SDXL base 1.0 is a 2023 model - malformed geometry is model-level)",
)
ch.write_text(cc, encoding="utf-8")
print("done")
