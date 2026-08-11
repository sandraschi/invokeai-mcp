import { create } from "zustand";

export interface HealthState {
  configured: boolean | null;
  version: string;
  server: string;
  checking: boolean;
  check: () => Promise<void>;
}

export const useHealthStore = create<HealthState>((set) => ({
  configured: null,
  version: "",
  server: "",
  checking: false,

  check: async () => {
    set({ checking: true });
    try {
      const r = await fetch("/api/health");
      if (!r.ok) throw new Error(String(r.status));
      const data = (await r.json()) as {
        configured: boolean;
        version: string;
        server: string;
      };
      set({
        configured: data.configured,
        version: data.version,
        server: data.server,
        checking: false,
      });
    } catch {
      set({ configured: false, checking: false });
    }
  },
}));
