# Rule: The Execution Loop

Applies to: **every build task.** Source: `docs/BACKLOG.md` (task structure), `docs/15-development-plan.md` (sprints + `TC-*`), `.claude/rules/devos.md` (drift), `docs/09-coding-standards.md` §8.

`workflow.md` says *docs first, branch, self-check*. **This file says how a task actually gets built** — Stitch design → React page → API → tests → a real browser → PR.

One task per session. Follow the ten steps. Do not skip step 2.

---

## Step 1 — Open the issue

It names a `BACKLOG.md` task ID (`S2-UI-1`, `S0.4`, …). That task names:
- the **spec sections** to work from,
- the **branch**,
- the **`TC-*`** cases it must satisfy,
- its **blocker**, if any.

If the task is `BLOCKED`, **stop.** The blocker is a *document*, not a coding problem — no amount of effort unblocks it. Fix the owning doc first (`CLAUDE.md`).

---

## Step 2 — ⚠️ Read the spec sections. Never a summary.

**This is the single most important line in this file, and it has now failed twice.**

1. Doc 11 §4 paraphrased the PRD. The paraphrase drifted. It produced a **false bug report**. (`OWNERSHIP.md` §5 #4)
2. `CLAUDE.md` summarised a gap list as *"no job scheduler."* The scheduler had existed for a day. The claim reached **eight documents**, and a **mandatory** requirement (FR10.2b) was planned as unbuildable **for an entire sprint**. (`GAPS.md` §5A)

**Nobody lied either time. Every step was a faithful copy of the one above it.** That is what makes summary-drift lethal — it doesn't look like an error, it looks like consensus.

**So: open the owning doc. Read the section. Do not trust a table that summarises it — including one in `BACKLOG.md`.** The backlog *points*; it does not *paraphrase*. That is the only reason it is allowed to exist.

Gap state lives in **`GAPS.md` alone**. Cite the ID or read the owner.

---

## Step 3 — Branch

```bash
git checkout -b <the branch named in BACKLOG.md>   # feature/<module>-<desc>
```

**Never commit to `main`.** Commit at each coherent decision, not at the end.

---

## Step 4 — If it's a UI task

**The Stitch HTML is a REFERENCE, not an implementation.**

| File | Use it for |
|---|---|
| `docs/stitch_design/<screen>/screen.png` | The **visual target**. This is what it should look like. |
| `docs/stitch_design/<screen>/code.html` | **Structure and spacing only.** |

**Do not port `code.html` into React.** It carries ~55 hardcoded hex values per screen (≈550 across the admin portal), a Tailwind **CDN** script, and a Google-Fonts `<link>`. Porting it forks the design system 550 ways and `check_drift.py` will fail you.

**Type the components yourself:**

- **Token classes only** — `bg-primary`, `text-on-surface`, `chip-status-published`. **Never a hex literal.** The `forked-hex-frontend` check fails the commit.
- **Extract to `components/`.** The table, the status chip, the step indicator, the dropzone are reused across screens. Build each once.
- **Build the states Stitch does not render.** It gives you the happy path and nothing else:
  - **loading** (skeletons),
  - **error**,
  - **empty** — *this is the state a brand-new tenant actually sees on day one*, and it is the most-viewed screen in the product,
  - **focus** — a 2px `primary` ring. **Never `tertiary`** (ADR-0008).
- **`tertiary` marks AI output and nothing else** (ADR-0007). In the admin portal that is exactly: the Chatbot / AI Search source chips, the two AI bars in the dashboard chart, and the **bot's** messages and tool calls. **Not** a human agent's reply.
- **Status uses the semantic ramp** (ADR-0009/0018), always with a **text label**, never a brand colour.
- **Responsive** per `13-ui-ux-flows.md` §4.7. Desktop-first is a *decision* in the admin portal — a usable read-only mobile view is the bar, not parity.

---

## Step 5 — If it's an API task

**The endpoint must already exist in `04-api-spec.md`. Grep to prove it:**

```bash
grep -n "/admin/chat/queue" docs/04-api-spec.md   # no hit → the spec changes FIRST
```

This is the rule that stops a prompt or a screen inventing an API. It is how the "AI Insights" panel got fully designed for a feature that existed in no spec.

**Layering — never skip a layer:**

```
Router (api/v1/*.py) → Service (services/*.py) → Repository (repositories/*.py) → DB
```

- **Router:** parse, call **one** service method, return. No logic.
- **Service:** business logic + domain exceptions (`PropertyNotFoundError`). **No raw SQL.**
- **Repository:** the *only* place SQLAlchemy lives. **Every query tenant-scoped.**
- **`async def`** on every I/O path. `asyncpg`, never `psycopg2` — a sync driver blocks the event loop on every query.
- Errors → the envelope in `04-api-spec.md` §1. **A raw DB or Bedrock error must never reach a client.**

**A new tenant-owned table costs you three things, not one:**
1. the migration (Alembic — never a hand edit),
2. an **RLS policy via the reusable macro** (never hand-written per-table SQL),
3. a **cross-tenant isolation test that fails at the DB layer** (ADR-0003).

> Test #3 is not "covered by" an API test. An API test passing tells you the application filtered correctly *this time*. **The entire point of RLS is that it holds when the application forgets.** Prove it by disabling the app-level filter — the test must still pass.

---

## Step 6 — Tests alongside, not after

Name each test for the `TC-*` case it satisfies, so the trace is mechanical:

```python
async def test_TC_PROP_02_bulk_upload_reports_per_row_errors(): ...
```

- Services: unit-tested with repositories **mocked**.
- Repositories + RLS: integration tests against a **real** test Postgres.
- **Mock Bedrock.** Never hit live Bedrock in the fast run — it is slow, costly, non-deterministic, and it will make the suite flaky enough that people start ignoring it.
- **AI fallback paths get their own tests.** They only run when things are already going wrong, so they're the least exercised and the most load-bearing.

---

## Step 7 — ★ Verify in a browser

**"The unit test passed" is not verification.** jsdom is not a browser: it will happily pass while the page renders blank, the drag is broken, or the layout bears no resemblance to the design.

```
/verify
```

Launch the app, **drive the actual flow**, take a screenshot. For a UI task, put the screenshot next to `docs/stitch_design/<screen>/screen.png` and *look at them*.

**Do not pixel-diff against the Stitch render as a gate** (ADR-0019). It is a *reference*, not pixel-truth — the real page legitimately differs (real data, real fonts, real empty states). Diffing it produces false failures until you loosen the threshold so far that it catches nothing. **Use it as a human-reviewed artifact.**

---

## Step 8 — Drift check

```bash
python scripts/check_drift.py     # no NEW findings
```

The pre-commit hook enforces it. **Do not `--no-verify` past it.** The first bypass is the last time the gate works.

If a finding is *wrong*, **fix the check** — never the baseline. A false positive that gets ignored trains everyone to ignore the true ones.

---

## Step 9 — The self-check

`docs/09-coding-standards.md` §8. Actually run it.

---

## Step 10 — PR

Through the GitHub MCP. The body carries:

- `closes #<issue>`
- **the `TC-*` cases demonstrated** — not "tests pass", the actual cases
- **the browser screenshot** from step 7
- anything you had to decide that wasn't in a spec → **that goes in the spec, or in an ADR, before the PR merges**

---

## The ten-second version

```
issue → READ THE SPEC (not a summary) → branch
  → UI: screen.png is the target, token classes only, build the empty state
  → API: endpoint must exist in the spec; Router→Service→Repo; RLS + isolation test
  → tests named for their TC-*
  → VERIFY IN A BROWSER
  → check_drift → §8 self-check → PR
```

**If you find yourself working around a gap in code, stop.** Fix the owning doc first. That rule is the whole architecture.
