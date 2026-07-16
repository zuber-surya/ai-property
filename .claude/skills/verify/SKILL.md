---
name: verify
description: Verify a PropVista change actually works by driving it in a real browser — launch the app, exercise the flow, screenshot. Use before committing any UI or API change with a runtime surface. Not for docs-only diffs.
---

# Verify — drive it in a real browser

**"The unit test passed" is not verification.**

`vitest` runs in jsdom, and **jsdom is not a browser**. It will pass while the page renders blank, the Kanban drag silently does nothing, a fetch 500s into an empty list, or the layout bears no resemblance to the design. Every one of those ships green.

This skill exists to close that gap (ADR-0019).

---

## 1. Launch

```bash
# Backend
cd backend && ./.venv/Scripts/python.exe -m uvicorn app.main:app --reload --port 8000

# The frontend — ONE app (ADR-0020): / is public, /admin/* is the CRM
cd frontend && npm run dev         # 127.0.0.1:5173
```

(Or `make backend` / `make web` from the repo root.)

Sanity first — if `/health` isn't 200, nothing downstream means anything:

```bash
curl -s localhost:8000/health     # {"status":"ok"}
```

## 2. Drive the actual flow

Playwright. **Drive what a user would do**, not what the test file finds convenient.

```bash
cd e2e && npx playwright test --headed          # watch it
npx playwright test --update-snapshots          # refresh screenshots
```

For an ad-hoc check, write a throwaway script — this is normal and encouraged:

```ts
import { chromium } from '@playwright/test';

const browser = await chromium.launch();
const page = await browser.newPage();
// 127.0.0.1, not localhost: on Windows 'localhost' resolves to ::1 and Vite
// binds to 127.0.0.1 (see frontend/vite.config.ts).
await page.goto('http://127.0.0.1:5173/admin/leads');

// Drive the thing you actually changed.
await page.dragAndDrop('[data-lead="priya"]', '[data-column="contacted"]');

await page.screenshot({ path: 'verify.png', fullPage: true });
await browser.close();
```

**Then look at `verify.png`.** Read it. That is the point of the step.

## 3. What to actually check

| Kind of change | What you must see with your own eyes |
|---|---|
| **A screen from Stitch** | Put `verify.png` next to `docs/stitch_design/<screen>/screen.png`. Same layout? Same spacing? Same hierarchy? |
| **Any UI** | The **empty state**. It is what a brand-new tenant sees on day one, and it is the single most-viewed screen in the product. Stitch never renders it. |
| **Any UI** | **Focus**: tab through it. The ring is `primary`. **It is never `tertiary`** (ADR-0008). |
| **Status chips** | `New` and `Contacted` must be **visibly different colours** — neutral vs. info. If they look the same, the `info` token didn't land (gap D1). |
| **Anything with AI** | `tertiary` violet marks **model output and nothing else** (ADR-0007). A human agent's chat reply in violet means the screen is lying about who is talking. |
| **A table** | Real data, and **overflow**. A 60-character property title is not a hypothetical. |
| **An API** | Not just 200 — the **shape**. And the error path: does a failure return the `{"error":{"code","message"}}` envelope, or a stack trace? |
| **Anything multi-tenant** | **Log in as Tenant A, paste a Tenant B UUID into the URL.** You must get a 403/404, not data. This is the one that ends the company. |

## 4. The Stitch render is a reference, NOT a gate

Do **not** pixel-diff `verify.png` against `docs/stitch_design/<screen>/screen.png` and fail the build on it.

That render is a *reference*, not pixel-truth. The real page legitimately differs — real data instead of lorem, real fonts, real empty states, real overflow, a real tenant name. Diffing it produces false failures until you loosen the threshold so far that it catches nothing — and then you have a gate everyone ignores, which is the exact failure ADR-0016 was written to prevent.

**Look at them side by side. Use your judgement. Attach the screenshot to the PR.**

## 5. Before you call it verified

```bash
make check                             # drift gate + tokens-current + lint + types
cd backend && ./.venv/Scripts/python.exe -m pytest -q
cd frontend && npm run lint && npm run test
```

Then the `docs/09-coding-standards.md` §8 self-check.

---

## The honest bar

> **If you did not open a browser and look at the thing, you did not verify it.**

Attach the screenshot to the PR. If you cannot produce one, say so in the PR body rather than implying you checked.
