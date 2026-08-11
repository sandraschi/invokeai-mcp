"""Configuration for invokeai-mcp.

One source of truth: environment variables (loaded from repo-root .env when
present). All values have fleet-registered defaults.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_dotenv(path: Path | None = None) -> None:
    """Minimal dotenv loader (no extra dependency)."""
    env_file = path or (_REPO_ROOT / ".env")
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


_load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Runtime settings for the server."""

    invokeai_url: str = field(
        default_factory=lambda: os.getenv("INVOKEAI_URL", "http://127.0.0.1:9090")
    )
    queue_id: str = field(default_factory=lambda: os.getenv("INVOKEAI_QUEUE_ID", "default"))
    download_dir: Path = field(
        default_factory=lambda: Path(
            os.getenv("INVOKEAI_DOWNLOAD_DIR", str(_REPO_ROOT / "data" / "downloads"))
        )
    )
    backend_port: int = field(default_factory=lambda: int(os.getenv("INVOKEAI_MCP_PORT", "11154")))
    frontend_port: int = field(
        default_factory=lambda: int(os.getenv("INVOKEAI_FRONTEND_PORT", "11155"))
    )
    access_token: str | None = field(
        default_factory=lambda: os.getenv("INVOKEAI_ACCESS_TOKEN") or None
    )
    request_timeout: float = field(
        default_factory=lambda: float(os.getenv("INVOKEAI_TIMEOUT", "120"))
    )

    @property
    def api_base(self) -> str:
        return self.invokeai_url.rstrip("/")

    def image_url(self, image_name: str) -> str:
        """Absolute URL to fetch a full-size image from InvokeAI."""
        return f"{self.api_base}/api/v1/images/i/{image_name}/full"


def get_settings() -> Settings:
    return Settings()
