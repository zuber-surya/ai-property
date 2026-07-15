# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Current State: Sprint 0 shipped, building the first feature

The full spec set (`docs/00`–`docs/22`) plus the DevOS (`OWNERSHIP.md`, `GAPS.md`, `scripts/check_drift.py`) are in place. **Sprint 0 is built:** `backend/` (FastAPI, async, `/health`), `frontend/` (one route-based React app — `/` public, `/admin/*` CRM, ADR-0020), the token pipeline (`scripts/gen_tokens.py`), and browser verification (`.claude/skills/verify/` + `e2e/`). The build is under way; the target is **PropVista CRM** — an AI-first, multi-tenant real estate CRM SaaS — to pilot-ready.

**The docs are the source of truth, not the code.** If a requirement changes mid-build, update the relevant doc *first*, then implement. Do not invent endpoints, tables, or behavior that isn't in the specs — add it to the spec first (see `docs/09-coding-standards.md` §1).

## Documentation Map

Read the relevant doc before working on a feature; point tasks at specific doc sections rather than working from memory.

| Doc | Use it for |
|---|---|
| `docs/00-project-overview.md` | Product intent, stack decisions, roles. Read first. |
| `docs/01-prd.md` | Functional requirements per module (FR numbers). |
| `docs/02-architecture.md` | **Folder structure, layering, multi-tenancy strategy.** The blueprint for all scaffolding. |
| `docs/03-database-schema.md` | Tables, columns, relationships, RLS pattern. |
| `docs/04-api-spec.md` | REST endpoints + the standard error envelope. |
| `docs/05/06/07-ai-*.md` | Chatbot, AI Search, AI Recommendation specs (the three USP features). |
| `docs/08-auth-roles-spec.md` | Auth, tenant isolation, role permissions. |
| `docs/09-coding-standards.md` | **Conventions to follow on every change.** |
| `docs/10-deployment-devops.md` | Environments, CI/CD, hosting. |
| `docs/11-14` | Stitch design prompts, SRS/NFRs, UI/UX flows, screen workflows. |
| `docs/15-development-plan.md` | **Sprint-by-sprint build order + per-module test cases.** Follow this sequencing. |
| `docs/16-customer-spec/` | **Per-page spec for the customer surface** (public site + portal). One file per page and per cross-page feature. Start at its `README.md`. |
| `docs/17-admin-spec/` | **Per-screen spec for the admin portal.** One file per screen. Start at its `README.md`. |

**Before building any screen, open its file in `docs/16-customer-spec/` or `docs/17-admin-spec/`.** Each one gives the layout, the click-by-click workflow, every API call it makes, the tables it touches, the role/tenant rules, the edge cases, and the `TC-*` cases it must pass — and ends with an **Open Questions** section you must not silently guess your way past.

⚠️ **`docs/GAPS.md` is the ONLY place a gap's state is recorded.** Do not trust a gap list summarised anywhere else — including the one that used to live in this paragraph.

> **This paragraph was itself the bug.** It claimed "no job scheduler" and "no email/SMS provider" long after `02-architecture.md` had decided both (§4.4 — `pg_cron` + a jobs worker; §3 — SendGrid + Twilio, **2026-07-13**). That stale summary was copied into `16-customer-spec/README.md` §5, and from there into six more documents, and an agent then reported a *mandatory* PRD requirement (FR10.2b) as unbuildable when it had been buildable for a day. Three levels of paraphrase, all confidently wrong.
>
> **The rule this produced:** cite `GAPS.md` by gap ID, or read the owning doc. **Never restate a gap list.** (`OWNERSHIP.md` §3, `.claude/rules/devos.md` §1.)

Run `python scripts/check_drift.py` — it fails on a stale gap citation.

Two docs are now **stale against the schema** and must be corrected: `01-prd.md` FR10.1 still promises configurable pipeline stages (the schema fixes the enum for MVP), and `04-api-spec.md` §14 still implies a persisted report with an ID (reports are stateless).

## Intended Stack (per docs)

- **Backend:** Python + FastAPI (async), SQLAlchemy + Alembic, in `backend/`.
- **Frontend:** One React (Vite + TypeScript) app in `frontend/`, route-based — `/` + customer routes are the public surface; `/admin/*` is the agent/admin CRM (lazy-loaded as a separate chunk). One build, one deploy. Superseded the earlier two-app split on 2026-07-15 — see ADR-0020.
- **Data:** Supabase Postgres + `pgvector`. SQLAlchemy talks directly to the Postgres connection string; Supabase's own client is used **only** for Auth and Storage, never for data access.
- **LLM:** Anthropic Claude models via Amazon Bedrock (`boto3` bedrock-runtime). Embeddings: Amazon Titan Text Embeddings V2, 1024 dims.
- **Architecture:** Modular monolith (single FastAPI backend). AI features are internal modules with clean interfaces.

## Non-Negotiable Rules

These come from `docs/02` and `docs/09` and are the ones easiest to get wrong:

1. **Tenant isolation is enforced at the DB layer via Postgres RLS**, not just app-side filtering. Every tenant-owned table has `tenant_id UUID NOT NULL REFERENCES tenants(id)`. App-level `tenant_id` filtering is a *second* layer, never the only one. AI modules must always scope embeddings queries and Bedrock context to `tenant_id` — never search/recommend across tenants. Every new tenant-owned table needs an explicit cross-tenant-access test.
2. **Backend layering: Router → Service → Repository → DB.** Routers only parse/call-one-service/return — no business logic. Services hold logic and never write raw SQL. Repositories are the only place SQLAlchemy queries live. AI modules add an AI Client layer: `Router → AI Service → AI Client (Bedrock) + Repository`. Never call `ai_clients/` from a router.
3. **All schema changes go through an Alembic migration** — no manual edits to the Supabase Postgres instance, even in early dev. RLS policies use one reusable migration helper, not hand-written SQL per table.
4. **AI prompts live only in `app/ai_clients/prompts/*.py`**, versioned via comment/docstring — never inlined in a service function.
5. **Every new endpoint must already exist in `docs/04-api-spec.md`** and trace to a PRD module. If it doesn't, update the spec first.
6. **Secrets via env vars through `core/config.py`** — commit only `.env.example`.
7. **All I/O-bound endpoints are `async def`**; Bedrock calls use the async boto3 pattern to avoid blocking the event loop.

Run the self-check in `docs/09-coding-standards.md` §8 before considering any change complete.

## Rules & Module Playbooks (`.claude/`)

The non-negotiables above are the summary. Deeper, on-demand guidance lives in `.claude/` — read the specific file when your task touches that area (see `.claude/README.md` for the map):

- **`.claude/rules/`** — cross-cutting engineering rules: `workflow` (docs-first process, git, self-check), `backend` (FastAPI layering), `frontend` (React/TS), `database` (schema, Alembic, RLS), `ai` (Bedrock/prompts), `security` (tenant isolation, auth, secrets), `testing`. `rules/security.md` applies to almost everything.
- **`.claude/modules/`** — per-domain playbooks that name the exact `docs/` sections, tables, FR numbers, and `TC-*` acceptance tests for a module: `auth-tenant`, `property`, `lead-crm`, `ai-chatbot`, `ai-search`, `ai-recommendation`. `modules/README.md` maps all 16 PRD modules onto these domains.
- **`.claude/settings.json`** — shared permission allowlist for safe dev tooling (ruff/black/pytest/npm/etc.).

When starting a module, open its `modules/*.md` playbook first, then follow the `rules/*.md` files the change touches. These files summarize and point into `docs/` — if they ever disagree, the `docs/` win; update whichever is stale.

## Conventions

- **Python:** `black` + `ruff`; type hints required on all signatures; Pydantic schemas suffixed by purpose (`PropertyCreate`/`PropertyUpdate`/`PropertyOut`); domain exceptions in the service layer mapped to the standard error envelope by a shared handler — never leak raw DB/Bedrock errors.
- **React/TS:** `prettier` + `eslint`; strict mode, no unjustified `any`; function components + hooks only; the three USP widgets (chat, search, recommendation wizard) each get a self-contained `components/<feature>/` subfolder. Frontend types generated from the FastAPI OpenAPI schema where practical.
- **Testing:** `pytest` (services unit-tested with repos mocked; integration tests for repo/RLS correctness against a test Supabase Postgres). Mock Bedrock in standard unit tests; AI golden-set eval suites run separately, not in fast CI. `Vitest` + React Testing Library for key interactive components.
- **Git:** branches `feature/<module>-<desc>` / `fix/<desc>`; small focused commits referencing the PRD module; no direct commits to `main`.

## Commands

No build tooling exists yet — establish it during Sprint 0 (`docs/15` §4). Once scaffolded, the intended commands are:

- **Backend:** `uvicorn app.main:app --reload` (run), `pytest` (test), `ruff check .` / `black .` (lint/format), `alembic upgrade head` / `alembic revision --autogenerate` (migrations).
- **Frontend** (in `frontend/`): `npm run dev` (Vite), `npm run build`, `npm run test` (Vitest), `npm run lint`.

Verify actual scripts against each app's `package.json` / backend tooling once created, and update this section with the real commands.

## Build Order

Follow the phased plan in `docs/15-development-plan.md`: Phase 1 Foundation & Core CRM (auth, schema, tenancy, non-AI property/lead management, Sprints 0–4) → Phase 2 AI Layer (search, chatbot, recommendation, Sprints 5–7) → Phase 3 Scale & Polish (Sprints 8–11). Each sprint in that doc lists concrete tasks and `TC-*` test cases with a Definition of Done — treat those as the acceptance criteria.
