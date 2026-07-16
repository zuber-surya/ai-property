# AGENTS.md — AI Coding Agent Instructions

> **Centralized guide for AI coding agents (Claude, Cursor, Copilot) building PropVista CRM.** This file synthesizes the project's conventions, non-negotiables, and workflows. Start here; then dive into `.claude/rules/` and `.claude/modules/` as your task requires.

---

## 🎯 Core Principles

1. **Docs are the source of truth.** Code must never drift ahead of specs. Read the relevant `docs/` section *before* writing code. If a requirement isn't in the docs, add it there first.
2. **One owner per concept.** Every value (color, endpoint, table, gap) has exactly one owner file. Never fork a definition into multiple places.
3. **Tenant isolation is non-negotiable.** Enforced at the DB layer (Postgres RLS), not just the app layer.
4. **All I/O is async.** FastAPI endpoints, Bedrock calls, and repository queries use `async def`.
5. **Explicit > implicit.** Tenacity over cleverness. Future agents must read the code without the conversation history.

---

## 🚀 Quick Start for a New Task

### Before you start
```
1. Read CLAUDE.md (2 min) — non-negotiables, stack, build order
2. Identify your domain → read .claude/modules/{domain}.md (3 min)
3. Read .claude/rules/{relevant-rules}.md (varies by domain)
4. Read the owning doc (docs/0X-*.md) cited in the module playbook (10 min)
```

### Example: Add a new property endpoint
```
Task: Add POST /api/v1/admin/properties/approve

1. CLAUDE.md § Rules #5 → "Every endpoint must exist in docs/04-api-spec.md first"
   → Grep to prove it:  grep -n "properties/{id}/approve" docs/04-api-spec.md
   → No hit? The spec changes FIRST. (This one IS specced — §8.)

2. Read .claude/modules/property.md
   → Tells you: "Tables: properties, property_media, property_embeddings.
               (There is no property_approvals table — approval is a
                status transition on properties.status.)
               Rules: backend.md, database.md, testing.md, security.md"
   
3. Read those four rule files
   → backend.md: "Router → Service → Repository → DB"
   → database.md: "Use Alembic for schema, RLS enforces tenant_id"
   → testing.md: "Unit test service (repos mocked); integration test with real Postgres"
   → security.md: "Enforce tenant_id + role on every query"

4. Read docs/04-api-spec.md §8 (you updated it) + docs/17-admin-spec/06-property-approvals-status.md
   → Tells you: "Screen shows draft → pending → published flow.
                 Approval is admin-only (role check).
                 Publishing ENQUEUES the jobs pipeline: embed → index →
                 match saved profiles → notify (02-architecture.md §4.4).
                 Rejection REQUIRES a reason — an approval gate that can
                 only say 'yes' isn't one."

5. Code with confidence knowing exactly what you're building and why
```

---

## 📚 Documentation Map

| File | Purpose | When to Read |
|---|---|---|
| `CLAUDE.md` | Non-negotiables, stack, build order | Start here (2 min) |
| `ROUTE_MAP.md` | All routes + endpoints, tenant scoping, implementation status | Planning frontend/backend work |
| `docs/00-project-overview.md` | Product intent, stack decisions, known gaps | Context (5 min) |
| `docs/01-prd.md` | Functional requirements (FR1–FR16) | Understanding a feature (varies) |
| `docs/02-architecture.md` | Folder structure, layering, multi-tenancy | Scaffolding new modules |
| `docs/03-database-schema.md` | Tables, columns, RLS pattern | Building data access |
| `docs/04-api-spec.md` | Endpoints + request/response contracts | Adding/modifying endpoints |
| `docs/05/06/07-ai-*.md` | Chatbot, Search, Recommendation specs | Building AI features |
| `docs/08-auth-roles-spec.md` | Auth flow, role permissions, tenant resolution | Implementing access control |
| `docs/09-coding-standards.md` | Style, testing, self-check | Every code submission |
| `docs/10-deployment-devops.md` | Environments, CI/CD, secrets | Deployment work |
| `docs/15-development-plan.md` | Sprint-by-sprint build order + test cases | Planning work scope |
| `docs/16-customer-spec/` | Per-page specs (public site + portal) | Building customer-facing screens |
| `docs/17-admin-spec/` | Per-screen specs (admin portal) | Building admin screens |
| `docs/DESIGN.md` | Colors, type, spacing, components | Styling any UI |
| `docs/GAPS.md` | Known spec gaps (G1–G11) | Unblocking work |
| `docs/OWNERSHIP.md` | Who owns each concept + dependency graph | Resolving conflicts |
| `.claude/rules/` | Cross-cutting engineering practices | Reading as-needed |
| `.claude/modules/` | Domain-specific playbooks + test cases | When starting a domain |

---

## 🛠️ The Non-Negotiables

Read `.claude/rules/{relevant}.md` for details. These are the easiest to get wrong:

### Tenant Isolation (`.claude/rules/security.md`)
- **Every** tenant-owned table has `tenant_id UUID NOT NULL REFERENCES tenants(id)`
- RLS enforces `tenant_id = current_tenant_id()` at the DB layer
- App-layer filters `user_id` on every by-ID fetch (IDOR prevention)
- Tests must verify: Tenant A cannot read/write Tenant B rows (failing at DB layer)

### Backend Layering (`.claude/rules/backend.md`)
```
Router → Service → Repository → DB

- Router: Parse request, call ONE service method, return response
- Service: Business logic, orchestrate repos + AI clients, never raw SQL
- Repository: SQLAlchemy queries only, enforce tenant_id scoping
- Never: Call ai_clients/ from a router, raw SQL in a service
```

### AI Modules (`.claude/rules/ai.md`)
- Prompts live **only** in `app/ai_clients/prompts/*.py`, versioned via docstring
- **Always** pass `tenant_id` to Bedrock (never search/recommend across tenants)
- Log latency + token usage on every call (cost tracking + debugging)
- Features degrade on failure (fallback search, connect-to-agent, closest-match list)
- Use lighter Claude model for quick tasks (e.g., query parsing); stronger for reasoning

### Database (`.claude/rules/database.md`)
- **All** schema changes via Alembic migration — no manual Postgres edits
- RLS policies via one reusable migration macro, never hand-written per-table SQL
- Soft-delete (deleted_at) on user-facing entities (properties, leads, users)

### Async (`.claude/rules/backend.md`)
- All I/O endpoints: `async def`
- Bedrock calls use async boto3 (don't block the event loop)
- Services never construct sync queries

### API First (CLAUDE.md § Non-Negotiables #5)
- New endpoint → add to `docs/04-api-spec.md` **first**
- New table → add to `docs/03-database-schema.md` **first**
- New gap → record in `docs/GAPS.md` **first**

---

## 📋 Module Playbooks

When starting a domain, open its playbook in `.claude/modules/`:

| Playbook | Covers | Quick Link |
|---|---|---|
| **auth-tenant** | Auth, roles, tenant scoping (Module 11, 16) | `.claude/modules/auth-tenant.md` |
| **property** | Property CRUD, bulk upload, approvals (Module 9) | `.claude/modules/property.md` |
| **lead-crm** | Lead capture, pipeline, assignment (Module 10) | `.claude/modules/lead-crm.md` |
| **ai-chatbot** | Chatbot service, system prompts, handoff (Module 1) | `.claude/modules/ai-chatbot.md` |
| **ai-search** | AI search, query parsing, ranking (Module 2) | `.claude/modules/ai-search.md` |
| **ai-recommendation** | Requirement wizard, rec engine, matching (Module 3) | `.claude/modules/ai-recommendation.md` |

Each playbook names:
- Exact `docs/` sections to read
- Database tables + relationships
- PRD FR numbers
- Acceptance test cases (`TC-*`)
- Specific non-negotiables from `.claude/rules/`

---

## 🗺️ Routing & APIs

**Use `ROUTE_MAP.md` as your master reference for routes and endpoints.**

Key facts:
- **Public site** (`/`, `/search`, `/property/:id`, etc.) — anonymous via `X-Session-Id`
- **Customer portal** (`/portal/*`) — authenticated (`Bearer` token)
- **Admin portal** (`/admin/*`, `/platform/*`) — authenticated + role-based
- **API layer** (`/api/v1/*`) — all endpoints cross-tenant, scoped by bearer/session

See `ROUTE_MAP.md` for:
- Complete route listings per surface
- Request/response bodies
- Tenant scoping rules
- Implementation status (MVP vs. post-MVP)
- By-module quick reference

---

## ✅ Submission Checklist

Before marking a task complete, run:

```bash
python scripts/check_drift.py     # Must pass with no NEW findings
```

Then check `docs/09-coding-standards.md` §8:
- [ ] Matches folder/layering in `docs/02-architecture.md`?
- [ ] Every new endpoint exists in `docs/04-api-spec.md` (or spec updated first)?
- [ ] Tenant-owned tables/queries respect `tenant_id` scoping (RLS + app-layer)?
- [ ] AI prompts in `app/ai_clients/prompts/`, not inlined?
- [ ] DB changes via Alembic migration?
- [ ] Secrets from env vars (`.env.example` current)?
- [ ] Tests cover logic + tenant-isolation + edge cases?
- [ ] Type hints on all signatures?
- [ ] Code formatted (`black .` / `prettier`)?
- [ ] Commit message references PRD module (e.g., `Add property approval endpoint (PRD Module 9)`)?

---

## 🚨 Sandboxes & Safety

**Permission allowlist** (`.claude/settings.json`):
- ✅ `python`, `npm`, `bash` — safe tools only
- ✅ File read/write in `/docs`, `/backend`, `/public-site`, `/admin-portal`, `.claude/`
- ❌ Unrestricted network, database write, shell eval

**Building a new app?** Use the `project-setup` skill. It scaffolds complete project structures with proper layering.

---

## 🔍 Common Pitfalls

1. **"I'll invent this endpoint locally"** → No. Add it to `docs/04-api-spec.md` first, then implement.
2. **"I'll put this color in the code"** → No. Add it to `docs/DESIGN.md`, then reference the token.
3. **"I'll just filter by tenant in the service"** → No. RLS enforces it at the DB layer; service filtering is the *second* layer.
4. **"I'll use sync SQLAlchemy for this one"** → No. All I/O is async.
5. **"I'll put the prompt in the function"** → No. Prompts live in `app/ai_clients/prompts/*.py` only.
6. **"I don't have time to test tenant isolation"** → Then you haven't tested. Every new tenant-owned table needs a cross-tenant-access test.
7. **"The docs say X but the code does Y"** → Update the docs first, then the code. Never the other way around.

---

## 🤔 Stuck?

- **Spec gap blocking you?** → Check `docs/GAPS.md`. Record the gap if it's not there.
- **Conflict between two docs?** → Check `docs/OWNERSHIP.md`. The owner file wins.
- **Unsure if this is a new table?** → Check `docs/03-database-schema.md` §3 (table index).
- **Unsure if this is a new endpoint?** → Check `docs/04-api-spec.md`.
- **Unsure of the build order?** → Follow `docs/15-development-plan.md` §4 (phased plan).

---

## 📖 Session Workflows

**Iterative refinement:** Use `/chronicle improve` to track patterns across sessions and iteratively refine instructions.

**Code review ready?** Ensure the commit:
- References a PRD module in the message
- Passes `check_drift.py`
- Includes tests (unit + integration for repos, cross-tenant for new tables)
- Matches the self-check in `docs/09-coding-standards.md` §8

---

**Last updated:** 2026-07-14 | **Verified against:** `CLAUDE.md`, `.claude/rules/`, `.claude/modules/`, `ROUTE_MAP.md`, `docs/04-api-spec.md`
