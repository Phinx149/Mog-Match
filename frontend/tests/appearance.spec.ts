import { expect, test } from "@playwright/test";

test("settings switches the site's color scheme and remembers it", async ({ page }) => {
  await page.goto("/login");
  await page.getByLabel("Username").fill("samfullstack");
  await page.getByLabel("Password", { exact: true }).fill("mogmatch-demo");
  await page.getByRole("button", { name: "Log in", exact: true }).click();
  await expect(page).toHaveURL(/discover/);

  const html = page.locator("html");
  const pageColor = () => page.evaluate(() => getComputedStyle(document.body).backgroundColor);
  // Click the card like a person would: the radio input itself is visually hidden.
  const choose = (name: string) => page.locator("label").filter({ hasText: name }).click();

  await page.goto("/settings");
  await expect(html).toHaveAttribute("data-appearance", "default");
  await expect(page.getByRole("radio", { name: /Default/ })).toBeChecked();
  expect(await pageColor()).toBe("rgb(11, 13, 20)");

  // Hacker is black, applies immediately, and survives a reload (no flash of the default look).
  await choose("Hacker");
  await expect(html).toHaveAttribute("data-appearance", "hacker");
  await expect.poll(pageColor).toBe("rgb(0, 0, 0)");
  await page.reload();
  await expect(html).toHaveAttribute("data-appearance", "hacker");
  await expect(page.getByRole("radio", { name: /Hacker/ })).toBeChecked();
  expect(await pageColor()).toBe("rgb(0, 0, 0)");

  // Other pages and the logged-out pages use it too.
  await page.goto("/discover");
  await expect(html).toHaveAttribute("data-appearance", "hacker");
  await page.getByRole("button", { name: "Log out" }).click();
  await expect(page).toHaveURL(/login/);
  expect(await pageColor()).toBe("rgb(0, 0, 0)");

  // And back again.
  await page.getByLabel("Username").fill("samfullstack");
  await page.getByLabel("Password", { exact: true }).fill("mogmatch-demo");
  await page.getByRole("button", { name: "Log in", exact: true }).click();
  await expect(page).toHaveURL(/discover/);
  await page.goto("/settings");
  await choose("Default");
  await expect(html).toHaveAttribute("data-appearance", "default");
  await expect.poll(pageColor).toBe("rgb(11, 13, 20)");
});
