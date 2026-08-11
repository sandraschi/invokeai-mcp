import path from "node:path";
import { fileURLToPath } from "node:url";
import { test } from "@playwright/test";

const SHOTS = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../docs/screenshots");

test.describe("README screenshots", () => {
  test("capture dashboard and generate", async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.addInitScript(() => {
      document.documentElement.classList.add("dark");
    });

    await page.goto("/app/dashboard", { waitUntil: "networkidle" });
    await page.waitForTimeout(2500);
    await page.screenshot({ path: `${SHOTS}/dashboard.png`, fullPage: false });

    await page.goto("/app/generate", { waitUntil: "networkidle" });
    await page.waitForTimeout(1500);
    await page.screenshot({ path: `${SHOTS}/generate.png`, fullPage: false });
  });
});
