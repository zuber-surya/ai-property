import { defineConfig } from '@playwright/test';

/**
 * E2E is deliberately THIN (18-test-strategy.md §2.5). It is expensive and
 * brittle, so we buy only what protects revenue — the four money paths — plus
 * the smoke test below that proves the verification loop itself works.
 *
 * The Stitch render is NOT a pixel-diff gate (ADR-0019). Screenshots here are
 * human-reviewed artifacts attached to a PR, not assertions.
 */
export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  reporter: [['list']],
  use: {
    baseURL: 'http://127.0.0.1:5173',
    screenshot: 'only-on-failure',
    trace: 'retain-on-failure',
  },
  webServer: {
    command: 'npm run dev',
    cwd: '../frontend',
    url: 'http://127.0.0.1:5173',
    reuseExistingServer: true,
    timeout: 60_000,
  },
});
