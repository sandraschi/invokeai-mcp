/**
 * Generation presets - the style/material library and example prompts.
 * Shared by the Generate page (tabs, batch, composed prompt).
 */

export interface StylePreset {
  id: string;
  name: string;
  prompt: string;
  negative: string;
  cfg: number;
  steps: number;
}

export const STYLES: StylePreset[] = [
  // Photography
  {
    id: "photorealistic",
    name: "Photorealistic",
    prompt:
      "photorealistic, ultra detailed, natural lighting, shot on 85mm f/1.4, shallow depth of field",
    negative: "cartoon, painting, illustration, 3d render, anime, sketch",
    cfg: 6.5,
    steps: 34,
  },
  {
    id: "cinematic",
    name: "Cinematic",
    prompt:
      "cinematic still, dramatic lighting, film grain, anamorphic lens flare, color graded, movie frame",
    negative: "flat lighting, amateur snapshot, low quality",
    cfg: 6.0,
    steps: 36,
  },
  {
    id: "film-noir",
    name: "Film Noir",
    prompt:
      "film noir, high contrast, hard shadows, black and white, venetian blinds, 1940s detective mood",
    negative: "color, bright, cheerful, modern lighting",
    cfg: 7.0,
    steps: 30,
  },
  {
    id: "tilt-shift",
    name: "Tilt Shift",
    prompt:
      "tilt-shift photography, miniature diorama effect, selective focus, exaggerated depth of field, birds eye view, toy town look",
    negative: "sharp full focus, wide depth of field, realistic scale",
    cfg: 7.0,
    steps: 32,
  },
  {
    id: "long-exposure",
    name: "Long Exposure",
    prompt:
      "long exposure photography, silky smooth water, light trails, motion blur, dreamy atmosphere",
    negative: "sharp water, frozen motion",
    cfg: 6.5,
    steps: 34,
  },
  {
    id: "macro",
    name: "Macro",
    prompt:
      "extreme macro photography, incredible detail, shallow depth of field, bokeh background",
    negative: "wide shot, blurred subject",
    cfg: 6.5,
    steps: 34,
  },
  {
    id: "aerial",
    name: "Aerial / Drone",
    prompt:
      "aerial drone photography, top-down view, geographic patterns, crisp daylight",
    negative: "ground level, low angle",
    cfg: 6.5,
    steps: 32,
  },
  {
    id: "polaroid",
    name: "Polaroid",
    prompt:
      "polaroid photo, instant film aesthetic, slightly faded colors, white frame edges, vintage snapshot",
    negative: "digital render, sharp modern look",
    cfg: 6.5,
    steps: 28,
  },
  {
    id: "product-shot",
    name: "Product Shot",
    prompt:
      "professional product photography, softbox lighting, seamless background, commercial advertising quality",
    negative: "amateur, cluttered background, harsh shadows, low quality",
    cfg: 6.0,
    steps: 32,
  },
  {
    id: "golden-hour",
    name: "Golden Hour",
    prompt:
      "golden hour lighting, warm amber sun, long shadows, glowing atmosphere",
    negative: "harsh midday light, blue tint",
    cfg: 6.5,
    steps: 32,
  },

  // Painting
  {
    id: "watercolor",
    name: "Watercolor",
    prompt:
      "watercolor painting, soft washes, textured paper, artistic, loose expressive brushwork",
    negative: "photograph, digital art, sharp vector edges",
    cfg: 7.5,
    steps: 28,
  },
  {
    id: "oil-painting",
    name: "Oil Painting",
    prompt:
      "oil painting, impasto brushstrokes, classical technique, rich colors, visible canvas texture",
    negative: "photograph, digital smooth gradient, pixelated",
    cfg: 7.5,
    steps: 30,
  },
  {
    id: "acrylic",
    name: "Acrylic",
    prompt:
      "acrylic painting, bold flat color blocks, modern canvas art, textured strokes",
    negative: "oil impasto, watercolor wash",
    cfg: 7.5,
    steps: 28,
  },
  {
    id: "gouache",
    name: "Gouache",
    prompt:
      "gouache painting, matte finish, opaque layers, flat illustration style",
    negative: "glossy, transparent watercolor",
    cfg: 7.5,
    steps: 28,
  },
  {
    id: "pastel",
    name: "Pastel Drawing",
    prompt:
      "soft pastel drawing, chalk texture, muted powdery colors, gentle strokes",
    negative: "oil paint, sharp digital lines",
    cfg: 7.5,
    steps: 28,
  },
  {
    id: "pencil-sketch",
    name: "Pencil Sketch",
    prompt:
      "detailed pencil sketch, graphite shading, hatching, paper texture, monochrome",
    negative: "color, painted, digital render",
    cfg: 7.5,
    steps: 26,
  },
  {
    id: "charcoal",
    name: "Charcoal",
    prompt:
      "charcoal drawing, dramatic smudged shading, high contrast, gritty paper texture",
    negative: "clean digital lines, color",
    cfg: 7.5,
    steps: 26,
  },
  {
    id: "ukiyo-e",
    name: "Ukiyo-e",
    prompt:
      "ukiyo-e woodblock print, japanese woodcut, bold outlines, flat colors, wave patterns, washi paper",
    negative: "modern digital, photographic",
    cfg: 7.5,
    steps: 30,
  },
  {
    id: "art-nouveau",
    name: "Art Nouveau",
    prompt:
      "art nouveau, ornate flowing lines, decorative borders, botanical motifs, muted gold and green palette",
    negative: "minimalist, brutalist, photographic",
    cfg: 7.5,
    steps: 32,
  },
  {
    id: "art-deco",
    name: "Art Deco",
    prompt:
      "art deco, geometric patterns, gold and black palette, symmetrical elegance, 1920s style",
    negative: "organic curves, muted colors",
    cfg: 7.5,
    steps: 32,
  },
  {
    id: "baroque",
    name: "Baroque",
    prompt:
      "baroque painting, dramatic chiaroscuro, opulent detail, rich dark palette, classical grandeur",
    negative: "flat lighting, modern minimalism",
    cfg: 7.5,
    steps: 34,
  },
  {
    id: "impressionist",
    name: "Impressionist",
    prompt:
      "impressionist painting, visible brushstrokes, dappled light, plein air feel, soft focus details",
    negative: "sharp photorealism, hard edges",
    cfg: 7.5,
    steps: 32,
  },
  {
    id: "pointillism",
    name: "Pointillism",
    prompt:
      "pointillism, tiny distinct dots of color, seurat style, mosaic of paint dots",
    negative: "smooth blending, broad strokes",
    cfg: 7.5,
    steps: 32,
  },
  {
    id: "stained-glass",
    name: "Stained Glass",
    prompt:
      "stained glass window, colorful glass panels, lead lines, glowing backlight, intricate mosaic",
    negative: "painted, blurry, photographic",
    cfg: 7.5,
    steps: 32,
  },
  {
    id: "fresco",
    name: "Fresco",
    prompt:
      "fresco mural, ancient wall painting, chalky texture, muted earthy pigments, historical",
    negative: "glossy, digital smoothness",
    cfg: 7.5,
    steps: 32,
  },
  {
    id: "surrealism",
    name: "Surrealism",
    prompt:
      "surrealist painting, dreamlike impossible scene, daliesque melting forms, symbolic imagery",
    negative: "literal, mundane, realistic composition",
    cfg: 7.5,
    steps: 34,
  },
  {
    id: "pop-art",
    name: "Pop Art",
    prompt:
      "pop art, bold halftone dots, saturated primary colors, comic book style, warhol aesthetic",
    negative: "subtle palette, photorealism",
    cfg: 7.0,
    steps: 28,
  },

  // Illustration & Digital
  {
    id: "anime",
    name: "Anime",
    prompt:
      "anime style, vibrant colors, cel shading, detailed lineart, studio quality key visual",
    negative: "photorealistic, 3d render, realistic skin texture",
    cfg: 7.0,
    steps: 30,
  },
  {
    id: "manga",
    name: "Manga",
    prompt:
      "manga panel, black and white ink, screentone shading, dynamic speed lines, japanese comic",
    negative: "color, painted, 3d",
    cfg: 7.5,
    steps: 30,
  },
  {
    id: "pixel-art",
    name: "Pixel Art",
    prompt:
      "pixel art, 16-bit, crisp pixels, retro game aesthetic, limited color palette",
    negative: "smooth gradients, blurry, realistic detail",
    cfg: 6.5,
    steps: 24,
  },
  {
    id: "low-poly",
    name: "Low Poly",
    prompt:
      "low poly art, geometric faceted surfaces, flat shading, stylized 3d, game asset look",
    negative: "smooth high poly, realistic textures",
    cfg: 6.5,
    steps: 30,
  },
  {
    id: "voxel",
    name: "Voxel Art",
    prompt:
      "voxel art, blocky cube-based 3d, minecraft-like, chunky pixels, colorful",
    negative: "smooth surfaces, realistic lighting",
    cfg: 6.5,
    steps: 28,
  },
  {
    id: "papercraft",
    name: "Papercraft",
    prompt:
      "papercraft, layered cut paper, origami folds, 3d paper diorama, visible paper edges",
    negative: "photograph, digital painting",
    cfg: 7.0,
    steps: 30,
  },
  {
    id: "claymation",
    name: "Claymation",
    prompt:
      "claymation, stop motion clay figures, fingerprint texture, plasticine, handmade charm",
    negative: "smooth cgi, digital render",
    cfg: 7.0,
    steps: 30,
  },
  {
    id: "lego",
    name: "Lego Brick",
    prompt:
      "lego minifigure style, plastic brick construction, studs visible, toy diorama, vibrant plastic",
    negative: "realistic skin, fabric texture",
    cfg: 7.0,
    steps: 30,
  },
  {
    id: "isometric",
    name: "Isometric",
    prompt:
      "isometric illustration, 3/4 angle view, clean vector shapes, detailed environment",
    negative: "perspective view, flat 2d",
    cfg: 6.5,
    steps: 32,
  },
  {
    id: "flat-design",
    name: "Flat Design",
    prompt:
      "flat vector design, solid colors, no gradients, minimal shapes, modern UI illustration",
    negative: "texture, gradient, 3d depth",
    cfg: 6.5,
    steps: 26,
  },
  {
    id: "line-art",
    name: "Line Art",
    prompt:
      "clean line art, single stroke weight, white background, minimal, elegant outlines",
    negative: "shading, color, texture",
    cfg: 7.0,
    steps: 26,
  },
  {
    id: "sticker",
    name: "Sticker",
    prompt:
      "die-cut sticker, thick white border, glossy finish, cute illustration, vinyl look",
    negative: "photographic, complex background",
    cfg: 7.0,
    steps: 28,
  },
  {
    id: "tattoo",
    name: "Tattoo",
    prompt:
      "tattoo design, bold black ink, fine linework, stencil style, traditional flash art",
    negative: "color wash, blurry, photographic",
    cfg: 7.5,
    steps: 30,
  },
  {
    id: "graffiti",
    name: "Graffiti",
    prompt:
      "graffiti street art, spray paint texture, bold lettering, vivid splashes, urban wall",
    negative: "clean digital, gallery art",
    cfg: 7.5,
    steps: 30,
  },
  {
    id: "super-mario",
    name: "Super Mario",
    prompt:
      "super mario world style, bright cheerful platformer, blocky pipes, cartoon clouds, 90s nintendo art",
    negative: "realistic, dark, gritty",
    cfg: 6.5,
    steps: 28,
  },
  {
    id: "disco",
    name: "Disco",
    prompt:
      "disco aesthetic, glitter ball, neon dance floor, 70s retro nightclub, mirror tiles, groovy",
    negative: "modern club, muted colors",
    cfg: 7.0,
    steps: 30,
  },

  // Modern / Digital Art
  {
    id: "cyberpunk",
    name: "Cyberpunk",
    prompt:
      "cyberpunk, neon lights, rain-soaked streets, futuristic megacity, blade runner aesthetic",
    negative: "daylight, rural, medieval, low tech",
    cfg: 7.0,
    steps: 34,
  },
  {
    id: "vaporwave",
    name: "Vaporwave",
    prompt:
      "vaporwave, pastel pink and cyan, retro futurism, greek statues, grid sun, cassette tape nostalgia",
    negative: "realistic, dark, muted",
    cfg: 7.0,
    steps: 32,
  },
  {
    id: "synthwave",
    name: "Synthwave",
    prompt:
      "synthwave, retro 80s neon, chrome sun, grid perspective, purple and orange, outrun aesthetic",
    negative: "muted colors, natural lighting",
    cfg: 7.0,
    steps: 32,
  },
  {
    id: "steampunk",
    name: "Steampunk",
    prompt:
      "steampunk, brass gears, victorian machinery, copper pipes, goggles, sepia and bronze tones",
    negative: "modern technology, clean plastic",
    cfg: 7.0,
    steps: 34,
  },
  {
    id: "dieselpunk",
    name: "Dieselpunk",
    prompt:
      "dieselpunk, 1940s war machinery, riveted metal, greasy industrial, retro futurism with diesel engines",
    negative: "clean futuristic, victorian elegance",
    cfg: 7.0,
    steps: 34,
  },
  {
    id: "solargoth",
    name: "Solar Goth",
    prompt:
      "solarpunk, sustainable future, lush greenery, solar panels, optimistic architecture, sunlight",
    negative: "dystopian, dark, polluted",
    cfg: 7.0,
    steps: 34,
  },
  {
    id: "dark-fantasy",
    name: "Dark Fantasy",
    prompt:
      "dark fantasy, ominous atmosphere, gothic ruins, candlelight, intricate armor, moody",
    negative: "bright cheerful, cartoon",
    cfg: 7.0,
    steps: 36,
  },
  {
    id: "fantasy",
    name: "Epic Fantasy",
    prompt:
      "epic fantasy, magical atmosphere, sweeping vista, dramatic sky, painterly rendering, mythic scale",
    negative: "modern, mundane, plain background, contemporary",
    cfg: 7.0,
    steps: 36,
  },
  {
    id: "sci-fi",
    name: "Sci-Fi Concept",
    prompt:
      "sci-fi concept art, futuristic technology, alien landscapes, spaceship design, hard surface detail",
    negative: "fantasy magic, historical",
    cfg: 6.5,
    steps: 34,
  },
  {
    id: "3d-render",
    name: "3D Render",
    prompt:
      "3d render, octane render, subsurface scattering, ray traced reflections, depth of field, high poly",
    negative: "2d, flat, drawing, sketch, low poly",
    cfg: 5.5,
    steps: 36,
  },
  {
    id: "blender-cycles",
    name: "Blender Cycles",
    prompt:
      "blender cycles render, physically based lighting, realistic materials, pristine studio setup",
    negative: "stylized, painterly",
    cfg: 5.5,
    steps: 36,
  },
  {
    id: "unreal-engine",
    name: "Unreal Engine",
    prompt:
      "unreal engine 5 render, nanite detail, lumen global illumination, cinematic post processing, game still",
    negative: "2d, flat illustration",
    cfg: 6.0,
    steps: 34,
  },
  {
    id: "minimalist",
    name: "Minimalist",
    prompt:
      "minimalist, clean composition, generous negative space, muted palette, soft studio lighting",
    negative: "cluttered, busy, ornate, high detail, texture overload",
    cfg: 6.0,
    steps: 26,
  },
  {
    id: "brutalist",
    name: "Brutalist",
    prompt:
      "brutalist architecture, raw concrete, massive geometric forms, stark shadows, monumental scale",
    negative: "ornate, cozy, colorful",
    cfg: 6.5,
    steps: 32,
  },
  {
    id: "cyber-goth",
    name: "Cyber Goth",
    prompt:
      "cyber goth, dark futuristic fashion, neon accents, industrial textures, dramatic makeup",
    negative: "bright, pastel, mainstream fashion",
    cfg: 7.0,
    steps: 32,
  },
  {
    id: "glitch",
    name: "Glitch Art",
    prompt:
      "glitch art, digital distortion, rgb channel shift, scanlines, corrupted data aesthetic",
    negative: "clean image, smooth gradients",
    cfg: 6.5,
    steps: 26,
  },
  {
    id: "hdr",
    name: "HDR",
    prompt:
      "high dynamic range photography, extreme contrast, vivid saturated colors, glowing highlights",
    negative: "flat lighting, muted colors",
    cfg: 6.5,
    steps: 32,
  },
  {
    id: "double-exposure",
    name: "Double Exposure",
    prompt:
      "double exposure, silhouette merged with landscape, film photography effect, ethereal layering",
    negative: "single exposure, plain background",
    cfg: 7.0,
    steps: 32,
  },
  {
    id: "infrared",
    name: "Infrared",
    prompt:
      "infrared photography, surreal foliage glow, white pink vegetation, dreamy red-orange palette",
    negative: "natural colors, normal foliage",
    cfg: 6.5,
    steps: 32,
  },
  {
    id: "astrophotography",
    name: "Astrophotography",
    prompt:
      "astrophotography, deep space detail, star trails, milky way, long exposure sky, telescope clarity",
    negative: "flat night sky, city light pollution",
    cfg: 6.5,
    steps: 36,
  },
  {
    id: "bokeh",
    name: "Bokeh",
    prompt:
      "dreamy bokeh background, glowing circular out-of-focus lights, shallow depth of field, christmas lights feel",
    negative: "sharp busy background",
    cfg: 6.5,
    steps: 30,
  },
  {
    id: "van-gogh",
    name: "Van Gogh",
    prompt:
      "van gogh style, swirling textured brushstrokes, vivid impasto, expressive color, post-impressionist",
    negative: "smooth flat painting",
    cfg: 7.5,
    steps: 32,
  },
  {
    id: "picasso",
    name: "Picasso / Cubism",
    prompt:
      "cubist painting, fragmented geometric forms, multiple perspectives, picasso style, abstract",
    negative: "realistic proportions, single viewpoint",
    cfg: 7.5,
    steps: 30,
  },
  {
    id: "monet",
    name: "Monet",
    prompt:
      "monet impressionist style, soft water reflections, pastel light, garden scenes, loose strokes",
    negative: "sharp detail, dark palette",
    cfg: 7.5,
    steps: 32,
  },
  {
    id: "banksy",
    name: "Banksy / Stencil",
    prompt:
      "stencil street art, banksy style, stark silhouettes, political satire, sprayed texture, limited palette",
    negative: "detailed realism, colorful",
    cfg: 7.0,
    steps: 28,
  },
  {
    id: "gothic",
    name: "Gothic",
    prompt:
      "gothic art, pointed arches, dark cathedrals, candlelit gloom, ornate stained light, medieval mystique",
    negative: "modern, bright, cheerful",
    cfg: 7.5,
    steps: 34,
  },
];

export interface Material {
  id: string;
  name: string;
  prompt: string;
}

export const MATERIALS: Material[] = [
  { id: "none", name: "No material", prompt: "" },
  { id: "metal", name: "Brushed metal", prompt: "made of brushed aluminum" },
  { id: "gold", name: "Gold", prompt: "made of polished gold" },
  { id: "silver", name: "Silver", prompt: "made of polished silver" },
  { id: "glass", name: "Glass", prompt: "made of transparent glass" },
  { id: "wood", name: "Dark oak wood", prompt: "made of dark oak wood" },
  { id: "stone", name: "Carved stone", prompt: "made of carved stone" },
  {
    id: "marble",
    name: "White marble",
    prompt: "made of polished white marble",
  },
  { id: "fabric", name: "Soft fabric", prompt: "made of soft flowing fabric" },
  { id: "leather", name: "Brown leather", prompt: "made of brown leather" },
  { id: "ceramic", name: "Glazed ceramic", prompt: "made of glazed ceramic" },
  { id: "concrete", name: "Raw concrete", prompt: "made of raw concrete" },
  { id: "plastic", name: "Glossy plastic", prompt: "made of glossy plastic" },
  { id: "chrome", name: "Chrome", prompt: "made of mirror-polished chrome" },
  { id: "copper", name: "Copper", prompt: "made of aged copper" },
  {
    id: "obsidian",
    name: "Obsidian",
    prompt: "made of black volcanic obsidian",
  },
  { id: "crystal", name: "Crystal", prompt: "made of faceted crystal" },
  { id: "jade", name: "Jade", prompt: "made of carved green jade" },
  { id: "rubber", name: "Rubber", prompt: "made of matte black rubber" },
  { id: "carbon", name: "Carbon fiber", prompt: "made of woven carbon fiber" },
  { id: "paper", name: "Paper", prompt: "made of folded paper" },
  { id: "bone", name: "Bone / Ivory", prompt: "made of carved bone" },
  { id: "bronze", name: "Bronze", prompt: "made of weathered bronze" },
  { id: "titanium", name: "Titanium", prompt: "made of brushed titanium" },
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
