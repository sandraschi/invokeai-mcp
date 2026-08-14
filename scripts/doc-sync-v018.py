"""Doc sync for v0.1.8 (exact style attribution)."""
import pathlib

c = pathlib.Path("CHANGELOG.md").read_text(encoding="utf-8")
c = c.replace(
    "## [0.1.7] - 2026-08-12",
    """## [0.1.8] - 2026-08-12

### Added
- Exact per-image style attribution: enqueue-time registry
  (data/attribution.json, item_id -> styles), joined through
  image.session_id == queue item session_id
- Gallery feed returns per-image styles[]; style filter matches exactly,
  falling back to prompt-signature matching for pre-registry images
- Style chips on gallery tiles + lightbox (up to 3, +N overflow)
- Fixed per-item attribution bug (was recording the full style set on
  every job of a batch)

## [0.1.7] - 2026-08-12""",
)
pathlib.Path("CHANGELOG.md").write_text(c, encoding="utf-8")

l = pathlib.Path("llms-full.txt").read_text(encoding="utf-8")
l = l.replace(
    "## v0.1.7 additions",
    """## v0.1.8 additions

Exact style attribution: invokeai_generate records item_id -> style ids
in data/attribution.json at enqueue time; gallery images link back via
image.session_id (== the queue item's session_id). The gallery feed
returns styles[] per image and the style filter prefers exact matches,
falling back to prompt-signature matching only for pre-registry images.

## v0.1.7 additions""",
)
pathlib.Path("llms-full.txt").write_text(l, encoding="utf-8")
print("docs updated")
