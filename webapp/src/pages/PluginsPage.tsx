import { Boxes, GitBranch, Package, RefreshCw, Trash2 } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { EmptyState, PageHeader, SectionCard, Spinner } from "../components/ui";
import { apiGet, apiPost } from "../lib/api";

interface NodePack {
  name: string;
  version?: string;
  node_types?: string[];
  workflows?: string[];
}

interface Capability {
  count: number;
  nodes: string[];
}

export default function PluginsPage() {
  const [packs, setPacks] = useState<NodePack[]>([]);
  const [capabilities, setCapabilities] = useState<Record<string, Capability>>(
    {},
  );
  const [source, setSource] = useState("");
  const [installing, setInstalling] = useState(false);
  const [reloading, setReloading] = useState(false);
  const [loading, setLoading] = useState(true);
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await apiGet<{
        packs: NodePack[];
        capabilities: Record<string, Capability>;
      }>("/invokeai/plugins");
      setPacks(data.packs ?? []);
      setCapabilities(data.capabilities ?? {});
    } catch (e) {
      setError(e instanceof Error ? e.message : "load failed");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const install = async () => {
    if (!source.trim()) return;
    setInstalling(true);
    setError("");
    setNotice("");
    try {
      const res = await apiPost<{ success: boolean; message?: string }>(
        "/invokeai/plugins/install",
        { source: source.trim() },
      );
      setNotice(res.message ?? (res.success ? "Installed" : "Install failed"));
      setSource("");
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "install failed");
    } finally {
      setInstalling(false);
    }
  };

  const uninstall = async (name: string) => {
    const r = await fetch(`/api/invokeai/plugins/${encodeURIComponent(name)}`, {
      method: "DELETE",
    });
    if (r.ok) {
      setNotice(`Uninstalled ${name}.`);
      await load();
    } else {
      setError(`Uninstall failed: HTTP ${r.status}`);
    }
  };

  const reload = async () => {
    setReloading(true);
    setError("");
    try {
      await apiPost("/invokeai/plugins/reload", {});
      setNotice("Custom nodes reloaded.");
    } catch (e) {
      setError(e instanceof Error ? e.message : "reload failed");
    } finally {
      setReloading(false);
    }
  };

  const totalCapabilities = Object.values(capabilities).reduce(
    (a, c) => a + c.count,
    0,
  );
  const inputCls =
    "rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm outline-none focus:border-amber-500/60";

  return (
    <div className="mx-auto max-w-6xl p-6" data-testid="plugins-page">
      <PageHeader
        title="Plugins"
        subtitle={`${packs.length} custom node packs + ${totalCapabilities} built-in engine nodes`}
      />
      {notice && <p className="mb-3 text-xs text-emerald-300">{notice}</p>}
      {error && <p className="mb-3 text-xs text-red-300">{error}</p>}

      <SectionCard title="Custom node packs" testid="plugins-packs">
        <div className="mb-4 flex gap-3">
          <input
            value={source}
            onChange={(e) => setSource(e.target.value)}
            placeholder="Git URL of the node pack (e.g. https://github.com/user/node-pack)"
            className={`${inputCls} flex-1`}
            data-testid="plugin-install-source"
          />
          <button
            onClick={install}
            disabled={installing || !source.trim()}
            className="flex items-center gap-1.5 rounded-lg bg-amber-500 px-4 py-2 text-sm font-semibold text-slate-950 hover:bg-amber-400 disabled:opacity-40"
            data-testid="plugin-install"
          >
            {installing ? (
              <Spinner label="" />
            ) : (
              <GitBranch className="h-4 w-4" />
            )}{" "}
            Install
          </button>
          <button
            onClick={reload}
            disabled={reloading}
            className="flex items-center gap-1.5 rounded-lg border border-slate-700 px-4 py-2 text-sm text-slate-400 hover:bg-slate-800 disabled:opacity-40"
            data-testid="plugin-reload"
          >
            {reloading ? (
              <Spinner label="" />
            ) : (
              <RefreshCw className="h-4 w-4" />
            )}{" "}
            Reload
          </button>
        </div>
        {loading && <Spinner />}
        {!loading && packs.length === 0 && (
          <EmptyState
            icon={<Package className="h-8 w-8" />}
            title="No custom node packs"
            hint="Install one from a git URL above - the engine clones it into its nodes directory."
          />
        )}
        <div className="space-y-2">
          {packs.map((p) => (
            <div
              key={p.name}
              className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-900/60 px-4 py-3"
              data-testid="plugin-row"
            >
              <div className="min-w-0">
                <div className="flex items-center gap-2 text-sm font-medium text-slate-200">
                  <Package className="h-4 w-4 text-amber-400/70" />
                  {p.name}
                  {p.version && (
                    <span className="rounded bg-slate-800 px-1.5 py-0.5 text-[11px] text-slate-400">
                      v{p.version}
                    </span>
                  )}
                </div>
                <div className="mt-1 text-[11px] text-slate-400">
                  {p.node_types?.length ?? 0} node type(s)
                  {p.workflows?.length
                    ? ` · ${p.workflows.length} workflow(s)`
                    : ""}
                </div>
              </div>
              <button
                onClick={() => uninstall(p.name)}
                className="text-slate-400 hover:text-red-400"
                title="Uninstall"
              >
                <Trash2 className="h-4 w-4" />
              </button>
            </div>
          ))}
        </div>
      </SectionCard>

      <div className="mt-5">
        <SectionCard
          title={`Built-in engine nodes (${totalCapabilities})`}
          testid="plugins-capabilities"
        >
          {Object.keys(capabilities).length === 0 ? (
            <Spinner />
          ) : (
            <div className="grid gap-2 md:grid-cols-2 lg:grid-cols-3">
              {Object.entries(capabilities)
                .sort((a, b) => b[1].count - a[1].count)
                .map(([cat, cap]) => (
                  <div
                    key={cat}
                    className="rounded-lg border border-slate-800 bg-slate-950/40 p-3"
                    data-testid={`capability-${cat}`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="flex items-center gap-1.5 text-sm font-medium text-slate-200">
                        <Boxes className="h-3.5 w-3.5 text-amber-400/70" />
                        {cat}
                      </span>
                      <span className="rounded-full bg-slate-800 px-2 py-0.5 text-[11px] text-slate-400">
                        {cap.count}
                      </span>
                    </div>
                    <div className="mt-1.5 flex flex-wrap gap-1">
                      {cap.nodes.map((n) => (
                        <code
                          key={n}
                          className="rounded bg-slate-900 px-1.5 py-0.5 text-[10px] text-slate-400"
                        >
                          {n.replace("Invocation", "")}
                        </code>
                      ))}
                      {cap.count > cap.nodes.length && (
                        <span className="text-[10px] text-slate-400">
                          +{cap.count - cap.nodes.length} more
                        </span>
                      )}
                    </div>
                  </div>
                ))}
            </div>
          )}
        </SectionCard>
      </div>
    </div>
  );
}
