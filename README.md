# PropVista CRM

An **AI-first, multi-tenant real estate CRM SaaS**. Each real estate business gets a public property site plus an internal CRM, backed by a shared application and shared AI services.

Three AI features are the product's reason to exist — a **conversational chatbot**, **natural-language property search**, and a **requirement-analysis recommendation engine**. Everything else is table stakes.

> **Status: Sprint 0 shipped; the first feature slice is in.** `backend/` (FastAPI, async, `/health`), `frontend/` (one route-based React app), the token pipeline, the drift gate and browser verification are all built. The property slice runs end to end — an admin publishes, a buyer sees it. Next up is the sprint sequencing in `docs/15-development-plan.md` §4.

---

## Start here

| You are… | Read |
|---|---|
| **New to the project** | `docs/00-project-overview.md`, then this file's *How this repo works* below |
| **About to write code** | `CLAUDE.md` → `.claude/rules/devos.md` → the `.claude/modules/` playbook for your module |
| **Building a screen** | Its file in `docs/16-customer-spec/` or `docs/17-admin-spec/` — never work from memory |
| **Touching anything visual** | `docs/DESIGN.md`. It is the only file that defines a color. |
| **Wondering why something is the way it is** | `docs/adr/` |
| **Blocked** | `docs/GAPS.md` — it is the only place a gap's state is recorded |

---

## How this repo works

**The docs are the source of truth, not the code.** If a requirement changes, change the doc *first*, then implement. Never let code drift ahead of the specs.

This is enforced, not merely requested:

```bash
python scripts/check_drift.py     # nine checks; each named after a failure that happened
python scripts/check_drift.py --selftest   # the checks' own fixtures — a gate nobody tests is a gate nobody has
```

Every check exists because that exact thing went wrong here. Two design systems once coexisted for weeks, and 33 specs cited the dead one. A schema fix closed four gaps and three specs still call them blocking. The check is how we stop paying for that twice.

**One concept, one owner.** `docs/OWNERSHIP.md` says who owns what. A hex color lives only in `DESIGN.md`; an endpoint only in `04-api-spec.md`; a gap only in `GAPS.md`. Everything else links and never copies.

The pre-commit hook gates on **new** drift, not on the known debt (`.drift-baseline.json`). Install it once:

```bash
git config core.hooksPath .githooks
```

---

## The stack

| Layer | Choice |
|---|---|
| Backend | Python + FastAPI (async), SQLAlchemy + Alembic — `backend/` |
| Frontend | One React (Vite + TS) app — `frontend/`, route-based (`/` public, `/admin/*` CRM, lazy-loaded) |
| Data | Supabase Postgres + `pgvector`. SQLAlchemy talks to Postgres directly; the Supabase client is used **only** for Auth and Storage |
| LLM | Anthropic Claude via **Amazon Bedrock**. Embeddings: Titan Text Embeddings V2 (1024-dim) |
| Architecture | Modular monolith. AI features are internal modules with clean interfaces |

---

## The rules that are easiest to get wrong

1. **Tenant isolation is enforced at the DB layer via Postgres RLS** — not just app-side filtering. App-level `tenant_id` filtering is a *second* layer, never the only one. AI modules must scope every embeddings query and Bedrock context to `tenant_id`.
2. **Layering: Router → Service → Repository → DB.** Routers hold no logic. Services write no SQL. AI adds a client layer; routers never call `ai_clients/`.
3. **Every schema change goes through an Alembic migration** — no manual edits to the database, ever.
4. **AI prompts live only in `app/ai_clients/prompts/*.py`**, versioned — never inlined in a service.
5. **Every endpoint must already exist in `docs/04-api-spec.md`.** If it doesn't, update the spec first.
6. **`tertiary` violet marks AI-generated output and nothing else.** It is a semantic color, not a decorative one.

Full set: `CLAUDE.md` and `.claude/rules/`.

---

## Commands

The `Makefile` is the entry point — Sprint 0's DoD is "clone and run", and that must be a command, not a wiki page:

```bash
make setup    # backend venv + tokens + frontend + the git hook
make dev      # how to run both processes
make test     # pytest + vitest
make check    # drift gate + tokens-current + lint + types — run before every commit
make tokens   # regenerate design tokens FROM docs/DESIGN.md
```

Underneath:

```bash
# backend/
uvicorn app.main:app --reload      # run
pytest                             # test
ruff check . && black .            # lint + format
alembic upgrade head               # migrate

# frontend/ (one app: / public, /admin CRM)
npm run dev / build / test / lint
```

---

## Document map

| # | Doc | Owns |
|---|---|---|
| 00 | `00-project-overview.md` | Product intent, stack decisions, roles |
| 01 | `01-prd.md` | **Functional requirements (FR numbers), Modules 1–16** |
| 02 | `02-architecture.md` | **Folder structure, layering, multi-tenancy strategy** |
| 03 | `03-database-schema.md` | **Tables, columns, enums, RLS pattern** |
| 04 | `04-api-spec.md` | **REST endpoints + the error envelope** |
| 05–07 | `05/06/07-ai-*.md` | Chatbot, AI Search, AI Recommendation — the three USP features |
| 08 | `08-auth-roles-spec.md` | Auth, tenant isolation, role permissions |
| 09 | `09-coding-standards.md` | Conventions + the §8 self-check |
| 10 | `10-deployment-devops.md` | Environments, CI/CD, hosting |
| 11 | `11-stitch-design-prompts.md` | Stitch prompts — 16 per-screen, 2 single-paste |
| 12 | `12-srs.md` | NFRs |
| 13 | `13-ui-ux-flows.md` | Personas, flows, site maps, breakpoints |
| 14 | `14-screen-workflows.md` | Within-screen interaction sequences |
| 15 | `15-development-plan.md` | **Sprint sequencing + `TC-*` acceptance cases** |
| 16 | `16-customer-spec/` | Per-page customer spec (public site + portal) |
| 17 | `17-admin-spec/` | Per-screen admin spec |
| 18 | `18-test-strategy.md` | **Test levels, AI evaluation, coverage gates** |
| 19 | `19-security-and-privacy.md` | **Threat model, PII handling, DPDP** |
| 20 | `20-operations-runbook.md` | **On-call, incidents, rollback** |
| 21 | `21-release-management.md` | **Versioning, release process, rollback** |
| 22 | `22-risk-register.md` | **Project risks (≠ spec gaps)** |
| — | `DESIGN.md` | **The design system. The only file that defines a color.** |
| — | `OWNERSHIP.md` | Who owns what |
| — | `GAPS.md` | **The only place a gap's state is recorded** |
| — | `adr/` | **Why decisions were made** |

---

## Build order

**Phase 1 — Foundation & Core CRM** (Sprints 0–4): auth, schema, tenancy, non-AI property and lead management.
**Phase 2 — AI Layer** (Sprints 5–7): search, chatbot, recommendation.
**Phase 3 — Scale & Polish** (Sprints 8–11).

Each sprint in `docs/15-development-plan.md` lists concrete tasks and `TC-*` cases with a Definition of Done. Treat those as the acceptance criteria.
