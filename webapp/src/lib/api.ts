/** API base for the webapp. Dev: Vite proxies /api to the backend (11154). */

export const API_BASE = "/api";

export async function apiGet<T>(path: string): Promise<T> {
  const r = await fetch(`${API_BASE}${path}`);
  if (!r.ok) throw new Error(`GET ${path} -> HTTP ${r.status}`);
  return (await r.json()) as T;
}

export async function apiPost<T>(path: string, body: unknown): Promise<T> {
  const r = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(`POST ${path} -> HTTP ${r.status}`);
  return (await r.json()) as T;
}
