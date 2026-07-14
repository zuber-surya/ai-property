import { expect, test } from '@playwright/test';

/**
 * Sprint 0 smoke: prove the verification loop works BEFORE any screen depends
 * on it.
 *
 * This is not a formality. jsdom is not a browser — vitest will happily pass
 * while the page renders blank. Only a real browser can tell you the app
 * actually mounted.
 */
test('the admin portal renders in a real browser', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'PropVista Admin' })).toBeVisible();
});

/**
 * The D1 regression, as an executable assertion.
 *
 * "New" (neutral) and "Contacted" (info) MUST be different colours. For months
 * they were both neutral, so an agent could not tell "nobody has touched this"
 * from "someone is working it" — the whole reason the info token exists
 * (ADR-0018).
 *
 * We read the COMPUTED colour from a real browser. A unit test asserting on a
 * className would pass even if the token never reached the stylesheet.
 */
test('New and Contacted are visibly different colours (gap D1)', async ({ page }) => {
  await page.goto('/');

  const bg = (label: string) =>
    page
      .getByText(label, { exact: true })
      .evaluate((el) => getComputedStyle(el).backgroundColor);

  const [neutral, info] = await Promise.all([bg('New'), bg('Contacted')]);

  expect(neutral).not.toBe('rgba(0, 0, 0, 0)'); // the token actually landed
  expect(info).not.toBe(neutral); // ← the entire point of D1
});
