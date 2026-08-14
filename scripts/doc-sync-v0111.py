"""Doc sync for v0.1.11 (franchise presets)."""
import pathlib

c = pathlib.Path("CHANGELOG.md").read_text(encoding="utf-8")
c = c.replace(
    "## [0.1.10] - 2026-08-12",
    """## [0.1.11] - 2026-08-12

### Added
- invokeai_franchises tool + 23 fan-style franchise presets (Super Mario,
  Zelda, Pokemon, Minecraft, Ghibli, Shinkai, Disney, Pixar, Tim Burton,
  Simpsons, Marvel, Star Wars, LotR, Harry Potter, D&D, Warhammer 40k,
  MTG, Doom, Portal, Sonic, Hollow Knight, Undertale, Animal Crossing)
  - fan-style descriptors for personal creative use
- invokeai_generate franchises=[...] param; appended LAST (strongest
  identity cue): base -> style -> material -> painter -> franchise;
  styles x artists x franchises cartesian (capped 100)
- Attribution records franchises; gallery franchise filter + chips
  (fuchsia); REST /api/invokeai/franchises; Generate page 4th checkbox
  group; Gallery filter dropdown
- Fixed duplicated name in anchors ("in the style of Super Mario, super
  mario style..." -> clean signature)

## [0.1.10] - 2026-08-12""",
)
pathlib.Path("CHANGELOG.md").write_text(c, encoding="utf-8")

l = pathlib.Path("llms-full.txt").read_text(encoding="utf-8")
l = l.replace(
    "## v0.1.10 additions",
    """## v0.1.11 additions

invokeai_franchises (operation=list|get|search) exposes 23 fan-style
franchise presets (data/franchises.json): Mario, Zelda, Pokemon, Ghibli,
Shinkai, Disney, Pixar, Tim Burton, Simpsons, Marvel, Star Wars, LotR,
Harry Potter, D&D, Warhammer 40k, MTG, Doom, Portal, Sonic, Hollow Knight,
Undertale, Animal Crossing. invokeai_generate(franchises=[...]) appends
them LAST - priority: base -> style -> material -> painter -> franchise.
All four dims cartesian (cap 100) with per-item attribution; gallery
franchise= filter + fuchsia chips. REST: GET /api/invokeai/franchises.

## v0.1.10 additions""",
)
pathlib.Path("llms-full.txt").write_text(l, encoding="utf-8")

a = pathlib.Path("AGENTS.md").read_text(encoding="utf-8")
a = a.replace(
    "invokeai_styles (list/get/search), invokeai_artists (list/get/search), invokeai_workflows, invokeai_system",
    "invokeai_styles (list/get/search), invokeai_artists (list/get/search),\ninvokeai_franchises (list/get/search), invokeai_workflows, invokeai_system",
)
pathlib.Path("AGENTS.md").write_text(a, encoding="utf-8")
print("docs updated")
