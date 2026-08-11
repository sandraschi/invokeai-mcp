import { Workflow as WorkflowIcon } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { EmptyState, PageHeader, Spinner } from "../components/ui";
import { apiGet, apiPost } from "../lib/api";

interface WorkflowRec {
  id: string;
  name?: string;
  description?: string;
  category?: string;
  created_at?: string;
  updated_at?: string;
}

export default function WorkflowsPage() {
  const [workflows, setWorkflows] = useState<WorkflowRec[]>([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<WorkflowRec | null>(null);
  const [json, setJson] = useState("");
  const [saving, setSaving] = useState(false);
  const [notice, setNotice] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await apiGet<{ workflows: WorkflowRec[] }>(
        "/invokeai/workflows",
      );
      setWorkflows(data.workflows ?? []);
    } catch {
      setWorkflows([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const save = async () => {
    setSaving(true);
    setNotice("");
    try {
      const res = await apiPost<{ success: boolean; message?: string }>(
        "/invokeai/workflows",
        {
          operation: "save",
          workflow_json: json,
        },
      );
      setNotice(res.message ?? (res.success ? "Saved" : "Save failed"));
      if (res.success) void load();
    } catch (e) {
      setNotice(e instanceof Error ? e.message : "save failed");
    } finally {
      setSaving(false);
    }
  };

  const open = async (w: WorkflowRec) => {
    setSelected(w);
    try {
      const res = await apiPost<{ success: boolean; data?: unknown }>(
        "/invokeai/workflows",
        {
          operation: "get",
          workflow_id: w.id,
        },
      );
      setJson(JSON.stringify(res.data ?? res, null, 2));
    } catch {
      setJson("{}");
    }
  };

  const remove = async (id: string) => {
    await apiPost<{ success: boolean }>("/invokeai/workflows", {
      operation: "delete",
      workflow_id: id,
    });
    if (selected?.id === id) setSelected(null);
    void load();
  };

  const inputCls =
    "w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm outline-none focus:border-amber-500/60";

  return (
    <div className="mx-auto max-w-6xl p-6" data-testid="workflows-page">
      <PageHeader
        title="Workflows"
        subtitle="The node workflow library - save, load, and inspect"
      />
      {notice && <p className="mb-3 text-xs text-emerald-300">{notice}</p>}

      <div className="grid gap-5 lg:grid-cols-2">
        <div>
          {loading && <Spinner />}
          {!loading && workflows.length === 0 && (
            <EmptyState
              icon={<WorkflowIcon className="h-8 w-8" />}
              title="No workflows"
              hint="Save a workflow from the InvokeAI editor to see it here."
            />
          )}
          <div className="space-y-2">
            {workflows.map((w) => (
              <div
                key={w.id}
                className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-900/60 px-4 py-3"
                data-testid="workflow-row"
              >
                <button onClick={() => open(w)} className="min-w-0 text-left">
                  <div className="truncate text-sm font-medium text-slate-200">
                    {w.name ?? w.id}
                  </div>
                  <div className="truncate text-[11px] text-slate-500">
                    {w.description ?? w.id}
                  </div>
                </button>
                <button
                  onClick={() => remove(w.id)}
                  className="ml-2 shrink-0 text-slate-500 hover:text-red-400"
                  title="Delete"
                >
                  <WorkflowIcon className="h-4 w-4 opacity-0" />
                </button>
              </div>
            ))}
          </div>
        </div>
        <div>
          <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
            <div className="mb-2 flex items-center justify-between">
              <h2 className="text-sm font-semibold text-slate-200">
                {selected
                  ? `Edit: ${selected.name ?? selected.id}`
                  : "New / edit workflow JSON"}
              </h2>
              <button
                onClick={() => setSelected(null)}
                className="text-xs text-slate-500 hover:text-slate-300"
              >
                Clear
              </button>
            </div>
            <textarea
              value={json}
              onChange={(e) => setJson(e.target.value)}
              rows={18}
              className={`${inputCls} font-mono text-xs`}
              placeholder='{"nodes": {...}, "edges": [...]}'
              data-testid="workflow-json"
            />
            <button
              onClick={save}
              disabled={saving || !json.trim()}
              className="mt-3 w-full rounded-lg bg-amber-500 px-4 py-2 text-sm font-semibold text-slate-950 hover:bg-amber-400 disabled:opacity-40"
              data-testid="workflow-save"
            >
              {saving ? "Saving..." : "Save workflow"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
