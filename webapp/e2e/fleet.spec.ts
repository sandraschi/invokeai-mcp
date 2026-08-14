import { test, expect } from "@playwright/test";

const BE = "http://127.0.0.1:11154";
const FE = "http://127.0.0.1:11155";

test.describe("Fleet Audit", () => {
  test("Backend health", async ({ request }) => {
    const resp = await request.get(`${BE}/api/health`);
    expect(resp.status()).toBe(200);
    const body = await resp.json();
    expect(body.server).toBe("invokeai-mcp");
    expect(typeof body.configured).toBe("boolean");
  });

  test("Tools discovery", async ({ request }) => {
    const resp = await request.get(`${BE}/api/tools`);
    expect(resp.status()).toBe(200);
    const body = await resp.json();
    expect(body.tools.length).toBeGreaterThan(10);
    const names = body.tools.map((t: { name: string }) => t.name);
    expect(names).toContain("invokeai_generate");
    expect(names).toContain("invokeai_queue");
  });

  test("Frontend loads without console errors", async ({ page }) => {
    const errors: string[] = [];
    page.on("console", (msg) => {
      if (msg.type() === "error") errors.push(msg.text());
    });
    page.on("pageerror", (err) => errors.push(String(err)));
    await page.goto(FE, { timeout: 20000 });
    await page.waitForTimeout(4000);
    await expect(page.locator("#root")).toBeAttached();
    expect(errors).toEqual([]);
  });

  test("Dashboard renders KPIs", async ({ page }) => {
    await page.goto(`${FE}/app/dashboard`);
    await expect(page.locator('[data-testid="dashboard"]')).toBeVisible({ timeout: 20000 });
    await expect(page.locator('[data-testid="kpi-server"]')).toBeVisible();
    await expect(page.locator('[data-testid="kpi-tools"]')).toBeVisible();
    await expect(page.locator('[data-testid="backend-dot"]')).toBeVisible();
  });

  test("Navigation covers main pages", async ({ page }) => {
    await page.goto(`${FE}/app/dashboard`);
    for (const route of ["generate", "gallery", "models", "plugins", "queue", "boards", "workflows", "inbox", "tools", "skills", "chat", "settings", "help", "logs"]) {
      await page.goto(`${FE}/app/${route}`);
      await page.waitForTimeout(800);
      await expect(page.locator(`[data-testid="${route}-page"]`)).toBeAttached({ timeout: 10000 });
    }
  });

  test("Generate page surfaces all mode tabs", async ({ page }) => {
    await page.goto(`${FE}/app/generate`);
    await expect(page.locator('[data-testid="mode-tabs"]')).toBeVisible({ timeout: 15000 });
    for (const tab of ["txt2img", "img2img", "inpaint", "outpaint", "upscale", "controlnet", "ipadapter", "seamless"]) {
      await expect(page.locator(`[data-testid="mode-tab-${tab}"]`)).toBeAttached();
    }
    await expect(page.locator('[data-testid="batch-panel-toggle"]')).toBeVisible();
    await page.locator('[data-testid="batch-panel-toggle"]').click();
    await expect(page.locator('[data-testid="style-checks"]')).toBeVisible();
  });

  test("Plugins page lists capabilities", async ({ page }) => {
    await page.goto(`${FE}/app/plugins`);
    await expect(page.locator('[data-testid="plugins-page"]')).toBeVisible({ timeout: 15000 });
    await expect(page.locator('[data-testid="plugins-capabilities"]')).toBeVisible();
  });

  test("Settings probes LLM providers", async ({ page }) => {
    await page.goto(`${FE}/app/settings`);
    await expect(page.locator('[data-testid="llm-provider-select"]')).toBeVisible({ timeout: 15000 });
  });
});
