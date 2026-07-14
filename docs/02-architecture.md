# System Architecture — PropVista CRM

> **Doc 02 of the PropVista CRM documentation set.** Defines how the FastAPI + React + Supabase + Amazon Bedrock stack fits together, the multi-tenancy strategy, and the folder structure Claude Code should follow when scaffolding the project.
>
> **Status:** Draft v1.0 · **Last updated:** July 2026
> Depends on: `00-project-overview.md`, `01-prd.md`
> **Data layer finalized:** SQLAlchemy + Alembic (talking directly to the Supabase Postgres connection string) — Supabase's own client is used for Auth and Storage only, not for data access.

---

## 1. Architectural Style

**Chosen approach: Modular Monolith** (single FastAPI backend, single Supabase Postgres instance), not microservices.

Rationale:
- MVP scope doesn't justify microservices operational overhead.
- Tenant isolation is handled at the data layer (Section 3), not by splitting services per tenant.
- The three AI features (chat, search, recommendation) are built as internal **modules/services** within the monolith, each with a clean interface — so they *could* be extracted into standalone services later without a rewrite, if load requires it.

```
┌──────────────────────────────────────────────────────────────────┐
│                         FastAPI Backend (monolith)                 │
│                                                                     │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌────────────────┐  │
│  │ Property  │  │   Lead /  │  │   Auth /  │  │  AI Modules     │  │
│  │  Module   │  │   CRM     │  │  Tenant   │  │  - Chatbot      │  │
│  │           │  │  Module   │  │  Module   │  │  - Search       │  │
│  │           │  │           │  │           │  │  - Recommend.   │  │
│  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └────────┬────────┘  │
│        │              │              │                 │           │
└────────┼──────────────┼──────────────┼─────────────────┼───────────┘
         │              │              │                 │
         ▼              ▼              ▼                 ▼
   ┌─────────────────────────────────────────┐   ┌─────────────────┐
   │   Supabase (Postgres + pgvector +         │   │  Amazon Bedrock  │
   │   Auth + Storage) — tenant-isolated       │   │  (Claude models) │
   └─────────────────────────────────────────┘   └─────────────────┘
```

---

## 2. Component Overview

| Component | Technology | Responsibility |
|---|---|---|
| Public Site (React) | React (Vite) | Customer-facing site: search, chat, listings, details, contact, portal |
| Admin Portal (React) | React (Vite) | Admin/agent CRM back office |
| API Backend | FastAPI (Python) | All business logic, auth verification, AI orchestration |
| Database | Supabase Postgres | Relational data, row-level security, tenant isolation |
| Vector Store | Supabase `pgvector` | Property embeddings for AI Search & Recommendation |
| Auth | Supabase Auth | Identity, session/JWT issuance for both customers and admin users |
| File Storage | Supabase Storage | Property images, floor plans, documents |
| LLM Provider | Amazon Bedrock (Claude) | Chat responses, query understanding, recommendation reasoning |
| Scheduled Jobs | **Supabase `pg_cron`** | SQL-only time jobs: stale leads, listing expiry, abandoned chats, nightly rollups/purges, stuck-job reaping |
| Async Jobs | **Python worker polling a `jobs` table** | Embedding generation, de-indexing, bulk CSV import, notification dispatch. **No Celery, no Redis** |
| Email | **SendGrid** | Transactional email (new lead, escalation, match alerts) |
| SMS | **Twilio** | Opt-in, capped. Indian SMS requires DLT registration |

---

## 3. Multi-Tenancy Strategy

**Chosen approach: Shared database, shared schema, tenant-scoped via `tenant_id` + Postgres Row-Level Security (RLS).**

Rationale vs. alternatives:

| Approach | Pros | Cons | Decision |
|---|---|---|---|
| DB-per-tenant | Strongest isolation | Expensive, hard to scale/manage for many small tenants | ❌ Not chosen |
| Schema-per-tenant | Good isolation | Migration complexity grows linearly with tenants | ❌ Not chosen |
| Shared schema + `tenant_id` + RLS | Simple to scale, single migration path, Supabase-native RLS enforcement | Requires strict discipline on every query/policy | ✅ **Chosen** |

**Enforcement rules (non-negotiable):**
1. Every tenant-owned table has a `tenant_id` column (see `03-database-schema.md`).
2. Postgres RLS policies enforce `tenant_id = current_tenant_id()` at the database level — **not only** application-level filtering. This is the primary safety net against tenant data leakage.
3. The FastAPI layer resolves `tenant_id` from the authenticated request (subdomain, custom domain mapping, or JWT claim) at the very start of the request lifecycle and sets it for the duration of that request (e.g. via a Postgres session variable used by RLS policies, or explicit filtering as a second layer of defense).
4. AI modules (search, recommendation, chatbot) must always pass `tenant_id` into any embeddings query or Bedrock prompt context — never search/recommend across tenants.

---

## 4. Backend Architecture (FastAPI)

### 4.1 Layering

```
Router (HTTP layer)
   → Service (business logic)
      → Repository (data access, Supabase/Postgres queries)
         → Database
```

AI modules follow the same shape, with an added **AI Client** layer that wraps Bedrock calls:

```
Router → AI Service (e.g. ChatService) → AI Client (Bedrock wrapper) → Amazon Bedrock
                                        → Repository (property data, embeddings)
```

### 4.2 Folder Structure

```
backend/
├── app/
│   ├── main.py                     # FastAPI app entrypoint
│   ├── core/
│   │   ├── config.py               # Settings (env vars, Bedrock region, Supabase keys)
│   │   ├── security.py             # JWT verification, current-user/tenant resolution
│   │   ├── tenancy.py              # Tenant context resolution & RLS session var setup
│   │   └── logging.py
│   ├── api/
│   │   ├── deps.py                 # Shared dependencies (get_db, get_current_user, get_tenant)
│   │   └── v1/
│   │       ├── router.py           # Aggregates all v1 routers
│   │       ├── properties.py
│   │       ├── leads.py
│   │       ├── auth.py
│   │       ├── users.py
│   │       ├── agents.py
│   │       ├── reports.py
│   │       ├── tenants.py
│   │       ├── cms.py
│   │       └── ai/
│   │           ├── chat.py         # Chatbot endpoints
│   │           ├── search.py       # AI search endpoint
│   │           └── recommend.py    # Requirement-analysis endpoint
│   ├── services/
│   │   ├── property_service.py
│   │   ├── lead_service.py
│   │   ├── user_service.py
│   │   ├── agent_service.py
│   │   ├── report_service.py
│   │   ├── tenant_service.py
│   │   └── ai/
│   │       ├── chat_service.py
│   │       ├── search_service.py
│   │       └── recommend_service.py
│   ├── ai_clients/
│   │   ├── bedrock_client.py       # Thin wrapper around boto3 bedrock-runtime
│   │   ├── embeddings_client.py    # Embedding generation calls
│   │   └── prompts/                # Versioned prompt templates per AI module
│   │       ├── chat_prompts.py
│   │       ├── search_prompts.py
│   │       └── recommend_prompts.py
│   ├── repositories/
│   │   ├── property_repository.py
│   │   ├── lead_repository.py
│   │   ├── user_repository.py
│   │   └── embedding_repository.py # pgvector queries
│   ├── models/                     # SQLAlchemy ORM models
│   ├── schemas/                    # Pydantic request/response schemas
│   ├── services/
│   │   └── metrics_service.py      # THE definition of conversion/active/response time
│   ├── notifiers/                  # Channel adapters (mockable, swappable)
│   │   ├── email_sendgrid.py
│   │   ├── sms_twilio.py
│   │   └── in_app.py
│   ├── workers/                    # The jobs worker (§4.4) — a separate process
│   │   ├── runner.py               # Poll loop: FOR UPDATE SKIP LOCKED
│   │   └── handlers/
│   │       ├── embed_property.py
│   │       ├── deindex_property.py
│   │       ├── match_new_property.py
│   │       ├── bulk_import.py
│   │       └── dispatch_notification.py
│   └── tests/
├── alembic/                        # DB migrations (SQLAlchemy models → Supabase Postgres)
├── requirements.txt
└── .env.example
```

### 4.3 Key Backend Design Notes

- **`ai_clients/` is isolated from `services/`** so prompt/model changes never require touching business logic, and so Bedrock could be swapped/mocked in tests easily.
- **Prompts are versioned files**, not inline strings — this matters once tenants can customize chatbot behavior (Module 13 in the PRD) and for auditing what prompt produced a given response.
- **One `metrics_service.py`** owns the definitions of conversion rate, active leads, and response time (`03-database-schema.md` §6). The Dashboard, the Agents leaderboard, and Reports all call it. **No screen writes its own metric SQL** — three screens computing "conversion" three ways is how a CRM's numbers become untrusted.

---

### 4.4 Background Work — pg_cron + a Python Jobs Worker

*Decided 2026-07-13. Replaces the earlier "FastAPI BackgroundTasks, promote to Celery later" note, which was not viable: a lost `BackgroundTask` means a published property that silently never enters the search index — no error, no broken page, just a listing that doesn't exist to the feature the product is sold on.*

**Two mechanisms, because `pg_cron` is SQL-only** and cannot call Bedrock, SendGrid, Twilio, or parse a CSV.

```
┌── pg_cron (inside Postgres — SQL only) ────────────────────┐
│  mark_stale_leads()        → INSERT INTO jobs (notify)     │
│  expire_listings()         → INSERT INTO jobs (notify)     │
│  due_follow_ups()          → INSERT INTO jobs (notify)     │
│  mark_abandoned_chats()      (pure SQL)                    │
│  nightly_rollups_and_purge() (pure SQL — retention)        │
│  reap_stuck_jobs()           (reset stale `running` rows)  │
└────────────────────────────────────────────────────────────┘
                     │ enqueues
                     ▼
               ┌──────────┐
FastAPI ──────►│   jobs   │◄──── poll: FOR UPDATE SKIP LOCKED
 (on publish,  │  table   │                     │
  bulk upload, └──────────┘                     │
  lead create)                    ┌─────────────┴──────────────┐
                                  │  app/workers/runner.py      │
                                  │   • embed_property (Titan)  │
                                  │   • deindex_property        │
                                  │   • match_new_property      │
                                  │   • bulk_import (CSV/Excel) │
                                  │   • dispatch_notification   │
                                  │     (SendGrid / Twilio)     │
                                  └─────────────────────────────┘
```

**Deployment:** the worker is a **second long-running process** alongside the FastAPI service (a separate ECS service / App Runner instance) running `python -m app.workers.runner`. See `10-deployment-devops.md`.

**Reports are synchronous** — generated in-request, row-capped. There is no report job and no `reports` table.

#### The three things that will bite

1. **⚠️ The worker bypasses RLS.** It processes jobs across every tenant, so it connects with a role that isn't tenant-scoped. It **must** `SET LOCAL app.current_tenant_id` from `jobs.tenant_id` before touching tenant data. **A worker that forgets has no tenant isolation at all** — and unlike every other code path, RLS is not there to catch the mistake. This is the highest-risk code in the system: it gets its own cross-tenant test.

2. **⚠️ We are hand-rolling the queue** (the accepted cost of avoiding Redis). Three things must be right or work is silently lost: exponential backoff via `jobs.run_after`; a `dead` status after `max_attempts` with the error retained; and a **stuck-job reaper**, because a worker that crashes mid-job leaves a row `running` forever and nothing will ever retry it.

3. **⚠️ A failed embedding job is invisible.** The property is live on the public site and simply absent from AI search. Alert on `jobs` reaching `dead`, and surface published-but-unindexed properties in the admin property list — otherwise the failure mode is "customer says search is bad" three weeks later.

**Testing:** the worker's job handlers are unit-tested with Bedrock/SendGrid/Twilio mocked, exactly as the AI services are (`.claude/rules/testing.md`).

---

## 5. Frontend Architecture (React)

### 5.1 App Structure Decision

**Two separate React apps** (not one app with route-based role switching):
- `public-site/` — public site + customer portal (shared auth context, since customer portal is just an authenticated view of the public site).
- `admin-portal/` — admin/agent/super-admin CRM interface.

Rationale: different audiences, different design needs, and independent deploy cadences.

> **Branding — MVP scope (decided 2026-07-13).** The public site is **not tenant-branded in the MVP.** Both apps ship the single fixed palette in `docs/DESIGN.md`; there is no theming layer. Per-tenant branding is **post-MVP** (PRD FR16.2) — the split into two apps still holds on audience and deploy-cadence grounds alone, and it is what will make per-tenant theming cheap to add to `public-site/` later without touching the admin portal.

### 5.2 Folder Structure (applies to both apps, same shape)

```
public-site/
├── src/
│   ├── main.tsx
│   ├── App.tsx
│   ├── routes/
│   ├── pages/
│   │   ├── Home/
│   │   ├── Search/
│   │   ├── PropertyDetails/
│   │   ├── RequirementAnalysis/
│   │   ├── Contact/
│   │   └── CustomerPortal/
│   ├── components/
│   │   ├── chat/                   # Chatbot widget component
│   │   ├── search/                 # Search bar, filters, results grid
│   │   ├── property/               # Property card, gallery, etc.
│   │   └── shared/
│   ├── hooks/
│   ├── api/                        # API client functions calling FastAPI
│   ├── context/                    # Auth/tenant context providers
│   ├── styles/
│   └── utils/
├── package.json
└── vite.config.ts

admin-portal/
├── src/
│   ├── pages/
│   │   ├── Dashboard/
│   │   ├── Properties/
│   │   ├── Leads/                  # Kanban + table pipeline views
│   │   ├── Users/
│   │   ├── Agents/
│   │   ├── AIConfig/
│   │   ├── CMS/
│   │   ├── Reports/
│   │   └── TenantSettings/
│   ├── components/
│   ├── hooks/
│   ├── api/
│   ├── context/
│   └── ...
```

### 5.3 Shared Code

A `packages/shared-ui/` or `packages/shared-types/` (if using a monorepo tool like Turborepo/pnpm workspaces) can hold:
- Shared TypeScript types generated from the FastAPI OpenAPI schema (keeps frontend/backend contracts in sync).
- Shared design tokens if any visual elements are common between public site and admin portal.

This is a recommendation, not a hard requirement — can start as two independent apps and introduce a monorepo only if duplication becomes painful.

---

## 6. AI Data Flows

### 6.1 AI Search Flow

```
User types query → public-site/search
   → POST /api/v1/ai/search {query, tenant_id, filters}
      → search_service.py:
          1. Parse query via Bedrock (extract structured constraints: type, budget, bedrooms, location)
          2. Generate query embedding (embeddings_client.py)
          3. Query pgvector for semantic matches (scoped to tenant_id)
          4. Merge structured filter results + semantic results, rank
      → Return ranked property list
```

### 6.2 AI Chatbot Flow

```
User sends message → public-site/chat widget
   → POST /api/v1/ai/chat {message, session_id, tenant_id}
      → chat_service.py:
          1. Load conversation history (session or user-scoped)
          2. Build prompt (system prompt + tenant config from Module 13 + history + message)
          3. Call Bedrock (Claude) — with tool-calling for property lookups / lead creation if needed
          4. Persist assistant response + any lead/appointment created
      → Return bot response (+ any UI actions, e.g. "show property card")
```

### 6.3 AI Recommendation Flow

```
User submits requirement form → public-site/RequirementAnalysis
   → POST /api/v1/ai/recommend {requirements, tenant_id}
      → recommend_service.py:
          1. Generate embedding from structured requirements
          2. Query pgvector for candidate properties (tenant-scoped)
          3. Score candidates using tenant-configured weighting (Module 13)
          4. Optionally call Bedrock to generate a plain-language match reason per result
      → Return ranked shortlist with match reasons
```

### 6.4 Property Publish → Embedding Index Flow

```
Admin publishes property → admin-portal/Properties
   → POST/PUT /api/v1/properties/{id}
      → property_service.py saves property
      → triggers workers/embed_property.py (background task)
          1. Build text representation of property (description, location, amenities, etc.)
          2. Generate embedding
          3. Upsert into pgvector table, tagged with tenant_id and property_id
```

---

## 7. Authentication & Session Handling

- **Supabase Auth** issues JWTs for both customer and admin-portal users.
- FastAPI verifies the JWT on each request (`core/security.py`), extracting `user_id` and role claims.
- `tenant_id` is resolved via:
  - Admin portal: from the authenticated user's tenant association (a user belongs to exactly one tenant, except super admins).
  - Public site: from the domain/subdomain the request came in on (mapped to a tenant in `tenants` table), independent of whether the visitor is logged in.
- Anonymous visitors (not logged in) can browse, search, chat, and submit inquiries; a lightweight session ID (not a full account) tracks favorites/chat history until they register.

Full detail in `08-auth-roles-spec.md`.

---

## 8. Environments

| Environment | Purpose |
|---|---|
| **Local** | Docker Compose or local Supabase CLI + local FastAPI + local React dev servers |
| **Staging** | Mirrors production; used for tenant pilot onboarding and QA |
| **Production** | Live multi-tenant environment |

Full CI/CD and hosting detail in `10-deployment-devops.md`.

---

## 9. Third-Party Integrations (Placeholders)

| Integration | Used For | Notes |
|---|---|---|
| Maps provider (e.g. Google Maps/Mapbox) | Property location, map view | Choice TBD |
| SMS/WhatsApp provider | Notifications, callback confirmations | Choice TBD |
| Email provider | Transactional email (confirmations, notifications) | Supabase-compatible or separate (e.g. SES, given AWS/Bedrock usage) |

---

## 10. Security Considerations

- RLS as the primary tenant-isolation enforcement (Section 3) — application code is a second layer, never the only layer.
- Secrets (Supabase service key, AWS credentials for Bedrock) stored in environment variables / secrets manager, never committed.
- Rate limiting on public AI endpoints (chat, search, recommend) to control Bedrock cost exposure from abuse.
- Input validation on all AI-facing endpoints before constructing prompts (basic prompt-injection hygiene — full detail in `05-ai-chatbot-spec.md`).
- Audit logging for all admin-portal write actions (ties to PRD Module 11).

---

## 11. Open Questions / Assumptions to Confirm

- [x] ORM choice for FastAPI → **SQLAlchemy + Alembic** for migrations, used alongside the Supabase-hosted Postgres instance (Supabase Auth/Storage still used as-is; Supabase's own client is not used for data access — SQLAlchemy talks directly to the Postgres connection string).
- [ ] Monorepo (Turborepo/pnpm workspaces) vs. two fully independent React repos — recommendation given, not yet confirmed.
- [x] ~~Whether background jobs start with FastAPI `BackgroundTasks` or Celery/RQ.~~ **DECIDED 2026-07-13 — see §4.4: `pg_cron` + a Python jobs worker.** This line sat here contradicting §4.4 for a day, and it is a large part of why a *mandatory* requirement (FR10.2b) was reported as unbuildable. **An open question that has been answered is not harmless — it is a lie with a checkbox.**
- [ ] Maps and SMS/WhatsApp provider selection.

---

**Next document:** `03-database-schema.md` — entities, tables, and relationships, including the `tenant_id` + RLS pattern applied concretely.
