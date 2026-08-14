"""Doc sync for v0.1.7 (gallery sort/filter/batch)."""
import pathlib

c = pathlib.Path("CHANGELOG.md").read_text(encoding="utf-8")
c = c.replace(
    "## [0.1.6] - 2026-08-12",
    """## [0.1.7] - 2026-08-12

### Added
- Gallery: sorting (created_at/name/starred, asc/desc), filters (starred,
  board, style from the catalog, prompt search) via dedicated REST feed
- Batch ops: multi-select mode, select-page, batch star/unstar/delete,
  zip export (backend streams a real archive), move-to-board
- invokeai_gallery batch ops: batch_delete/batch_star/batch_unstar/
  board_add/board_remove (MCP parity)
- GET /api/invokeai/boards; client.list_boards v6 "all" param fix
- Style matching for gallery filtering (match_style_for_prompt)

## [0.1.6] - 2026-08-12""",
)
pathlib.Path("CHANGELOG.md").write_text(c, encoding="utf-8")

l = pathlib.Path("llms-full.txt").read_text(encoding="utf-8")
l = l.replace(
    "## v0.1.6 additions",
    """## v0.1.7 additions

Gallery REST feed GET /api/invokeai/gallery supports query/sort
(created_at|name|starred)/order/starred/board/style (catalog style ids,
matched against embedded prompt metadata)/limit/offset. Batch routes:
POST /api/invokeai/gallery/batch {operation: delete|star|unstar,
image_names}, POST /api/invokeai/gallery/board (+DELETE) for board
assignment, POST /api/invokeai/gallery/zip -> zip archive, and
GET /api/invokeai/boards. invokeai_gallery gained batch ops
(batch_delete/batch_star/batch_unstar/board_add/board_remove) with the
image_names parameter. The gallery webapp page has select mode + batch bar.

## v0.1.6 additions""",
)
pathlib.Path("llms-full.txt").write_text(l, encoding="utf-8")
print("docs updated")
