"""Run a 60-style batch through the webapp generate API.

Replicates GeneratePage style application: base prompt + style.prompt
suffix, style.negative, style.cfg/steps. Prints progress, polls the
engine queue, summarizes results. Usage: uv run python scripts/batch-60-styles.py
"""

from __future__ import annotations

import json
import re
import sys
import time

import httpx

BACKEND = "http://127.0.0.1:11154"
ENGINE = "http://127.0.0.1:9090"
MODEL_KEY = "juggernaut-xl-v9"  # engine key; may differ, resolved at runtime

BASE_PROMPT = (
    "a lone detective in a trench coat and fedora standing in a rain-soaked street at night, "
    "film noir, 1950s Los Angeles, neon signs reflecting in wet asphalt puddles, "
    "cigarette smoke curling in the rain, chiaroscuro lighting, dramatic shadows, cinematic, "
    "highly detailed, masterpiece, best quality, 8k"
)
DEFAULT_NEGATIVE = "cartoon, painting, illustration, 3d render, anime, sketch, blurry, low quality"


def parse_styles(path: str) -> list[dict]:
    text = open(path, encoding="utf-8").read()
    block = text.split("export const STYLES", 1)[1].split("];", 1)[0]
    styles: list[dict] = []
    for chunk in re.split(r"(?=^\s*\{)", block, flags=re.M):
        if "id:" not in chunk:
            continue
        def grab(key: str) -> str:
            m = re.search(rf"{key}:\s*\"(.*?)\"", chunk, re.S)
            return m.group(1) if m else ""
        def grab_num(key: str) -> float | None:
            m = re.search(rf"{key}:\s*([\d.]+)", chunk)
            return float(m.group(1)) if m else None
        styles.append(
            {
                "id": grab("id"),
                "name": grab("name"),
                "prompt": grab("prompt"),
                "negative": grab("negative"),
                "cfg": grab_num("cfg"),
                "steps": grab_num("steps"),
            }
        )
    return [s for s in styles if s["id"]]


def resolve_model_key() -> str:
    r = httpx.get(f"{ENGINE}/api/v2/models/?model_type=main", timeout=15)
    for m in r.json().get("models", []):
        if m.get("base") == "sdxl":
            return m["key"]
    return ""


def main() -> None:
    styles = parse_styles("webapp/src/lib/presets.ts")
    if not styles:
        print("no styles parsed")
        sys.exit(1)
    model_key = resolve_model_key()
    print(f"{len(styles)} styles, model {model_key}")
    if len(styles) > 60:
        styles = styles[:60]
    print(f"running {len(styles)} styles")

    items: list[dict] = []
    with httpx.Client(timeout=90) as client:
        for i, s in enumerate(styles, 1):
            payload = {
                "operation": "txt2img",
                "prompt": f"{BASE_PROMPT}, {s['prompt']}".strip(),
                "negative_prompt": s["negative"] or DEFAULT_NEGATIVE,
                "model_key": model_key,
                "width": 1024,
                "height": 1024,
                "steps": int(s["steps"] or 35),
                "cfg_scale": s["cfg"] or 7.0,
                "scheduler": "dpmpp_2m_sde",
                "seed": None,
            }
            try:
                r = client.post(f"{BACKEND}/api/invokeai/generate", json=payload)
                j = r.json()
            except Exception as exc:
                print(f"  [{i}] {s['id']}: FAILED enqueue {exc}")
                items.append({"style": s["id"], "queue_id": None, "error": str(exc)})
                continue
            if not j.get("success"):
                print(f"  [{i}] {s['id']}: {j.get('message', j.get('error'))}")
                items.append({"style": s["id"], "queue_id": None, "error": j.get("message")})
            else:
                items.append({"style": s["id"], "queue_id": j["queue_item_id"]})
        print(f"enqueued {sum(1 for it in items if it['queue_id'])} / {len(items)}")

        pending = [it for it in items if it["queue_id"]]
        deadline = time.time() + 1500
        while pending and time.time() < deadline:
            time.sleep(20)
            q = client.get(f"{ENGINE}/api/v1/queue/default/status", timeout=15).json()
            done = 0
            for it in pending:
                st = client.get(f"{ENGINE}/api/v1/queue/default/i/{it['queue_id']}", timeout=15)
                if st.status_code == 200:
                    item = st.json()
                    if item.get("status") in ("completed", "failed", "cancelled"):
                        it["status"] = item["status"]
                        it["error"] = item.get("error_type")
                        done += 1
            pending = [it for it in pending if "status" not in it]
            qb = q.get("queue", {})
            print(
                f"  progress: {done}/{len(items) - len(pending)} done "
                f"(queue in_progress={qb.get('in_progress', 0)}, pending={qb.get('pending', 0)})"
            )
        for it in pending:
            it["status"] = "timeout"

    ok = [it for it in items if it.get("status") == "completed"]
    bad = [it for it in items if it.get("status") not in ("completed",)]
    print(f"\n=== batch done: {len(ok)}/{len(items)} completed ===")
    if bad:
        print("failures:")
        for it in bad:
            print(f"  {it['style']}: {it.get('error') or it.get('status')}")
    json.dump(items, open("scripts/batch-60-styles-result.json", "w"), indent=2)
    print("result: scripts/batch-60-styles-result.json")


if __name__ == "__main__":
    main()
