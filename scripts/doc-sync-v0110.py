"""Doc sync for invokeai-mcp v0.1.10."""
import pathlib

root = pathlib.Path(".")

# ---------- repo CHANGELOG ----------
p = pathlib.Path("CHANGELOG.md")
c = p.read_text(encoding="utf-8")
c = c.replace(
    "## [0.1.9] - 2026-08-12",
    """## [0.1.10] - 2026-08-12

### Changed
- Generate page: styles/materials/painters checkbox panels moved into a
  collapsible "Batch presets" card (hidden by default, selection count in
  the header); batch action button lives in its own always-visible card

## [0.1.9] - 2026-08-12""",
)
p.write_text(c, encoding="utf-8")

# ---------- llms-full ----------
p = pathlib.Path("llms-full.txt")
c = p.read_text(encoding="utf-8")
c = c.replace(
    "## v0.1.9 additions",
    """## v0.1.10 additions

Generate webapp: batch presets (styles/materials/painters checkboxes) live
in a collapsible card hidden by default; the Batch run card with the
generate button stays visible.

## v0.1.9 additions""",
)
p.write_text(c, encoding="utf-8")
print("repo docs updated")
