"""Painter catalog - 60 important painters, Giotto to Giger.

Each entry: id, name, prompt (the anchor suffix appended LAST - the
strongest style cue). Generated programmatically from the list below.
"""

from __future__ import annotations

import json
import pathlib
from functools import lru_cache
from typing import Any

_DATA = pathlib.Path(__file__).parent / "data" / "artists.json"

_PAINTERS: list[tuple[str, str, str]] = [
    ("giotto", "Giotto", "Proto-Renaissance fresco, gold-leaf altarpieces, monumental figures, flat spatial depth"),
    ("van-eyck", "Jan van Eyck", "Northern Renaissance oil, meticulous detail, glowing jewel tones, mirror reflections"),
    ("botticelli", "Botticelli", "Renaissance elegance, flowing line, mythological grace, pastel palette"),
    ("leonardo", "Leonardo da Vinci", "sfumato, serene composition, Renaissance chiaroscuro, anatomical precision"),
    ("michelangelo", "Michelangelo", "heroic musculature, dynamic contrapposto, Sistine fresco grandeur"),
    ("raphael", "Raphael", "High Renaissance harmony, soft idealized faces, balanced pyramidal composition"),
    ("titian", "Titian", "Venetian colorito, rich reds and golds, painterly flesh, warm luminosity"),
    ("durer", "Albrecht Dürer", "meticulous engraving, fine cross-hatching, symmetrical detail"),
    ("el-greco", "El Greco", "elongated figures, ecstatic spiritual drama, turbulent skies, icy palette"),
    ("bruegel", "Pieter Bruegel the Elder", "peasant life panorama, seasonal landscapes, teeming detail"),
    ("caravaggio", "Caravaggio", "tenebrism, stark dramatic chiaroscuro, gritty realism, theatrical candlelight"),
    ("rubens", "Rubens", "Baroque dynamism, fleshy opulence, swirling diagonals, rich warm color"),
    ("rembrandt", "Rembrandt", "deep brown shadow, golden glazing, soulful portraits, textured impasto"),
    ("vermeer", "Vermeer", "quiet interior light, lapis blue, pearl highlights, photographic stillness"),
    ("velazquez", "Velázquez", "courtly realism, loose brushwork up close, austere elegance"),
    ("goya", "Goya", "dark romanticism, biting satire, ghostly shadows, loose expressive strokes"),
    ("turner", "J.M.W. Turner", "sublime swirling light, atmospheric storms, glowing veils of color"),
    ("constable", "John Constable", "English countryside, billowing clouds, fresh green, broken color"),
    ("delacroix", "Delacroix", "Romantic color, exotic drama, turbulent motion, blazing hues"),
    ("friedrich", "Caspar David Friedrich", "Romantic solitude, misty peaks, lone figures, sublime vastness"),
    ("courbet", "Courbet", "realist earthiness, palette-knife texture, everyday labor, forest gloom"),
    ("manet", "Édouard Manet", "modern-life realism, flat tonal planes, black-and-white contrast, casual poses"),
    ("monet", "Claude Monet", "Impressionist light, dappled water, soft haze, broken color patches"),
    ("renoir", "Renoir", "warm Impressionist glow, soft-focus flesh, festive leisure, rosy light"),
    ("degas", "Degas", "ballet dancers, cropped compositions, pastel strokes, candid motion"),
    ("cezanne", "Paul Cézanne", "geometric brushstrokes, tilted planes, muted earth palette, structured forms"),
    ("van-gogh", "Vincent van Gogh", "swirling impasto, electric yellow, cypress spirals, emotional color"),
    ("gauguin", "Gauguin", "Tahitian flat color, symbolic shapes, earthy exotic palette, decorative outlines"),
    ("seurat", "Seurat", "pointillist dots, calm geometric light, seaside summer stillness"),
    ("toulouse-lautrec", "Toulouse-Lautrec", "Montmartre cabaret, bold posters, cropped diagonals, gaslight glow"),
    ("munch", "Edvard Munch", "existential anguish, swirling skies, stark color, psychological dread"),
    ("klimt", "Gustav Klimt", "gold leaf patterns, ornate flatness, jewel mosaic, sensual portraits"),
    ("kandinsky", "Kandinsky", "abstract color music, bold geometry, spiritual vibrations"),
    ("matisse", "Henri Matisse", "Fauvist color, cut-paper shapes, decorative simplicity, joyful flatness"),
    ("picasso", "Pablo Picasso", "Cubist facets, fractured planes, blue period mood, distorted forms"),
    ("mondrian", "Mondrian", "Neoplastic grid, primary colors, black lines, pure abstraction"),
    ("modigliani", "Modigliani", "elongated necks, almond eyes, warm ochre flesh, gentle melancholy"),
    ("klee", "Paul Klee", "childlike geometry, whimsical symbols, watercolor squares, poetic abstraction"),
    ("duchamp", "Marcel Duchamp", "Dada irony, readymade objects, conceptual wit, mechanical drawings"),
    ("dali", "Salvador Dalí", "melting clocks, surreal desert light, hyperreal dreamscapes"),
    ("magritte", "René Magritte", "bowler hats, floating objects, twilight clouds, quiet surreal paradox"),
    ("okeefe", "Georgia O'Keeffe", "close-up flower abstractions, desert bones, sensuous curves, luminous color"),
    ("hopper", "Edward Hopper", "lonely Americana, stark sunlight, empty diners, cinematic stillness"),
    ("kahlo", "Frida Kahlo", "self-portrait symbolism, vivid Mexican color, surreal honesty"),
    ("pollock", "Jackson Pollock", "drip painting, tangled skeins, energetic splatter, all-over action"),
    ("rothko", "Mark Rothko", "floating color fields, soft-edged rectangles, meditative glow"),
    ("warhol", "Andy Warhol", "pop silkscreen, celebrity repetition, flat bright blocks, camp color"),
    ("escher", "M.C. Escher", "impossible staircases, tessellated birds, optical paradox, black-white precision"),
    ("bacon", "Francis Bacon", "screaming popes, distorted flesh, cage-like brushstrokes, visceral dread"),
    ("lichtenstein", "Roy Lichtenstein", "Ben-Day dots, comic panels, bold outlines, pop irony"),
    ("hockney", "David Hockney", "California pools, swimming reflections, bold flat shapes, cheerful color"),
    ("basquiat", "Jean-Michel Basquiat", "graffiti crowns, raw text scrawl, skeletal figures, neo-expressionist energy"),
    ("beksinski", "Zdzisław Beksiński", "post-apocalyptic dreamscapes, decaying grandeur, surreal detail, dark fantasy"),
    ("giger", "H.R. Giger", "biomechanical nightmare, organic machinery, dark airbrushed alien corridors"),
    ("malevich", "Malevich", "Suprematist black square, geometric purity, avant-garde reduction"),
    ("de-chirico", "Giorgio de Chirico", "empty piazzas, long shadows, mannequins, metaphysical stillness"),
    ("schiele", "Egon Schiele", "angular nudes, raw outlines, orange flesh, nervous lines"),
    ("sorolla", "Joaquín Sorolla", "Mediterranean sunlight, sparkling seaside, dazzling white, plein-air joy"),
    ("sargent", "John Singer Sargent", "Edwardian elegance, swift confident strokes, shimmering satin"),
    ("balthus", "Balthus", "hushed interiors, adolescent stillness, muted tones, quiet tension"),
]


def _build() -> list[dict[str, Any]]:
    out = []
    for pid, name, sig in _PAINTERS:
        out.append(
            {
                "id": pid,
                "name": name,
                "prompt": f"in the style of {name}, {sig}",
            }
        )
    return out


@lru_cache(maxsize=1)
def load_artists() -> list[dict[str, Any]]:
    if not _DATA.exists():
        _DATA.parent.mkdir(parents=True, exist_ok=True)
        _DATA.write_text(json.dumps(_build(), indent=2), encoding="utf-8")
    return json.loads(_DATA.read_text(encoding="utf-8"))


def list_artists() -> list[dict[str, Any]]:
    return load_artists()


def get_artist(artist_id: str) -> dict[str, Any] | None:
    for a in load_artists():
        if a["id"] == artist_id:
            return a
    return None


def search_artists(query: str, limit: int = 20) -> list[dict[str, Any]]:
    q = query.lower()
    hits = []
    for a in load_artists():
        if q in a["id"].lower() or q in a["name"].lower() or q in a["prompt"].lower():
            hits.append(a)
            if len(hits) >= limit:
                break
    return hits


def apply_artist(artist: dict[str, Any], prompt: str) -> str:
    """Append the painter anchor suffix - LAST, the strongest style cue."""
    suffix = artist.get("prompt", "").strip()
    if not suffix:
        return prompt.strip()
    return f"{prompt.strip()}, {suffix}"
