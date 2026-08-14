"""Doc sync for v0.1.9 (painters, display names, URL fix)."""
import pathlib

c = pathlib.Path("CHANGELOG.md").read_text(encoding="utf-8")
c = c.replace(
    "## [0.1.8] - 2026-08-12",
    """## [0.1.9] - 2026-08-12

### Added
- invokeai_artists tool + 60-painter catalog (Giotto to Giger) with
  curated one-line signatures; painters anchor the prompt LAST
  (base -> style -> material -> painter = strongest cue)
- invokeai_generate artists=[...] param; styles x artists cartesian
  (capped 100); per-item attribution now records styles + artists
- Gallery: painter filter (exact + fallback) and painter chips
- Fixed broken images: engine returns RELATIVE image urls - feed now
  normalizes to absolute (browser was 404ing against the webapp origin)
- display_name: prompt-slug + short id (marlowe-in-rain-2774b797)
  instead of the raw uuid; Generate page painter checkboxes (search,
  select-all) cross-batched with styles x materials

## [0.1.8] - 2026-08-12""",
)
pathlib.Path("CHANGELOG.md").write_text(c, encoding="utf-8")

l = pathlib.Path("llms-full.txt").read_text(encoding="utf-8")
l = l.replace(
    "## v0.1.8 additions",
    """## v0.1.9 additions

invokeai_artists (operation=list|get|search) exposes the 60-painter
catalog (Giotto to Giger, data/artists.json, curated signatures).
invokeai_generate(artists=[...]) appends "in the style of X" anchors
LAST - prompt priority: base -> style -> material -> painter. styles
x artists is a cartesian product (capped at 100 jobs) with per-item
attribution for both dims. Gallery: artist= filter param + painter
chips; image urls are normalized to absolute engine urls; images carry
display_name (prompt slug + short id).

## v0.1.8 additions""",
)
pathlib.Path("llms-full.txt").write_text(l, encoding="utf-8")

a = pathlib.Path("AGENTS.md").read_text(encoding="utf-8")
a = a.replace(
    "invokeai_styles (list/get/search), invokeai_workflows, invokeai_system",
    "invokeai_styles (list/get/search), invokeai_artists (list/get/search), invokeai_workflows, invokeai_system",
)
a = a.replace(
    "styles=[...] multi-style batches - outpaint via webapp pad+mask),",
    "styles=[...] + artists=[...] multi-dim batches - outpaint via webapp pad+mask),",
)
pathlib.Path("AGENTS.md").write_text(a, encoding="utf-8")
print("docs updated")
