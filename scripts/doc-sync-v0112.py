"""Doc sync for invokeai-mcp v0.1.12 (community packs + ops)."""
import pathlib

# ---------- CHANGELOG ----------
p = pathlib.Path("CHANGELOG.md")
c = p.read_text(encoding="utf-8")
c = c.replace(
    "## [0.1.11] - 2026-08-12",
    """## [0.1.12] - 2026-08-12

### Added
- A1111 community style packs: fetch-community-styles.py batch-imports
  Douleb/SDXL-A1111-Styles (850+) + SDXL-750-Styles-GPT4 -> 1321 styles
  in data/community_styles.json (normalized, explicit-filtered, source
  tagged); invokeai_styles operation='community'; REST
  /api/invokeai/styles?community=1; webapp 'Include community pack'
  toggle; community ids work in batches + attribution
- Port zombie sweep: clear-port-zombies.ps1 + just zombies (dry run) /
  zombie-clean (labeled kill of listeners on fleet-registered ports)
- Service banners in start terminals (named BACKEND/FRONTEND + urls +
  window title)

### Changed
- Console spam silenced: httpx/httpcore loggers -> WARNING, uvicorn
  access_log off
- justfile imports the vendored fleet recipe book (fleet.just): gained
  cua-nsis-test, fleet-stop, tauri-audit, emojibuster, zombies
- mcpb-pack gate fixed: import probe no longer pollutes mcpb/src with
  __pycache__ (PYTHONDONTWRITEBYTECODE + sweep); bunx absolute path;
  fleet layout entry point mcpb/pack.ps1 (gitignore exception)

## [0.1.11] - 2026-08-12""",
)
p.write_text(c, encoding="utf-8")

# ---------- llms-full ----------
p = pathlib.Path("llms-full.txt")
c = p.read_text(encoding="utf-8")
c = c.replace(
    "## v0.1.11 additions",
    """## v0.1.12 additions

A1111 community style packs: data/community_styles.json holds 1321 styles
imported from Douleb's 850+ and GPT4-750 packs (fetch-community-styles.py,
idempotent). invokeai_styles(operation='community', query=...) lists them;
get() resolves community ids so batches + attribution work unchanged.
REST: GET /api/invokeai/styles?community=1 (total includes community).
Webapp: 'Include community pack' toggle in the styles panel.

Ops: just zombies (dry run) / zombie-clean kills stale listeners on
fleet-registered ports with product labels (clear-port-zombies.ps1,
vendored in scripts/just/). Fleet recipe book is imported from the
vendored scripts/just/fleet.just - do not redefine recipes that exist
there (mcpb-pack, cua-*, zombies, fleet-stop, tauri-audit, emojibuster).

## v0.1.11 additions""",
)
p.write_text(c, encoding="utf-8")

# ---------- AGENTS.md ----------
p = pathlib.Path("AGENTS.md")
c = p.read_text(encoding="utf-8")
c = c.replace(
    "invokeai_styles (list/get/search), invokeai_artists (list/get/search),",
    "invokeai_styles (list/get/search/community - 1321 A1111 pack styles), invokeai_artists (list/get/search),",
)
c = c.replace(
    "```powershell\n.\\start.ps1\nuv run pytest tests/ -q\ncd webapp; bun run dev\njust mcpb-pack\n```",
    "```powershell\n.\\start.ps1\nuv run pytest tests/ -q\ncd webapp; bun run dev\njust mcpb-pack   # fleet recipe (mcpb/pack.ps1)\njust zombies     # dry-run port zombie sweep\njust zombie-clean\n```",
)
p.write_text(c, encoding="utf-8")

# ---------- README feature line ----------
p = pathlib.Path("README.md")
c = p.read_text(encoding="utf-8")
c = c.replace(
    "- Gallery search, boards, star/favorite organization",
    "- Gallery search, boards, star/favorite organization; sort/filter by style,\n  painter, franchise, board, starred; batch ops (star/unstar/delete/zip/move)\n  with exact per-image attribution\n- 76 curated styles + 23 franchise presets + 60 painters + 1321 A1111 community\n  style pack entries - all batchable in any combination",
)
p.write_text(c, encoding="utf-8")
print("repo docs updated")
