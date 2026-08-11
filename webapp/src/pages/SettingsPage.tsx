import { ArrowRight, Cpu, Zap } from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { PageHeader, SectionCard, StatusPill } from "../components/ui";
import { apiGet } from "../lib/api";
import { useHealthStore } from "../store/health";
import { useLlmStore } from "../store/llm";

export default function SettingsPage() {
  const configured = useHealthStore((s) => s.configured);
  const checkHealth = useHealthStore((s) => s.check);
  const {
    providers,
    status,
    selectedProvider,
    selectedModel,
    models,
    probing,
    setProvider,
    setModel,
    probe,
  } = useLlmStore();
  const [invokeaiUrl, setInvokeaiUrl] = useState("");
  const [version, setVersion] = useState("");

  useEffect(() => {
    const load = async () => {
      try {
        const s = await apiGet<{
          configured: boolean;
          invokeai_url: string;
          version?: string;
        }>("/invokeai/status");
        setInvokeaiUrl(s.invokeai_url);
        setVersion(s.version ?? "");
      } catch {
        /* ignore */
      }
    };
    load();
  }, []);

  return (
    <div className="mx-auto max-w-4xl p-6" data-testid="settings-page">
      <PageHeader
        title="Settings"
        subtitle="Engine connection and local intelligence"
      />

      <div className="space-y-5">
        <SectionCard title="InvokeAI engine" testid="settings-engine">
          <div className="mb-3 flex items-center gap-3">
            <StatusPill
              ok={configured !== false}
              label={
                configured === null
                  ? "Checking..."
                  : configured
                    ? "Connected"
                    : "Offline"
              }
            />
            {configured === false && (
              <Link
                to="/app/help"
                className="flex items-center gap-1 text-xs text-red-400 hover:text-red-300"
              >
                Complete onboarding <ArrowRight className="h-3.5 w-3.5" />
              </Link>
            )}
          </div>
          <div className="grid grid-cols-1 gap-3 text-sm md:grid-cols-3">
            <div className="rounded-lg border border-slate-800 bg-slate-950/50 p-3">
              <div className="flex items-center gap-1.5 text-[11px] uppercase text-slate-500">
                <Cpu className="h-3.5 w-3.5" /> URL
              </div>
              <code className="mt-1 block text-xs text-slate-300">
                {invokeaiUrl || "http://127.0.0.1:9090"}
              </code>
            </div>
            <div className="rounded-lg border border-slate-800 bg-slate-950/50 p-3">
              <div className="flex items-center gap-1.5 text-[11px] uppercase text-slate-500">
                <Zap className="h-3.5 w-3.5" /> Version
              </div>
              <div className="mt-1 text-xs text-slate-300">
                {version || "-"}
              </div>
            </div>
            <div className="rounded-lg border border-slate-800 bg-slate-950/50 p-3">
              <div className="flex items-center gap-1.5 text-[11px] uppercase text-slate-500">
                <Cpu className="h-3.5 w-3.5" /> Backend port
              </div>
              <div className="mt-1 text-xs text-slate-300">
                11154 (this app)
              </div>
            </div>
          </div>
          <button
            onClick={() => checkHealth()}
            className="mt-3 rounded-md border border-slate-700 px-3 py-1.5 text-xs text-slate-400 hover:bg-slate-800"
          >
            Re-check health
          </button>
        </SectionCard>

        <SectionCard
          title="Local intelligence (LLM for Chat)"
          testid="settings-llm"
        >
          <div className="mb-3 grid grid-cols-3 gap-3">
            {(["Ollama", "LM Studio", "vLLM"] as const).map((p) => (
              <div
                key={p}
                className="rounded-lg border border-slate-800 bg-slate-950/50 p-3 text-center"
                data-testid={`provider-${p.toLowerCase().replace(" ", "-")}`}
              >
                <div className="text-xs font-medium text-slate-300">{p}</div>
                <div
                  className={`mt-1 text-[11px] ${status[p] === "detected" ? "text-emerald-400" : status[p] === "probing" || probing ? "text-slate-500" : "text-slate-600"}`}
                >
                  {probing || status[p] === "probing"
                    ? "Probing..."
                    : status[p] === "detected"
                      ? "Detected"
                      : "Not found"}
                </div>
              </div>
            ))}
          </div>
          <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-500">
                Provider
              </label>
              <select
                value={selectedProvider}
                onChange={(e) => setProvider(e.target.value)}
                className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm"
                data-testid="llm-provider-select"
              >
                {providers.length === 0 && (
                  <option value="">No local LLM detected</option>
                )}
                {providers.map((p) => (
                  <option key={p.name} value={p.name}>
                    {p.name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-500">
                Model
              </label>
              <select
                value={selectedModel}
                onChange={(e) => setModel(e.target.value)}
                className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm"
                data-testid="llm-model-select"
              >
                {models.length === 0 && (
                  <option value="">No models found</option>
                )}
                {models.map((m) => (
                  <option key={m} value={m}>
                    {m}
                  </option>
                ))}
              </select>
            </div>
          </div>
          <button
            onClick={() => probe()}
            className="mt-3 rounded-md border border-slate-700 px-3 py-1.5 text-xs text-slate-400 hover:bg-slate-800"
          >
            Re-scan providers
          </button>
          {providers.length === 0 && (
            <p className="mt-3 text-xs text-amber-400/80">
              Install Ollama or LM Studio to enable AI features.
            </p>
          )}
        </SectionCard>

        <SectionCard title="About" testid="settings-about">
          <p className="text-xs leading-relaxed text-slate-500">
            invokeai-mcp v0.1.0 - fleet creative engine bridge. Backend 11154,
            webapp 11155. Wraps InvokeAI (port 9090). See{" "}
            <Link to="/app/help" className="text-amber-400">
              Help
            </Link>{" "}
            and docs/ONBOARDING.md for setup.
          </p>
        </SectionCard>
      </div>
    </div>
  );
}
