# Coding Standards — PropVista CRM

> **Doc 09 of the PropVista CRM documentation set.** Conventions Claude Code (and any human contributors) should follow consistently across the FastAPI backend and the React frontend, so the codebase stays coherent as it's built incrementally, doc by doc, module by module.
>
> **Status:** Draft v1.0 · **Last updated:** July 2026
> Depends on: `02-architecture.md` (folder structure), `03-database-schema.md`, `04-api-spec.md`

---

## 1. General Principles

- **Follow the folder structure in `02-architecture.md` exactly** — don't introduce new top-level folders or reorganize layers (router → service → repository) without updating that doc first.
- **Every new API endpoint must trace back to a PRD module** (`01-prd.md`) and an entry in `04-api-spec.md`. If it doesn't exist there, add it to the spec before implementing — the docs are the source of truth, not the other way around.
- **Prefer explicit over clever.** This codebase will be built incrementally by an AI coding agent across many sessions — code should be readable without needing the full conversation history that produced it.
- **Small, focused commits/PRs** — one module or one clear change per commit, not sweeping multi-module changes.

---

## 2. Python / FastAPI Conventions

### 2.1 Style & Tooling
- Formatter: `black`. Linter: `ruff`. Import sorting: `ruff` (isort-compatible) or `isort` directly.
- Type hints are **required** on all function signatures — this codebase leans on Pydantic + type hints for correctness, not runtime checks.
- Docstrings (short, one-line is fine) required on all service-layer functions and any non-trivial repository method — router functions can rely on FastAPI's own OpenAPI description via the endpoint decorator instead.

### 2.2 Naming
- Files/modules: `snake_case.py`.
- Classes: `PascalCase` (`PropertyService`, `LeadRepository`).
- Functions/variables: `snake_case`.
- Pydantic schemas: suffix by purpose — `PropertyCreate`, `PropertyUpdate`, `PropertyOut` (never reuse one schema for both request and response shapes if they differ).

### 2.3 Layering Discipline
- Routers (`api/v1/*.py`) only: parse request, call one service method, return response. No business logic in routers.
- Services (`services/*.py`) hold business logic and orchestrate repositories/AI clients. Services never construct raw SQL — that's the repository's job.
- Repositories (`repositories/*.py`) are the only place raw SQLAlchemy queries live.
- AI modules follow `Router → AI Service → AI Client (Bedrock) + Repository`, per `02-architecture.md` Section 4.1 — never call `ai_clients/` directly from a router.

### 2.4 Error Handling
- Raise domain-specific exceptions in the service layer (e.g. `PropertyNotFoundError`), caught by a shared FastAPI exception handler that maps them to the standard error envelope from `04-api-spec.md` Section 1 (`{"error": {"code": ..., "message": ...}}`).
- Never let a raw database or Bedrock exception bubble up to the client response — always translate to the standard error shape.

### 2.5 Async
- All I/O-bound endpoints (DB calls, Bedrock calls) are `async def`. Bedrock calls specifically use the async boto3 client pattern to avoid blocking the event loop, since chat/search/recommend are latency-sensitive (per `05`–`07` spec docs).

### 2.6 Migrations
- Every schema change goes through an **Alembic migration** — no manual schema edits against the Supabase Postgres instance directly, even in early development, so `03-database-schema.md` and the actual DB never drift apart silently.
- RLS policies (per `03-database-schema.md` Section 4) follow a **repeatable migration macro/helper** rather than hand-written SQL per table, since the same tenant-isolation pattern applies to every tenant-owned table — write one helper function once, reuse it in each table's migration.

### 2.7 AI Prompt Files
- Prompts live only in `ai_clients/prompts/*.py`, never inlined in a service function (per `02-architecture.md` Section 4.3).
- Each prompt constant/function is versioned in a comment or docstring (e.g. `# v1 - initial chatbot base prompt`) so changes are traceable when evaluation results shift (ties to the evaluation approach in `05`/`06`/`07`).

---

## 3. React / TypeScript Conventions

### 3.1 Style & Tooling
- Formatter: `prettier`. Linter: `eslint` (TypeScript + React rules).
- TypeScript strict mode on. No `any` without an inline comment justifying it.
- Functional components with hooks only — no class components.

### 3.2 Naming
- Component files: `PascalCase.tsx` matching the component name (`PropertyCard.tsx`).
- Hooks: `useSomething.ts`.
- API client functions: `camelCase`, grouped by domain in `api/` (e.g. `api/properties.ts` exporting `getProperties()`, `getPropertyById()`).

### 3.3 Structure
- Follow the `pages/` + `components/` + `hooks/` + `api/` + `context/` split from `02-architecture.md` Section 5.2 — page components own data-fetching/orchestration, `components/` stays presentational/reusable where possible.
- The chat widget, search bar, and recommendation wizard (the three USP features) each get their own component subfolder (`components/chat/`, `components/search/`, etc.) — keep their logic self-contained rather than scattered across shared components, since these are the most iterated-on parts of the product.

### 3.4 API Contract Sync
- Frontend types for API request/response shapes should be generated from the FastAPI OpenAPI schema where practical (per the open question in `04-api-spec.md` Section 17) rather than hand-duplicated — reduces drift between backend Pydantic schemas and frontend TypeScript types.

### 3.5 State Management
- Local/component state via `useState`/`useReducer` by default. Only introduce a global state library (if ever needed) for genuinely cross-cutting state (e.g. auth/tenant context) — implemented via React Context (`context/`), not a heavier state library, unless a concrete need emerges.

---

## 4. Git Conventions

- **Branch naming:** `feature/<module>-<short-description>`, `fix/<short-description>` (e.g. `feature/ai-search-ranking`, `fix/lead-assignment-bug`).
- **Commit messages:** short imperative summary line, referencing the PRD module or doc where relevant (e.g. `Add property bulk-upload endpoint (PRD Module 9)`).
- **No direct commits to `main`** — even for a solo-plus-AI-agent workflow, keep changes reviewable in small units.

---

## 5. Testing Conventions

- Backend: `pytest`. Unit tests for services (business logic) with repositories mocked; a smaller set of integration tests hitting a real (test) Supabase Postgres instance for repository-layer and RLS-policy correctness.
- AI modules: cannot be fully unit-tested against a live Bedrock call in CI — use the golden test sets described in `05`/`06`/`07` as a separate, manually or periodically run evaluation suite, not part of the standard fast unit-test run. Mock the Bedrock client for standard unit tests of surrounding logic (e.g. "does the service correctly call `create_lead` when the model requests that tool").
- Frontend: component tests via Vitest/React Testing Library for key interactive components (chat widget, search bar, requirement wizard, lead Kanban board).
- **Tenant isolation must have explicit tests** — at least one test per tenant-owned table confirming a user from Tenant A cannot read/write Tenant B's rows, given the earlier decision to keep RLS defined and enforced (`03-database-schema.md`) even though `08-auth-roles-spec.md` didn't re-derive it.

---

## 6. Documentation-in-Code

- Every new module (backend service or frontend feature folder) gets a short `README.md` only if its purpose isn't obvious from the doc set — prefer keeping the numbered docs (`00`–`10`) as the canonical reference over scattering explanation across the codebase.
- FastAPI's auto-generated OpenAPI docs (`/docs`) should stay accurate — meaning endpoint docstrings/response models are kept in sync with actual behavior, not just written once and forgotten.

---

## 7. Secrets & Configuration

- All secrets (Supabase service key, AWS credentials for Bedrock) via environment variables, loaded through `core/config.py` (per `02-architecture.md`) — never hardcoded, never committed. `.env.example` lists required variables with placeholder values.
- Config values that differ by environment (Section 8 of `02-architecture.md`) are environment-variable-driven, not hardcoded conditionals on an environment name.

---

## 8. Code Review Checklist (Self-Check for Claude Code)

Before considering a change complete:
- [ ] Does it match the folder/layering structure in `02-architecture.md`?
- [ ] Does every new endpoint exist in `04-api-spec.md`? If not, was the spec updated first?
- [ ] Are tenant-owned tables/queries respecting `tenant_id` scoping (`03-database-schema.md`)?
- [ ] Are AI prompts in `ai_clients/prompts/`, not inlined?
- [ ] Do new DB changes go through an Alembic migration?
- [ ] Are secrets read from environment variables, not hardcoded?
- [ ] Are there tests covering the new logic (and tenant-isolation tests, if a new tenant-owned table was added)?

---

## 9. Open Questions / Assumptions to Confirm

- [ ] Whether OpenAPI-to-TypeScript type generation is automated in CI or run manually as a dev-time step.
- [ ] CI provider/setup — to be finalized alongside `10-deployment-devops.md`.

---

**Next document:** `10-deployment-devops.md` — environments, CI/CD, and hosting approach, closing out the documentation set.
