"""CUA webapp smoke test - pre-Tauri browser walk (fleet standard).

Phases: kill stale -> start stack -> backend health -> frontend ready ->
open browser -> connected badge wait (OCR) -> nav walk with per-page
screenshots -> diagnostics -> cleanup.

Copy of the fleet template adapted for invokeai-mcp (ports 11154/11155).
Requires: pywinauto, Pillow, pytesseract (uv run with dev extras).
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

CUA_SMOKE_VERSION = "3.1.0"
ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "cua-reports"

CONFIG = json.loads((ROOT / "scripts" / "cua-nsis-config.json").read_text(encoding="utf-8"))

BACKEND_PORT = CONFIG["backend_port"]
FRONTEND_PORT = CONFIG["frontend_port"]
HEALTH_PATH = CONFIG["health_path"]
CONNECTED_TIMEOUT = CONFIG.get("connected_timeout", 60)
NAV_ROUTES = CONFIG.get("nav_routes", [])
BACKEND_MODULE = CONFIG.get("backend_module", "")
START_SCRIPT = ROOT / CONFIG.get("start_script", "start.ps1")


def log(phase: str, ok: bool, detail: str = "") -> None:
    mark = "PASS" if ok else "FAIL"
    print(f"[{mark}] {phase} {detail}")
    return ok


def kill_stale() -> None:
    for port in (BACKEND_PORT, FRONTEND_PORT):
        cmd = (
            f"Get-NetTCPConnection -LocalPort {port} -ErrorAction SilentlyContinue "
            "| ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"
        )
        subprocess.run(["powershell.exe", "-NoProfile", "-Command", cmd], capture_output=True)
    subprocess.run(
        ["taskkill", "/F", "/IM", "node.exe", "/FI", f"WINDOWTITLE eq {CONFIG['server_name']}*"],
        capture_output=True,
    )


def start_stack() -> subprocess.Popen | None:
    if START_SCRIPT.exists():
        return subprocess.Popen(
            ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(START_SCRIPT), "-Headless"],
            cwd=str(ROOT),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    return None


def wait_http(port: int, path: str, timeout: int = 60) -> bool:
    import urllib.request

    for _ in range(timeout):
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=2) as r:
                if r.status == 200:
                    return True
        except Exception:
            pass
        time.sleep(1)
    return False


def ocr_window() -> str:
    try:
        import pytesseract
        from PIL import Image
        from pywinauto import Desktop

        win = Desktop(backend="uia").window(title_re=CONFIG.get("window_title_re", "InvokeAI"))
        if not win.exists():
            return ""
        img = win.capture_as_image()
        text = pytesseract.image_to_string(img)
        return text.lower()
    except Exception:
        return ""


def wait_connected(timeout: int = CONNECTED_TIMEOUT) -> bool:
    for _ in range(timeout):
        text = ocr_window()
        for kw in ("connected", "system online", "online", "ready"):
            if kw in text:
                return True
        time.sleep(2)
    return False


def nav_walk() -> list[tuple[str, bool, int]]:
    try:
        from pywinauto import Desktop

        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        win = Desktop(backend="uia").window(title_re=CONFIG.get("window_title_re", "InvokeAI"))
        win.maximize()
        results: list[tuple[str, bool, int]] = []
        for label, expected in NAV_ROUTES:
            try:
                elem = win.descendants(title=label)
                if not elem:
                    elem = win.descendants(control_type="Hyperlink")
                    elem = [e for e in elem if label.lower() in (e.window_text() or "").lower()]
                if elem:
                    elem[0].click_input()
                    time.sleep(1.5)
                    shot = REPORT_DIR / f"webapp-{label.lower()}.png"
                    win.capture_as_image().save(shot)
                    results.append((label, True, shot.stat().st_size))
                else:
                    results.append((label, False, 0))
            except Exception:
                results.append((label, False, 0))
        return results
    except Exception as exc:
        print(f"[FAIL] nav walk: {exc}")
        return []


def diagnostics() -> dict:
    import urllib.request

    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{BACKEND_PORT}/api/tools", timeout=5) as r:
            return json.loads(r.read())
    except Exception as exc:
        return {"error": str(exc)}


def main() -> int:
    print("=" * 60)
    print(f"CUA webapp test v{CUA_SMOKE_VERSION} - {CONFIG['server_name']}")
    print("Automation will open and drive the browser. Move your mouse away.")
    print("=" * 60)
    time.sleep(3)

    kill_stale()
    proc = start_stack()
    time.sleep(5)

    ok = wait_http(BACKEND_PORT, HEALTH_PATH)
    log("backend health", ok)
    if not ok:
        print("Backend did not come up - aborting.")
        return 1

    frontend_ok = wait_http(FRONTEND_PORT, "/")
    log("frontend ready", frontend_ok)

    import webbrowser

    webbrowser.open(f"http://127.0.0.1:{FRONTEND_PORT}")
    connected = wait_connected()
    log("connected badge", connected)

    nav = nav_walk()
    distinct = len({size for _, ok, size in nav if ok})
    log("nav walk", len(nav) > 0 and distinct >= 3, f"pages={len(nav)} distinct_sizes={distinct}")

    diag = diagnostics()
    tools = diag.get("tools", [])
    log("diagnostics tools", isinstance(tools, list) and len(tools) >= 10, f"count={len(tools) if isinstance(tools, list) else '?'}")

    kill_stale()
    print("=" * 60)
    print("DONE. Screenshots in cua-reports/")
    return 0 if (ok and connected and len(nav) > 0) else 1


if __name__ == "__main__":
    sys.exit(main())
