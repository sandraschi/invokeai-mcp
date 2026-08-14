import { ArrowRight, Cpu, Zap } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
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
  const [hfStatus, setHfStatus] = useState("unknown");
  const [hfToken, setHfToken] = useState("");
  const [hfBusy, setHfBusy] = useState(false);
  const [hfMsg, setHfMsg] = useState("");
  const [hfErr, setHfErr] = useState("");
  const [engineRunning, setEngineRunning] = useState(false);
  const [engineVersion, setEngineVersion] = useState("");
  const [engineUrl, setEngineUrl] = useState("");
  const [engineBusy, setEngineBusy] = useState(false);
  const [engineMsg, setEngineMsg] = useState("");

  const loadEngine = useCallback(async () => {
    try {
      const r = await fetch("/api/invokeai/engine/status");
      if (r.ok) {
        const j = (await r.json()) as {
          running: boolean;
          version?: string | null;
          invokeai_url?: string;
        };
        setEngineRunning(j.running);
        setEngineVersion(j.version ?? "");
        setEngineUrl(j.invokeai_url ?? "");
      }
    } catch {
      /* degraded */
    }
  }, []);

  useEffect(() => {
    loadEngine();
  }, [loadEngine]);

  const engineStart = async () => {
    setEngineBusy(true);
    setEngineMsg("");
    try {
      const r = await fetch("/api/invokeai/engine/start", { method: "POST" });
      const j = (await r.json()) as {
        success: boolean;
        message?: string;
        error?: string;
      };
      setEngineMsg(
        j.message ?? (j.success ? "Engine starting." : "Start failed."),
      );
      await new Promise((res) => setTimeout(res, 8000));
      await loadEngine();
    } finally {
      setEngineBusy(false);
    }
  };

  const engineStop = async () => {
    setEngineBusy(true);
    setEngineMsg("");
    try {
      await fetch("/api/invokeai/engine/stop", { method: "POST" });
      setEngineRunning(false);
      setEngineMsg("Engine stopped.");
    } finally {
      setEngineBusy(false);
    }
  };

  const loadHf = useCallback(async () => {
    try {
      const r = await fetch("/api/invokeai/hf/status");
      if (r.ok) {
        const j = (await r.json()) as { status: string };
        setHfStatus(j.status);
      }
    } catch {
      /* degraded */
    }
  }, []);

  useEffect(() => {
    loadHf();
  }, [loadHf]);

  const hfLogin = async () => {
    setHfBusy(true);
    setHfErr("");
    setHfMsg("");
    try {
      const r = await fetch("/api/invokeai/hf/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token: hfToken.trim() }),
      });
      const j = (await r.json()) as {
        success: boolean;
        status?: string;
        error?: string;
      };
      if (j.success) {
        setHfStatus(j.status ?? "unknown");
        setHfMsg(
          j.status === "valid"
            ? "Logged in - gated models now installable."
            : "Token accepted (unverified).",
        );
        setHfToken("");
      } else {
        setHfErr(j.error ?? "login failed");
      }
    } catch (e) {
      setHfErr(e instanceof Error ? e.message : "login failed");
    } finally {
      setHfBusy(false);
    }
  };

  const hfLogout = async () => {
    try {
      await fetch("/api/invokeai/hf/logout", { method: "DELETE" });
      setHfStatus("invalid");
      setHfMsg("Logged out.");
    } catch {
      /* ignore */
    }
  };
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
              <div className="flex items-center gap-1.5 text-[11px] uppercase text-slate-400">
                <Cpu className="h-3.5 w-3.5" /> URL
              </div>
              <code className="mt-1 block text-xs text-slate-300">
                {invokeaiUrl || "http://127.0.0.1:9090"}
              </code>
            </div>
            <div className="rounded-lg border border-slate-800 bg-slate-950/50 p-3">
              <div className="flex items-center gap-1.5 text-[11px] uppercase text-slate-400">
                <Zap className="h-3.5 w-3.5" /> Version
              </div>
              <div className="mt-1 text-xs text-slate-300">
                {version || "-"}
              </div>
            </div>
            <div className="rounded-lg border border-slate-800 bg-slate-950/50 p-3">
              <div className="flex items-center gap-1.5 text-[11px] uppercase text-slate-400">
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
                  className={`mt-1 text-[11px] ${status[p] === "detected" ? "text-emerald-400" : status[p] === "probing" || probing ? "text-slate-400" : "text-slate-400"}`}
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
              <label className="mb-1 block text-xs font-medium text-slate-400">
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
              <label className="mb-1 block text-xs font-medium text-slate-400">
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

        <SectionCard title="Engine control" testid="settings-engine-control">
          <div className="mb-3 flex items-center gap-3">
            <StatusPill
              ok={engineRunning}
              label={engineRunning ? `Running (v${engineVersion})` : "Stopped"}
            />
            <a
              href={engineUrl || "http://127.0.0.1:9090"}
              target="_blank"
              rel="noreferrer"
              className="text-xs text-amber-400 hover:text-amber-300"
            >
              Open InvokeAI canvas UI
            </a>
          </div>
          <div className="flex gap-2">
            <button
              onClick={engineStart}
              disabled={engineBusy || engineRunning}
              className="rounded-lg bg-amber-500 px-4 py-2 text-sm font-semibold text-slate-950 hover:bg-amber-400 disabled:opacity-40"
              data-testid="engine-start"
            >
              {engineBusy ? "..." : "Start engine"}
            </button>
            <button
              onClick={engineStop}
              disabled={engineBusy || !engineRunning}
              className="rounded-lg border border-red-500/40 bg-red-500/10 px-4 py-2 text-sm text-red-300 hover:bg-red-500/20 disabled:opacity-40"
              data-testid="engine-stop"
            >
              Stop engine
            </button>
          </div>
          {engineMsg && (
            <p className="mt-2 text-xs text-emerald-300">{engineMsg}</p>
          )}
          <p
            className="mt-3 text-[11px] leading-relaxed text-slate-400"
            data-testid="engine-note"
          >
            The engine (InvokeAI 6.13.7, canvas GUI on 9090) is a separate
            process. This card starts, stops, and reports it - generation tools
            show 'offline' while it is stopped. Models live on
            N:\InvokeAI-models.
          </p>
        </SectionCard>

        <SectionCard title="HuggingFace" testid="settings-hf">
          <div className="mb-3 flex items-center gap-3">
            <StatusPill
              ok={hfStatus === "valid"}
              label={
                hfStatus === "valid"
                  ? "Logged in"
                  : hfStatus === "unknown"
                    ? "Token present, unverified"
                    : "Anonymous"
              }
            />
            <span className="text-xs text-slate-400" data-testid="hf-status">
              {hfStatus === "valid"
                ? "Gated models (FLUX.1, SD3.5) are installable."
                : "Login to install gated HuggingFace models."}
            </span>
          </div>
          <div className="flex gap-2">
            <input
              type="password"
              value={hfToken}
              onChange={(e) => setHfToken(e.target.value)}
              placeholder="hf_... (HuggingFace access token)"
              className="flex-1 rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm outline-none focus:border-amber-500/60"
              data-testid="hf-token-input"
            />
            <button
              onClick={hfLogin}
              disabled={hfBusy || !hfToken.trim()}
              className="shrink-0 rounded-lg bg-amber-500 px-4 py-2 text-sm font-semibold text-slate-950 hover:bg-amber-400 disabled:opacity-40"
              data-testid="hf-login"
            >
              {hfBusy ? "Logging in..." : "Login"}
            </button>
            {hfStatus === "valid" && (
              <button
                onClick={hfLogout}
                className="shrink-0 rounded-lg border border-slate-700 px-4 py-2 text-sm text-slate-400 hover:bg-slate-800"
                data-testid="hf-logout"
              >
                Logout
              </button>
            )}
          </div>
          {hfMsg && <p className="mt-2 text-xs text-emerald-300">{hfMsg}</p>}
          {hfErr && <p className="mt-2 text-xs text-red-300">{hfErr}</p>}
          <p className="mt-3 text-[11px] leading-relaxed text-slate-400">
            The token is stored by the InvokeAI engine (HF login) and used for
            gated model downloads. Create one at huggingface.co/settings/tokens
            (read scope is enough).
          </p>
        </SectionCard>

        <SectionCard title="About" testid="settings-about">
          <p className="text-xs leading-relaxed text-slate-400">
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
