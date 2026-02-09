import { test, expect } from "@playwright/test";

test.describe("Navigation", () => {
    test.beforeEach(async ({ page }) => {
        // Login before each test
        await page.goto("/queue/management/dashboard/");
        await page.fill("input[name='userId']", "testuser");
        await page.click("button[type='submit'], nve-button[type='submit']");
        await expect(page).toHaveURL(/\/tasks/);
    });

    test("can navigate to Tasks", async ({ page }) => {
        await page.click("text=Tasks");
        await expect(page).toHaveURL(/\/tasks/);
        await expect(
            page.getByRole("heading", { name: "Tasks" })
        ).toBeVisible();
    });

    test("can navigate to Definitions", async ({ page }) => {
        await page.click("text=Definitions");
        await expect(page).toHaveURL(/\/jobs/);
    });

    test("can navigate to Taskflows", async ({ page }) => {
        await page.click("text=Taskflows");
        await expect(page).toHaveURL(/\/taskflows/);
        await expect(
            page.getByRole("heading", { name: "Taskflows" })
        ).toBeVisible();
    });

    test("can navigate to Agents", async ({ page }) => {
        await page.click("text=Agents");
        await expect(page).toHaveURL(/\/agents/);
        await expect(
            page.getByRole("heading", { name: "Agents" })
        ).toBeVisible();
    });
});
