"""Extract STYLES from webapp/src/lib/presets.ts into backend data/styles.json."""
import json
import pathlib
import re

text = pathlib.Path("webapp/src/lib/presets.ts").read_text(encoding="utf-8")
block = text.split("export const STYLES", 1)[1].split("];", 1)[0]
styles = []
for chunk in re.split(r"(?=^\s*\{)", block, flags=re.M):
    if "id:" not in chunk:
        continue

    def grab(key: str) -> str:
        m = re.search(rf'{key}:\s*"(.*?)"', chunk, re.S)
        return m.group(1) if m else ""

    def num(key: str) -> float | None:
        m = re.search(rf"{key}:\s*([\d.]+)", chunk)
        return float(m.group(1)) if m else None

    s = {
        "id": grab("id"),
        "name": grab("name"),
        "prompt": grab("prompt"),
        "negative": grab("negative"),
        "cfg": num("cfg"),
        "steps": num("steps"),
    }
    if s["id"]:
        styles.append(s)

out = pathlib.Path("src/invokeai_mcp/data/styles.json")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(styles, indent=2), encoding="utf-8")
print(f"extracted {len(styles)} styles -> {out}")
