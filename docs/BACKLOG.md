# Execution Backlog — PropVista CRM

> **Owns: the STRUCTURE of the work.** Task IDs, subtasks, spec references, branch names, and what's blocked by what.
>
> **This doc does NOT own status.** Status lives in **GitHub Issues** — [github.com/zuber-surya/ai-property/issues](https://github.com/zuber-surya/ai-property/issues). A markdown status column is mutable state hand-maintained in lockstep with reality, and drift is this project's characteristic failure. **This file carries no status, so it cannot lie about progress.**
>
> **This doc does NOT own the plan.** `15-development-plan.md` owns sprint sequencing, scope and the `TC-*` acceptance cases. This file **cites** it and never restates it — a paraphrase of a spec inside another doc always drifts, and this project has already paid for that once (`OWNERSHIP.md` §5, failure 4).
>
> **Status:** v1.0 · **Last updated:** 2026-07-14

---

## 1. How this works

| Concept | Owner | Changes |
|---|---|---|
| The **plan** — sprints, scope, `TC-*` cases | `15-development-plan.md` | Rarely |
| The **structure** — tasks, subtasks, specs, branches, blockers | **this file** | Rarely |
| The **status** — TODO → WIP → DONE | **GitHub Issues** | Daily |

**Seeding the board:** `bash scripts/seed_issues.sh` creates one issue per task below (requires `gh`). Run `--dry-run` first.

**Rules**

1. **Work from the spec section, never from this file's summary.** Every task names the section to open. This backlog *points*; it does not *paraphrase*. That distinction is the whole reason it's allowed to exist.
2. Branch per task: `feature/<module>-<desc>` or `fix/<desc>` (`.claude/rules/workflow.md`). **No direct commits to `main`.**
3. A task is done when its **acceptance criteria are demonstrated** — not when the code compiles.
4. **Blocked tasks name their blocker** — a gap ID from `GAPS.md`. A blocked task with no named blocker is an excuse.

**No estimates.** `15-development-plan.md` assumes 2-week sprints and says the *sequencing* matters more than durations. Fake precision here would only obscure that.

---

## 2. ⛔ Blocked-by-gap index

**Read this before planning a sprint.** These tasks cannot start, no matter how much capacity you have. Each is blocked by a documented gap whose owner is a **document**, not a developer — so no amount of engineering effort unblocks them.

| Blocked task | Gap | Doc that must change | Cost of ignoring |
|---|---|---|---|
| `P.2` Provision Supabase + AWS | **I1** — Bedrock region vs. India users vs. Supabase co-location | `10-deployment-devops.md` | Provisioning in the wrong region is expensive to undo |
| `P.3` Font pipeline | **I2** — Plus Jakarta Sans hosting undecided | `13-ui-ux-flows.md` §5 | Frontend build can't be finalised |
| `S0.5` CI + staging deploy | **I1** (same) | `10-deployment-devops.md` | — |
| `S4.5` Lead Kanban stage colors | **D1** — no `info` status color | `DESIGN.md` | 3 of 5 pipeline stages have no honest color |
| `S4.6` **Stale-lead alert (FR10.2b — mandatory)** | **G9a** — no scheduler | `02-architecture.md` | **A mandatory PRD requirement is unbuildable.** `BackgroundTasks` cannot fire on a timer |
| *(Phase 2)* CMS public page | **G5** — no public read endpoint | `04-api-spec.md` | The module is inert |
| ~~*(Phase 2)* Chat escalation reply~~ | ~~**G7**~~ ✅ **UNBLOCKED 2026-07-14** | — | Endpoints now exist (`04-api-spec.md` §12A), handoff state machine specced (`05-ai-chatbot-spec.md` §10A), screen specced (`17-admin-spec/22`). **No migration needed.** |
| *(Phase 2/3)* Notifications | **G9b** — no email/SMS provider | `10-deployment-devops.md` | ⚠️ Indian SMS needs **DLT registration — calendar lead time.** Start now or cut it |

**Sprints 0–2 are otherwise unblocked.** Don't let the gap list stall the scaffolding — but **I1 blocks provisioning**, so it genuinely comes first.

---

## 3. Pre-flight

Must be true before any application code is written.

### `P.1` — Commit the doc set, install the DevOS gate
- **Branch:** `feature/devos-and-design-system`
- **Why:** ~26 files changed, zero commits. Two days of decisions with no diff and no revert path — the largest avoidable risk in the repo (`22-risk-register.md` §7).
- [ ] Branch off `main` (never commit to `main` — `21-release-management.md` §1)
- [ ] Commit: the design-system reconciliation, the doc-13 kill, the branding deferral
- [ ] Commit: the DevOS (`OWNERSHIP.md`, `GAPS.md`, `check_drift.py`, `rules/devos.md`, `.githooks/`)
- [ ] Commit: the SDLC docs (18–22, `adr/`, root `README.md`)
- [ ] `git config core.hooksPath .githooks`
- **Acceptance:** `main` protected; work on a branch; `python scripts/check_drift.py` reports no *new* drift.

### `P.2` — Decide the AWS region ⛔ **I1**
- **Why:** `10-deployment-devops.md` §1's entire rationale is *"co-locate compute with Bedrock."* This is an India-first product, and that rationale was never checked against it. If Claude-on-Bedrock isn't in `ap-south-1`, you must choose between user+DB latency and AI latency (`22-risk-register.md` §5).
- [ ] Confirm Bedrock Claude model availability by region — **from facts, not memory**
- [ ] Decide: compute region, and the Supabase project region (**co-locate them**)
- [ ] Record as an **ADR** — precisely the kind of decision that gets silently reversed later
- [ ] Update `10-deployment-devops.md` §1; close I1 in `GAPS.md`
- **Blocks:** `P.3`, `S0.4`, `S0.5`, all provisioning.

### `P.3` — Decide font hosting ⛔ **I2**
- **Why:** Plus Jakarta Sans is the entire type system and has no hosting decision. Self-hosted (no third-party request per page load, no CDN dependency) vs. Google Fonts.
- **Acceptance:** decided, recorded in `13-ui-ux-flows.md` §5, I2 closed.

### `P.4` — Absorb and delete `SPRINT0_PLAN.md`
- **Branch:** `fix/absorb-sprint0-plan`
- **Why:** It owns nothing (`OWNERSHIP.md` §6) **and it is wrong**: pins `psycopg2-binary` (synchronous) against a `CLAUDE.md` rule that every I/O endpoint is `async`, and lists `@vitejs/plugin-tsx`, which is not a real package. Its content is absorbed into §4 below with both bugs fixed.
- [ ] Confirm §4 supersedes it entirely
- [ ] `git rm SPRINT0_PLAN.md`
- [ ] Re-baseline: `python scripts/check_drift.py --accept`
- **Acceptance:** `async-violation` drops **2 → 0**. *The count going down is the proof.*

### `P.5` — Sweep the 25 stale gap citations
- **Branch:** `fix/sweep-stale-gap-citations`
- **Why:** Schema v1.1 closed G1, G2, the `favorites` uniqueness constraint and `leads.user_id`. **Three portal specs still call all four blocking.** An agent reading `07-portal-dashboard.md` today reports a blocker that no longer exists.
- [ ] `python scripts/check_drift.py` — **the `stale-gap` findings ARE the worklist**
- [ ] Fix `16-customer-spec/07`, `08`, `09`, `10`, `11`; `17-admin-spec/08`, `19`
- [ ] Re-baseline
- **Acceptance:** `stale-gap` drops to **0**.

---

## 4. Sprint 0 — Environment & Foundation

**Goal & DoD:** `15-development-plan.md` §4 — *a developer can clone the repo, run all three apps locally, and hit a real (empty) staging deployment.*

### `S0.1` — Scaffold `backend/`
- **Branch:** `feature/sprint0-backend-scaffold`
- **Spec:** `02-architecture.md` §4.2 — follow the folder structure **exactly**; don't add top-level folders.
- [ ] Structure per §4.2: `api/v1/`, `services/`, `repositories/`, `models/`, `schemas/`, `ai_clients/prompts/`, `core/`
- [ ] `requirements.txt`: `fastapi`, `uvicorn[standard]`, `sqlalchemy[asyncio]`, **`asyncpg`**, `alembic`, `pydantic`, `pydantic-settings`, `boto3`, `pgvector`, `python-jose`
  - ⚠️ **`asyncpg`, NOT `psycopg2`.** psycopg2 is synchronous and blocks the event loop; `CLAUDE.md` mandates async I/O end-to-end. This is the bug in the old `SPRINT0_PLAN.md`.
- [ ] Dev deps: `pytest`, `pytest-asyncio`, `httpx`, `ruff`, `black`
- [ ] `app/core/config.py` — **all** settings load here, env vars only, never hardcoded
- [ ] `app/main.py` — FastAPI instance, v1 router, `/health` → `{"status":"ok"}`
- [ ] Shared exception handler → the error envelope in `04-api-spec.md` §1. **A raw DB or Bedrock error must never reach a client.**
- [ ] `.env.example` with placeholders (commit this; never a real `.env`)
- **Acceptance:** `uvicorn app.main:app --reload` serves `/health` → 200; `ruff` + `black` clean.

### `S0.2` — Scaffold `public-site/`
- **Branch:** `feature/sprint0-public-site-scaffold`
- **Spec:** `02-architecture.md` §5.2 · `.claude/rules/frontend.md`
- [ ] Vite + React + TypeScript, **strict mode on**, no unjustified `any`
- [ ] `@vitejs/plugin-react` — ⚠️ **`@vitejs/plugin-tsx` does not exist.** The React plugin handles TSX.
- [ ] Folder shape: `pages/`, `components/`, `hooks/`, `api/`, `context/`
- [ ] `eslint` + `prettier`; `vitest` + React Testing Library, one smoke test
- [ ] Design tokens from `DESIGN.md` → the CSS-var / Tailwind config
  - ⚠️ **This is a second sanctioned fork of the tokens.** Mark the generated file, and **add it to `check_drift.py`'s watch list** — the same way doc 11 §17/§18 are watched. An unwatched fork is how this project got two design systems.
- **Acceptance:** `npm run dev` serves a page; `build`, `lint`, `test` all pass.

### `S0.3` — Scaffold `admin-portal/`
- **Branch:** `feature/sprint0-admin-portal-scaffold`
- Same shape as `S0.2`. **Not tenant-branded** (ADR-0010) — it carries the PropVista brand.
- **Acceptance:** as `S0.2`.

### `S0.4` — Database + Alembic  ⛔ *(depends on `P.2`)*
- **Branch:** `feature/sprint0-db-alembic`
- **Spec:** `03-database-schema.md` · `.claude/rules/database.md`
- [ ] Supabase project (dev). **Same region as the backend** — see `P.2`.
- [ ] Async SQLAlchemy engine against the Postgres connection string. **The Supabase client is used only for Auth and Storage — never data access** (ADR-0005)
- [ ] `alembic init`; wire the URL from `core/config.py`
- [ ] Enable `pgvector`
- [ ] **The reusable RLS migration helper** — one macro, reused per tenant-owned table. **Never hand-write per-table policy SQL.**
- [ ] Empty baseline migration
- **Acceptance:** `alembic upgrade head` applies from empty; `downgrade` returns.

### `S0.5` — CI/CD + staging deploy ⛔ **I1**
- **Branch:** `feature/sprint0-ci-staging`
- **Spec:** `10-deployment-devops.md` §3 · `21-release-management.md` §4
- [ ] GitHub Actions on PR: `ruff`/`black`/`eslint`/`prettier`, `pytest`, `tsc`, `vitest`
- [ ] **Add `python scripts/check_drift.py` to CI** — same gate as pre-commit
- [ ] On merge to `main`: build image + two static builds → Alembic → staging
- [ ] **Manual approval gate before production.** Deliberate: one bad migration touches every tenant at once, and there is no blast-radius containment between tenants
- [ ] **Migrations run only via CI.** Never by hand, in any environment, ever
- [ ] **Secret scanning** — a committed key is the likeliest real breach for a small team (`22-risk-register.md`)
- **Acceptance (`TC`, doc 15 §4):** CI passes on an empty commit; `/health` returns 200 **in staging**.

### `S0.6` — Local dev in one command
- **Branch:** `feature/sprint0-local-dev`
- **Why:** the sprint's DoD is literally *"a developer can clone the repo and run all three apps."* That must be one command, not a wiki page.
- [ ] `make setup` / `dev` / `test` / `check` (or npm-script equivalents)
- [ ] Seed script: **two tenants, always.** A single-tenant fixture cannot catch a cross-tenant bug (`18-test-strategy.md` §7)
- [ ] Seed properties across **all six** statuses, and leads across every stage and source
- [ ] README "Start here" verified by someone who has never run it
- **Acceptance:** clean clone → running in under 10 minutes.

### `S0.7` — Structured logging + Bedrock observability
- **Branch:** `feature/sprint0-logging`
- **Spec:** `10-deployment-devops.md` §5 · `.claude/rules/ai.md`
- **Why now:** every Bedrock call must log **latency, token usage and model ID**. If that isn't in the client wrapper from the first line it never gets retrofitted — and it is the only defence against both silent AI degradation and runaway cost (`22-risk-register.md` §2, §3).
- [ ] `core/logging.py` — structured logs
- [ ] The Bedrock client wrapper logs all three **by construction**, so a caller cannot forget
- **Acceptance:** a stubbed Bedrock call emits a log line carrying latency, tokens and model ID.

---

## 5. Sprint 1 — Data Layer, Auth & Tenancy

**Goal:** every subsequent feature can assume auth and tenant scoping work.
**DoD (doc 15):** two seeded tenants; **cross-tenant access fails at the DB layer, not just the API layer.**

> **This is the sprint that protects the company** (ADR-0003). Do not compress it.

| ID | Task | Branch | Spec |
|---|---|---|---|
| `S1.1` | `tenants`, `users`, `roles_permissions` + migrations | `feature/auth-tenant-core-tables` | `03` §3.1–3.3 |
| `S1.2` | **RLS policies via the reusable macro**, every tenant-owned table | `feature/auth-tenant-rls` | `03` §4 |
| `S1.3` | `core/tenancy.py` — resolve `tenant_id` at request start; set the Postgres session var RLS reads | `feature/auth-tenant-resolution` | `02` §7 · `rules/security.md` |
| `S1.4` | Supabase Auth + `core/security.py` JWT verification + `require_role` | `feature/auth-jwt-roles` | `08` §1–2 |
| `S1.5` | Anonymous session (`X-Session-Id`) + the session→account migration contract | `feature/auth-anon-session` | `08` §4 · `16-feature-favorites-session.md` |
| `S1.6` | **Tenant-isolation test harness** | `feature/auth-tenant-isolation-tests` | `18-test-strategy.md` §2.3 |

**`S1.3` — where `tenant_id` comes from**
- Admin portal: the **authenticated user's** tenant association.
- Public site: the **request domain**. Independent of whether the visitor is logged in.
- **Never** a client-supplied value. No customer-facing endpoint accepts a `tenant_id`.
- The `users` table — **not the JWT** — is the source of truth for role and tenant, so a role change takes effect immediately rather than at next refresh.

**`S1.6` — non-negotiable**
- `TC-AUTH-01`, `TC-AUTH-02`, `TC-TENANT-01`, `TC-TENANT-02` (doc 15 §4).
- **Build a helper any future table's isolation test can reuse in three lines.** If the test is laborious it will be skipped — and then ADR-0003 is decoration.
- ⚠️ **Explicit tests for the `tenants` table**, which has **no RLS backstop**. The only defences are `require_role(["super_admin"])` and *"derive the tenant from the JWT, never from a request parameter"* (`19-security-and-privacy.md` T1). **This is the thinnest part of the entire defence.**

---

## 6. Sprint 2 — Property Management (non-AI)

**DoD (doc 15):** an admin can add, edit, approve and feature a property **through the real UI** and see it persist on reload.

| ID | Task | Branch | Notes |
|---|---|---|---|
| `S2.1` | `properties`, `property_media`, `amenities` + **RLS + isolation test** | `feature/property-tables` | Every new tenant-owned table repeats `S1.6`. **No exceptions.** |
| `S2.2` | Property CRUD endpoints | `feature/property-crud` | `04-api-spec.md` §8. **Every endpoint must already exist in the spec** |
| `S2.3` | Status workflow — **six** states: `draft`/`pending_approval`/`published`/`sold`/`on_hold`/`archived` | `feature/property-status-workflow` | `17-admin-spec/06` §2.1. **De-indexing on `sold` matters as much as indexing** — a sold property that keeps getting recommended makes the AI look broken |
| `S2.4` | Bulk upload — **partial import** | `feature/property-bulk-upload` | `TC-PROP-02`: malformed rows report **per-row** errors, never a full-batch failure. Never make someone fix 14 rows before they get value from the other 128 |
| `S2.5` | Admin UI: property list + multi-step add/edit | `feature/property-admin-ui` | Prompts: doc 11 §§7 (list + form) |
| `S2.6` | Approvals queue | `feature/property-approvals` | **Rejection requires a reason** — a rejection without one is a dead end for the agent who submitted it |

---

## 7. Sprint 3 — Public Listing & Details

| ID | Task | Branch |
|---|---|---|
| `S3.1` | `GET /properties` with structured filters (`TC-LIST-01`) | `feature/property-public-list` |
| `S3.2` | `GET /properties/{id}` | `feature/property-public-detail` |
| `S3.3` | Public site: listing page (grid / list / map) | `feature/public-listing-page` |
| `S3.4` | Public site: details page — **must survive partial data** (`TC-DETAILS-01`) | `feature/public-details-page` |
| `S3.5` | Favorites: anonymous → migrate to account on register (`TC-LIST-02`, ADR-0015) | `feature/favorites-session-migration` |

> `S3.5` depends on the `favorites` **uniqueness constraint** — without it the session→account migration produces duplicates. Already closed in schema v1.1; make sure the code actually relies on it rather than deduping in Python.

---

## 8. Sprint 4 — Lead Capture & CRM Pipeline

| ID | Task | Branch | Notes |
|---|---|---|---|
| `S4.1` | `leads`, `lead_notes`, `lead_activities` + RLS + isolation test | `feature/lead-crm-tables` | |
| `S4.2` | `POST /leads` + idempotency (`leads.idempotency_key`) | `feature/lead-capture-endpoint` | `TC-LEAD-01`: **every lead has a non-null `source`** |
| `S4.3` | Public: contact form + callback slot picker | `feature/lead-contact-form` | |
| `S4.4` | **Atomic** lead claim — two agents claiming at once must not both succeed | `feature/lead-atomic-claim` | `03` §3.8.1 · ADR-0014 |
| `S4.5` | Admin Lead Kanban + table view ⛔ **D1** | `feature/lead-crm-kanban` | 3 of 5 stages are *in progress* and have **no honest color**. `neutral` is a placeholder, not an answer |
| `S4.6` | **Stale-lead alert — FR10.2b, MANDATORY** ⛔ **G9a** | `feature/lead-stale-alert` | **`BackgroundTasks` cannot fire on a timer. There is no scheduler.** |

> **`S4.6` is the sharpest item in this backlog.** Manual claim (ADR-0014) is only safe *because* of the staleness alert — it is the floor under the entire design. **That floor does not exist.** Either pick a scheduler (`pg_cron` is free and already in the stack) or reopen the auto-assignment decision. Do not build the pipeline and hope.

---

## 9. Sprints 5–11 — not decomposed

**Deliberately.** Decomposing Sprint 9 today would be fiction — those tasks depend on what Phase 1 teaches. A precise-looking plan for work that far out is a liability, not an asset.

Headline scope (`15-development-plan.md`):

| Phase | Sprints | Scope | Known blockers |
|---|---|---|---|
| **2 — AI Layer** | 5–7 | AI Search · Chatbot · Recommendation · **Agent Chat Console** (`17-admin-spec/22`) | **G3** autosuggest · **G5** CMS read · ~~G7~~ ✅ closed |
| **3 — Scale & Polish** | 8–11 | Remaining admin modules, hardening, deploy, pilot | **G9b** email/SMS (⚠️ DLT lead time) · **DPDP** (`19-security-and-privacy.md` §3 — likely a **pilot blocker**) |

**Decompose a sprint when it becomes the next one.**

**Two things that must not wait for their sprint:**

1. **AI eval baselines.** The golden sets are specced; **no baselines are recorded anywhere.** Until they are, "the AI got worse" is an opinion, not a measurement (`22-risk-register.md` §2). Record them **the day the first AI feature works** — not at the end of Phase 2.
2. **DPDP.** Consent capture, data export and an erasure mechanism are **build items that appear in no sprint**, and erasure conflicts architecturally with soft-delete. Discovered at a pilot, they are ruinously expensive. Get counsel now (`19-security-and-privacy.md` §3).
