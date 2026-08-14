import {
  BookOpen,
  Database,
  HelpCircle,
  Layers,
  Terminal,
  Wand2,
} from "lucide-react";
import { Link } from "react-router-dom";
import { PageHeader, SectionCard } from "../components/ui";

const LINKS = [
  { href: "https://github.com/invoke-ai/InvokeAI", label: "InvokeAI GitHub" },
  { href: "https://invoke.ai", label: "InvokeAI docs" },
  { href: "https://discord.gg/ZmtBAhwWhy", label: "InvokeAI Discord" },
  {
    href: "https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0",
    label: "SDXL on HuggingFace",
  },
];

export default function HelpPage() {
  return (
    <div className="mx-auto max-w-4xl p-6" data-testid="help-page">
      <PageHeader
        title="Help"
        subtitle="Architecture, ports, environment, and troubleshooting"
      />

      <div className="space-y-5">
        <SectionCard title="What is this?" testid="help-overview">
          <p className="text-sm leading-relaxed text-slate-300">
            invokeai-mcp bridges AI coding agents and this dashboard to your
            local InvokeAI creative engine. Generate images (txt2img, img2img,
            masked inpaint, 4x upscale), manage the queue, install models,
            browse the gallery, and organize boards - all on your own GPU.
            InvokeAI runs separately (launcher install) and is never bundled.
          </p>
        </SectionCard>

        <SectionCard title="Architecture" testid="help-architecture">
          <div className="space-y-1 font-mono text-xs text-slate-400">
            <div>
              Claude / Cursor / opencode (stdio) -&gt; invokeai-mcp (11154)
            </div>
            <div>
              Browser -&gt; Vite webapp (11155) -&gt; /api -&gt; invokeai-mcp
              (11154)
            </div>
            <div>invokeai-mcp -&gt; InvokeAI REST API (127.0.0.1:9090)</div>
            <div className="pt-2 text-slate-400">
              MCP transport: /mcp (streamable HTTP) + stdio
            </div>
          </div>
        </SectionCard>

        <SectionCard title="Key pages" testid="help-pages">
          <div className="grid gap-2 text-sm md:grid-cols-2">
            {[
              {
                to: "/app/generate",
                icon: Wand2,
                label: "Generate",
                desc: "Prompt, settings, enqueue, live result",
              },
              {
                to: "/app/models",
                icon: Layers,
                label: "Models",
                desc: "Install from HF/Civitai, browse, delete",
              },
              {
                to: "/app/queue",
                icon: Terminal,
                label: "Queue",
                desc: "Live status, cancel, clear, resume",
              },
              {
                to: "/app/gallery",
                icon: Database,
                label: "Gallery",
                desc: "Search, star, download, delete images",
              },
              {
                to: "/app/settings",
                icon: HelpCircle,
                label: "Settings",
                desc: "Engine health + local LLM config",
              },
              {
                to: "/app/logs",
                icon: BookOpen,
                label: "Logs",
                desc: "Server ring-buffer log",
              },
            ].map(({ to, icon: Icon, label, desc }) => (
              <Link
                key={to}
                to={to}
                className="flex items-start gap-3 rounded-lg border border-slate-800 bg-slate-950/40 p-3 hover:border-amber-500/40"
              >
                <Icon className="mt-0.5 h-4 w-4 shrink-0 text-amber-400" />
                <div>
                  <div className="font-medium text-slate-200">{label}</div>
                  <div className="text-xs text-slate-400">{desc}</div>
                </div>
              </Link>
            ))}
          </div>
        </SectionCard>

        <SectionCard title="Environment" testid="help-env">
          <table className="w-full text-xs">
            <thead>
              <tr className="text-left text-slate-400">
                <th className="py-1">Variable</th>
                <th>Default</th>
                <th>Purpose</th>
              </tr>
            </thead>
            <tbody className="font-mono text-slate-400">
              <tr>
                <td className="py-1">INVOKEAI_URL</td>
                <td>http://127.0.0.1:9090</td>
                <td className="font-sans">Engine base URL</td>
              </tr>
              <tr>
                <td className="py-1">INVOKEAI_MCP_PORT</td>
                <td>11154</td>
                <td className="font-sans">Backend port</td>
              </tr>
              <tr>
                <td className="py-1">INVOKEAI_FRONTEND_PORT</td>
                <td>11155</td>
                <td className="font-sans">Webapp port</td>
              </tr>
              <tr>
                <td className="py-1">INVOKEAI_DOWNLOAD_DIR</td>
                <td>data/downloads</td>
                <td className="font-sans">Download folder</td>
              </tr>
            </tbody>
          </table>
        </SectionCard>

        <SectionCard title="External resources" testid="help-links">
          <ul className="space-y-1 text-sm">
            {LINKS.map((l) => (
              <li key={l.href}>
                <a
                  href={l.href}
                  target="_blank"
                  rel="noreferrer"
                  className="text-amber-400 hover:text-amber-300"
                >
                  {l.label}
                </a>
              </li>
            ))}
          </ul>
        </SectionCard>
      </div>
    </div>
  );
}
