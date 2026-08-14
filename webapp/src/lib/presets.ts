/**
 * Generation presets - the style/material library and example prompts.
 * Shared by the Generate page (tabs, batch, composed prompt).
 */

export interface StylePreset {
  id: string;
  name: string;
  prompt: string;
  negative?: string;
  cfg?: number;
  steps?: number;
}

export const STYLES: StylePreset[] = [
  {
    id: "photorealistic",
    name: "Photorealistic",
    prompt:
      "photorealistic, ultra detailed, natural lighting, shot on 85mm f/1.4, shallow depth of field",
    negative: "cartoon, painting, illustration, 3d render, anime, sketch",
    cfg: 6.5,
    steps: 34.0,
  },
  {
    id: "cinematic",
    name: "Cinematic",
    prompt:
      "cinematic still, dramatic lighting, film grain, anamorphic lens flare, color graded, movie frame",
    negative: "flat lighting, amateur snapshot, low quality",
    cfg: 6.0,
    steps: 36.0,
  },
  {
    id: "film-noir",
    name: "Film Noir",
    prompt:
      "film noir, high contrast, hard shadows, black and white, venetian blinds, 1940s detective mood",
    negative: "color, bright, cheerful, modern lighting",
    cfg: 7.0,
    steps: 30.0,
  },
  {
    id: "tilt-shift",
    name: "Tilt Shift",
    prompt:
      "tilt-shift photography, miniature diorama effect, selective focus, exaggerated depth of field, birds eye view, toy town look",
    negative: "sharp full focus, wide depth of field, realistic scale",
    cfg: 7.0,
    steps: 32.0,
  },
  {
    id: "long-exposure",
    name: "Long Exposure",
    prompt:
      "long exposure photography, silky smooth water, light trails, motion blur, dreamy atmosphere",
    negative: "sharp water, frozen motion",
    cfg: 6.5,
    steps: 34.0,
  },
  {
    id: "macro",
    name: "Macro",
    prompt:
      "extreme macro photography, incredible detail, shallow depth of field, bokeh background",
    negative: "wide shot, blurred subject",
    cfg: 6.5,
    steps: 34.0,
  },
  {
    id: "aerial",
    name: "Aerial / Drone",
    prompt:
      "aerial drone photography, top-down view, geographic patterns, crisp daylight",
    negative: "ground level, low angle",
    cfg: 6.5,
    steps: 32.0,
  },
  {
    id: "polaroid",
    name: "Polaroid",
    prompt:
      "polaroid photo, instant film aesthetic, slightly faded colors, white frame edges, vintage snapshot",
    negative: "digital render, sharp modern look",
    cfg: 6.5,
    steps: 28.0,
  },
  {
    id: "product-shot",
    name: "Product Shot",
    prompt:
      "professional product photography, softbox lighting, seamless background, commercial advertising quality",
    negative: "amateur, cluttered background, harsh shadows, low quality",
    cfg: 6.0,
    steps: 32.0,
  },
  {
    id: "golden-hour",
    name: "Golden Hour",
    prompt:
      "golden hour lighting, warm amber sun, long shadows, glowing atmosphere",
    negative: "harsh midday light, blue tint",
    cfg: 6.5,
    steps: 32.0,
  },
  {
    id: "ukiyo-e",
    name: "Ukiyo-e",
    prompt:
      "ukiyo-e woodblock print, japanese woodcut, bold outlines, flat colors, wave patterns, washi paper",
    negative: "modern digital, photographic",
    cfg: 7.5,
    steps: 30.0,
  },
  {
    id: "art-nouveau",
    name: "Art Nouveau",
    prompt:
      "art nouveau, ornate flowing lines, decorative borders, botanical motifs, muted gold and green palette",
    negative: "minimalist, brutalist, photographic",
    cfg: 7.5,
    steps: 32.0,
  },
  {
    id: "art-deco",
    name: "Art Deco",
    prompt:
      "art deco, geometric patterns, gold and black palette, symmetrical elegance, 1920s style",
    negative: "organic curves, muted colors",
    cfg: 7.5,
    steps: 32.0,
  },
  {
    id: "baroque",
    name: "Baroque",
    prompt:
      "baroque painting, dramatic chiaroscuro, opulent detail, rich dark palette, classical grandeur",
    negative: "flat lighting, modern minimalism",
    cfg: 7.5,
    steps: 34.0,
  },
  {
    id: "impressionist",
    name: "Impressionist",
    prompt:
      "impressionist painting, visible brushstrokes, dappled light, plein air feel, soft focus details",
    negative: "sharp photorealism, hard edges",
    cfg: 7.5,
    steps: 32.0,
  },
  {
    id: "pointillism",
    name: "Pointillism",
    prompt:
      "pointillism, tiny distinct dots of color, seurat style, mosaic of paint dots",
    negative: "smooth blending, broad strokes",
    cfg: 7.5,
    steps: 32.0,
  },
  {
    id: "surrealism",
    name: "Surrealism",
    prompt:
      "surrealist painting, dreamlike impossible scene, daliesque melting forms, symbolic imagery",
    negative: "literal, mundane, realistic composition",
    cfg: 7.5,
    steps: 34.0,
  },
  {
    id: "pop-art",
    name: "Pop Art",
    prompt:
      "pop art, bold halftone dots, saturated primary colors, comic book style, warhol aesthetic",
    negative: "subtle palette, photorealism",
    cfg: 7.0,
    steps: 28.0,
  },
  {
    id: "anime",
    name: "Anime",
    prompt:
      "anime style, vibrant colors, cel shading, detailed lineart, studio quality key visual",
    negative: "photorealistic, 3d render, realistic skin texture",
    cfg: 7.0,
    steps: 30.0,
  },
  {
    id: "manga",
    name: "Manga",
    prompt:
      "manga panel, black and white ink, screentone shading, dynamic speed lines, japanese comic",
    negative: "color, painted, 3d",
    cfg: 7.5,
    steps: 30.0,
  },
  {
    id: "low-poly",
    name: "Low Poly",
    prompt:
      "low poly art, geometric faceted surfaces, flat shading, stylized 3d, game asset look",
    negative: "smooth high poly, realistic textures",
    cfg: 6.5,
    steps: 30.0,
  },
  {
    id: "voxel",
    name: "Voxel Art",
    prompt:
      "voxel art, blocky cube-based 3d, minecraft-like, chunky pixels, colorful",
    negative: "smooth surfaces, realistic lighting",
    cfg: 6.5,
    steps: 28.0,
  },
  {
    id: "isometric",
    name: "Isometric",
    prompt:
      "isometric illustration, 3/4 angle view, clean vector shapes, detailed environment",
    negative: "perspective view, flat 2d",
    cfg: 6.5,
    steps: 32.0,
  },
  {
    id: "flat-design",
    name: "Flat Design",
    prompt:
      "flat vector design, solid colors, no gradients, minimal shapes, modern UI illustration",
    negative: "texture, gradient, 3d depth",
    cfg: 6.5,
    steps: 26.0,
  },
  {
    id: "line-art",
    name: "Line Art",
    prompt:
      "clean line art, single stroke weight, white background, minimal, elegant outlines",
    negative: "shading, color, texture",
    cfg: 7.0,
    steps: 26.0,
  },
  {
    id: "sticker",
    name: "Sticker",
    prompt:
      "die-cut sticker, thick white border, glossy finish, cute illustration, vinyl look",
    negative: "photographic, complex background",
    cfg: 7.0,
    steps: 28.0,
  },
  {
    id: "tattoo",
    name: "Tattoo",
    prompt:
      "tattoo design, bold black ink, fine linework, stencil style, traditional flash art",
    negative: "color wash, blurry, photographic",
    cfg: 7.5,
    steps: 30.0,
  },
  {
    id: "graffiti",
    name: "Graffiti",
    prompt:
      "graffiti street art, spray paint texture, bold lettering, vivid splashes, urban wall",
    negative: "clean digital, gallery art",
    cfg: 7.5,
    steps: 30.0,
  },
  {
    id: "disco",
    name: "Disco",
    prompt:
      "disco aesthetic, glitter ball, neon dance floor, 70s retro nightclub, mirror tiles, groovy",
    negative: "modern club, muted colors",
    cfg: 7.0,
    steps: 30.0,
  },
  {
    id: "cyberpunk",
    name: "Cyberpunk",
    prompt:
      "cyberpunk, neon lights, rain-soaked streets, futuristic megacity, blade runner aesthetic",
    negative: "daylight, rural, medieval, low tech",
    cfg: 7.0,
    steps: 34.0,
  },
  {
    id: "vaporwave",
    name: "Vaporwave",
    prompt:
      "vaporwave, pastel pink and cyan, retro futurism, greek statues, grid sun, cassette tape nostalgia",
    negative: "realistic, dark, muted",
    cfg: 7.0,
    steps: 32.0,
  },
  {
    id: "synthwave",
    name: "Synthwave",
    prompt:
      "synthwave, retro 80s neon, chrome sun, grid perspective, purple and orange, outrun aesthetic",
    negative: "muted colors, natural lighting",
    cfg: 7.0,
    steps: 32.0,
  },
  {
    id: "steampunk",
    name: "Steampunk",
    prompt:
      "steampunk, brass gears, victorian machinery, copper pipes, goggles, sepia and bronze tones",
    negative: "modern technology, clean plastic",
    cfg: 7.0,
    steps: 34.0,
  },
  {
    id: "dieselpunk",
    name: "Dieselpunk",
    prompt:
      "dieselpunk, 1940s war machinery, riveted metal, greasy industrial, retro futurism with diesel engines",
    negative: "clean futuristic, victorian elegance",
    cfg: 7.0,
    steps: 34.0,
  },
  {
    id: "solargoth",
    name: "Solar Goth",
    prompt:
      "solarpunk, sustainable future, lush greenery, solar panels, optimistic architecture, sunlight",
    negative: "dystopian, dark, polluted",
    cfg: 7.0,
    steps: 34.0,
  },
  {
    id: "dark-fantasy",
    name: "Dark Fantasy",
    prompt:
      "dark fantasy, ominous atmosphere, gothic ruins, candlelight, intricate armor, moody",
    negative: "bright cheerful, cartoon",
    cfg: 7.0,
    steps: 36.0,
  },
  {
    id: "fantasy",
    name: "Epic Fantasy",
    prompt:
      "epic fantasy, magical atmosphere, sweeping vista, dramatic sky, painterly rendering, mythic scale",
    negative: "modern, mundane, plain background, contemporary",
    cfg: 7.0,
    steps: 36.0,
  },
  {
    id: "sci-fi",
    name: "Sci-Fi Concept",
    prompt:
      "sci-fi concept art, futuristic technology, alien landscapes, spaceship design, hard surface detail",
    negative: "fantasy magic, historical",
    cfg: 6.5,
    steps: 34.0,
  },
  {
    id: "3d-render",
    name: "3D Render",
    prompt:
      "3d render, octane render, subsurface scattering, ray traced reflections, depth of field, high poly",
    negative: "2d, flat, drawing, sketch, low poly",
    cfg: 5.5,
    steps: 36.0,
  },
  {
    id: "minimalist",
    name: "Minimalist",
    prompt:
      "minimalist, clean composition, generous negative space, muted palette, soft studio lighting",
    negative: "cluttered, busy, ornate, high detail, texture overload",
    cfg: 6.0,
    steps: 26.0,
  },
  {
    id: "brutalist",
    name: "Brutalist",
    prompt:
      "brutalist architecture, raw concrete, massive geometric forms, stark shadows, monumental scale",
    negative: "ornate, cozy, colorful",
    cfg: 6.5,
    steps: 32.0,
  },
  {
    id: "cyber-goth",
    name: "Cyber Goth",
    prompt:
      "cyber goth, dark futuristic fashion, neon accents, industrial textures, dramatic makeup",
    negative: "bright, pastel, mainstream fashion",
    cfg: 7.0,
    steps: 32.0,
  },
  {
    id: "glitch",
    name: "Glitch Art",
    prompt:
      "glitch art, digital distortion, rgb channel shift, scanlines, corrupted data aesthetic",
    negative: "clean image, smooth gradients",
    cfg: 6.5,
    steps: 26.0,
  },
  {
    id: "hdr",
    name: "HDR",
    prompt:
      "high dynamic range photography, extreme contrast, vivid saturated colors, glowing highlights",
    negative: "flat lighting, muted colors",
    cfg: 6.5,
    steps: 32.0,
  },
  {
    id: "double-exposure",
    name: "Double Exposure",
    prompt:
      "double exposure, silhouette merged with landscape, film photography effect, ethereal layering",
    negative: "single exposure, plain background",
    cfg: 7.0,
    steps: 32.0,
  },
  {
    id: "infrared",
    name: "Infrared",
    prompt:
      "infrared photography, surreal foliage glow, white pink vegetation, dreamy red-orange palette",
    negative: "natural colors, normal foliage",
    cfg: 6.5,
    steps: 32.0,
  },
  {
    id: "astrophotography",
    name: "Astrophotography",
    prompt:
      "astrophotography, deep space detail, star trails, milky way, long exposure sky, telescope clarity",
    negative: "flat night sky, city light pollution",
    cfg: 6.5,
    steps: 36.0,
  },
  {
    id: "bokeh",
    name: "Bokeh",
    prompt:
      "dreamy bokeh background, glowing circular out-of-focus lights, shallow depth of field, christmas lights feel",
    negative: "sharp busy background",
    cfg: 6.5,
    steps: 30.0,
  },
  {
    id: "gothic",
    name: "Gothic",
    prompt:
      "gothic art, pointed arches, dark cathedrals, candlelit gloom, ornate stained light, medieval mystique",
    negative: "modern, bright, cheerful",
    cfg: 7.5,
    steps: 34.0,
  },
  {
    id: "rococo",
    name: "Rococo",
    prompt: "rococo, ornate pastel elegance, gilded curves",
  },
  {
    id: "post-impressionist",
    name: "Post-Impressionist",
    prompt: "post-impressionist, bold color blocks, expressive form",
  },
  {
    id: "expressionism",
    name: "Expressionism",
    prompt: "expressionist, distorted emotion, bold color, gestural strokes",
  },
  {
    id: "abstract-expressionism",
    name: "Abstract Expressionism",
    prompt: "abstract expressionism, gestural color fields, action painting",
  },
  {
    id: "art-brut",
    name: "Art Brut",
    prompt: "art brut, raw naive marks, outsider art",
  },
  {
    id: "documentary",
    name: "Documentary",
    prompt: "documentary photography, candid realism, natural light",
  },
  {
    id: "editorial",
    name: "Editorial",
    prompt: "editorial photography, magazine quality, striking composition",
  },
  {
    id: "fashion",
    name: "Fashion",
    prompt: "fashion photography, high-end editorial, studio elegance",
  },
  {
    id: "architectural",
    name: "Architectural",
    prompt: "architectural photography, clean lines, geometric composition",
  },
  {
    id: "blue-hour",
    name: "Blue Hour",
    prompt: "blue hour, twilight blue tones, city lights",
  },
  {
    id: "cosmic-horror",
    name: "Cosmic Horror",
    prompt: "cosmic horror, vast unknowable dread, dark nebulae",
  },
  {
    id: "neon-noir",
    name: "Neon Noir",
    prompt: "neon noir, neon-lit night, wet streets, magenta cyan glow",
  },
  {
    id: "retro-futurism",
    name: "Retro-Futurism",
    prompt: "retro-futurism, 1950s sci-fi optimism, chrome and plastic",
  },
  {
    id: "mid-century-modern",
    name: "Mid-Century Modern",
    prompt: "mid-century modern, clean retro design, atomic age",
  },
  {
    id: "kawaii",
    name: "Kawaii",
    prompt: "kawaii, cute pastel, chibi charm",
  },
  {
    id: "dreamy",
    name: "Dreamy",
    prompt: "dreamy, soft haze, pastel glow",
  },
  {
    id: "ethereal",
    name: "Ethereal",
    prompt: "ethereal, translucent light, otherworldly",
  },
  {
    id: "moody",
    name: "Moody",
    prompt: "moody, dramatic shadows, deep contrast",
  },
  {
    id: "gritty",
    name: "Gritty",
    prompt: "gritty, raw texture, urban grime",
  },
  {
    id: "whimsical",
    name: "Whimsical",
    prompt: "whimsical, playful imagination, storybook charm",
  },
  {
    id: "elegant",
    name: "Elegant",
    prompt: "elegant, refined composition, graceful",
  },
  {
    id: "industrial",
    name: "Industrial",
    prompt: "industrial, raw mechanical, functional",
  },
  {
    id: "geometric",
    name: "Geometric",
    prompt: "geometric abstraction, precise shapes",
  },
  {
    id: "holographic",
    name: "Holographic",
    prompt: "holographic, iridescent rainbow sheen",
  },
  {
    id: "halftone",
    name: "Halftone",
    prompt: "halftone print, dotted shading, comic print",
  },
  {
    id: "comic-book",
    name: "Comic Book",
    prompt: "comic book art, bold ink lines, dynamic panels",
  },
  {
    id: "abstract",
    name: "Abstract",
    prompt: "abstract, non-representational forms",
  },
];

export interface Material {
  id: string;
  name: string;
  prompt: string;
}

export const MATERIALS: Material[] = [
  {
    id: "none",
    name: "No material",
    prompt: "",
  },
  {
    id: "chalk",
    name: "Chalk",
    prompt: "chalk drawing on dark paper",
  },
  {
    id: "pastel",
    name: "Soft Pastel",
    prompt: "soft pastel drawing, powdery texture",
  },
  {
    id: "oil-paint",
    name: "Oil Paint",
    prompt: "oil painting, thick visible brushstrokes",
  },
  {
    id: "watercolor",
    name: "Watercolor",
    prompt: "watercolor painting, soft washes, paper texture",
  },
  {
    id: "gouache",
    name: "Gouache",
    prompt: "gouache painting, flat matte color blocks",
  },
  {
    id: "acrylic",
    name: "Acrylic",
    prompt: "acrylic painting, bold opaque strokes",
  },
  {
    id: "pencil",
    name: "Pencil",
    prompt: "pencil drawing, graphite shading",
  },
  {
    id: "pen-ink",
    name: "Pen and Ink",
    prompt: "pen and ink drawing, fine hatching",
  },
  {
    id: "ink-wash",
    name: "Ink Wash",
    prompt: "sumi-e ink wash painting",
  },
  {
    id: "charcoal",
    name: "Charcoal",
    prompt: "charcoal sketch, smudged dark strokes",
  },
  {
    id: "marker",
    name: "Marker",
    prompt: "marker drawing, vibrant flat color",
  },
  {
    id: "crayon",
    name: "Crayon",
    prompt: "wax crayon drawing, waxy texture",
  },
  {
    id: "collage",
    name: "Collage",
    prompt: "paper collage, cut-out shapes",
  },
  {
    id: "papercut",
    name: "Papercut",
    prompt: "layered papercut art, intricate cut paper",
  },
  {
    id: "crochet",
    name: "Crochet",
    prompt: "crocheted fabric, yarn texture",
  },
  {
    id: "knitting",
    name: "Knitting",
    prompt: "knitted wool texture",
  },
  {
    id: "embroidery",
    name: "Embroidery",
    prompt: "embroidered fabric, thread texture",
  },
  {
    id: "quilting",
    name: "Quilting",
    prompt: "patchwork quilt, stitched fabric",
  },
  {
    id: "stained-glass",
    name: "Stained Glass",
    prompt: "stained glass artwork, leaded panels",
  },
  {
    id: "mosaic",
    name: "Mosaic",
    prompt: "mosaic tiles, grouted pieces",
  },
  {
    id: "origami",
    name: "Origami",
    prompt: "origami paper sculpture, folded paper",
  },
  {
    id: "linocut",
    name: "Linocut",
    prompt: "linocut print, bold carved blocks",
  },
  {
    id: "woodcut",
    name: "Woodcut",
    prompt: "woodcut print, carved grain",
  },
  {
    id: "etching",
    name: "Etching",
    prompt: "etching, fine engraved lines",
  },
  {
    id: "screen-print",
    name: "Screen Print",
    prompt: "screen print, flat spot colors",
  },
  {
    id: "scratchboard",
    name: "Scratchboard",
    prompt: "scratchboard art, white-on-black scratches",
  },
  {
    id: "pixel-art",
    name: "Pixel Art",
    prompt: "pixel art, low resolution",
  },
];

export const QUALITY_TAGS = "highly detailed, masterpiece, best quality, 8k";

export const EXAMPLE_PROMPTS: { group: string; items: string[] }[] = [
  {
    group: "Creative",
    items: [
      "Neon cyberpunk city at night, rain, reflections",
      "A lighthouse at dusk on a rocky coast, dramatic clouds",
      "Steampunk robot portrait, brass gears, dramatic light",
      "Colorful nebula over a lone astronaut, deep space",
      "A cozy coffee shop interior, isometric view",
      "Anime girl with flowing hair in a cherry blossom storm",
    ],
  },
  {
    group: "Architecture & Worlds",
    items: [
      "Brutalist concrete building at sunrise, long shadows",
      "Floating islands with waterfalls, fantasy sky",
      "Ancient roman temple ruins overgrown with vines",
      "A futuristic space station orbiting a gas giant",
      "Tiny village on a misty mountain slope, lanterns glowing",
      "Underwater city dome, bioluminescent coral",
    ],
  },
  {
    group: "Characters & Portrait",
    items: [
      "Cinematic portrait of an old fisherman, weathered skin",
      "A dragon in flight above a burning battlefield",
      "Sci-fi bounty hunter, full character sheet",
      "A fox spirit with nine tails in a bamboo forest",
      "Viking warrior in furs, snow storm background",
      "A friendly robot barista serving coffee",
    ],
  },
  {
    group: "Products & Design",
    items: [
      "Ceramic teapot on slate, minimalist product shot",
      "A mechanical keyboard made of brass and wood",
      "Designer sneaker floating, dynamic studio light",
      "A luxury watch with visible gears, macro shot",
      "Glass perfume bottle with gold accents, soft light",
      "A retro radio from the 1950s, pastel colors",
    ],
  },
];
