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

**Estimates.** Story points appear in Part B only (the admin-portal build, where the work is concretely scoped against real files). They are **relative sizes, not hours** — `15-development-plan.md` says sequencing matters more than duration, and it is right. Do not convert them to dates.

---

## 2. ⛔ Blocked-by-gap index

**Read this before planning a sprint.** These tasks cannot start, no matter how much capacity you have. Each is blocked by a documented gap whose owner is a **document**, not a developer — so no amount of engineering effort unblocks them.

| Blocked task | Gap | Doc that must change | Cost of ignoring |
|---|---|---|---|
| `P.2` Provision Supabase + AWS | **I1** — Bedrock region vs. India users vs. Supabase co-location | `10-deployment-devops.md` | Provisioning in the wrong region is expensive to undo |
| `P.3` Font pipeline | **I2** — Plus Jakarta Sans hosting undecided | `13-ui-ux-flows.md` §5 | Frontend build can't be finalised |
| `S0.5` CI + staging deploy | **I1** (same) | `10-deployment-devops.md` | — |
| `S4.5` Lead Kanban stage colors | **D1** — no `info` status color | `DESIGN.md` | 3 of 5 pipeline stages have no honest color |
| ~~`S4.6`~~ | ~~**G9a**~~ ✅ **UNBLOCKED — the gap was never real** | — | `02-architecture.md` **§4.4** has specified `pg_cron` + a jobs worker since 2026-07-13, with **`mark_stale_leads()` listed by name**. FR10.2b was buildable all along (`GAPS.md` §5A) |
| *(Phase 2)* CMS public page | **G5** — no public read endpoint | `04-api-spec.md` | The module is inert |
| ~~*(Phase 2)* Chat escalation reply~~ | ~~**G7**~~ ✅ **UNBLOCKED 2026-07-14** | — | Endpoints now exist (`04-api-spec.md` §12A), handoff state machine specced (`05-ai-chatbot-spec.md` §10A), screen specced (`17-admin-spec/22`). **No migration needed.** |
| ~~*(Phase 2/3)* Notifications~~ | ~~**G9b**~~ ✅ **UNBLOCKED — never real** | — | `02-architecture.md` **§3**: SendGrid + Twilio, decided 2026-07-13. ⚠️ Indian SMS still needs **DLT registration — calendar lead time.** Start it now |

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
| `S4.6` | **Stale-lead alert — FR10.2b, MANDATORY** ✅ buildable | `feature/lead-stale-alert` | A **`pg_cron`** job (`02-architecture.md` §4.4) enqueues into `jobs`; the worker dispatches. `mark_stale_leads()` is already named in §4.4 |

> **`S4.6` is the sharpest item in this backlog.** Manual claim (ADR-0014) is only safe *because* of the staleness alert — it is the floor under the entire design. **That floor does not exist.** Either pick a scheduler (`pg_cron` is free and already in the stack) or reopen the auto-assignment decision. Do not build the pipeline and hope.

---

## 9. Sprints 5–11 — not decomposed

**Deliberately.** Decomposing Sprint 9 today would be fiction — those tasks depend on what Phase 1 teaches. A precise-looking plan for work that far out is a liability, not an asset.

Headline scope (`15-development-plan.md`):

| Phase | Sprints | Scope | Known blockers |
|---|---|---|---|
| **2 — AI Layer** | 5–7 | AI Search · Chatbot · Recommendation · **Agent Chat Console** (`17-admin-spec/22`) | **G3** autosuggest · **G5** CMS read · ~~G7~~ ✅ closed |
| **3 — Scale & Polish** | 8–11 | Remaining admin modules, hardening, deploy, pilot | ⚠️ **DLT registration** for Indian SMS (regulatory lead time) · **DPDP** (`19-security-and-privacy.md` §3 — likely a **pilot blocker**) |

**Decompose a sprint when it becomes the next one.**

**Two things that must not wait for their sprint:**

1. **AI eval baselines.** The golden sets are specced; **no baselines are recorded anywhere.** Until they are, "the AI got worse" is an opinion, not a measurement (`22-risk-register.md` §2). Record them **the day the first AI feature works** — not at the end of Phase 2.
2. **DPDP.** Consent capture, data export and an erasure mechanism are **build items that appear in no sprint**, and erasure conflicts architecturally with soft-delete. Discovered at a pilot, they are ruinously expensive. Get counsel now (`19-security-and-privacy.md` §3).

---

# Part B — Admin Portal Build (UI · API · Integration)

> **Scope:** the **10 admin screens** Stitch generated, in `docs/stitch_design/`. Sequenced onto the sprints in `15-development-plan.md` — this section decomposes that schedule, it does not invent a new one.
>
> **Story points** are relative sizes (Fibonacci), not hours. Do not convert them to dates.

---

## B0. Read this before writing a single component

### B0.1 ⚠️ The Stitch HTML is a REFERENCE, not an implementation

Each screen is `docs/stitch_design/<screen>/code.html` plus a `screen.png` render. **Do not port that HTML into React.** It will look right and be wrong:

| What Stitch emitted | Why it can't ship | What to do instead |
|---|---|---|
| **~55 hardcoded hex values per screen** (≈550 across the admin portal) | Every one is a fork of `DESIGN.md`. This is the exact failure that produced two design systems here (`OWNERSHIP.md` §5). | **Token classes only** — `bg-primary`, never an arbitrary-value hex class. |
| `<script src="cdn.tailwindcss.com">` | A CDN script is not a build. No purge, no config, no types. | A real Tailwind config **generated from `DESIGN.md`** (task `B.1`). |
| Google Fonts `<link>` for Plus Jakarta Sans | **Font hosting is undecided — gap I2.** Stitch chose for us. | Resolve `P.3` first. Self-hosting recommended. |
| **Material Symbols** icon font | In **no spec.** `13-ui-ux-flows.md` §4.6 asks for line icons at 1.5px stroke. Nobody decided this. | Decide it (`B.0`), don't inherit it. |

**Use `screen.png` as the visual target and `code.html` for structure and spacing. Type the components yourself.**

### B0.2 The rules that will actually bite

- **`tertiary` marks AI output and nothing else** (ADR-0007). In this portal: the Chatbot / AI Search source chips, the two AI bars in the dashboard chart, and the **bot's** messages and tool calls. **Not** focus rings — those are `primary` (ADR-0008). **Not** a human agent's chat reply.
- **Status uses the semantic ramp, never brand colours** (ADR-0009).
- **Router → Service → Repository.** Routers hold no logic. Services write no SQL.
- **Every endpoint must already exist in `04-api-spec.md`.** If it doesn't, the spec changes first.
- **Every new tenant-owned table needs a cross-tenant isolation test that fails at the DB layer** (ADR-0003). Not an API test. Not negotiable.

---

## B.0 — Pre-work: decisions Stitch made for us

**3 pts** · Branch `fix/frontend-dependency-decisions`

Stitch silently picked an icon set and a font-delivery mechanism. **Neither is in any spec.**

- [ ] **Icon set** — Material Symbols (what Stitch used) vs. Lucide/Phosphor. Record in `13-ui-ux-flows.md` §4.6.
- [ ] **Font hosting** (gap **I2**, task `P.3`) — self-hosted vs. Google Fonts. **Recommend self-hosted:** no third-party request per page load, no CDN dependency, and a Google Fonts `<link>` ships every visitor's IP to a third party on every page (`19-security-and-privacy.md`).

**DoD:** both decisions written into their owning docs; `GAPS.md` I2 closed.

---

## B.1 — The token pipeline (once; everything below depends on it)

**5 pts** · Branch `feature/frontend-design-tokens` · **Blocks every UI task.**

**`DESIGN.md` is the only file that defines a colour.** The Tailwind config must be **generated from it**, never hand-typed — otherwise it is a sixth fork, and this project already has five.

- [ ] `scripts/gen_tokens.py` — parse the `DESIGN.md` YAML front-matter → emit `admin-portal/src/styles/tokens.css` + the Tailwind `theme.extend`.
- [ ] Header the generated files: `/* GENERATED FROM docs/DESIGN.md — DO NOT EDIT */`.
- [ ] **Extend `scripts/check_drift.py`** with a `forked-hex-frontend` check: fail on any hex literal in `admin-portal/src/**` or `public-site/src/**` outside the generated token files.
  - Without this, a developer pastes one line of Stitch HTML and the whole discipline is gone. **The check IS the discipline.**
- [ ] Semantic classes, so a component never touches a raw token: `.chip-status-published`, `.chip-source-ai`, `.ai-widget` (the primary→tertiary gradient border + glow).

**DoD:** changing a hex in `DESIGN.md`, re-running `gen_tokens.py`, changes the UI. A hex typed into a `.tsx` **fails the drift check.**

---

## Sprint 2 — Property Management

**Focus:** admins manage listings end-to-end.
**Depends on:** Sprint 1 (auth, tenancy, RLS) · `B.1` (tokens).
**Screens:** 4 · **52 pts**

### UI Tasks

| # | Task | Design reference | Pts |
|---|---|---|---|
| `S2-UI-1` | Properties List | `docs/stitch_design/propvista_properties_list/` | 8 |
| `S2-UI-2` | Add / Edit Property (multi-step) | `docs/stitch_design/propvista_add_edit_property/` | 8 |
| `S2-UI-3` | Bulk Upload | `docs/stitch_design/propvista_bulk_upload/` | 5 |
| `S2-UI-4` | Approvals Queue | `docs/stitch_design/propvista_approvals_queue/` | 5 |

**Every UI task carries these four subtasks:**

- [ ] **Layout** — from `screen.png` + `code.html` structure, **token classes only** — no arbitrary-value hex classes. The drift check enforces it.
- [ ] **Components** — extract to `components/`, don't inline. The table, the status chip, the step indicator and the dropzone are reused; build each once.
- [ ] **Interactive states** — hover · **focus (2px `primary` ring, NOT tertiary)** · loading skeletons · error · **and the empty state.** Stitch renders none of these, and they are the states users actually spend time in.
- [ ] **Responsive** — `13-ui-ux-flows.md` §4.7 (mobile <640 · tablet 641–1024 · desktop >1024). Sidebar → icon-only on tablet. **Desktop-first is a decision** (`17-admin-spec/README.md` §4.6): a usable read-only mobile view is the bar, not parity.

**Screen-specific — the details a pixel-match will miss:**

- `S2-UI-1` — status chips from the **semantic ramp**. Six states: Draft · Pending · Published · Sold · Rejected · Archived.
- `S2-UI-3` — the review step shows **per-row errors in plain language** and offers **partial import**. *"Import the 128 valid rows"* is the entire point of the screen (`TC-PROP-02`). Never make someone fix 14 rows to get value from the other 128.
- `S2-UI-4` — **Reject requires a reason.** A rejection with no reason is a dead end for the agent who submitted it.

### API Tasks — `04-api-spec.md` §8

| # | Task | Pts |
|---|---|---|
| `S2-API-1` | `properties`, `property_media`, `amenities` + migrations + **RLS via the reusable macro** | 5 |
| `S2-API-2` | Property CRUD per **§8** | 5 |
| `S2-API-3` | Status workflow — six states, incl. **de-indexing on `sold`** | 3 |
| `S2-API-4` | Bulk upload — **per-row validation, partial commit** | 5 |

**Every API task carries these four subtasks:**

- [ ] **Repository** — SQLAlchemy lives *only* here. Every query tenant-scoped. `async`.
- [ ] **Service** — business logic + domain exceptions (`PropertyNotFoundError`). **No raw SQL.**
- [ ] **Router** — parse, call **one** service method, return. No logic. Errors → the standard envelope (`04-api-spec.md` §1). **A raw DB error must never reach a client.**
- [ ] **Tests** — service unit tests with repos mocked · integration test for the RLS policy · **the cross-tenant isolation test.**

> `S2-API-3` — **de-indexing matters as much as indexing.** A `sold` property left in `property_embeddings` keeps getting recommended and keeps being offered by the chatbot. That makes the AI look broken, and nobody reports it because it looks like an opinion.

### Integration Tasks

| # | Task | Pts |
|---|---|---|
| `S2-INT-1` | Wire list + form + bulk upload + approvals to their endpoints | 8 |

- [ ] React Query. **Cache keys include `tenant_id`.**
- [ ] Loading / error / **empty** states wired to real responses.
- [ ] **Optimistic updates** on status change — **with rollback on failure.** Never leave the UI lying about server state.
- [ ] **Tenant isolation from the client side:** a Tenant A session must not fetch a Tenant B property by pasting its UUID into the URL.

### Acceptance

| TC | Case |
|---|---|
| `TC-PROP-01` | A `pending_approval` property is **not publicly visible** until approved |
| `TC-PROP-02` | Bulk upload with malformed rows reports **per-row** errors, not a full-batch failure |
| `TC-PROP-03` | An agent without `properties.edit` gets **403** on writes |
| `TC-TENANT-01` | Tenant A cannot read/write Tenant B's properties — **failing at the DB layer** |

**DoD:** an admin adds, edits, approves and features a property **through the real UI** and it persists on reload · all TC cases pass · `check_drift.py` clean · **no hex literal anywhere in `admin-portal/src/`** · `09-coding-standards.md` §8 self-check run.

---

## Sprint 4 — Lead CRM

**Focus:** inquiries become trackable leads; agents work them.
**Depends on:** Sprint 2.
**Screens:** 3 · **39 pts**

> ### ⛔ Two blockers. Read before committing capacity.
>
> **D1 — `DESIGN.md` has no "in progress" colour.** Three of the five pipeline stages (`contacted`, `site_visit_scheduled`, `negotiation`) are *in progress* — not done, not failed, not inert, and **not a warning**. None of `success`/`warning`/`error`/`neutral` fits. The Stitch screens render them `neutral` because the prompt said so, and **`neutral` is a placeholder, not an answer.** Add an `info` family to `DESIGN.md` **before** `S4-UI-1`, or you build the board twice.
>
> ~~**G9a — no scheduler.**~~ ✅ **WITHDRAWN.** `02-architecture.md` §4.4 has had `pg_cron` + a jobs worker since 2026-07-13, and **`mark_stale_leads()` is listed in it by name.** `S4-API-5` is fully buildable. This entry was a stale summary copied from `CLAUDE.md`, and it cost this sprint a fictitious blocker — see `GAPS.md` §5A.

### UI Tasks

| # | Task | Design reference | Pts |
|---|---|---|---|
| `S4-UI-1` | Leads Kanban — 5 columns, drag between stages | `docs/stitch_design/propvista_leads_kanban/` | 8 |
| `S4-UI-2` | Leads Table — sortable, filterable, bulk assign | `docs/stitch_design/propvista_leads_table/` | 5 |
| `S4-UI-3` | Lead Detail — the slide-in panel *(this is the "customer" view)* | `docs/stitch_design/propvista_lead_detail_view/` | 5 |

Same four subtasks as Sprint 2, plus:

- `S4-UI-1` — **drag-and-drop with optimistic reorder and rollback.** A card that snaps back is honest; a card that stays put after the server rejected the move is a lie. **Unassigned leads must be visually loud** — an unassigned lead is nobody's responsibility. The Kanban is **explicitly not a mobile experience**; ship a read-only fallback.
- `S4-UI-2` — **the AGE column is the point of this screen.** It is what a manager sorts by, and it is what surfaces the leads quietly rotting. Prominent, red past a threshold.
- `S4-UI-3` — **source chips: `tertiary` for Chatbot and AI Search only.** Requirement form, contact form and walk-in are neutral.

### API Tasks — `04-api-spec.md` §5, §9

| # | Task | Pts |
|---|---|---|
| `S4-API-1` | `leads`, `lead_notes`, `lead_activities` + RLS + isolation test | 5 |
| `S4-API-2` | `POST /leads` + **idempotency** (`leads.idempotency_key`) | 3 |
| `S4-API-3` | Lead list / detail / stage-change / notes per **§9** | 5 |
| `S4-API-4` | **Atomic** claim — two agents at once → exactly one winner | 3 |
| `S4-API-5` | **Stale-lead alert (FR10.2b)** — a `pg_cron` job + the worker | 3 |

> **`S4-API-5` — build it.** Manual claim (ADR-0014) is only *safe* because of the staleness alert: FR10.2b calls it **mandatory** — *"without it, manual claim loses leads."*
>
> ✅ **It is buildable today.** `02-architecture.md` §4.4: a **`pg_cron`** job (`mark_stale_leads()`, already named there) enqueues into the `jobs` table; the Python worker dispatches the notification via SendGrid/Twilio/in-app.
>
> ⚠️ **The worker bypasses RLS** (§4.4, "the three things that will bite"). It must `SET LOCAL app.current_tenant_id` from `jobs.tenant_id` before touching tenant data. **A worker that forgets has no tenant isolation at all**, and unlike every other code path RLS is not there to catch it. This job gets its own cross-tenant test.

### Integration Tasks

| # | Task | Pts |
|---|---|---|
| `S4-INT-1` | Wire Kanban + table + detail panel to the lead endpoints | 5 |

- [ ] Optimistic stage change on drag → **rollback + toast on failure**.
- [ ] The claim race: the loser sees *"Ravi took this one"* — **not an error toast.** It is a normal race and it will happen daily.
- [ ] A Tenant A lead never appears on a Tenant B board.

### Acceptance

| TC | Case |
|---|---|
| `TC-LEAD-01` | **Every lead has a non-null `source`** |
| `TC-LEAD-02` | Stage changes recorded in `lead_activities` with correct timestamps |
| — | Simultaneous double-claim → **exactly one owner** (FR10.2a) |
| `TC-TENANT-01` | Cross-tenant lead access fails at the DB layer |

**DoD:** an agent works a lead from capture to close through the real UI · the claim race is provably safe · **D1 resolved**, or the board ships knowingly with three indistinguishable stages · drift check clean.

---

## Sprint 6 — AI Chatbot (admin side)

**Focus:** review what the bot did, and take over when it fails.
**Depends on:** Sprint 4 · the Sprint 6 chatbot backend.
**Screens:** 2 · **31 pts**

### UI Tasks

| # | Task | Design reference | Pts |
|---|---|---|---|
| `S6-UI-1` | AI Chat Logs — read-only transcripts | `docs/stitch_design/propvista_ai_chat_logs/` | 5 |
| `S6-UI-2` | **Agent Chat Console** — the live handoff ★ | `docs/stitch_design/propvista_agent_chat_console/` | 8 |

> ### ★ `S6-UI-2` is the highest-risk UI task in the project
>
> **Three voices must look different, and the AI-colour rule decides it:**
>
> | Voice | Treatment |
> |---|---|
> | 👤 Visitor | Plain, neutral |
> | 🤖 **Bot** | **`tertiary`** — model output. Tool calls rendered **inline** (`[🔧 lookup_property(id: "a3f…")]`) — that inline call is how you verify the bot used live data instead of inventing it |
> | 🙋 **Agent** | **NEVER `tertiary`.** A human wrote it. Attribute by name |
>
> Paint a human agent's reply in the AI colour and **the screen lies about who is talking** — on the one screen whose entire purpose is showing a worried customer that a real person arrived. Spec: `17-admin-spec/22-agent-chat-console.md` §3.1.
>
> **Waiting time is the most important number in this portal.** Everywhere else a stale view costs someone minutes. Here, a person is sitting in a chat window right now.

- [ ] Queue polls ~10s; the visitor's widget polls ~4s (**ADR-0017** — polling, not Realtime, because ADR-0005 restricts the Supabase client to Auth and Storage).
- [ ] **The composer is disabled until you have claimed the conversation.**
- [ ] Empty queue = *"No one's waiting."* **Calm, not celebratory.** It is the normal state.

### API Tasks — `04-api-spec.md` §12, **§12A**

| # | Task | Pts |
|---|---|---|
| `S6-API-1` | `GET /admin/ai-config/chat-logs` — browse, filter, flag (**§12**) | 3 |
| `S6-API-2` | **§12A** — `GET /admin/chat/queue` · `POST …/claim` · `POST …/reply` · `POST …/close` | 5 |
| `S6-API-3` | **The bot goes silent when escalated** — `POST /ai/chat/message` persists and **does not call Bedrock** (§12A.2) | 3 |
| `S6-API-4` | Atomic claim → **`409`** to the loser (§12A.1). **Reuse the lead-claim pattern.** | 2 |

> **No migration needed.** `chat_messages.sender` already accepts `agent`; `chat_conversations` already has `assigned_agent_id`. The schema was built for this (G7, closed 2026-07-14).
>
> `S6-API-3` is load-bearing: without it the visitor is talking to a human **and** a machine at once — worse than never offering a human at all.

### Integration Tasks

| # | Task | Pts |
|---|---|---|
| `S6-INT-1` | Wire the console end to end: queue → claim → reply → close | 5 |

- [ ] **The whole point:** an agent replies and **it reaches the visitor's open chat widget.** Test with two browsers.
- [ ] Claim race → `409` → *"Ravi picked this one up"*, queue refreshes.
- [ ] An agent **cannot open another tenant's conversation by pasting its UUID** (`04-api-spec.md` §12A.5 — threat T1, on transcripts containing phone numbers and budgets).

### Acceptance

| TC | Case |
|---|---|
| — | An escalated conversation appears in the queue **within one poll cycle** (FR1.7: *"real time or near-real time"*) |
| — | The agent's reply **reaches the visitor's widget** |
| — | Two agents claiming → exactly one owner; the loser gets a clear message |
| — | While escalated, a visitor message is **persisted without invoking Bedrock** |
| — | The agent's reply is **not** rendered in the AI colour (ADR-0007) |

**DoD:** the escalation loop closes end-to-end in a live two-browser test · bot and agent are distinguishable at a glance · drift check clean.

---

## Sprint 8 — Admin Dashboard

**Focus:** operational visibility.
**Depends on:** Sprints 2, 4, 6 — **it is last because it has nothing to show until the data exists.**
**Screens:** 1 · **13 pts**

### UI Tasks

| # | Task | Design reference | Pts |
|---|---|---|---|
| `S8-UI-1` | Admin Dashboard — KPIs, charts, activity feed | `docs/stitch_design/propvista_admin_dashboard/` | 8 |

- [ ] Four KPI cards · a 30-day leads line chart · a lead-source bar chart · a borderless activity feed.
- [ ] **The source chart is the point of this screen.** Chatbot and AI Search bars are **`tertiary`**; the other three are `primary`. That contrast is the whole reason the chart exists: **it shows whether the AI features are earning their Bedrock cost** (`22-risk-register.md` §3).
- [ ] **Escalated chats in the activity feed are flagged `error`** — the only genuinely time-sensitive item on the page.
- [ ] Charts follow the `dataviz` guidance. Semantic colour is **not** the accent.

### API Tasks — `04-api-spec.md` §11

| # | Task | Pts |
|---|---|---|
| `S8-API-1` | `GET /admin/dashboard/summary` — KPIs + chart series in **one** call | 5 |

- [ ] Every aggregate **tenant-scoped.** A KPI that leaks another tenant's lead count is still a cross-tenant leak.
- [ ] The `source` breakdown must distinguish the AI sources — that reporting is the justification for the AI spend.

### Integration Tasks

- [ ] Wire it; skeleton the loading; and **design the day-one empty state.** A brand-new tenant has zero of everything, and four zeroes with no explanation is the first thing every new admin will ever see.

**DoD:** a real tenant's real numbers render · the AI-vs-non-AI split is visible at a glance · the empty state is designed, not defaulted.

---

## B.2 — Summary

| Sprint | Focus | Screens | UI | API | Int | **Total** |
|---|---|---|---|---|---|---|
| Pre | Decisions + token pipeline | — | — | — | — | **8** |
| 2 | Property Management | 4 | 26 | 18 | 8 | **52** |
| 4 | Lead CRM | 3 | 18 | 16 | 5 | **39** |
| 6 | AI Chatbot (admin) | 2 | 13 | 13 | 5 | **31** |
| 8 | Dashboard | 1 | 8 | 5 | — | **13** |
| | | **10** | | | | **143 pts** |

### The two things to fix before you start

✅ **Both former blockers are gone.**

- **D1** — the `info` status colour is now in `DESIGN.md` (a cyan family — see Semantic Status Colors). ⚠️ **The Kanban, leads-table and lead-detail Stitch screens were generated before it and must be regenerated** — they render three in-progress stages as `neutral`.
- **G9a** — **was never real.** `02-architecture.md` §4.4 has had `pg_cron` + a jobs worker since 2026-07-13, `mark_stale_leads()` included. `S4-API-5` is buildable (`GAPS.md` §5A).

**Sprint 4 is unblocked.**
