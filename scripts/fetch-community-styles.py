"""Batch-download A1111 community style packs and import them.

Sources (all open, no auth):
- Douleb/SDXL-A1111-Styles         850+ styles (styles.csv)
- Douleb/SDXL-750-Styles-GPT4-     750+ styles (styles.csv)

Normalizes the A1111 "{prompt} ... suffix" template to our append-suffix
model (the tail after {prompt} becomes the suffix), filters explicit
content, dedupes, and writes data/community_styles.json + a report.

Usage: uv run python scripts/fetch-community-styles.py
"""

from __future__ import annotations

import csv
import io
import json
import pathlib
import re
import sys
import urllib.parse

import httpx

OUT = pathlib.Path("src/invokeai_mcp/data/community_styles.json")

PACKS: list[tuple[str, str]] = [
    (
        "a1111-sdxl-850",
        "https://raw.githubusercontent.com/Douleb/SDXL-A1111-Styles/main/"
        "All%20in%20one%20Styles%20(pro%20%2B%20experiemental%20GPT4)%20850%2B/styles.csv",
    ),
    (
        "a1111-sdxl-gpt4-750",
        "https://raw.githubusercontent.com/Douleb/SDXL-750-Styles-GPT4-/main/styles.csv",
    ),
]

EXPLICIT_TOKENS = [
    "nsfw", "porn", "sex ", " nude", "nude ", "hentai", "erotic", "bdsm", "fetish",
    "kink", "penis", "vagina", " tits", "cum", "fuck", "sexual", "naked woman",
    "naked man", "lingerie", "bikini", "sex scene",
]

_SLUG_CLEAN = re.compile(r"[^a-z0-9]+")


def slug(name: str) -> str:
    words = []
    for token in name.lower().replace(":", " ").split():
        clean = _SLUG_CLEAN.sub("", token)
        if clean:
            words.append(clean)
        if len(words) >= 5:
            break
    return "-".join(words) if words else "style"


def is_explicit(text: str) -> bool:
    low = text.lower()
    return any(tok in low for tok in EXPLICIT_TOKENS)


def normalize_prompt(raw: str) -> str:
    """A1111 template 'prefix {prompt} suffix' -> append-suffix model."""
    text = raw.strip()
    if "{prompt}" in text:
        tail = text.split("{prompt}", 1)[1]
        tail = tail.strip().lstrip(". ").lstrip(",").strip()
        if len(tail) >= 4:
            return tail
        head = text.split("{prompt}", 1)[0]
        head = head.strip().rstrip(". ").rstrip(",").strip()
        if len(head) >= 4:
            return head
        return ""
    return text


def fetch_csv(client: httpx.Client, url: str) -> list[list[str]]:
    r = client.get(url, timeout=60)
    r.raise_for_status()
    text = r.content.decode("utf-8-sig", errors="replace")
    return list(csv.reader(io.StringIO(text)))


def main() -> None:
    merged: dict[str, dict] = {}
    report: list[str] = []
    with httpx.Client(follow_redirects=True) as client:
        for pack_id, url in PACKS:
            try:
                rows = fetch_csv(client, url)
            except Exception as exc:
                report.append(f"[{pack_id}] FETCH FAILED: {exc}")
                continue
            header = rows[0] if rows else []
            body = [r for r in rows[1:] if len(r) >= 1 and r[0].strip()]
            imported = 0
            skipped = 0
            for row in body:
                name = row[0].strip().replace("Style: ", "").strip()
                if not name:
                    continue
                pos = row[1].strip() if len(row) > 1 else ""
                neg = row[2].strip() if len(row) > 2 else ""
                if is_explicit(name) or is_explicit(pos):
                    skipped += 1
                    continue
                suffix = normalize_prompt(pos)
                if len(suffix) < 8:
                    skipped += 1
                    continue
                sid = f"{pack_id}-{slug(name)}"
                entry = {
                    "id": sid,
                    "name": f"{name} [community]",
                    "prompt": suffix,
                    "negative": neg,
                    "source": pack_id,
                }
                if sid in merged:
                    skipped += 1
                    continue
                merged[sid] = entry
                imported += 1
            report.append(f"[{pack_id}] header={header[:3]} rows={len(body)} imported={imported} filtered={skipped}")

    entries = list(merged.values())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(entries, indent=2), encoding="utf-8")

    print("=== community styles import ===")
    for line in report:
        print(f"  {line}")
    print(f"  TOTAL: {len(entries)} styles -> {OUT}")
    print()
    print("=== interesting content sample ===")
    for e in entries[:18]:
        print(f"  {e['name']}: {e['prompt'][:70]}")
    print()
    print("=== longest / most distinctive ===")
    top = sorted(entries, key=lambda e: len(e["prompt"]), reverse=True)[:5]
    for e in top:
        print(f"  {e['name']} ({len(e['prompt'])} chars)")


if __name__ == "__main__":
    main()
