import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const backend = process.env.VITE_API_TARGET || "http://127.0.0.1:11154";

export default defineConfig({
  plugins: [react()],
  server: {
    port: Number(process.env.VITE_PORT || 11155),
    host: true,
    proxy: {
      "/api": { target: backend, changeOrigin: true },
      "/mcp": { target: backend, changeOrigin: true, ws: true },
    },
  },
  build: { outDir: "dist", sourcemap: false },
});
