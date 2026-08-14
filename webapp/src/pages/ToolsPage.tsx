import { Blocks, ChevronDown, ChevronUp } from "lucide-react";
import { useEffect, useState } from "react";
import { EmptyState, PageHeader, Spinner } from "../components/ui";
import { apiGet } from "../lib/api";

interface ToolRec {
  name: string;
  description: string;
}

export default function ToolsPage() {
  const [tools, setTools] = useState<ToolRec[]>([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await apiGet<{ tools: ToolRec[] }>("/tools");
        setTools(data.tools ?? []);
      } catch {
        setTools([]);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  return (
    <div className="mx-auto max-w-5xl p-6" data-testid="tools-page">
      <PageHeader
        title="Tools"
        subtitle={`${tools.length} MCP tools discovered dynamically from the server`}
      />
      {loading && <Spinner />}
      {!loading && tools.length === 0 && (
        <EmptyState
          icon={<Blocks className="h-8 w-8" />}
          title="No tools discovered"
          hint="The server registers tools on boot; check backend logs."
        />
      )}
      <div className="space-y-2">
        {tools.map((t) => (
          <div
            key={t.name}
            className="rounded-lg border border-slate-800 bg-slate-900/60"
            data-testid="tool-row"
          >
            <button
              onClick={() => setOpen(open === t.name ? null : t.name)}
              className="flex w-full items-center justify-between px-4 py-3 text-left"
            >
              <div className="min-w-0">
                <code className="text-sm font-semibold text-amber-300">
                  {t.name}
                </code>
                <p className="mt-0.5 truncate text-xs text-slate-400">
                  {t.description}
                </p>
              </div>
              {open === t.name ? (
                <ChevronUp className="h-4 w-4 shrink-0 text-slate-400" />
              ) : (
                <ChevronDown className="h-4 w-4 shrink-0 text-slate-400" />
              )}
            </button>
            {open === t.name && (
              <div className="border-t border-slate-800 px-4 py-3">
                <p className="text-sm leading-relaxed text-slate-300">
                  {t.description}
                </p>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
