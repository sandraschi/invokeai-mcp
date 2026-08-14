import { ArrowRight, Image, Layers, ListOrdered, Sparkles } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  EmptyState,
  KpiCard,
  MockBadge,
  MockBanner,
  Spinner,
  StatusPill,
} from "../components/ui";
import { apiGet } from "../lib/api";
import { MOCK } from "../lib/mockOnboarding";
import { useHealthStore } from "../store/health";

interface DashboardData {
  configured: boolean;
  version: string | null;
  model_count: number;
  queue: Record<string, number>;
  recent_images: { image_name: string; url: string; thumbnail_url: string }[];
}

export default function DashboardPage() {
  const configured = useHealthStore((s) => s.configured);
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    try {
      setData(await apiGet<DashboardData>("/dashboard"));
      setError("");
    } catch (e) {
      setError(e instanceof Error ? e.message : "load failed");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
    const id = setInterval(load, 15000);
    return () => clearInterval(id);
  }, [load]);

  const mock = configured === false;
  const kpis = mock
    ? {
        version: MOCK.dashboard.version,
        modelCount: MOCK.dashboard.modelCount,
        queue: MOCK.dashboard.queue,
      }
    : data
      ? {
          version: data.version ?? "?",
          modelCount: data.model_count,
          queue: data.queue,
        }
      : { version: "?", modelCount: 0, queue: {} };
  const recent = mock
    ? MOCK.dashboard.recentImages
    : (data?.recent_images ?? []);

  return (
    <div className="mx-auto max-w-6xl p-6" data-testid="dashboard">
      <div className="rounded-2xl border border-slate-800 bg-gradient-to-br from-slate-900 via-slate-900 to-amber-950/30 p-8">
        <div className="flex items-center gap-3 text-amber-400">
          <Sparkles className="h-8 w-8" />
          <span className="text-sm font-semibold uppercase tracking-widest">
            InvokeAI MCP
          </span>
        </div>
        <h1 className="mt-3 text-3xl font-bold text-slate-100">
          Your creative engine, in your chat.
        </h1>
        <p className="mt-2 max-w-2xl text-sm text-slate-400">
          Generate, transform, inpaint, and upscale images with SDXL, Flux, and
          more - on your own GPU, from Claude, Cursor, or this dashboard.
        </p>
        <div className="mt-4">
          <StatusPill
            ok={configured !== false}
            label={
              configured === null
                ? "Checking..."
                : configured
                  ? "InvokeAI connected"
                  : "InvokeAI offline"
            }
          />
        </div>
        {mock && (
          <Link
            to="/app/settings"
            className="mt-5 inline-flex items-center gap-2 rounded-lg bg-red-600 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-red-900/40 transition hover:bg-red-500"
            data-testid="onboarding-cue"
          >
            Complete onboarding - connect InvokeAI{" "}
            <ArrowRight className="h-4 w-4" />
          </Link>
        )}
      </div>

      {mock && (
        <div className="mt-4">
          <MockBanner />
        </div>
      )}

      <div className="mt-6 grid grid-cols-2 gap-4 md:grid-cols-4">
        <KpiCard
          testid="kpi-server"
          label="Engine"
          value={kpis.version}
          icon={<Sparkles className="h-3.5 w-3.5" />}
        />
        <KpiCard
          testid="kpi-tools"
          label="Models"
          value={kpis.modelCount}
          icon={<Layers className="h-3.5 w-3.5" />}
        />
        <KpiCard
          testid="kpi-queue"
          label="Queued"
          value={kpis.queue.queued ?? 0}
          icon={<ListOrdered className="h-3.5 w-3.5" />}
        />
        <KpiCard
          testid="kpi-completed"
          label="Completed"
          value={kpis.queue.completed ?? 0}
          icon={<Image className="h-3.5 w-3.5" />}
        />
      </div>

      <div className="mt-6">
        <h2 className="mb-3 text-sm font-semibold text-slate-200">
          Recent images
        </h2>
        {loading && <Spinner />}
        {error && !mock && <p className="text-xs text-red-400">{error}</p>}
        {!loading && recent.length === 0 && !mock && (
          <EmptyState
            icon={<Image className="h-8 w-8" />}
            title="No images yet"
            hint="Generate your first image on the Generate page."
          />
        )}
        {recent.length > 0 && (
          <div className="grid grid-cols-2 gap-3 md:grid-cols-3 lg:grid-cols-6">
            {recent.map((img) => (
              <Link
                key={img.image_name}
                to="/app/gallery"
                className="group relative overflow-hidden rounded-lg border border-slate-800"
                data-testid={`recent-image-${img.image_name}`}
              >
                {img.url ? (
                  <img
                    src={img.thumbnail_url || img.url}
                    alt={img.image_name}
                    className="aspect-square w-full object-cover transition group-hover:scale-105"
                    loading="lazy"
                  />
                ) : (
                  <div className="flex aspect-square w-full items-center justify-center bg-slate-900 text-slate-400">
                    <Image className="h-8 w-8" />
                  </div>
                )}
                {mock && (
                  <div className="absolute right-1 top-1">
                    <MockBadge />
                  </div>
                )}
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
