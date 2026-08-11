/** Local LLM provider probe (Ollama > LM Studio > vLLM). */

export interface LlmProvider {
  name: string;
  port: number;
  base: string;
}

export async function discoverProviders(): Promise<LlmProvider[]> {
  const r = await fetch("/api/llm/discover");
  if (!r.ok) return [];
  const data = (await r.json()) as { providers: LlmProvider[] };
  return data.providers ?? [];
}

export async function fetchModels(base: string): Promise<string[]> {
  try {
    const r = await fetch(`${base}/models`, {
      signal: AbortSignal.timeout(5000),
    });
    if (!r.ok) return [];
    const data = (await r.json()) as { data?: { id: string }[] };
    return (data.data ?? []).map((m) => m.id);
  } catch {
    return [];
  }
}

export function baseFor(name: string): string {
  if (name === "LM Studio") return "http://127.0.0.1:1234/v1";
  if (name === "vLLM") return "http://127.0.0.1:8000/v1";
  return "http://127.0.0.1:11434/v1";
}
