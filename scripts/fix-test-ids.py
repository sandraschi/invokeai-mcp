"""Fix style ids in tests after the catalog rebuild (watercolor -> cinematic)."""
import pathlib

subs = [
    ('search_styles("watercolor")', 'search_styles("noir")'),
    ('"watercolor" in s["id"] + s["name"] + s["prompt"]', '"noir" in s["id"] + s["name"] + s["prompt"]'),
    ('styles=["photorealistic", "watercolor", "film-noir"]', 'styles=["photorealistic", "cinematic", "film-noir"]'),
    ('"watercolor" in prompts[1]', '"cinematic" in prompts[1]'),
    ('"2": ["watercolor"]', '"2": ["cinematic"]'),
    ('styles=["photorealistic", "watercolor"]', 'styles=["photorealistic", "cinematic"]'),
]

for name in ("tests/test_styles.py", "tests/test_artists.py"):
    p = pathlib.Path(name)
    c = p.read_text(encoding="utf-8")
    for old, new in subs:
        c = c.replace(old, new)
    p.write_text(c, encoding="utf-8")
    print(name, "updated")
