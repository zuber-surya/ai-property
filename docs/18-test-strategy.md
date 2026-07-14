# Test Strategy — PropVista CRM

> **Doc 18.** Owns: **test levels, what runs where, the AI evaluation strategy, and the gates.**
> `.claude/rules/testing.md` is the *rule* (write tests alongside the code). `15-development-plan.md` owns the **`TC-*` cases**. This doc owns the **system** they run in.
>
> **Status:** v1.0 · **Created:** 2026-07-14

---

## 1. What actually threatens this product

Test strategy should be shaped by what would hurt, not by a pyramid diagram. For this system, in order:

| # | Failure | Why it's the worst |
|---|---|---|
| 1 | **A cross-tenant data leak** | One real-estate business sees a competitor's buyer pipeline. Not a bug — an extinction event. Everything else is recoverable. |
| 2 | **The AI silently degrades** | Search stops finding things, the bot invents listings, recommendations go random. It fails *quietly* — no exception, no alert, just worse answers. Conventional tests cannot see this. |
| 3 | **A lead is lost** | The entire product is a funnel. A dropped inquiry is unrecoverable revenue and invisible. |
| 4 | **Bedrock cost runs away** | The only unbounded variable cost. An abuse loop on a public `ai/*` endpoint is a bill, not an outage. |

Everything below is arranged around those four.

---

## 2. Test levels

### 2.1 Unit — services, repositories mocked (`pytest`)

The default. Business logic in `app/services/` with repositories mocked. Fast, hermetic, runs on every commit.

**For AI services, mock the Bedrock client.** Test the *orchestration*, not the model: "does the service call `create_lead` when the model requests that tool?", "does a malformed model response fall back to filter search instead of raising?". **Never hit live Bedrock in fast CI** — it is slow, costly, and non-deterministic, and it will make the suite flaky enough that people start ignoring it.

### 2.2 Integration — against a real test Postgres

A smaller suite hitting a **real Supabase Postgres test instance**, because the things most likely to kill us live in the database and cannot be mocked:

- **RLS policy correctness.** A mocked repository will happily prove a policy works that doesn't exist.
- Migration correctness (`alembic upgrade head` from empty, and `downgrade` back).
- Constraint behavior — the `favorites` uniqueness constraint, the `leads.idempotency_key` unique index, the atomic lead claim.

### 2.3 Tenant isolation — its own level, not a category of integration test

**Every tenant-owned table requires an explicit test that Tenant A cannot read or write Tenant B's rows — failing at the DB layer, not the API layer.** This is not negotiable and it is not "covered by" an API test: an API test passing tells you the application filtered correctly *this time*. The point of RLS is that it holds when the application forgets.

- Two seeded test tenants exist in every integration run.
- `TC-TENANT-01` / `TC-TENANT-02` from Sprint 1 are the template; every new table adds its own case.
- **A new tenant-owned table without an isolation test does not merge.** (ADR-0003.)

### 2.4 Frontend — `Vitest` + React Testing Library

Component tests for the four genuinely interactive components, not for presentational ones:

- the chat widget (streaming, tool-call rendering, escalation path)
- the AI search bar (parsed-query chips, the fallback-to-filter path)
- the requirement wizard (multi-step state, pre-filled edit)
- the lead Kanban board (drag between stages, optimistic update + rollback)

### 2.5 End-to-end — thin, and only on the money paths

E2E is expensive and brittle; buy only what protects revenue:

1. Anonymous visitor → search → favorite → register → **the favorite survived** (the whole anonymous-first promise, ADR-0015).
2. Visitor submits an inquiry → it appears in the admin Kanban with a non-null `source`.
3. Admin publishes a property → it appears on the public site **and** in the search index.
4. Admin marks a property Sold → it leaves the public site **and is de-indexed** (a sold property that keeps getting recommended makes the AI look broken).

---

## 3. AI evaluation — a separate suite, not part of CI

Unit tests prove the AI *plumbing* works. They cannot prove the AI is any *good*, and quality is the product.

**The golden sets in `05`/`06`/`07` are an evaluation suite, run separately** — periodically and pre-release, never in the fast run, because they make real Bedrock calls.

| Feature | What's measured | Regression signal |
|---|---|---|
| **Chatbot** (`05`) | Did it use a tool instead of inventing an answer? Did it escalate when it should have? Did it stay in scope? | Escalation rate rising = the bot is failing. It's the number to watch (`17-admin-spec/15`). |
| **AI Search** (`06`) | Recall on a golden query set. Parse accuracy on natural-language constraints. | **Fallback rate** — silent degradation shows here before customers complain (`17-admin-spec/16`). |
| **Recommendation** (`07`) | Ranking quality against the golden buyer profiles. Are the `match_reason` strings truthful? | A reordered shortlist that nobody asked for. |

**Prompt changes are the trigger.** Prompts are versioned files (`app/ai_clients/prompts/*.py`, versioned by comment). **Any prompt change re-runs the eval suite** — that's the entire reason they're versioned files rather than inline strings.

### 3.1 What "good" means must be recorded before the change

Set the baseline score *first*, then change the prompt. Otherwise you will read the new score and rationalize it.

---

## 4. Gates

| Gate | Runs | Blocks |
|---|---|---|
| `python scripts/check_drift.py` | pre-commit + CI | **New drift.** Not existing debt — see ADR-0016. |
| `ruff` + `black` + `eslint` + `prettier` | pre-commit + PR | Style |
| `pytest` (unit) | PR | Any failure |
| `pytest` (integration + RLS) | PR | Any failure |
| `tsc` + `vitest` | PR | Any failure |
| `docs/09-coding-standards.md` §8 self-check | before "done" | — (manual; see §6) |
| AI eval suite | pre-release, and on any prompt change | A regression against the recorded baseline |
| E2E money paths | pre-release | Any failure |

**Migrations are applied only through CI** — never by hand against staging or production. That's what keeps `03-database-schema.md` and the live schema from drifting (same principle as the drift check, applied to the database).

---

## 5. Coverage

No blanket percentage target — it produces tests written to satisfy a number.

Instead, **required coverage by kind**:

- Every service method with a branch → unit test for each branch.
- Every tenant-owned table → an isolation test (§2.3). **No exceptions.**
- Every `TC-*` case in `15-development-plan.md` → a test that asserts it. The `TC-*` id goes in the test name so the trace is mechanical.
- Every AI fallback path → a test that the fallback fires (timeout, 429, malformed parse). These are the paths that only run when things are already going wrong, so they are the least exercised and the most load-bearing.

---

## 6. The self-check is not yet a script — and that's a known weakness

`docs/09-coding-standards.md` §8 defines a seven-point Definition of Done. **It is prose, and it has never been executed.** That is the same class of failure the drift check was built to end: a rule nobody runs is a rule nobody follows.

**Open:** promote §8 to a script and put it behind the same gate as `check_drift.py`. Tracked in `22-risk-register.md`.

---

## 7. Test data

- **Two seeded tenants**, always. A single-tenant fixture set cannot catch a cross-tenant bug, and that is the bug that matters most.
- Seeded properties across **every status** — `draft`, `pending_approval`, `published`, `sold`, `on_hold`, `archived` — because status determines public visibility *and* search-index membership, and the interesting bugs are at that boundary.
- Seeded leads across every stage and every `source`, including the AI sources, since source drives the reporting that justifies the AI features.
- **Never seed production data into a test environment.** This database holds buyer PII (`19-security-and-privacy.md`).

---

## 8. Open questions

- [ ] Which Postgres does the integration suite run against — a dedicated Supabase test project, or ephemeral Postgres + `pgvector` in CI? Supabase is more faithful (RLS behaves identically); a container is faster and free. **Faithfulness probably wins here, because RLS is the thing being tested.**
- [ ] E2E tooling (Playwright assumed, not confirmed).
- [ ] Where the AI eval baselines are stored so a regression is mechanically detectable rather than eyeballed.
