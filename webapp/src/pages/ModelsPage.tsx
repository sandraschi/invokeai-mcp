import { Layers, Plus, Trash2 } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import {
  EmptyState,
  MockBadge,
  MockBanner,
  PageHeader,
  Spinner,
} from "../components/ui";
import { apiGet, apiPost } from "../lib/api";
import { MOCK } from "../lib/mockOnboarding";
import { useHealthStore } from "../store/health";

interface ModelRec {
  key: string;
  name: string;
  base: string;
  type: string;
  format?: string;
}

export default function ModelsPage() {
  const configured = useHealthStore((s) => s.configured);
  const [models, setModels] = useState<ModelRec[]>([]);
  const [loading, setLoading] = useState(true);
  const [modelType, setModelType] = useState("main");
  const [source, setSource] = useState("");
  const [installing, setInstalling] = useState(false);
  const [notice, setNotice] = useState("");

  const load = useCallback(
    async (type = modelType) => {
      setLoading(true);
      try {
        const data = await apiGet<{ models: ModelRec[] }>(
          `/invokeai/models?model_type=${encodeURIComponent(type)}`,
        );
        setModels(data.models ?? []);
      } catch {
        setModels([]);
      } finally {
        setLoading(false);
      }
    },
    [modelType],
  );

  useEffect(() => {
    load();
  }, [load]);

  const install = async () => {
    if (!source.trim()) return;
    setInstalling(true);
    setNotice("");
    try {
      const res = await apiPost<{ success: boolean; message?: string }>(
        "/invokeai/models",
        {
          operation: "install",
          source: source.trim(),
        },
      );
      setNotice(
        res.message ?? (res.success ? "Install started" : "Install failed"),
      );
    } catch (e) {
      setNotice(e instanceof Error ? e.message : "install failed");
    } finally {
      setInstalling(false);
    }
  };

  const remove = async (key: string) => {
    await apiPost<{ success: boolean }>("/invokeai/models", {
      operation: "delete",
      key,
    });
    void load();
  };

  const mock = configured === false;
  const shown = mock
    ? MOCK.models.filter((m) => m.type === modelType || modelType === "main")
    : models;

  const inputCls =
    "rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm outline-none focus:border-amber-500/60";

  return (
    <div className="mx-auto max-w-6xl p-6" data-testid="models-page">
      <PageHeader
        title="Models"
        subtitle="Install and manage checkpoints, LoRAs, VAEs, and upscalers"
      />
      {mock && <MockBanner />}

      <div className="mb-5 flex flex-wrap items-end gap-3">
        <div className="flex-1 min-w-64">
          <label className="mb-1 block text-xs font-medium text-slate-500">
            Install source (HF repo id, Civitai URL, or path)
          </label>
          <input
            value={source}
            onChange={(e) => setSource(e.target.value)}
            placeholder="stabilityai/stable-diffusion-xl-base-1.0"
            className={`${inputCls} w-full`}
            data-testid="model-install-source"
          />
        </div>
        <button
          onClick={install}
          disabled={installing || !source.trim()}
          className="flex items-center gap-1.5 rounded-lg bg-amber-500 px-4 py-2 text-sm font-semibold text-slate-950 hover:bg-amber-400 disabled:opacity-40"
          data-testid="model-install"
        >
          <Plus className="h-4 w-4" /> Install
        </button>
      </div>
      {notice && <p className="mb-3 text-xs text-emerald-300">{notice}</p>}

      <div className="mb-3 flex flex-wrap gap-2">
        {["main", "lora", "vae", "controlnet", "spandrel_image_to_image"].map(
          (t) => (
            <button
              key={t}
              onClick={() => setModelType(t)}
              className={`rounded-md border px-3 py-1.5 text-xs font-medium ${
                modelType === t
                  ? "border-amber-500/60 bg-amber-500/15 text-amber-300"
                  : "border-slate-700 text-slate-400 hover:bg-slate-800"
              }`}
              data-testid={`type-${t}`}
            >
              {t.replace("_", " ")}
            </button>
          ),
        )}
      </div>

      {loading && <Spinner />}
      {!loading && shown.length === 0 && (
        <EmptyState
          icon={<Layers className="h-8 w-8" />}
          title={`No ${modelType} models`}
          hint="Install one above or in the InvokeAI UI."
        />
      )}
      <div className="grid gap-3 md:grid-cols-2">
        {shown.map((m) => (
          <div
            key={m.key}
            className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-900/60 p-4"
            data-testid="model-row"
          >
            <div className="min-w-0">
              <div className="flex items-center gap-2">
                <span className="truncate text-sm font-medium text-slate-200">
                  {m.name}
                </span>
                {mock && <MockBadge />}
              </div>
              <div className="mt-1 flex items-center gap-2 text-[11px] text-slate-500">
                <code className="rounded bg-slate-800 px-1.5 py-0.5">
                  {m.base ?? "?"}
                </code>
                <code className="rounded bg-slate-800 px-1.5 py-0.5">
                  {m.key}
                </code>
              </div>
            </div>
            {!mock && (
              <button
                onClick={() => remove(m.key)}
                className="text-slate-500 hover:text-red-400"
                title="Delete"
              >
                <Trash2 className="h-4 w-4" />
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
