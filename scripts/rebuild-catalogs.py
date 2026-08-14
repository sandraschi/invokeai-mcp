"""Rebuild the Generate catalogs along clean axes.

Styles = aesthetic/mood/movement ONLY (media moves to MATERIALS, painter
names to the artists catalog, software/IP junk is dropped).
Materials = artistic media/techniques (chalk, papercut, crochet, oil paint...).
"""

from __future__ import annotations

import pathlib
import re

PRESETS = pathlib.Path("webapp/src/lib/presets.ts")

REMOVE_STYLES = {
    "watercolor", "oil-painting", "acrylic", "gouache", "pastel", "pencil-sketch",
    "charcoal", "stained-glass", "fresco", "pixel-art", "papercraft", "claymation",
    "lego", "super-mario", "blender-cycles", "unreal-engine", "van-gogh", "picasso",
    "monet", "banksy",
}

NEW_STYLES: list[tuple[str, str, str]] = [
    ("rococo", "Rococo", "rococo, ornate pastel elegance, gilded curves"),
    ("post-impressionist", "Post-Impressionist", "post-impressionist, bold color blocks, expressive form"),
    ("expressionism", "Expressionism", "expressionist, distorted emotion, bold color, gestural strokes"),
    ("abstract-expressionism", "Abstract Expressionism", "abstract expressionism, gestural color fields, action painting"),
    ("art-brut", "Art Brut", "art brut, raw naive marks, outsider art"),
    ("documentary", "Documentary", "documentary photography, candid realism, natural light"),
    ("editorial", "Editorial", "editorial photography, magazine quality, striking composition"),
    ("fashion", "Fashion", "fashion photography, high-end editorial, studio elegance"),
    ("architectural", "Architectural", "architectural photography, clean lines, geometric composition"),
    ("blue-hour", "Blue Hour", "blue hour, twilight blue tones, city lights"),
    ("cosmic-horror", "Cosmic Horror", "cosmic horror, vast unknowable dread, dark nebulae"),
    ("neon-noir", "Neon Noir", "neon noir, neon-lit night, wet streets, magenta cyan glow"),
    ("retro-futurism", "Retro-Futurism", "retro-futurism, 1950s sci-fi optimism, chrome and plastic"),
    ("mid-century-modern", "Mid-Century Modern", "mid-century modern, clean retro design, atomic age"),
    ("kawaii", "Kawaii", "kawaii, cute pastel, chibi charm"),
    ("dreamy", "Dreamy", "dreamy, soft haze, pastel glow"),
    ("ethereal", "Ethereal", "ethereal, translucent light, otherworldly"),
    ("moody", "Moody", "moody, dramatic shadows, deep contrast"),
    ("gritty", "Gritty", "gritty, raw texture, urban grime"),
    ("whimsical", "Whimsical", "whimsical, playful imagination, storybook charm"),
    ("elegant", "Elegant", "elegant, refined composition, graceful"),
    ("industrial", "Industrial", "industrial, raw mechanical, functional"),
    ("geometric", "Geometric", "geometric abstraction, precise shapes"),
    ("holographic", "Holographic", "holographic, iridescent rainbow sheen"),
    ("halftone", "Halftone", "halftone print, dotted shading, comic print"),
    ("comic-book", "Comic Book", "comic book art, bold ink lines, dynamic panels"),
    ("abstract", "Abstract", "abstract, non-representational forms"),
]

MATERIALS: list[tuple[str, str, str]] = [
    ("none", "No material", ""),
    ("chalk", "Chalk", "chalk drawing on dark paper"),
    ("pastel", "Soft Pastel", "soft pastel drawing, powdery texture"),
    ("oil-paint", "Oil Paint", "oil painting, thick visible brushstrokes"),
    ("watercolor", "Watercolor", "watercolor painting, soft washes, paper texture"),
    ("gouache", "Gouache", "gouache painting, flat matte color blocks"),
    ("acrylic", "Acrylic", "acrylic painting, bold opaque strokes"),
    ("pencil", "Pencil", "pencil drawing, graphite shading"),
    ("pen-ink", "Pen and Ink", "pen and ink drawing, fine hatching"),
    ("ink-wash", "Ink Wash", "sumi-e ink wash painting"),
    ("charcoal", "Charcoal", "charcoal sketch, smudged dark strokes"),
    ("marker", "Marker", "marker drawing, vibrant flat color"),
    ("crayon", "Crayon", "wax crayon drawing, waxy texture"),
    ("collage", "Collage", "paper collage, cut-out shapes"),
    ("papercut", "Papercut", "layered papercut art, intricate cut paper"),
    ("crochet", "Crochet", "crocheted fabric, yarn texture"),
    ("knitting", "Knitting", "knitted wool texture"),
    ("embroidery", "Embroidery", "embroidered fabric, thread texture"),
    ("quilting", "Quilting", "patchwork quilt, stitched fabric"),
    ("stained-glass", "Stained Glass", "stained glass artwork, leaded panels"),
    ("mosaic", "Mosaic", "mosaic tiles, grouted pieces"),
    ("origami", "Origami", "origami paper sculpture, folded paper"),
    ("linocut", "Linocut", "linocut print, bold carved blocks"),
    ("woodcut", "Woodcut", "woodcut print, carved grain"),
    ("etching", "Etching", "etching, fine engraved lines"),
    ("screen-print", "Screen Print", "screen print, flat spot colors"),
    ("scratchboard", "Scratchboard", "scratchboard art, white-on-black scratches"),
    ("pixel-art", "Pixel Art", "pixel art, low resolution"),
]


def parse_styles(text: str) -> list[dict]:
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

        s = {"id": grab("id"), "name": grab("name"), "prompt": grab("prompt"),
             "negative": grab("negative"), "cfg": num("cfg"), "steps": num("steps")}
        if s["id"]:
            styles.append(s)
    return styles


def emit_styles(styles: list[dict]) -> str:
    lines = ["export const STYLES: StylePreset[] = ["]
    for s in styles:
        lines.append("  {")
        lines.append(f'    id: "{s["id"]}",')
        lines.append(f'    name: "{s["name"]}",')
        lines.append(f'    prompt:\n      "{s["prompt"]}",')
        if s["negative"]:
            lines.append(f'    negative: "{s["negative"]}",')
        if s["cfg"] is not None:
            lines.append(f"    cfg: {s['cfg']},")
        if s["steps"] is not None:
            lines.append(f"    steps: {s['steps']},")
        lines.append("  },")
    lines.append("];")
    return "\n".join(lines)


def emit_materials() -> str:
    lines = ["export const MATERIALS: Material[] = ["]
    for mid, name, prompt in MATERIALS:
        lines.append("  {")
        lines.append(f'    id: "{mid}",')
        lines.append(f'    name: "{name}",')
        lines.append(f'    prompt: "{prompt}",')
        lines.append("  },")
    lines.append("];")
    return "\n".join(lines)


def main() -> None:
    text = PRESETS.read_text(encoding="utf-8")

    styles = parse_styles(text)
    kept = [s for s in styles if s["id"] not in REMOVE_STYLES]
    existing_ids = {s["id"] for s in kept}
    for nid, name, prompt in NEW_STYLES:
        if nid not in existing_ids:
            kept.append({"id": nid, "name": name, "prompt": prompt,
                         "negative": "", "cfg": None, "steps": None})
    print(f"styles: {len(styles)} -> {len(kept)} (removed {len(styles) - len(kept)})")

    new_text = text
    styles_block = text.split("export const STYLES", 1)[1].split("];", 1)[0]
    new_text = new_text.replace(
        "export const STYLES" + styles_block + "];",
        emit_styles(kept),
    )
    materials_start = new_text.index("export const MATERIALS")
    materials_end = new_text.index("export const QUALITY_TAGS")
    new_text = (
        new_text[:materials_start]
        + emit_materials()
        + "\n\n"
        + new_text[materials_end:]
    )
    PRESETS.write_text(new_text, encoding="utf-8")
    print("presets.ts rewritten")


if __name__ == "__main__":
    main()
