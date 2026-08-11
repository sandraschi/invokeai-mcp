import { ExternalLink, Loader2, RefreshCw, Send, Wand2 } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { PageHeader, SectionCard, Spinner } from "../components/ui";
import { apiPost } from "../lib/api";
import { useHealthStore } from "../store/health";

interface ModelOption {
  key: string;
  name: string;
  base: string;
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
    local_paths?: string[];
  };
  message?: string;
}

export default function GeneratePage() {
  const configured = useHealthStore((s) => s.configured);
  const [models, setModels] = useState<ModelOption[]>([]);
  const [modelKey, setModelKey] = useState("");
  const [prompt, setPrompt] = useState("");
  const [negative, setNegative] = useState("");
  const [operation, setOperation] = useState<
    "txt2img" | "img2img" | "inpaint" | "upscale"
  >("txt2img");
  const [imageName, setImageName] = useState("");
  const [maskImageName, setMaskImageName] = useState("");
  const [width, setWidth] = useState(1024);
  const [height, setHeight] = useState(1024);
  const [steps, setSteps] = useState(30);
  const [cfg, setCfg] = useState(5);
  const [scheduler, setScheduler] = useState("euler");
  const [seed, setSeed] = useState("");
  const [strength, setStrength] = useState(0.75);
  const [busy, setBusy] = useState(false);
  const [outputs, setOutputs] = useState<string[]>([]);
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");

  const loadModels = useCallback(async () => {
    try {
      const r = await fetch("/api/invokeai/models");
      if (r.ok) {
        const j = (await r.json()) as { models?: ModelOption[] };
        setModels(j.models ?? []);
      }
    } catch {
      /* degraded */
    }
  }, []);

  useEffect(() => {
    loadModels();
  }, [loadModels]);

  const submit = async () => {
    setError("");
    setNotice("");
    setOutputs([]);
    setBusy(true);
    try {
      const res = await apiPost<GenerateResponse>("/invokeai/generate", {
        operation,
        prompt,
        negative_prompt: negative || null,
        model_key: modelKey || null,
        image_name: imageName || null,
        mask_image_name: operation === "inpaint" ? maskImageName || null : null,
        width,
        height,
        steps,
        cfg_scale: cfg,
        scheduler,
        seed: seed ? Number(seed) : null,
        strength,
      });
      if (res.success) {
        setNotice(
          `Enqueued item #${res.queue_item_id} - poll the Queue page or wait.`,
        );
        void pollResult(res.queue_item_id);
      } else {
        setError(res.message ?? "Enqueue failed");
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "request failed");
    } finally {
      setBusy(false);
    }
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
            (res.data.outputs ?? []).map((o) => o.url ?? o.image_name),
          );
          setNotice(
            `Item #${id} completed - ${res.data.outputs?.length ?? 0} image(s).`,
          );
          return;
        }
        if (res.data?.status === "failed" || res.data?.status === "canceled") {
          setError(`Item #${id} ${res.data.status}.`);
          return;
        }
      } catch {
        return;
      }
    }
  };

  const inputCls =
    "w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-100 outline-none focus:border-amber-500/60";
  const labelCls = "mb-1 block text-xs font-medium text-slate-500";

  return (
    <div className="mx-auto max-w-6xl p-6" data-testid="generate-page">
      <PageHeader
        title="Generate"
        subtitle="txt2img, img2img, masked inpaint, and upscaling via the local engine"
      />
      {configured === false && (
        <div className="mb-4 rounded-lg border border-dashed border-rose-500/40 bg-rose-500/5 px-4 py-2 text-xs text-rose-300">
          InvokeAI is offline. Complete onboarding (Settings) before generating.
        </div>
      )}
      <div className="grid gap-5 lg:grid-cols-2">
        <SectionCard title="Prompt" testid="generate-form">
          <div className="space-y-4">
            <div>
              <label className={labelCls}>Operation</label>
              <div className="flex flex-wrap gap-2">
                {(["txt2img", "img2img", "inpaint", "upscale"] as const).map(
                  (op) => (
                    <button
                      key={op}
                      onClick={() => setOperation(op)}
                      className={`rounded-md border px-3 py-1.5 text-xs font-medium transition ${
                        operation === op
                          ? "border-amber-500/60 bg-amber-500/15 text-amber-300"
                          : "border-slate-700 text-slate-400 hover:bg-slate-800"
                      }`}
                      data-testid={`op-${op}`}
                    >
                      {op}
                    </button>
                  ),
                )}
              </div>
            </div>
            <div>
              <label className={labelCls}>Model</label>
              <select
                value={modelKey}
                onChange={(e) => setModelKey(e.target.value)}
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
            {operation !== "upscale" && (
              <div>
                <label className={labelCls}>Prompt</label>
                <textarea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  rows={4}
                  className={inputCls}
                  placeholder="neon cyberpunk city at night, rain, cinematic lighting"
                  data-testid="prompt-input"
                />
              </div>
            )}
            {operation === "txt2img" && (
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
            {operation !== "txt2img" && (
              <div>
                <label className={labelCls}>Image name (from Gallery)</label>
                <input
                  value={imageName}
                  onChange={(e) => setImageName(e.target.value)}
                  className={inputCls}
                  placeholder="e.g. abc123.png"
                  data-testid="image-name-input"
                />
              </div>
            )}
            {operation === "inpaint" && (
              <div>
                <label className={labelCls}>
                  Mask image name (white = regenerate)
                </label>
                <input
                  value={maskImageName}
                  onChange={(e) => setMaskImageName(e.target.value)}
                  className={inputCls}
                  placeholder="mask.png"
                />
              </div>
            )}
            <div className="grid grid-cols-2 gap-3">
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
                <label className={labelCls}>Seed (blank = random)</label>
                <input
                  value={seed}
                  onChange={(e) => setSeed(e.target.value)}
                  className={inputCls}
                  placeholder="random"
                />
              </div>
            </div>
            {operation !== "txt2img" && operation !== "upscale" && (
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
            )}
            <button
              onClick={submit}
              disabled={busy || configured === false}
              className="flex w-full items-center justify-center gap-2 rounded-lg bg-amber-500 px-4 py-2.5 text-sm font-semibold text-slate-950 transition hover:bg-amber-400 disabled:opacity-40"
              data-testid="generate-submit"
            >
              {busy ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
              Enqueue {operation}
            </button>
          </div>
        </SectionCard>

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
  );
}
