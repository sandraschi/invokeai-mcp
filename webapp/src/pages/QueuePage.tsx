import { ListOrdered, Play, RefreshCw, Trash2, XCircle } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { EmptyState, PageHeader, Spinner } from "../components/ui";
import { apiGet, apiPost } from "../lib/api";

interface QueueItem {
  id?: number;
  queue_item_id?: number;
  status?: string;
  destination?: string;
  batch_id?: string;
  session_id?: string;
}

interface QueueStatus {
  queued: number;
  in_progress: number;
  completed: number;
  failed: number;
  canceled: number;
  paused?: boolean;
}

export default function QueuePage() {
  const [status, setStatus] = useState<QueueStatus | null>(null);
  const [items, setItems] = useState<QueueItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("");
  const [notice, setNotice] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const s = await apiGet<QueueStatus>("/invokeai/queue/status");
      setStatus(s);
      const list = await apiGet<{ items: QueueItem[] }>("/invokeai/queue/list");
      setItems(list.items ?? []);
    } catch {
      setStatus(null);
      setItems([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
    const id = setInterval(load, 5000);
    return () => clearInterval(id);
  }, [load]);

  const act = async (operation: string, itemId?: number) => {
    const res = await apiPost<{ success: boolean; message?: string }>(
      "/invokeai/queue",
      {
        operation,
        item_id: itemId,
      },
    );
    setNotice(res.message ?? "");
    void load();
  };

  const shown = filter
    ? items.filter((i) => (i.status ?? "").toLowerCase() === filter)
    : items;

  return (
    <div className="mx-auto max-w-6xl p-6" data-testid="queue-page">
      <PageHeader
        title="Queue"
        subtitle="Live generation queue - polls every 5s"
      />
      {notice && <p className="mb-3 text-xs text-emerald-300">{notice}</p>}

      <div className="mb-5 grid grid-cols-2 gap-3 md:grid-cols-5">
        {(
          ["queued", "in_progress", "completed", "failed", "canceled"] as const
        ).map((k) => (
          <div
            key={k}
            className="rounded-lg border border-slate-800 bg-slate-900/60 p-3"
            data-testid={`queue-${k}`}
          >
            <div className="text-[11px] uppercase tracking-wide text-slate-400">
              {k.replace("_", " ")}
            </div>
            <div className="text-xl font-bold text-slate-100">
              {status?.[k] ?? 0}
            </div>
          </div>
        ))}
      </div>

      <div className="mb-4 flex flex-wrap items-center gap-2">
        <button
          onClick={() => act("resume")}
          className="flex items-center gap-1.5 rounded-md border border-emerald-500/40 bg-emerald-500/10 px-3 py-1.5 text-xs font-medium text-emerald-300 hover:bg-emerald-500/20"
          data-testid="queue-resume"
        >
          <Play className="h-3.5 w-3.5" /> Resume
        </button>
        <button
          onClick={() => act("pause")}
          className="flex items-center gap-1.5 rounded-md border border-slate-700 px-3 py-1.5 text-xs font-medium text-slate-400 hover:bg-slate-800"
        >
          Pause
        </button>
        <button
          onClick={() => act("clear")}
          className="flex items-center gap-1.5 rounded-md border border-red-500/40 bg-red-500/10 px-3 py-1.5 text-xs font-medium text-red-300 hover:bg-red-500/20"
          data-testid="queue-clear"
        >
          <Trash2 className="h-3.5 w-3.5" /> Clear
        </button>
        <button
          onClick={() => load()}
          className="flex items-center gap-1.5 rounded-md border border-slate-700 px-3 py-1.5 text-xs text-slate-400 hover:bg-slate-800"
        >
          <RefreshCw className="h-3.5 w-3.5" /> Refresh
        </button>
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="ml-auto rounded-md border border-slate-700 bg-slate-900 px-2 py-1.5 text-xs"
        >
          <option value="">All statuses</option>
          {["pending", "in_progress", "completed", "failed", "canceled"].map(
            (s) => (
              <option key={s}>{s}</option>
            ),
          )}
        </select>
      </div>

      {loading && <Spinner />}
      {!loading && shown.length === 0 && (
        <EmptyState
          icon={<ListOrdered className="h-8 w-8" />}
          title="Queue is empty"
          hint="Generate something, or nothing will show here."
        />
      )}
      <div className="space-y-2">
        {shown.map((item) => {
          const id = item.id ?? item.queue_item_id;
          const st = item.status ?? "unknown";
          return (
            <div
              key={id}
              className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-900/60 px-4 py-3"
              data-testid="queue-item"
            >
              <div className="flex items-center gap-3">
                <span
                  className={`rounded-full px-2 py-0.5 text-[11px] font-semibold ${
                    st === "completed"
                      ? "bg-emerald-500/15 text-emerald-300"
                      : st === "failed"
                        ? "bg-red-500/15 text-red-300"
                        : st === "in_progress"
                          ? "bg-amber-500/15 text-amber-300"
                          : "bg-slate-700/40 text-slate-400"
                  }`}
                >
                  {st.replace("_", " ")}
                </span>
                <span className="text-xs text-slate-400">#{id}</span>
                <code className="hidden max-w-40 truncate rounded bg-slate-800 px-1.5 py-0.5 text-[11px] text-slate-400 md:block">
                  {item.batch_id}
                </code>
              </div>
              <div className="flex items-center gap-2">
                {(st === "pending" || st === "in_progress") && (
                  <button
                    onClick={() => act("cancel", id)}
                    className="text-slate-400 hover:text-red-400"
                    title="Cancel"
                  >
                    <XCircle className="h-4 w-4" />
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
