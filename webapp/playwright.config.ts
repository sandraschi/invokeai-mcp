import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  timeout: 60000,
  retries: 1,
  use: {
    baseURL: "http://127.0.0.1:11155",
    headless: true,
    screenshot: "only-on-failure",
  },
  webServer: {
    command:
      "uv run python -m invokeai_mcp.server --mode http --port 11154",
    port: 11154,
    cwd: "../",
    timeout: 60000,
    reuseExistingServer: true,
  },
  projects: [
    {
      name: "fleet-audit",
      testMatch: /(fleet|screenshots)\.spec\.ts/,
      use: { baseURL: "http://127.0.0.1:11155" },
    },
  ],
});


