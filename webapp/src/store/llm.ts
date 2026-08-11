import { create } from "zustand";
import { persist } from "zustand/middleware";
import { type LlmProvider, baseFor } from "../lib/provider";

interface LlmState {
  providers: LlmProvider[];
  status: Record<string, "probing" | "detected" | "not_found">;
  selectedProvider: string;
  selectedModel: string;
  models: string[];
  probing: boolean;
  probe: () => Promise<void>;
  setProvider: (name: string) => Promise<void>;
  setModel: (model: string) => void;
}

export const useLlmStore = create<LlmState>()(
  persist(
    (set, get) => ({
      providers: [],
      status: {},
      selectedProvider: "",
      selectedModel: "",
      models: [],
      probing: false,

      probe: async () => {
        set({ probing: true });
        const { discoverProviders, fetchModels } = await import(
          "../lib/provider"
        );
        const found = await discoverProviders();
        const status: Record<string, "probing" | "detected" | "not_found"> = {};
        for (const p of ["Ollama", "LM Studio", "vLLM"]) {
          status[p] = found.some((f) => f.name === p)
            ? "detected"
            : "not_found";
        }
        let selected = get().selectedProvider;
        if (!selected || !found.some((f) => f.name === selected)) {
          selected = found[0]?.name ?? "";
        }
        let models: string[] = [];
        if (selected) {
          models = await fetchModels(baseFor(selected));
        }
        const savedModel = get().selectedModel;
        set({
          providers: found,
          status,
          selectedProvider: selected,
          models,
          selectedModel: models.includes(savedModel)
            ? savedModel
            : (models[0] ?? ""),
          probing: false,
        });
      },

      setProvider: async (name) => {
        set({ selectedProvider: name, selectedModel: "" });
        const { fetchModels } = await import("../lib/provider");
        const models = await fetchModels(baseFor(name));
        set({ models, selectedModel: models[0] ?? "" });
      },

      setModel: (model) => set({ selectedModel: model }),
    }),
    {
      name: "llm-provider-store",
      partialize: (s) => ({
        selectedProvider: s.selectedProvider,
        selectedModel: s.selectedModel,
      }),
    },
  ),
);
