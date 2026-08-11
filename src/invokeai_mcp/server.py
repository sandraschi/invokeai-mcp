"""invokeai-mcp server - FastMCP 3.4 + Starlette REST + MCP HTTP transport.

Dual transport:
- stdio:  uv run python -m invokeai_mcp.server            (Claude Desktop, Cursor)
- HTTP:   INVOKEAI_MCP_PORT=11154 uv run python -m invokeai_mcp.server --mode http
          (webapp backend; MCP on /mcp, REST on /api/*)
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path

import uvicorn
from fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware

from invokeai_mcp import __version__
from invokeai_mcp.api.routes import routes
from invokeai_mcp.config import get_settings
from invokeai_mcp.runtime import log

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")

_CORS_ORIGINS = [
    "http://localhost:11155",
    "http://127.0.0.1:11155",
    "http://localhost:11154",
    "http://127.0.0.1:11154",
    "tauri://localhost",
    "http://tauri.localhost",
    "https://tauri.localhost",
]

_CORS_REGEX = (
    r"https?://(?:[a-zA-Z0-9-]+\.ts\.net|.*?\.tail-[a-f0-9]+\.ts\.net|tauri\.localhost|"
    r"localhost|127\.0\.0\.1|192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|"
    r"100\.\d{1,3}\.\d{1,3}\.\d{1,3})(?::\d+)?$|^tauri://localhost$"
)

mcp = FastMCP(
    "invokeai-mcp",
    version=__version__,
    instructions=(
        "Bridge to the local InvokeAI creative engine. Generate images "
        "(txt2img/img2img/inpaint/upscale), manage the queue, models, gallery, "
        "boards, and workflows. Call invokeai_help() for the index."
    ),
)

_SKILLS_ROOT = Path(__file__).parent / "skills"


@mcp.resource("skill://{name}")
def read_skill(name: str) -> str:
    """Read a skill's SKILL.md content (skill://{name} resource)."""
    path = _SKILLS_ROOT / name / "SKILL.md"
    if not path.exists():
        raise FileNotFoundError(f"skill {name} not found")
    return path.read_text(encoding="utf-8")


def _build_app() -> Starlette:
    """Starlette app: REST routes + mounted MCP HTTP app, CORS on the outer app.

    Middleware on the outer app covers mounted children, so one CORS block
    serves both /api/* and /mcp (fleet CORS_STANDARD).
    """
    mcp_http = mcp.http_app(path="/")
    app = Starlette(routes=routes, lifespan=mcp_http.lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_CORS_ORIGINS,
        allow_origin_regex=_CORS_REGEX,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.mount("/mcp", mcp_http)
    return app


def main(argv: list[str] | None = None) -> None:
    args = argv if argv is not None else sys.argv[1:]
    parser = argparse.ArgumentParser(prog="invokeai-mcp")
    parser.add_argument(
        "--mode",
        choices=["stdio", "http"],
        default=None,
        help="Transport mode (default: stdio unless INVOKEAI_MCP_PORT set)",
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=None)
    opts, _ = parser.parse_known_args(args)

    settings = get_settings()
    mode = opts.mode or ("http" if os.environ.get("INVOKEAI_MCP_PORT") else "stdio")

    import invokeai_mcp.tools  # noqa: F401 - portmanteau registration (import = register)

    if mode == "http":
        port = opts.port or settings.backend_port
        log("INFO", "server", f"starting HTTP on {opts.host}:{port} (MCP /mcp, REST /api)")
        app = _build_app()
        uvicorn.run(app, host=opts.host, port=port, log_level="info")
    else:
        log("INFO", "server", "starting stdio transport")
        import asyncio

        asyncio.run(mcp.run_stdio_async(show_banner=False))


if __name__ == "__main__":
    main()
