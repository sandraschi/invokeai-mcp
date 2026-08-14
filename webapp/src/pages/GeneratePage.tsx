import {
  CheckSquare,
  Copy,
  Dices,
  ExternalLink,
  ImagePlus,
  Loader2,
  RefreshCw,
  Send,
  Sparkles,
  Square,
  Wand2,
} from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import { PageHeader, SectionCard, Spinner } from "../components/ui";
import { apiGet, apiPost } from "../lib/api";
import {
  EXAMPLE_PROMPTS,
  MATERIALS,
  QUALITY_TAGS,
  STYLES as STYLES_CATALOG,
} from "../lib/presets";
import { useHealthStore } from "../store/health";
import { useLlmStore } from "../store/llm";

interface ModelOption {
  key: string;
  name: string;
  base: string;
  type: string;
}

interface GenerateResponse {
  success: boolean;
  queue_item_id?: number;
  message?: string;
  error?: string;
}

interface QueueResult {
  success: boolean;
  data?: {
    status: string;
    outputs?: { image_name: string; url?: string }[];
  };
  message?: string;
}

type ModeId =
  | "txt2img"
  | "img2img"
  | "inpaint"
  | "outpaint"
  | "upscale"
  | "controlnet"
  | "ipadapter"
  | "seamless";

interface ModeDef {
  id: ModeId;
  label: string;
  hint: string;
  needsPrompt: boolean;
  needsImage: boolean;
  needsMask: boolean;
  uploadLabel: string;
}

const MODES: ModeDef[] = [
  {
    id: "txt2img",
    label: "Text to Image",
    hint: "Prompt to fresh image",
    needsPrompt: true,
    needsImage: false,
    needsMask: false,
    uploadLabel: "",
  },
  {
    id: "img2img",
    label: "Image to Image",
    hint: "Transform an existing image",
    needsPrompt: true,
    needsImage: true,
    needsMask: false,
    uploadLabel: "Source image",
  },
  {
    id: "inpaint",
    label: "Inpaint",
    hint: "Regenerate a masked region",
    needsPrompt: true,
    needsImage: true,
    needsMask: true,
    uploadLabel: "Source image",
  },
  {
    id: "outpaint",
    label: "Outpaint",
    hint: "Extend the canvas beyond the edges",
    needsPrompt: true,
    needsImage: true,
    needsMask: false,
    uploadLabel: "Image to extend",
  },
  {
    id: "upscale",
    label: "Upscale",
    hint: "RealESRGAN 4x upscale",
    needsPrompt: false,
    needsImage: true,
    needsMask: false,
    uploadLabel: "Image to upscale",
  },
  {
    id: "controlnet",
    label: "ControlNet",
    hint: "Canny edge guided generation",
    needsPrompt: true,
    needsImage: true,
    needsMask: false,
    uploadLabel: "Control image (edges)",
  },
  {
    id: "ipadapter",
    label: "IP-Adapter",
    hint: "Style transfer from a reference",
    needsPrompt: true,
    needsImage: true,
    needsMask: false,
    uploadLabel: "Reference image",
  },
  {
    id: "seamless",
    label: "Seamless",
    hint: "Tileable textures",
    needsPrompt: true,
    needsImage: false,
    needsMask: false,
    uploadLabel: "",
  },
];

const HISTORY_KEY = "invokeai-mcp-recent-prompts";
const MAX_HISTORY = 8;
const MAX_BATCH = 60;

interface BatchItem {
  itemId: number;
  label: string;
  status:
    | "pending"
    | "in_progress"
    | "completed"
    | "failed"
    | "canceled"
    | "unknown";
}

export default function GeneratePage() {
  const configured = useHealthStore((s) => s.configured);
  const { selectedProvider, selectedModel } = useLlmStore();
  const [styles, setStyles] = useState(STYLES_CATALOG);
  useEffect(() => {
    apiGet<{
      styles?: {
        id: string;
        name: string;
        prompt: string;
        negative?: string;
        cfg?: number | null;
        steps?: number | null;
      }[];
    }>("/invokeai/styles")
      .then((d) => {
        if (d.styles?.length) setStyles(d.styles as typeof STYLES_CATALOG);
      })
      .catch(() => {
        /* backend offline - bundled catalog */
      });
  }, []);
  const [models, setModels] = useState<ModelOption[]>([]);
  const [controlModels, setControlModels] = useState<ModelOption[]>([]);
  const [ipModels, setIpModels] = useState<ModelOption[]>([]);
  const [modelKey, setModelKey] = useState("");
  const [controlModelKey, setControlModelKey] = useState("");
  const [ipModelKey, setIpModelKey] = useState("");
  const [mode, setMode] = useState<ModeId>("txt2img");
  const [prompt, setPrompt] = useState("");
  const [negative, setNegative] = useState("");
  const [styleFilter, setStyleFilter] = useState("");
  const [selectedStyles, setSelectedStyles] = useState<Set<string>>(
    new Set(["photorealistic"]),
  );
  const [selectedMaterials, setSelectedMaterials] = useState<Set<string>>(
    new Set(),
  );
  const [applyStyleSettings, setApplyStyleSettings] = useState(true);
  const [imageName, setImageName] = useState("");
  const [maskImageName, setMaskImageName] = useState("");
  const [controlImageName, setControlImageName] = useState("");
  const [ipImageName, setIpImageName] = useState("");
  const [controlWeight, setControlWeight] = useState(0.8);
  const [cannyLow, setCannyLow] = useState(100);
  const [cannyHigh, setCannyHigh] = useState(200);
  const [ipWeight, setIpWeight] = useState(0.7);
  const [seamlessX, setSeamlessX] = useState(true);
  const [seamlessY, setSeamlessY] = useState(true);
  const [outLeft, setOutLeft] = useState(0);
  const [outRight, setOutRight] = useState(0);
  const [outTop, setOutTop] = useState(0);
  const [outBottom, setOutBottom] = useState(0);
  const [width, setWidth] = useState(1024);
  const [height, setHeight] = useState(1024);
  const [steps, setSteps] = useState(35);
  const [cfg, setCfg] = useState(5);
  const [scheduler, setScheduler] = useState("dpmpp_2m_sde");
  const [seed, setSeed] = useState("");
  const [strength, setStrength] = useState(0.75);
  const [history, setHistory] = useState<string[]>(() => {
    try {
      return JSON.parse(localStorage.getItem(HISTORY_KEY) ?? "[]") as string[];
    } catch {
      return [];
    }
  });
  const [busy, setBusy] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [refining, setRefining] = useState(false);
  const [outputs, setOutputs] = useState<string[]>([]);
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");
  const [batch, setBatch] = useState<BatchItem[]>([]);
  const [batchTotal, setBatchTotal] = useState(0);
  const pollTimer = useRef<ReturnType<typeof setInterval> | null>(null);

  const modeDef = MODES.find((m) => m.id === mode) ?? MODES[0];
  const primaryStyle = styles.find((s) => selectedStyles.has(s.id)) ?? null;
  const primaryMaterial =
    MATERIALS.find((m) => selectedMaterials.has(m.id) && m.id !== "none") ??
    null;

  const composedPrompt = [
    prompt,
    primaryStyle?.prompt,
    primaryMaterial?.prompt,
    QUALITY_TAGS,
  ]
    .filter((p): p is string => !!p && p.trim().length > 0)
    .join(", ");

  const [painters, setPainters] = useState<
    { id: string; name: string; prompt: string }[]
  >([]);
  const [selectedPainters, setSelectedPainters] = useState<Set<string>>(
    new Set(),
  );
  const [painterFilter, setPainterFilter] = useState("");
  useEffect(() => {
    apiGet<{ artists?: { id: string; name: string; prompt: string }[] }>(
      "/invokeai/artists",
    )
      .then((d) => setPainters(d.artists ?? []))
      .catch(() => setPainters([]));
  }, []);

  const batchCount =
    (selectedStyles.size || 1) *
    (selectedMaterials.size || 1) *
    (selectedPainters.size || 1);
  const doneCount = batch.filter((b) =>
    ["completed", "failed", "canceled"].includes(b.status),
  ).length;
  const batchPercent =
    batchTotal > 0 ? Math.round((doneCount / batchTotal) * 100) : 0;
  const batchRunning = batch.length > 0 && doneCount < batchTotal;

  const visibleStyles = styles.filter((s) =>
    s.name.toLowerCase().includes(styleFilter.toLowerCase()),
  );
  const visiblePainters = painters.filter((p) =>
    p.name.toLowerCase().includes(painterFilter.toLowerCase()),
  );

  const loadModels = useCallback(async () => {
    try {
      const r = await fetch("/api/invokeai/models");
      if (r.ok) {
        const j = (await r.json()) as { models?: ModelOption[] };
        setModels((j.models ?? []).filter((m) => m.type === "main"));
        setControlModels(
          (j.models ?? []).filter((m) => m.type === "controlnet"),
        );
        setIpModels((j.models ?? []).filter((m) => m.type === "ip_adapter"));
      }
    } catch {
      /* degraded */
    }
  }, []);

  useEffect(() => {
    loadModels();
  }, [loadModels]);

  useEffect(() => {
    return () => {
      if (pollTimer.current) clearInterval(pollTimer.current);
    };
  }, []);

  const rememberPrompt = (p: string) => {
    const next = [p, ...history.filter((h) => h !== p)].slice(0, MAX_HISTORY);
    setHistory(next);
    localStorage.setItem(HISTORY_KEY, JSON.stringify(next));
  };

  const uploadFile = async (file: File): Promise<string> => {
    setUploading(true);
    setError("");
    try {
      const fd = new FormData();
      fd.append("file", file);
      const r = await fetch("/api/invokeai/upload", {
        method: "POST",
        body: fd,
      });
      if (!r.ok) throw new Error(`upload HTTP ${r.status}`);
      const res = (await r.json()) as {
        success: boolean;
        data?: { image_name?: string; image?: { image_name?: string } };
      };
      const name = res.data?.image_name ?? res.data?.image?.image_name;
      if (!name) throw new Error("upload returned no image name");
      setNotice(`Uploaded ${name.slice(0, 20)}...`);
      return name;
    } catch (e) {
      setError(e instanceof Error ? e.message : "upload failed");
      throw e;
    } finally {
      setUploading(false);
    }
  };

  const padImageForOutpaint = async (
    source: string,
    l: number,
    r: number,
    t: number,
    b: number,
  ) => {
    const img = new Image();
    img.src = `/api/invokeai/image/${source}`;
    await new Promise((res, rej) => {
      img.onload = res;
      img.onerror = rej;
    });
    const canvas = document.createElement("canvas");
    canvas.width = img.width + l + r;
    canvas.height = img.height + t + b;
    const ctx = canvas.getContext("2d");
    if (!ctx) throw new Error("canvas unavailable");
    ctx.fillStyle = "#000000";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(img, l, t);
    const paddedBlob = await new Promise<Blob | null>((res) =>
      canvas.toBlob(res, "image/png"),
    );
    if (!paddedBlob) throw new Error("pad failed");

    const maskCanvas = document.createElement("canvas");
    maskCanvas.width = canvas.width;
    maskCanvas.height = canvas.height;
    const mctx = maskCanvas.getContext("2d");
    if (!mctx) throw new Error("canvas unavailable");
    mctx.fillStyle = "#000000";
    mctx.fillRect(0, 0, maskCanvas.width, maskCanvas.height);
    mctx.fillStyle = "#FFFFFF";
    mctx.fillRect(0, 0, maskCanvas.width, t);
    mctx.fillRect(0, maskCanvas.height - b, maskCanvas.width, b);
    mctx.fillRect(0, 0, l, maskCanvas.height);
    mctx.fillRect(maskCanvas.width - r, 0, r, maskCanvas.height);
    const maskBlob = await new Promise<Blob | null>((res) =>
      maskCanvas.toBlob(res, "image/png"),
    );
    if (!maskBlob) throw new Error("mask failed");

    const paddedName = await uploadFile(
      new File([paddedBlob], "outpaint-padded.png", { type: "image/png" }),
    );
    const maskName = await uploadFile(
      new File([maskBlob], "outpaint-mask.png", { type: "image/png" }),
    );
    return { paddedName, maskName };
  };

  const enqueueOne = async (
    opts: Record<string, unknown>,
  ): Promise<number | undefined> => {
    const res = await apiPost<GenerateResponse>("/invokeai/generate", opts);
    return res.queue_item_id;
  };

  const baseParams = () => ({
    model_key: modelKey || null,
    width,
    height,
    steps,
    cfg_scale: cfg,
    scheduler,
    seed: seed ? Number(seed) : null,
  });

  const buildSinglePayload = async () => {
    switch (mode) {
      case "img2img":
        return {
          operation: "img2img",
          prompt: composedPrompt,
          negative_prompt: negative || null,
          image_name: imageName,
          strength,
          ...baseParams(),
        };
      case "inpaint":
        return {
          operation: "inpaint",
          prompt: composedPrompt,
          negative_prompt: negative || null,
          image_name: imageName,
          mask_image_name: maskImageName,
          strength,
          ...baseParams(),
        };
      case "outpaint": {
        if (!(outLeft || outRight || outTop || outBottom)) {
          throw new Error("Set at least one expansion direction (pixels).");
        }
        const { paddedName, maskName } = await padImageForOutpaint(
          imageName,
          outLeft,
          outRight,
          outTop,
          outBottom,
        );
        return {
          operation: "inpaint",
          prompt: composedPrompt,
          negative_prompt: negative || null,
          image_name: paddedName,
          mask_image_name: maskName,
          strength: 0.85,
          ...baseParams(),
        };
      }
      case "upscale":
        return { operation: "upscale", image_name: imageName };
      case "controlnet": {
        const cm =
          controlModels.find((m) => m.key === controlModelKey) ??
          controlModels[0];
        if (!cm)
          throw new Error(
            "No ControlNet model installed. Install one below first.",
          );
        return {
          operation: "txt2img",
          prompt: composedPrompt,
          negative_prompt: negative || null,
          control_image_name: controlImageName,
          control_model: cm,
          control_weight: controlWeight,
          canny_low: cannyLow,
          canny_high: cannyHigh,
          ...baseParams(),
        };
      }
      case "ipadapter": {
        const im = ipModels.find((m) => m.key === ipModelKey) ?? ipModels[0];
        if (!im)
          throw new Error(
            "No IP-Adapter model installed. Install one below first.",
          );
        return {
          operation: "txt2img",
          prompt: composedPrompt,
          negative_prompt: negative || null,
          ip_image_name: ipImageName,
          ip_model: im,
          ip_weight: ipWeight,
          ...baseParams(),
        };
      }
      case "seamless":
        return {
          operation: "txt2img",
          prompt: composedPrompt,
          negative_prompt: negative || null,
          seamless_x: seamlessX,
          seamless_y: seamlessY,
          ...baseParams(),
        };
      default:
        return {
          operation: "txt2img",
          prompt: composedPrompt,
          negative_prompt: negative || null,
          ...baseParams(),
        };
    }
  };

  const submitSingle = async () => {
    if (modeDef.needsPrompt && !composedPrompt.trim()) {
      setError("Write a prompt or pick an example below.");
      return;
    }
    if (modeDef.needsImage && !imageName) {
      setError("Upload a source image first.");
      return;
    }
    setError("");
    setNotice("");
    setOutputs([]);
    setBusy(true);
    if (prompt.trim()) rememberPrompt(prompt.trim());
    try {
      const payload = await buildSinglePayload();
      const id = await enqueueOne(payload);
      if (id) {
        setNotice(`Enqueued item #${id} - result appears below.`);
        void pollResult(id);
      } else {
        setError("Enqueue returned no item id.");
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "request failed");
    } finally {
      setBusy(false);
    }
  };

  const submitBatch = async () => {
    if (!prompt.trim()) {
      setError(
        "Write a prompt first - the batch applies styles/materials to it.",
      );
      return;
    }
    const selectedStyleObjs = styles.filter((s) => selectedStyles.has(s.id));
    const materials = MATERIALS.filter((m) => selectedMaterials.has(m.id));
    const painterObjs = painters.filter((p) => selectedPainters.has(p.id));
    if (
      selectedStyleObjs.length === 0 &&
      materials.length === 0 &&
      painterObjs.length === 0
    ) {
      setError(
        "Select at least one style, material, or painter for the batch.",
      );
      return;
    }
    const stylePool = selectedStyleObjs.length ? selectedStyleObjs : [null];
    const materialPool = materials.length ? materials : [null];
    const painterPool = painterObjs.length ? painterObjs : [null];
    const combos: {
      label: string;
      prompt: string;
      negative: string;
      styleId?: string;
      artistId?: string;
    }[] = [];
    for (const s of stylePool) {
      for (const m of materialPool) {
        for (const a of painterPool) {
          combos.push({
            label:
              [s?.name, m?.id !== "none" ? m?.name : null, a?.name]
                .filter(Boolean)
                .join(" × ") || "plain",
            // priority: base -> style -> material -> quality -> painter (painter last = strongest cue)
            prompt: [prompt, s?.prompt, m?.prompt, QUALITY_TAGS, a?.prompt]
              .filter(Boolean)
              .join(", "),
            negative: [negative, s?.negative].filter(Boolean).join(", "),
            styleId: s?.id,
            artistId: a?.id,
          });
        }
      }
    }
    if (combos.length > MAX_BATCH) {
      setError(
        `Batch would be ${combos.length} images - the cap is ${MAX_BATCH}.`,
      );
      return;
    }
    setError("");
    setNotice("");
    setOutputs([]);
    setBusy(true);
    rememberPrompt(prompt.trim());
    const items: BatchItem[] = [];
    try {
      for (let i = 0; i < combos.length; i++) {
        const c = combos[i];
        const id = await enqueueOne({
          operation: "txt2img",
          prompt: c.prompt,
          negative_prompt: c.negative || null,
          styles: c.styleId ? [c.styleId] : undefined,
          artists: c.artistId ? [c.artistId] : undefined,
          ...baseParams(),
          runs: 1,
        });
        items.push({
          itemId: id ?? 0,
          label: c.label,
          status: id ? "pending" : "failed",
        });
        setBatch([...items]);
        setBatchTotal(combos.length);
      }
      setNotice(`Batch of ${combos.length} enqueued.`);
      startPolling();
    } catch (e) {
      setError(e instanceof Error ? e.message : "batch enqueue failed");
    } finally {
      setBusy(false);
    }
  };

  const startPolling = () => {
    if (pollTimer.current) clearInterval(pollTimer.current);
    pollTimer.current = setInterval(async () => {
      try {
        const list = await apiPost<{
          data?: { items?: { item_id?: number; status?: string }[] };
        }>("/invokeai/queue", {
          operation: "list",
          limit: 200,
        });
        const byId = new Map(
          (list.data?.items ?? []).map((i) => [i.item_id, i.status]),
        );
        setBatch((prev) => {
          let changed = false;
          const next = prev.map((b) => {
            if (b.itemId === 0) return b;
            const st = byId.get(b.itemId);
            if (st && st !== b.status) {
              changed = true;
              return { ...b, status: st as BatchItem["status"] };
            }
            return b;
          });
          return changed ? next : prev;
        });
        const snapshot = await new Promise<BatchItem[]>((resolve) => {
          setBatch((prev) => {
            resolve(prev);
            return prev;
          });
        });
        const finished = snapshot.filter((b) =>
          ["completed", "failed", "canceled"].includes(b.status),
        ).length;
        if (finished >= snapshot.length && snapshot.length > 0) {
          if (pollTimer.current) clearInterval(pollTimer.current);
          pollTimer.current = null;
          const completed = snapshot.filter(
            (b) => b.status === "completed",
          ).length;
          setNotice(
            `Batch finished: ${completed}/${snapshot.length} completed.`,
          );
          const first = snapshot.find((b) => b.status === "completed");
          if (first?.itemId) void pollResult(first.itemId);
        }
      } catch {
        /* transient */
      }
    }, 4000);
  };

  const cancelBatch = async () => {
    const pending = batch
      .filter((b) => ["pending", "in_progress"].includes(b.status))
      .map((b) => b.itemId);
    for (const id of pending) {
      await apiPost("/invokeai/queue", {
        operation: "cancel",
        item_id: id,
      }).catch(() => null);
    }
    setNotice(`Cancel requested for ${pending.length} item(s).`);
  };

  const pollResult = async (id?: number) => {
    if (!id) return;
    for (let i = 0; i < 40; i++) {
      await new Promise((r) => setTimeout(r, 3000));
      try {
        const res = await apiPost<QueueResult>("/invokeai/queue", {
          operation: "result",
          item_id: id,
          wait_seconds: 0,
        });
        if (res.success && res.data?.status === "completed") {
          setOutputs(
            (res.data.outputs ?? []).map(
              (o) => o.url ?? `/api/invokeai/image/${o.image_name}`,
            ),
          );
          return;
        }
        if (["failed", "canceled"].includes(res.data?.status ?? "")) return;
      } catch {
        return;
      }
    }
  };

  const refinePrompt = async () => {
    if (!prompt.trim() || !selectedModel) {
      setError(
        "Pick a local LLM in Settings, then write a base prompt to refine.",
      );
      return;
    }
    setRefining(true);
    setError("");
    try {
      const system =
        "You are an expert AI image prompt engineer. Take the user's base prompt and produce ONE enhanced prompt that: keeps their subject exactly, adds the requested style and material, includes camera/lens/lighting detail for photorealistic styles, uses vivid descriptive vocabulary, appends quality tags. Return ONLY the enhanced prompt text - no quotes, no commentary, no markdown.";
      const styleNames =
        styles
          .filter((s) => selectedStyles.has(s.id))
          .map((s) => s.name)
          .join(", ") || "none";
      const materialNames =
        MATERIALS.filter((m) => selectedMaterials.has(m.id) && m.id !== "none")
          .map((m) => m.name)
          .join(", ") || "none";
      const res = await apiPost<{ content?: string; error?: string }>(
        "/llm/chat",
        {
          provider: selectedProvider,
          model: selectedModel,
          messages: [
            { role: "system", content: system },
            {
              role: "user",
              content: `Base prompt: "${prompt}"\nStyles: ${styleNames}\nMaterials: ${materialNames}\n\nEnhance it.`,
            },
          ],
        },
      );
      if (res.error) setError(res.error);
      else if (res.content) {
        setPrompt(res.content.trim().replace(/^"|"$/g, ""));
        setNotice("Prompt refined by local LLM.");
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "refine failed");
    } finally {
      setRefining(false);
    }
  };

  const randomSeed = () =>
    setSeed(String(Math.floor(Math.random() * 2147483647)));

  const copyComposed = async () => {
    try {
      await navigator.clipboard.writeText(composedPrompt);
      setNotice("Composed prompt copied.");
    } catch {
      /* clipboard blocked */
    }
  };

  const toggleStyle = (id: string) => {
    setSelectedStyles((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
    if (applyStyleSettings) {
      const s = styles.find((x) => x.id === id);
      if (s) {
        setCfg(s.cfg);
        setSteps(s.steps);
      }
    }
  };

  const installControlModel = async () => {
    setBusy(true);
    setError("");
    try {
      const res = await apiPost<{ success: boolean; message?: string }>(
        "/invokeai/models",
        {
          operation: "install",
          source: "diffusers/controlnet-canny-sdxl-1.0",
          config: {
            name: "SDXL Canny ControlNet",
            type: "controlnet",
            base: "sdxl",
          },
        },
      );
      setNotice(
        res.message ??
          "ControlNet install started - refresh after it completes.",
      );
      await new Promise((r) => setTimeout(r, 3000));
      void loadModels();
    } catch (e) {
      setError(e instanceof Error ? e.message : "install failed");
    } finally {
      setBusy(false);
    }
  };

  const installIpModel = async () => {
    setBusy(true);
    setError("");
    try {
      const res = await apiPost<{ success: boolean; message?: string }>(
        "/invokeai/models",
        {
          operation: "install",
          source: "h94/IP-Adapter",
          config: { name: "IP-Adapter SDXL", type: "ip_adapter", base: "sdxl" },
        },
      );
      setNotice(
        res.message ??
          "IP-Adapter install started - refresh after it completes.",
      );
      await new Promise((r) => setTimeout(r, 3000));
      void loadModels();
    } catch (e) {
      setError(e instanceof Error ? e.message : "install failed");
    } finally {
      setBusy(false);
    }
  };

  const inputCls =
    "w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-100 outline-none focus:border-amber-500/60";
  const labelCls = "mb-1 block text-xs font-medium text-slate-500";
  const checkCls =
    "flex items-center gap-2 rounded-md border border-slate-700 px-2.5 py-1.5 text-xs text-slate-300 transition hover:border-amber-500/40 hover:bg-slate-800 cursor-pointer select-none";

  const renderUpload = (
    current: string,
    setter: (v: string) => void,
    label: string,
    testid: string,
  ) => (
    <div>
      <label className={labelCls}>{label}</label>
      <div className="flex gap-2">
        <input
          value={current}
          onChange={(e) => setter(e.target.value)}
          className={inputCls}
          placeholder="Image name, or upload below"
          data-testid={`${testid}-name`}
        />
        <label
          className={`flex shrink-0 cursor-pointer items-center gap-1.5 rounded-lg border border-slate-700 px-3 py-2 text-xs text-slate-300 hover:bg-slate-800 ${uploading ? "opacity-50" : ""}`}
        >
          {uploading ? (
            <Loader2 className="h-3.5 w-3.5 animate-spin" />
          ) : (
            <ImagePlus className="h-3.5 w-3.5" />
          )}
          Upload
          <input
            type="file"
            accept="image/*"
            className="hidden"
            data-testid={`${testid}-upload`}
            onChange={async (e) => {
              const f = e.target.files?.[0];
              if (f) {
                try {
                  setter(await uploadFile(f));
                } catch {
                  /* error already set */
                }
              }
              e.target.value = "";
            }}
          />
        </label>
      </div>
      {current && (
        <p className="mt-1 truncate text-[11px] text-emerald-400">
          ✓ {current}
        </p>
      )}
    </div>
  );

  const statusColor: Record<BatchItem["status"], string> = {
    pending: "bg-slate-700/40 text-slate-400",
    in_progress: "bg-amber-500/15 text-amber-300",
    completed: "bg-emerald-500/15 text-emerald-300",
    failed: "bg-red-500/15 text-red-300",
    canceled: "bg-slate-700/40 text-slate-500",
    unknown: "bg-slate-700/40 text-slate-500",
  };

  return (
    <div className="mx-auto max-w-7xl p-6" data-testid="generate-page">
      <PageHeader
        title="Generate"
        subtitle="All InvokeAI generation modes - single or batch"
      />
      {configured === false && (
        <div className="mb-4 rounded-lg border border-dashed border-rose-500/40 bg-rose-500/5 px-4 py-2 text-xs text-rose-300">
          InvokeAI is offline. Complete onboarding (Settings) before generating.
        </div>
      )}

      <div
        className="mb-5 flex gap-1.5 overflow-x-auto rounded-xl border border-slate-800 bg-slate-900/60 p-1.5"
        data-testid="mode-tabs"
      >
        {MODES.map((m) => (
          <button
            key={m.id}
            onClick={() => setMode(m.id)}
            title={m.hint}
            className={`shrink-0 rounded-lg px-4 py-2 text-sm font-medium transition ${
              mode === m.id
                ? "bg-amber-500 text-slate-950"
                : "text-slate-400 hover:bg-slate-800 hover:text-slate-200"
            }`}
            data-testid={`mode-tab-${m.id}`}
          >
            {m.label}
          </button>
        ))}
      </div>

      <div className="grid gap-5 xl:grid-cols-5">
        <div className="space-y-5 xl:col-span-3">
          <SectionCard title={modeDef.label} testid="generate-form">
            <div className="space-y-4">
              {modeDef.needsPrompt && (
                <div>
                  <div className="mb-1 flex items-center justify-between">
                    <label className="text-xs font-medium text-slate-500">
                      Prompt
                    </label>
                    <button
                      onClick={refinePrompt}
                      disabled={refining || !prompt.trim() || !selectedModel}
                      className="flex items-center gap-1 rounded-md border border-violet-500/40 bg-violet-500/10 px-2 py-1 text-[11px] font-medium text-violet-300 transition hover:bg-violet-500/20 disabled:opacity-40"
                      data-testid="prompt-refine"
                      title={
                        selectedModel
                          ? "Enhance with the local LLM"
                          : "Select a local LLM in Settings first"
                      }
                    >
                      {refining ? (
                        <Loader2 className="h-3 w-3 animate-spin" />
                      ) : (
                        <Sparkles className="h-3 w-3" />
                      )}
                      {refining ? "Refining..." : "AI Refine"}
                    </button>
                  </div>
                  <textarea
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    rows={3}
                    className={inputCls}
                    placeholder="What do you want to see?"
                    data-testid="prompt-input"
                  />
                </div>
              )}

              <div>
                <label className={labelCls}>Model</label>
                <select
                  value={modelKey}
                  onChange={(e) => {
                    const key = e.target.value;
                    setModelKey(key);
                    const m = models.find((x) => x.key === key);
                    if (m?.base === "flux") {
                      setSteps(4);
                      setCfg(1);
                      setScheduler("euler");
                    } else if (m?.base === "sdxl") {
                      setSteps(35);
                      setCfg(5);
                    }
                  }}
                  className={inputCls}
                  data-testid="model-select"
                >
                  <option value="">Default (first main model)</option>
                  {models.map((m) => (
                    <option key={m.key} value={m.key}>
                      {m.name} ({m.base})
                    </option>
                  ))}
                </select>
              </div>

              {modeDef.needsImage &&
                renderUpload(
                  imageName,
                  setImageName,
                  modeDef.uploadLabel,
                  "image",
                )}
              {modeDef.needsMask &&
                renderUpload(
                  maskImageName,
                  setMaskImageName,
                  "Mask image (white = regenerate)",
                  "mask",
                )}

              {mode === "outpaint" && (
                <div className="grid grid-cols-4 gap-3">
                  {(
                    [
                      ["Left", outLeft, setOutLeft],
                      ["Right", outRight, setOutRight],
                      ["Top", outTop, setOutTop],
                      ["Bottom", outBottom, setOutBottom],
                    ] as const
                  ).map(([label, val, setter]) => (
                    <div key={label}>
                      <label className={labelCls}>Expand {label} (px)</label>
                      <input
                        type="number"
                        min="0"
                        max="1024"
                        step="64"
                        value={val}
                        onChange={(e) => setter(Number(e.target.value))}
                        className={inputCls}
                      />
                    </div>
                  ))}
                </div>
              )}

              {mode === "controlnet" && (
                <>
                  {renderUpload(
                    controlImageName,
                    setControlImageName,
                    "Control image (edges extracted automatically)",
                    "control",
                  )}
                  <div>
                    <label className={labelCls}>ControlNet model</label>
                    <select
                      value={controlModelKey}
                      onChange={(e) => setControlModelKey(e.target.value)}
                      className={inputCls}
                      data-testid="controlnet-model"
                    >
                      {controlModels.length === 0 && (
                        <option value="">No ControlNet model installed</option>
                      )}
                      {controlModels.map((m) => (
                        <option key={m.key} value={m.key}>
                          {m.name}
                        </option>
                      ))}
                    </select>
                    {controlModels.length === 0 && (
                      <button
                        onClick={installControlModel}
                        disabled={busy}
                        className="mt-2 flex items-center gap-1.5 rounded-md border border-amber-500/40 bg-amber-500/10 px-3 py-1.5 text-xs text-amber-300 hover:bg-amber-500/20 disabled:opacity-50"
                        data-testid="install-controlnet"
                      >
                        <Wand2 className="h-3.5 w-3.5" /> Install SDXL Canny
                        ControlNet (~2.5 GB)
                      </button>
                    )}
                  </div>
                  <div className="grid grid-cols-3 gap-3">
                    <div>
                      <label className={labelCls}>
                        Weight: {controlWeight.toFixed(2)}
                      </label>
                      <input
                        type="range"
                        min="0"
                        max="1"
                        step="0.05"
                        value={controlWeight}
                        onChange={(e) =>
                          setControlWeight(Number(e.target.value))
                        }
                        className="w-full accent-amber-500"
                      />
                    </div>
                    <div>
                      <label className={labelCls}>Canny low</label>
                      <input
                        type="number"
                        min="0"
                        max="255"
                        value={cannyLow}
                        onChange={(e) => setCannyLow(Number(e.target.value))}
                        className={inputCls}
                      />
                    </div>
                    <div>
                      <label className={labelCls}>Canny high</label>
                      <input
                        type="number"
                        min="0"
                        max="255"
                        value={cannyHigh}
                        onChange={(e) => setCannyHigh(Number(e.target.value))}
                        className={inputCls}
                      />
                    </div>
                  </div>
                </>
              )}

              {mode === "ipadapter" && (
                <>
                  {renderUpload(
                    ipImageName,
                    setIpImageName,
                    "Reference image (style to copy)",
                    "ip",
                  )}
                  <div>
                    <label className={labelCls}>IP-Adapter model</label>
                    <select
                      value={ipModelKey}
                      onChange={(e) => setIpModelKey(e.target.value)}
                      className={inputCls}
                      data-testid="ipadapter-model"
                    >
                      {ipModels.length === 0 && (
                        <option value="">No IP-Adapter model installed</option>
                      )}
                      {ipModels.map((m) => (
                        <option key={m.key} value={m.key}>
                          {m.name}
                        </option>
                      ))}
                    </select>
                    {ipModels.length === 0 && (
                      <button
                        onClick={installIpModel}
                        disabled={busy}
                        className="mt-2 flex items-center gap-1.5 rounded-md border border-amber-500/40 bg-amber-500/10 px-3 py-1.5 text-xs text-amber-300 hover:bg-amber-500/20 disabled:opacity-50"
                        data-testid="install-ipadapter"
                      >
                        <Wand2 className="h-3.5 w-3.5" /> Install IP-Adapter
                        SDXL (h94/IP-Adapter)
                      </button>
                    )}
                  </div>
                  <div>
                    <label className={labelCls}>
                      Weight: {ipWeight.toFixed(2)}
                    </label>
                    <input
                      type="range"
                      min="0"
                      max="1"
                      step="0.05"
                      value={ipWeight}
                      onChange={(e) => setIpWeight(Number(e.target.value))}
                      className="w-full accent-amber-500"
                    />
                  </div>
                </>
              )}

              {mode === "seamless" && (
                <div className="flex gap-6">
                  <label className="flex items-center gap-2 text-sm text-slate-300">
                    <input
                      type="checkbox"
                      checked={seamlessX}
                      onChange={(e) => setSeamlessX(e.target.checked)}
                      className="accent-amber-500"
                    />
                    Seamless X (horizontal tiling)
                  </label>
                  <label className="flex items-center gap-2 text-sm text-slate-300">
                    <input
                      type="checkbox"
                      checked={seamlessY}
                      onChange={(e) => setSeamlessY(e.target.checked)}
                      className="accent-amber-500"
                    />
                    Seamless Y (vertical tiling)
                  </label>
                </div>
              )}

              {mode === "txt2img" && (
                <div>
                  <label className={labelCls}>Negative prompt</label>
                  <input
                    value={negative}
                    onChange={(e) => setNegative(e.target.value)}
                    className={inputCls}
                    placeholder="blurry, low quality"
                  />
                </div>
              )}
              {(mode === "img2img" ||
                mode === "inpaint" ||
                mode === "outpaint" ||
                mode === "controlnet" ||
                mode === "ipadapter") && (
                <div>
                  <label className={labelCls}>Negative prompt</label>
                  <input
                    value={negative}
                    onChange={(e) => setNegative(e.target.value)}
                    className={inputCls}
                    placeholder="blurry, low quality"
                  />
                </div>
              )}

              {mode !== "upscale" && (
                <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
                  <div>
                    <label className={labelCls}>Width</label>
                    <input
                      type="number"
                      value={width}
                      onChange={(e) => setWidth(Number(e.target.value))}
                      className={inputCls}
                    />
                  </div>
                  <div>
                    <label className={labelCls}>Height</label>
                    <input
                      type="number"
                      value={height}
                      onChange={(e) => setHeight(Number(e.target.value))}
                      className={inputCls}
                    />
                  </div>
                  <div>
                    <label className={labelCls}>Steps</label>
                    <input
                      type="number"
                      value={steps}
                      onChange={(e) => setSteps(Number(e.target.value))}
                      className={inputCls}
                    />
                  </div>
                  <div>
                    <label className={labelCls}>CFG scale</label>
                    <input
                      type="number"
                      step="0.5"
                      value={cfg}
                      onChange={(e) => setCfg(Number(e.target.value))}
                      className={inputCls}
                    />
                  </div>
                  <div>
                    <label className={labelCls}>Scheduler</label>
                    <select
                      value={scheduler}
                      onChange={(e) => setScheduler(e.target.value)}
                      className={inputCls}
                    >
                      {[
                        "euler",
                        "euler_a",
                        "dpmpp_2m",
                        "dpmpp_2m_sde",
                        "dpmpp_3m_sde",
                        "dpmpp_sde",
                        "ddim",
                        "unipc",
                      ].map((s) => (
                        <option key={s}>{s}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className={labelCls}>Seed</label>
                    <div className="flex gap-1">
                      <input
                        value={seed}
                        onChange={(e) => setSeed(e.target.value)}
                        className={inputCls}
                        placeholder="random"
                        data-testid="seed-input"
                      />
                      <button
                        onClick={randomSeed}
                        className="shrink-0 rounded-lg border border-slate-700 px-2 text-slate-400 hover:bg-slate-800"
                        title="Random seed"
                        data-testid="seed-dice"
                      >
                        <Dices className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </div>
              )}
              {mode === "img2img" ||
              mode === "inpaint" ||
              mode === "outpaint" ? (
                <div>
                  <label className={labelCls}>
                    Strength: {strength.toFixed(2)}
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.05"
                    value={strength}
                    onChange={(e) => setStrength(Number(e.target.value))}
                    className="w-full accent-amber-500"
                  />
                </div>
              ) : null}

              <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-3">
                <div className="mb-1 flex items-center justify-between">
                  <span className="text-[11px] font-semibold uppercase tracking-wide text-slate-500">
                    Composed prompt
                  </span>
                  <button
                    onClick={copyComposed}
                    className="flex items-center gap-1 text-[11px] text-slate-500 hover:text-amber-300"
                    data-testid="composed-copy"
                  >
                    <Copy className="h-3 w-3" /> Copy
                  </button>
                </div>
                <p
                  className="text-xs leading-relaxed text-slate-300"
                  data-testid="composed-preview"
                >
                  {composedPrompt ||
                    "Your style, material, and quality tags are composed here."}
                </p>
              </div>

              <button
                onClick={submitSingle}
                disabled={busy || configured === false || batchRunning}
                className="flex w-full items-center justify-center gap-2 rounded-lg bg-amber-500 px-4 py-2.5 text-sm font-semibold text-slate-950 transition hover:bg-amber-400 disabled:opacity-40"
                data-testid="generate-submit"
              >
                {busy ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Send className="h-4 w-4" />
                )}
                {mode === "upscale" ? "Upscale" : `Generate ${modeDef.label}`}
              </button>
            </div>
          </SectionCard>

          {mode === "txt2img" && (
            <SectionCard
              title="Styles & materials - batch"
              testid="batch-panel"
            >
              <div className="mb-2">
                <input
                  value={styleFilter}
                  onChange={(e) => setStyleFilter(e.target.value)}
                  placeholder="Search styles..."
                  className={`${inputCls} max-w-xs`}
                  data-testid="style-filter"
                />
              </div>
              <div className="mb-3">
                <div className="mb-1.5 flex items-center justify-between">
                  <span className="text-xs font-medium text-slate-500">
                    Styles{" "}
                    <span className="text-slate-600">
                      ({selectedStyles.size}/{styles.length})
                    </span>
                  </span>
                  <div className="flex gap-2">
                    <button
                      onClick={() =>
                        setSelectedStyles(new Set(styles.map((s) => s.id)))
                      }
                      className="flex items-center gap-1 text-[11px] text-slate-500 hover:text-amber-300"
                      data-testid="select-all-styles"
                    >
                      <CheckSquare className="h-3 w-3" /> All
                    </button>
                    <button
                      onClick={() => setSelectedStyles(new Set())}
                      className="flex items-center gap-1 text-[11px] text-slate-500 hover:text-red-400"
                      data-testid="clear-styles"
                    >
                      <Square className="h-3 w-3" /> None
                    </button>
                  </div>
                </div>
                <div
                  className="flex max-h-48 flex-wrap gap-1.5 overflow-y-auto"
                  data-testid="style-checks"
                >
                  {visibleStyles.map((s) => (
                    <label
                      key={s.id}
                      className={checkCls}
                      data-testid={`style-check-${s.id}`}
                    >
                      <input
                        type="checkbox"
                        checked={selectedStyles.has(s.id)}
                        onChange={() => toggleStyle(s.id)}
                        className="accent-amber-500"
                      />
                      {s.name}
                    </label>
                  ))}
                  {visibleStyles.length === 0 && (
                    <span className="text-xs text-slate-600">
                      No styles match.
                    </span>
                  )}
                </div>
              </div>
              <div>
                <div className="mb-1.5 flex items-center justify-between">
                  <span className="text-xs font-medium text-slate-500">
                    Materials{" "}
                    <span className="text-slate-600">
                      ({selectedMaterials.size}/{MATERIALS.length})
                    </span>
                  </span>
                  <div className="flex gap-2">
                    <button
                      onClick={() =>
                        setSelectedMaterials(
                          new Set(MATERIALS.map((m) => m.id)),
                        )
                      }
                      className="flex items-center gap-1 text-[11px] text-slate-500 hover:text-amber-300"
                      data-testid="select-all-materials"
                    >
                      <CheckSquare className="h-3 w-3" /> All
                    </button>
                    <button
                      onClick={() => setSelectedMaterials(new Set())}
                      className="flex items-center gap-1 text-[11px] text-slate-500 hover:text-red-400"
                      data-testid="clear-materials"
                    >
                      <Square className="h-3 w-3" /> None
                    </button>
                  </div>
                </div>
                <div
                  className="flex max-h-40 flex-wrap gap-1.5 overflow-y-auto"
                  data-testid="material-checks"
                >
                  {MATERIALS.map((m) => (
                    <label
                      key={m.id}
                      className={checkCls}
                      data-testid={`material-check-${m.id}`}
                    >
                      <input
                        type="checkbox"
                        checked={selectedMaterials.has(m.id)}
                        onChange={() =>
                          setSelectedMaterials((prev) => {
                            const next = new Set(prev);
                            if (next.has(m.id)) next.delete(m.id);
                            else next.add(m.id);
                            return next;
                          })
                        }
                        className="accent-amber-500"
                      />
                      {m.name}
                    </label>
                  ))}
                </div>
              </div>
              <div className="mt-3">
                <div className="mb-1.5 flex items-center justify-between">
                  <span className="text-xs font-medium text-slate-500">
                    Painters{" "}
                    <span className="text-slate-600">
                      ({selectedPainters.size}/{painters.length}) - Giotto to
                      Giger
                    </span>
                  </span>
                  <div className="flex gap-2">
                    <button
                      onClick={() =>
                        setSelectedPainters(new Set(painters.map((p) => p.id)))
                      }
                      className="flex items-center gap-1 text-[11px] text-slate-500 hover:text-amber-300"
                      data-testid="select-all-painters"
                    >
                      <CheckSquare className="h-3 w-3" /> All
                    </button>
                    <button
                      onClick={() => setSelectedPainters(new Set())}
                      className="flex items-center gap-1 text-[11px] text-slate-500 hover:text-red-400"
                      data-testid="clear-painters"
                    >
                      <Square className="h-3 w-3" /> None
                    </button>
                  </div>
                </div>
                <input
                  value={painterFilter}
                  onChange={(e) => setPainterFilter(e.target.value)}
                  placeholder="Search painters..."
                  className={`${inputCls} mb-1.5 max-w-xs`}
                  data-testid="painter-filter"
                />
                <div
                  className="flex max-h-40 flex-wrap gap-1.5 overflow-y-auto"
                  data-testid="painter-checks"
                >
                  {visiblePainters.map((p) => (
                    <label
                      key={p.id}
                      className={checkCls}
                      data-testid={`painter-check-${p.id}`}
                    >
                      <input
                        type="checkbox"
                        checked={selectedPainters.has(p.id)}
                        onChange={() =>
                          setSelectedPainters((prev) => {
                            const next = new Set(prev);
                            if (next.has(p.id)) next.delete(p.id);
                            else next.add(p.id);
                            return next;
                          })
                        }
                        className="accent-amber-500"
                      />
                      {p.name}
                    </label>
                  ))}
                  {visiblePainters.length === 0 && (
                    <span className="text-xs text-slate-600">
                      No painters match.
                    </span>
                  )}
                </div>
              </div>
              <label className="mt-3 flex items-center gap-2 text-xs text-slate-500">
                <input
                  type="checkbox"
                  checked={applyStyleSettings}
                  onChange={(e) => setApplyStyleSettings(e.target.checked)}
                  className="accent-amber-500"
                />
                Apply selected style's suggested steps/CFG
              </label>
              <button
                onClick={submitBatch}
                disabled={
                  busy || configured === false || batchRunning || !prompt.trim()
                }
                className="mt-3 flex w-full items-center justify-center gap-2 rounded-lg border border-amber-500/50 bg-amber-500/15 px-4 py-2.5 text-sm font-semibold text-amber-300 transition hover:bg-amber-500/25 disabled:opacity-40"
                data-testid="batch-generate"
              >
                {busy ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Wand2 className="h-4 w-4" />
                )}
                Batch generate ({batchCount} images)
              </button>
            </SectionCard>
          )}

          {batch.length > 0 && (
            <SectionCard
              title={`Batch progress ${batchPercent}%`}
              testid="batch-progress-card"
            >
              <div className="mb-3">
                <div className="mb-1 flex items-center justify-between text-xs">
                  <span className="text-slate-400" data-testid="batch-percent">
                    {doneCount}/{batchTotal} done ({batchPercent}%)
                  </span>
                  {batchRunning && (
                    <button
                      onClick={cancelBatch}
                      className="text-red-400 hover:text-red-300"
                      data-testid="batch-cancel"
                    >
                      Cancel remaining
                    </button>
                  )}
                </div>
                <div
                  className="h-2 w-full overflow-hidden rounded-full bg-slate-800"
                  data-testid="batch-progress"
                >
                  <div
                    className="h-full rounded-full bg-amber-500 transition-all duration-500"
                    style={{ width: `${batchPercent}%` }}
                  />
                </div>
              </div>
              <div className="grid max-h-64 grid-cols-2 gap-1.5 overflow-y-auto md:grid-cols-3">
                {batch.map((b, i) => (
                  <div
                    key={`${b.itemId}-${i}`}
                    className="flex items-center justify-between gap-1 rounded-md border border-slate-800 bg-slate-950/40 px-2 py-1.5 text-[11px]"
                    data-testid={`batch-item-${i}`}
                  >
                    <span className="truncate text-slate-300">{b.label}</span>
                    <span
                      className={`shrink-0 rounded-full px-1.5 py-0.5 font-semibold ${statusColor[b.status]}`}
                    >
                      {b.status.replace("_", " ")}
                    </span>
                  </div>
                ))}
              </div>
            </SectionCard>
          )}

          <SectionCard title="Example prompts" testid="example-prompts">
            <div className="space-y-3">
              {EXAMPLE_PROMPTS.map((g) => (
                <div key={g.group}>
                  <div className="mb-1.5 text-[11px] font-semibold uppercase tracking-wide text-slate-600">
                    {g.group}
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {g.items.map((ex) => (
                      <button
                        key={ex}
                        onClick={() => setPrompt(ex)}
                        className="rounded-full border border-slate-700 px-3 py-1 text-xs text-slate-400 transition hover:border-amber-500/50 hover:text-amber-300"
                        data-testid={`example-${g.group.toLowerCase().replace(/\W+/g, "-")}`}
                      >
                        {ex}
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </SectionCard>

          {history.length > 0 && (
            <SectionCard title="Recent prompts" testid="recent-prompts">
              <div className="flex flex-wrap gap-2">
                {history.map((h) => (
                  <button
                    key={h}
                    onClick={() => setPrompt(h)}
                    className="max-w-72 truncate rounded-full border border-slate-700 px-3 py-1 text-xs text-slate-400 transition hover:border-amber-500/50 hover:text-amber-300"
                  >
                    {h}
                  </button>
                ))}
              </div>
            </SectionCard>
          )}
        </div>

        <div className="xl:col-span-2">
          <SectionCard title="Output" testid="generate-output">
            {busy && <Spinner label="Enqueuing..." />}
            {notice && !busy && (
              <div className="mb-3 flex items-center gap-2 rounded-lg border border-emerald-500/40 bg-emerald-500/10 px-3 py-2 text-xs text-emerald-300">
                <RefreshCw className="h-3.5 w-3.5" />
                {notice}
              </div>
            )}
            {error && (
              <div className="mb-3 rounded-lg border border-red-500/40 bg-red-500/10 px-3 py-2 text-xs text-red-300">
                {error}
              </div>
            )}
            {outputs.length > 0 ? (
              <div className="grid grid-cols-2 gap-3">
                {outputs.map((url) => (
                  <div
                    key={url}
                    className="overflow-hidden rounded-lg border border-slate-800"
                  >
                    <img
                      src={url}
                      alt="generated"
                      className="w-full"
                      data-testid="generated-image"
                    />
                    <a
                      href={url}
                      target="_blank"
                      rel="noreferrer"
                      className="flex items-center justify-center gap-1 bg-slate-900 py-2 text-xs text-amber-300 hover:text-amber-200"
                    >
                      <ExternalLink className="h-3.5 w-3.5" /> Open full size
                    </a>
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex h-64 items-center justify-center rounded-xl border border-dashed border-slate-800 text-slate-600">
                <div className="text-center">
                  <Wand2 className="mx-auto mb-2 h-8 w-8" />
                  <p className="text-xs">Generated images appear here</p>
                </div>
              </div>
            )}
          </SectionCard>
        </div>
      </div>
    </div>
  );
}
