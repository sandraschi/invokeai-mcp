import { Download, Eraser, MessageSquare, Send } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import { apiPost } from "../lib/api";
import { useLlmStore } from "../store/llm";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  ts?: string;
}

const HISTORY_KEY = "invokeai-mcp-chat-history";
const PERSONALITY_KEY = "invokeai-mcp-chat-personality";
const MAX_MESSAGES = 100;

const PERSONALITIES: Record<string, string> = {
  "Image Director":
    "You are an expert AI image director. Give concise creative guidance, suggest prompts, and recommend model/settings for the user's goals.",
  "Technical Reviewer":
    "You are a critical technical reviewer of AI art workflows. Point out parameter pitfalls, VRAM limits, and quality trade-offs.",
  "Quick Summarizer":
    "You respond very briefly. One or two sentences, no fluff.",
};

const EXAMPLES = [
  {
    group: "Creative",
    items: [
      "Neon cyberpunk city at night, rain",
      "Lighthouse at dusk, oil painting style",
      "Steampunk robot portrait, dramatic light",
    ],
  },
  {
    group: "Edit",
    items: [
      "Make this image a watercolor painting",
      "Upscale my last image 4x",
      "Regenerate the masked region",
    ],
  },
  {
    group: "Ops",
    items: [
      "What models do I have installed?",
      "Is the queue healthy?",
      "Install SDXL base from HuggingFace",
    ],
  },
];

export default function ChatPage() {
  const { selectedProvider, selectedModel } = useLlmStore();
  const [messages, setMessages] = useState<ChatMessage[]>(() => {
    try {
      return JSON.parse(
        localStorage.getItem(HISTORY_KEY) ?? "[]",
      ) as ChatMessage[];
    } catch {
      return [];
    }
  });
  const [input, setInput] = useState("");
  const [personality, setPersonality] = useState(
    () => localStorage.getItem(PERSONALITY_KEY) ?? "Image Director",
  );
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, busy]);

  const persist = useCallback((msgs: ChatMessage[]) => {
    const capped = msgs.slice(-MAX_MESSAGES);
    localStorage.setItem(HISTORY_KEY, JSON.stringify(capped));
  }, []);

  const send = async (raw?: string) => {
    const text = (raw ?? input).trim();
    if (!text || busy || !selectedModel) {
      if (!selectedModel)
        setError(
          "No local LLM selected - pick a provider and model in Settings.",
        );
      return;
    }
    setError("");
    const system = `${PERSONALITIES[personality] ?? PERSONALITIES["Image Director"]}\n\nYou are chatting from the InvokeAI MCP webapp. The user can generate images via the Generate page.`;
    const next = [
      ...messages,
      { role: "user" as const, content: text, ts: new Date().toISOString() },
    ];
    setMessages(next);
    persist(next);
    setInput("");
    setBusy(true);
    try {
      const res = await apiPost<{ content?: string; error?: string }>(
        "/llm/chat",
        {
          provider: selectedProvider,
          model: selectedModel,
          messages: [
            { role: "system", content: system },
            ...next.map(({ role, content }) => ({ role, content })),
          ],
        },
      );
      if (res.error) {
        setError(res.error);
      } else {
        const withReply = [
          ...next,
          {
            role: "assistant" as const,
            content: res.content ?? "",
            ts: new Date().toISOString(),
          },
        ];
        setMessages(withReply);
        persist(withReply);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "chat failed");
    } finally {
      setBusy(false);
    }
  };

  const clear = () => {
    setMessages([]);
    localStorage.removeItem(HISTORY_KEY);
  };

  const exportTxt = () => {
    const body = messages
      .map((m) => `[${m.ts ?? ""}] ${m.role}: ${m.content}`)
      .join("\n\n");
    const blob = new Blob([body], { type: "text/plain" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `invokeai-mcp-chat-${new Date().toISOString().slice(0, 19).replaceAll(":", "-")}.txt`;
    a.click();
    URL.revokeObjectURL(a.href);
  };

  return (
    <div
      className="mx-auto flex h-full max-w-4xl flex-col p-6"
      data-testid="chat-page"
    >
      <div className="mb-3 flex items-center gap-3" data-testid="chat-controls">
        <select
          value={personality}
          onChange={(e) => {
            setPersonality(e.target.value);
            localStorage.setItem(PERSONALITY_KEY, e.target.value);
          }}
          className="rounded-md border border-slate-700 bg-slate-900 px-2 py-1.5 text-xs"
          data-testid="personality-select"
        >
          {Object.keys(PERSONALITIES).map((p) => (
            <option key={p}>{p}</option>
          ))}
        </select>
        <span className="text-xs text-slate-500">
          {selectedModel
            ? `${selectedProvider}: ${selectedModel}`
            : "no LLM selected"}
        </span>
        <div className="ml-auto flex gap-2">
          <button
            onClick={exportTxt}
            disabled={!messages.length}
            className="flex items-center gap-1 rounded border border-slate-700 px-2 py-1.5 text-xs text-slate-400 hover:bg-slate-800 disabled:opacity-30"
            data-testid="chat-export"
          >
            <Download className="h-3.5 w-3.5" /> Export
          </button>
          <button
            onClick={clear}
            disabled={!messages.length}
            className="flex items-center gap-1 rounded border border-slate-700 px-2 py-1.5 text-xs text-slate-400 hover:bg-slate-800 disabled:opacity-30"
            data-testid="chat-clear"
          >
            <Eraser className="h-3.5 w-3.5" /> Clear
          </button>
        </div>
      </div>

      <div
        className="flex-1 space-y-4 overflow-y-auto rounded-xl border border-slate-800 bg-slate-900/40 p-4"
        data-testid="chat-messages"
      >
        {messages.length === 0 && (
          <div className="py-8 text-center">
            <MessageSquare className="mx-auto mb-2 h-8 w-8 text-slate-600" />
            <p className="text-sm text-slate-500">
              Ask about prompts, models, or workflows. Requires a local LLM
              (Settings).
            </p>
            <div
              className="mt-5 space-y-4 text-left"
              data-testid="example-prompts"
            >
              {EXAMPLES.map((g) => (
                <div key={g.group}>
                  <div className="mb-1 text-[11px] font-semibold uppercase tracking-wide text-slate-600">
                    {g.group}
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {g.items.map((ex) => (
                      <button
                        key={ex}
                        onClick={() => setInput(ex)}
                        className="rounded-full border border-slate-700 px-3 py-1 text-xs text-slate-400 hover:border-amber-500/50 hover:text-amber-300"
                      >
                        {ex}
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
        {messages.map((m, i) => (
          <div
            key={i}
            className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[80%] rounded-xl px-4 py-2.5 text-sm ${
                m.role === "user"
                  ? "bg-amber-500/15 text-slate-100"
                  : "border border-slate-800 bg-slate-900 text-slate-200"
              }`}
            >
              {m.role === "assistant" ? (
                <ReactMarkdown className="markdown-body">
                  {m.content}
                </ReactMarkdown>
              ) : (
                m.content
              )}
            </div>
          </div>
        ))}
        {busy && <div className="text-xs text-slate-500">Thinking...</div>}
        {error && (
          <div className="rounded-lg border border-red-500/40 bg-red-500/10 px-3 py-2 text-xs text-red-300">
            {error}
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="mt-3 flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
          placeholder="Ask about prompts, models, workflows..."
          className="flex-1 rounded-lg border border-slate-700 bg-slate-900 px-3 py-2.5 text-sm outline-none focus:border-amber-500/60"
          data-testid="chat-input"
        />
        <button
          onClick={() => send()}
          disabled={busy || !input.trim()}
          className="flex items-center gap-1.5 rounded-lg bg-amber-500 px-4 text-sm font-semibold text-slate-950 hover:bg-amber-400 disabled:opacity-40"
          data-testid="chat-send"
        >
          <Send className="h-4 w-4" /> Send
        </button>
      </div>
    </div>
  );
}
