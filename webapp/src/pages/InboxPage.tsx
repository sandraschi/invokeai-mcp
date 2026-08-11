import {
  CheckCircle2,
  Inbox as InboxIcon,
  Loader2,
  XCircle,
} from "lucide-react";
import { useEffect, useState } from "react";
import { EmptyState, PageHeader, Spinner } from "../components/ui";
import { apiGet } from "../lib/api";

interface QueueItem {
  id?: number;
  queue_item_id?: number;
  status?: string;
  destination?: string;
  batch_id?: string;
  created_at?: string;
}

export default function InboxPage() {
  const [items, setItems] = useState<QueueItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await apiGet<{ items: QueueItem[] }>(
          "/invokeai/queue/list?limit=30",
        );
        const recent = (data.items ?? []).filter(
          (i) => (i.status ?? "") !== "pending",
        );
        setItems(recent);
      } catch {
        setItems([]);
      } finally {
        setLoading(false);
      }
    };
    load();
    const id = setInterval(load, 8000);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="mx-auto max-w-4xl p-6" data-testid="inbox-page">
      <PageHeader
        title="Inbox"
        subtitle="Recent generation events - completed, failed, and canceled jobs"
      />
      {loading && <Spinner />}
      {!loading && items.length === 0 && (
        <EmptyState
          icon={<InboxIcon className="h-8 w-8" />}
          title="Nothing here yet"
          hint="Completed generation jobs will appear in this feed."
        />
      )}
      <div className="space-y-2">
        {items.map((item) => {
          const id = item.id ?? item.queue_item_id;
          const st = item.status ?? "unknown";
          const ok = st === "completed";
          const fail = st === "failed" || st === "canceled";
          return (
            <div
              key={id}
              className="flex items-center gap-3 rounded-lg border border-slate-800 bg-slate-900/60 px-4 py-3"
              data-testid="inbox-item"
            >
              {ok ? (
                <CheckCircle2 className="h-5 w-5 shrink-0 text-emerald-400" />
              ) : fail ? (
                <XCircle className="h-5 w-5 shrink-0 text-red-400" />
              ) : (
                <Loader2 className="h-5 w-5 shrink-0 animate-spin text-amber-400" />
              )}
              <div className="min-w-0 flex-1">
                <div className="text-sm text-slate-200">
                  Queue item{" "}
                  <span className="font-mono text-amber-300">#{id}</span>{" "}
                  <span className="text-slate-500">
                    ({st.replace("_", " ")})
                  </span>
                </div>
                <div className="truncate text-[11px] text-slate-500">
                  batch: {item.batch_id} · destination:{" "}
                  {item.destination ?? "mcp"}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
