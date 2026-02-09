import { test, expect } from "@playwright/test";

test.describe("Login", () => {
    test.describe.configure({ mode: "serial" });
    test("can login with username", async ({ page }) => {
        // Navigate to dashboard
        await page.goto("/queue/management/dashboard/");

        // Should see login form
        await expect(page.locator("input[name='userId']")).toBeVisible();

        // Enter username
        await page.fill("input[name='userId']", "testuser");

        // Click login button
        await page.click("button[type='submit'], nve-button[type='submit']");

        // Should redirect to tasks page
        await expect(page).toHaveURL(/\/tasks/);

        // Verify we're logged in by checking for tasks page content
        await expect(
            page.getByRole("heading", { name: "Tasks" })
        ).toBeVisible();
    });

    test("can logout via profile menu", async ({ page }) => {
        // Login first
        await page.goto("/queue/management/dashboard/");
        await page.fill("input[name='userId']", "testuser");
        await page.click("button[type='submit'], nve-button[type='submit']");
        await expect(page).toHaveURL(/\/tasks/);

        // Click profile button (top right - has person icon)
        await page.click("nve-button:has(nve-icon[name='person'])");

        // Click logout menu item
        await page.click("nve-menu-item:has-text('logout')");

        // Should redirect to login page
        await expect(page.locator("input[name='userId']")).toBeVisible();
    });
});
