"""Run a 60-style batch through the new backend styles param.

One invokeai_generate call with styles=[...60 ids]; the backend enqueues
one item per style (prompt suffix + style cfg/steps). Prints progress and
polls the engine queue. Usage: uv run python scripts/batch-60-styles.py
"""

from __future__ import annotations

import json
import sys
import time

import httpx

BACKEND = "http://127.0.0.1:11154"
ENGINE = "http://127.0.0.1:9090"
MODEL_NAME = "Juggernaut XL v9"
PROMPT = (
    "Philip Marlowe, a lone detective in a trench coat and fedora, standing in a "
    "rain-soaked street at night, film noir, 1950s Los Angeles, neon signs "
    "reflecting in wet asphalt puddles, cigarette smoke curling in the rain, "
    "chiaroscuro lighting, dramatic shadows, cinematic"
)


def main() -> None:
    r = httpx.get(f"{BACKEND}/api/invokeai/styles", timeout=15)
    styles = r.json().get("styles", [])
    if not styles:
        print("no styles from backend")
        sys.exit(1)
    style_ids = [s["id"] for s in styles[:60]]
    print(f"{len(style_ids)} styles, model {MODEL_NAME}")

    payload = {
        "operation": "txt2img",
        "prompt": PROMPT,
        "model_key": MODEL_NAME,
        "width": 1024,
        "height": 1024,
        "styles": style_ids,
        "style_cfg": True,
        "scheduler": "dpmpp_2m_sde",
        "seed": None,
    }
    with httpx.Client(timeout=120) as client:
        g = client.post(f"{BACKEND}/api/invokeai/generate", json=payload)
        j = g.json()
        if not j.get("success"):
            print(f"enqueue failed: {j.get('message', j)}")
            sys.exit(1)
        ids = j["queue_item_ids"]
        print(f"enqueued {len(ids)} items ({j.get('style_count')} styles)")

        pending = list(ids)
        deadline = time.time() + 1800
        last = 0
        while pending and time.time() < deadline:
            time.sleep(20)
            remaining = []
            done = 0
            for it in pending:
                st = client.get(f"{ENGINE}/api/v1/queue/default/i/{it}", timeout=15)
                if st.status_code == 200:
                    item = st.json()
                    if item.get("status") in ("completed", "failed", "cancelled"):
                        done += 1
                    else:
                        remaining.append(it)
                else:
                    remaining.append(it)
            if done != last:
                print(f"  {done}/{len(ids)} done")
                last = done
            pending = remaining

        statuses = []
        for it in ids:
            st = client.get(f"{ENGINE}/api/v1/queue/default/i/{it}", timeout=15).json()
            statuses.append({"queue_id": it, "status": st.get("status"), "error": st.get("error_type")})
        ok = [s for s in statuses if s["status"] == "completed"]
        bad = [s for s in statuses if s["status"] != "completed"]
        print(f"\n=== batch done: {len(ok)}/{len(statuses)} completed ===")
        if bad:
            print("failures:")
            for s in bad:
                print(f"  item {s['queue_id']}: {s['status']} {s['error'] or ''}")
        json.dump(statuses, open("scripts/batch-60-styles-result.json", "w"), indent=2)


if __name__ == "__main__":
    main()
