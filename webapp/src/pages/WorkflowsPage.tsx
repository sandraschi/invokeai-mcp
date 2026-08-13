import { Workflow as WorkflowIcon } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import WorkflowGraph, { type NodeTpl } from "../components/WorkflowGraph";
import { EmptyState, PageHeader, Spinner } from "../components/ui";
import { apiGet, apiPost } from "../lib/api";

interface WorkflowRec {
  workflow_id: string;
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
  const [loaded, setLoaded] = useState<Record<string, unknown> | null>(null);
  const [templates, setTemplates] = useState<Record<string, NodeTpl>>({});
  const [json, setJson] = useState("");
  const [view, setView] = useState<"graph" | "json">("graph");
  const [saving, setSaving] = useState(false);
  const [notice, setNotice] = useState("");
  const [noticeErr, setNoticeErr] = useState(false);

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
    apiGet<{ templates?: Record<string, NodeTpl> }>(
      "/invokeai/workflow-templates",
    )
      .then((d) => setTemplates(d.templates ?? {}))
      .catch(() => setTemplates({}));
  }, [load]);

  const saveJson = async () => {
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
      setNoticeErr(!res.success);
      if (res.success) void load();
    } catch (e) {
      setNotice(e instanceof Error ? e.message : "save failed");
      setNoticeErr(true);
    } finally {
      setSaving(false);
    }
  };

  const open = async (w: WorkflowRec) => {
    setSelected(w);
    setView("graph");
    try {
      const res = await apiPost<{ success: boolean; data?: unknown }>(
        "/invokeai/workflows",
        {
          operation: "get",
          workflow_id: w.workflow_id,
        },
      );
      const data = (res.data ?? res) as Record<string, unknown>;
      setLoaded(data);
      setJson(JSON.stringify(data, null, 2));
    } catch {
      setLoaded(null);
      setJson("{}");
    }
  };

  const remove = async (id: string) => {
    await apiPost<{ success: boolean }>("/invokeai/workflows", {
      operation: "delete",
      workflow_id: id,
    });
    if (selected?.workflow_id === id) setSelected(null);
    void load();
  };

  const onSavedRecord = (rec: Record<string, unknown> | null, msg: string) => {
    setNotice(msg);
    setNoticeErr(false);
    const newId = (rec?.workflow_id as string) ?? (rec?.id as string);
    if (newId && selected && newId !== selected.workflow_id) {
      setNotice("Saved as a new user workflow - editing the copy now.");
      setSelected({
        workflow_id: newId,
        name: (rec?.name as string) ?? selected.name,
      });
    }
    void load();
  };

  const inputCls =
    "w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm outline-none focus:border-amber-500/60";

  return (
    <div className="mx-auto max-w-6xl p-6" data-testid="workflows-page">
      <PageHeader
        title="Workflows"
        subtitle="The node workflow library - graph editor or raw JSON"
      />
      {notice && (
        <p
          className={`mb-3 text-xs ${noticeErr ? "text-red-300" : "text-emerald-300"}`}
        >
          {notice}
        </p>
      )}

      <div className="grid gap-5 lg:grid-cols-[320px_1fr]">
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
                key={w.workflow_id}
                className={`flex items-center justify-between rounded-lg border px-4 py-3 ${
                  selected?.workflow_id === w.workflow_id
                    ? "border-amber-500/60 bg-slate-900"
                    : "border-slate-800 bg-slate-900/60"
                }`}
                data-testid="workflow-row"
              >
                <button onClick={() => open(w)} className="min-w-0 text-left">
                  <div className="truncate text-sm font-medium text-slate-200">
                    {w.name ?? w.workflow_id}
                  </div>
                  <div className="truncate text-[11px] text-slate-500">
                    {w.description ?? w.workflow_id}
                  </div>
                </button>
                {w.category !== "default" && (
                  <button
                    onClick={() => remove(w.workflow_id)}
                    className="ml-2 shrink-0 text-xs text-red-400/70 hover:text-red-400"
                    title="Delete"
                  >
                    delete
                  </button>
                )}
                {w.category === "default" && (
                  <span
                    className="ml-2 shrink-0 text-[10px] uppercase tracking-wide text-slate-600"
                    title="Engine defaults cannot be deleted; save edits a copy"
                  >
                    default
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
        <div>
          <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
            <div className="mb-2 flex items-center justify-between">
              <h2 className="text-sm font-semibold text-slate-200">
                {selected
                  ? `Edit: ${selected.name ?? selected.workflow_id}`
                  : "Select a workflow to edit"}
              </h2>
              <div className="flex items-center gap-2">
                {selected && (
                  <>
                    <div className="flex overflow-hidden rounded-md border border-slate-700 text-xs">
                      <button
                        onClick={() => setView("graph")}
                        className={`px-3 py-1.5 ${
                          view === "graph"
                            ? "bg-amber-500 font-semibold text-slate-950"
                            : "bg-slate-900 text-slate-300 hover:text-white"
                        }`}
                      >
                        Graph
                      </button>
                      <button
                        onClick={() => setView("json")}
                        className={`px-3 py-1.5 ${
                          view === "json"
                            ? "bg-amber-500 font-semibold text-slate-950"
                            : "bg-slate-900 text-slate-300 hover:text-white"
                        }`}
                      >
                        JSON
                      </button>
                    </div>
                    <button
                      onClick={() => {
                        setSelected(null);
                        setLoaded(null);
                      }}
                      className="text-xs text-slate-500 hover:text-slate-300"
                    >
                      Clear
                    </button>
                  </>
                )}
              </div>
            </div>

            {!selected && (
              <p className="py-16 text-center text-sm text-slate-500">
                Pick a workflow on the left - the graph editor shows nodes and
                connections, the JSON tab shows the raw artifact.
              </p>
            )}

            {selected && view === "graph" && loaded && (
              <WorkflowGraph
                workflow={loaded}
                templates={templates}
                onSaved={onSavedRecord}
                onError={(m) => {
                  setNotice(m);
                  setNoticeErr(true);
                }}
              />
            )}

            {selected && view === "json" && (
              <>
                <textarea
                  value={json}
                  onChange={(e) => setJson(e.target.value)}
                  rows={18}
                  className={`${inputCls} font-mono text-xs`}
                  placeholder='{"nodes": {...}, "edges": [...]}'
                  data-testid="workflow-json"
                />
                <button
                  onClick={saveJson}
                  disabled={saving || !json.trim()}
                  className="mt-3 w-full rounded-lg bg-amber-500 px-4 py-2 text-sm font-semibold text-slate-950 hover:bg-amber-400 disabled:opacity-40"
                  data-testid="workflow-save"
                >
                  {saving ? "Saving..." : "Save workflow"}
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
