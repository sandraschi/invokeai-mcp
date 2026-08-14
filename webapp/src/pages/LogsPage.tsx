import { Terminal } from "lucide-react";
import { useEffect, useState } from "react";
import { EmptyState, PageHeader, Spinner } from "../components/ui";
import { apiGet } from "../lib/api";

interface LogEntry {
  timestamp: string;
  level: string;
  source: string;
  message: string;
}

export default function LogsPage() {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [level, setLevel] = useState("");
  const [search, setSearch] = useState("");

  const load = async () => {
    setLoading(true);
    try {
      const q = new URLSearchParams();
      if (level) q.set("level", level);
      if (search) q.set("search", search);
      q.set("limit", "200");
      const data = await apiGet<{ logs: LogEntry[] }>(`/logs?${q.toString()}`);
      setLogs(data.logs ?? []);
    } catch {
      setLogs([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    const id = setInterval(load, 5000);
    return () => clearInterval(id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [level, search]);

  const color = (lvl: string) =>
    lvl === "ERROR"
      ? "text-red-400"
      : lvl === "WARNING"
        ? "text-amber-400"
        : lvl === "DEBUG"
          ? "text-slate-400"
          : "text-slate-400";

  return (
    <div className="mx-auto max-w-5xl p-6" data-testid="logs-page">
      <PageHeader
        title="Logs"
        subtitle="Backend ring buffer - auto-refreshes every 5s"
      />
      <div className="mb-3 flex gap-3">
        <select
          value={level}
          onChange={(e) => setLevel(e.target.value)}
          className="rounded-md border border-slate-700 bg-slate-900 px-2 py-1.5 text-xs"
        >
          <option value="">All levels</option>
          {["INFO", "WARNING", "ERROR", "DEBUG"].map((l) => (
            <option key={l}>{l}</option>
          ))}
        </select>
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search messages..."
          className="flex-1 rounded-md border border-slate-700 bg-slate-900 px-3 py-1.5 text-xs outline-none focus:border-amber-500/60"
        />
      </div>
      {loading && <Spinner />}
      {!loading && logs.length === 0 && (
        <EmptyState
          icon={<Terminal className="h-8 w-8" />}
          title="No log entries"
          hint="Backend events appear here."
        />
      )}
      <div
        className="rounded-xl border border-slate-800 bg-slate-950/80 font-mono text-xs"
        data-testid="log-view"
      >
        {logs.map((l, i) => (
          <div
            key={i}
            className="flex gap-3 border-b border-slate-900 px-3 py-1.5 last:border-0"
          >
            <span className="shrink-0 text-slate-400">{l.timestamp}</span>
            <span className={`w-16 shrink-0 font-semibold ${color(l.level)}`}>
              {l.level}
            </span>
            <span className="w-32 shrink-0 truncate text-slate-400">
              {l.source}
            </span>
            <span className="text-slate-300">{l.message}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
