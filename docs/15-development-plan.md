# Development Plan — Building PropVista CRM with Claude Code

> **Doc 15 of the PropVista CRM documentation set.** A practical execution plan for building this project using Claude Code in VS Code — environment setup, phased roadmap, sprint-by-sprint tasks, and a test-case checklist per module.
>
> **Status:** Draft v1.0 · **Last updated:** July 2026
> Depends on: the full `00`–`14` doc set (this doc sequences the work; it doesn't redefine requirements)

---

## 1. Before You Start: Environment & Setup

1. **Install Claude Code** in VS Code (the Claude Code extension, or the CLI integrated into the VS Code terminal).
2. **Initialize the repo** with the structure from `02-architecture.md` Section 4.2/5.2 — two top-level app folders: `backend/` and `frontend/` (one route-based React app: `/` public, `/admin/*` CRM, lazy-loaded — ADR-0020, superseding the earlier two-app split).
3. **Create a `docs/` folder at the repo root** and drop all 15 documents (`00`–`14`) into it — this is what makes Claude Code's output consistent with everything we've planned.
4. **Create a `CLAUDE.md`** at the repo root (project-level instructions Claude Code reads automatically each session). At minimum it should say:
   - "Read `docs/00-project-overview.md` through `docs/14-screen-workflows.md` before making architectural decisions."
   - "Follow `docs/09-coding-standards.md` for every change — folder layering, migrations, prompt file isolation."
   - "Every new endpoint must exist in `docs/04-api-spec.md` first; every schema change needs an Alembic migration."
   - I can generate this file for you now if useful — just ask.
5. **Set up `.env` files** per `09-coding-standards.md` Section 7 — Supabase connection string, Supabase service key, AWS credentials for Bedrock. Never commit these; commit only `.env.example`.
6. **Set up the base tooling**: `black`/`ruff` for Python, `eslint`/`prettier` for the React app, `pytest`, `Vitest` — per `09-coding-standards.md` Sections 2.1 and 3.1.

---

## 2. How to Work With Claude Code on This Project

- **One module or one sprint task per session/prompt** — don't ask for "the whole backend" in one go. Claude Code does best with a scoped, well-referenced task (e.g. "Implement the Property Management endpoints from `04-api-spec.md` Section 8, using the schema in `03-database-schema.md`").
- **Always point it at the relevant doc(s)** rather than re-explaining requirements from memory — the docs are the source of truth, and referencing them keeps output consistent across sessions.
- **Ask it to write tests alongside the implementation**, not after — cheaper to catch drift immediately (per `09-coding-standards.md` Section 5).
- **Run the code review checklist** (`09-coding-standards.md` Section 8) at the end of every task, before merging — ask Claude Code to self-check against it explicitly.
- **Update the docs first if requirements change mid-build** — if a sprint reveals a PRD gap, fix `01-prd.md` (or the relevant spec doc) before implementing the fix, so the docs don't drift from the code (same principle as `09-coding-standards.md` Section 1).

---

## 3. Development Phases (Expanded from `10-deployment-devops.md`)

| Phase | Focus | Sprints |
|---|---|---|
| **Phase 1 — Foundation & Core CRM** | Auth, schema, non-AI property/lead management | Sprint 0–4 |
| **Phase 2 — AI Layer** | AI Search, AI Chatbot, AI Recommendation | Sprint 5–7 |
| **Phase 3 — Scale & Polish** | Remaining admin modules, hardening, deployment, pilot prep | Sprint 8–11 |

Assumes 2-week sprints — adjust pace to your actual team size; the sequencing (what depends on what) matters more than the exact durations.

---

## 4. Sprint-by-Sprint Plan

### Sprint 0 — Environment & Foundation
**Goal:** A running skeleton, not features yet.
- Scaffold `backend/` (FastAPI app, folder structure per `02-architecture.md` §4.2) and `frontend/` (one Vite + React app, route-based — §5.2, ADR-0020).
- Set up Supabase project (Postgres, Auth, Storage), connect via SQLAlchemy + Alembic.
- Set up CI skeleton (lint + test on PR, per `10-deployment-devops.md` §3).
- `/health` endpoint working end-to-end (backend deployed to staging, per `10-deployment-devops.md` §1).
- **Test cases:** CI pipeline runs and passes on an empty commit; `/health` returns 200 in staging.
- **Definition of Done:** A developer can clone the repo, run both apps locally (`make setup` → `make dev`), and hit a real (empty) staging deployment.

### Sprint 1 — Data Layer, Auth & Tenancy
**Goal:** Every subsequent feature can assume auth and tenant scoping work.
- Implement core tables (`tenants`, `users`, `roles_permissions`) via Alembic migrations (`03-database-schema.md` §3.1–3.3).
- Implement RLS policies for tenant-owned tables using the repeatable migration macro (`03-database-schema.md` §4, `09-coding-standards.md` §2.6).
- Wire up Supabase Auth (`08-auth-roles-spec.md` §1–2); `core/security.py` JWT verification; `require_role` dependency.
- Anonymous session handling (`X-Session-Id` header pattern, `08-auth-roles-spec.md` §4).
- **Test cases:**
  - `TC-AUTH-01`: valid JWT resolves the correct `users` row and role.
  - `TC-AUTH-02`: expired/invalid JWT is rejected on a protected route (`NFR-SEC-2`).
  - `TC-TENANT-01`: a user from Tenant A cannot read/write a row belonging to Tenant B, for every tenant-owned table created so far (`NFR-SEC-1`).
  - `TC-TENANT-02`: anonymous session data is correctly scoped by `session_id`.
- **Definition of Done:** Two seeded test tenants exist; cross-tenant access attempts fail at the DB layer, not just the API layer.

### Sprint 2 — Property Management (Non-AI)
**Goal:** Admins can manage listings end-to-end.
- `properties`, `property_media` tables + Alembic migrations.
- CRUD endpoints (`04-api-spec.md` §8), bulk upload, approval workflow, status flags (PRD FR9.1–FR9.4).
- Admin UI: property list + multi-step add/edit form (matches the `07-property-management.jsx` mockup already built).
- **Test cases:**
  - `TC-PROP-01`: creating a property with `pending_approval` status is not publicly visible until approved.
  - `TC-PROP-02`: bulk upload with malformed rows reports per-row errors, not a full-batch failure.
  - `TC-PROP-03`: an agent without `properties.edit` permission gets a 403 on write endpoints (`NFR-SEC-3`).
- **Definition of Done:** An admin can add, edit, approve, and feature a property through the actual UI, and see it persist on reload.

### Sprint 3 — Public Property Listing & Details
**Goal:** The non-AI public browsing experience is fully functional.
- `GET /properties`, `GET /properties/{id}` endpoints with structured filters (`04-api-spec.md` §4).
- Public site: Property Listing and Property Details pages (matches `03-property-listing.jsx`, `04-property-details.jsx` mockups), grid/list/map toggle, favorites (session + persisted post-login).
- **Test cases:**
  - `TC-LIST-01`: combining multiple filters (price + type + bedrooms) returns correctly intersected results.
  - `TC-LIST-02`: favoriting works pre-login and migrates correctly to the account after registration (`08-auth-roles-spec.md` §4).
  - `TC-DETAILS-01`: Property Details page renders correctly with partial data (e.g. missing floor plan) — no layout breakage (per PRD §6 acceptance criteria).
- **Definition of Done:** A visitor can browse, filter, favorite, and view full details on real seeded property data.

### Sprint 4 — Contact/Lead Capture & Basic CRM Pipeline
**Goal:** Inquiries become trackable leads; agents can work them.
- `leads`, `lead_notes`, `lead_activities` tables + endpoints (`04-api-spec.md` §5, §9).
- Contact form + callback request UI on the public site.
- Admin Lead Pipeline Kanban (matches `08-lead-pipeline.jsx` mockup) — manual stage changes, notes, reminders (no AI-sourced leads yet, that comes in Phase 2).
- **Test cases:**
  - `TC-LEAD-01`: every lead has a non-null `source` field (`01-prd.md` FR10.4 acceptance criteria).
  - `TC-LEAD-02`: stage changes are recorded in `lead_activities` with correct timestamps.
  - `TC-LEAD-03`: an agent can only see/edit leads assigned to them, per the ownership-scoping rule (`08-auth-roles-spec.md` §5).
- **Definition of Done:** A submitted contact form becomes a lead visible in the Kanban board, and an agent can move it through stages end-to-end.

**— Phase 1 checkpoint —** at this point you have a fully functional non-AI real estate CRM. This is a legitimate internal milestone even before AI features exist.

### Sprint 5 — AI Search
**Goal:** Natural-language search works end-to-end.
- `property_embeddings` table (`03-database-schema.md` §3.6); embedding generation background job on property publish (`06-ai-search-spec.md` §4).
- `ai_clients/bedrock_client.py`, `ai_clients/embeddings_client.py`; query parsing + embedding pipeline (`06-ai-search-spec.md` §2–3).
- `/ai/search` endpoint with fallback behavior (`06-ai-search-spec.md` §8).
- Homepage search bar + auto-suggest wired to real results (matches `01-homepage.jsx` mockup).
- **Test cases:**
  - `TC-SEARCH-01`: golden query set (`06-ai-search-spec.md` §9) — spot-check relevance against human judgment.
  - `TC-SEARCH-02`: Bedrock timeout triggers fallback to standard filter search, not an error page (`NFR-AVAIL-1`).
  - `TC-SEARCH-03`: search results never include another tenant's properties (`NFR-SEC-1`).
- **Definition of Done:** Typing a natural-language query on the real homepage returns relevant, tenant-scoped results within the target latency.

### Sprint 6 — AI Chatbot
**Goal:** The conversational assistant works end-to-end, including lead creation and escalation.
- Chat prompt layering (`ai_clients/prompts/chat_prompts.py`, `05-ai-chatbot-spec.md` §3); tool definitions (§4).
- `/ai/chat/message`, `/ai/chat/history`, `/ai/chat/escalate` endpoints (`04-api-spec.md` §3.2).
- Chat widget UI wired to real streaming responses (matches `02-chat-widget.jsx` mockup).
- **Test cases:**
  - `TC-CHAT-01`: golden conversation test set (`05-ai-chatbot-spec.md` §12) — no hallucinated property facts.
  - `TC-CHAT-02`: a conversation that results in contact info being shared creates a lead with `source = 'chatbot'`.
  - `TC-CHAT-03`: explicit "talk to a human" request triggers escalation and is visible in the Lead Pipeline.
  - `TC-CHAT-04`: prompt-injection attempt in a user message does not alter bot behavior (`NFR-SEC-5`).
- **Definition of Done:** A real conversation on the live site can look up a real property, capture a lead, and escalate correctly.

### Sprint 7 — AI Recommendation
**Goal:** The requirement wizard produces real, explainable matches.
- `requirement_profiles`, `requirement_matches` tables + endpoints (`04-api-spec.md` §3.3).
- Scoring engine (`07-ai-recommendation-spec.md` §4) with tenant-configurable weights (`ai_config.recommendation_weights`).
- Match-reason generation via Bedrock (§5); saved-profile re-matching on new property publish (§6).
- Requirement Wizard UI wired to real results (matches `05-requirement-wizard.jsx` mockup).
- **Test cases:**
  - `TC-REC-01`: golden requirement-profile set (`07-ai-recommendation-spec.md` §9) — spot-check match quality.
  - `TC-REC-02`: submission with no strong matches returns a closest-match fallback, never an empty state (FR3.2).
  - `TC-REC-03`: a saved profile receives a new match/notification when a qualifying property is published.
- **Definition of Done:** A visitor can complete the wizard and get a ranked, explained shortlist from real data; a registered visitor gets notified when a new match appears later.

**— Phase 2 checkpoint —** all three core USP features (chat, search, recommendation) are live. This is the meaningful "MVP complete" milestone for demoing to pilot tenants.

### Sprint 8 — Remaining Admin Modules (Part 1)
**Goal:** Admins have full operational visibility.
- Admin Dashboard & Analytics (`04-api-spec.md` §7) wired to real data (matches `06-admin-dashboard.jsx` mockup).
- User & Role Management (`04-api-spec.md` §10), Agent/Broker Management (§11).
- **Test cases:**
  - `TC-DASH-01`: KPI numbers reconcile with underlying lead/property counts for the tenant.
  - `TC-ROLE-01`: a newly invited agent has correctly scoped access from first login.
- **Definition of Done:** An admin can invite a teammate, see them show up with correct permissions, and see accurate dashboard metrics.

### Sprint 9 — Remaining Admin Modules (Part 2)
**Goal:** Tenants can self-serve content, reports, and AI tuning.
- AI Configuration UI (`04-api-spec.md` §12) — chatbot greeting/FAQ, recommendation weights, conversation log viewer.
- CMS (§13), Reports & Notifications (§14).
- **Test cases:**
  - `TC-AICONFIG-01`: changing the chatbot greeting takes effect on the next new conversation without a deployment.
  - `TC-REPORT-01`: exported report figures match the dashboard for the same filter/date range.
- **Definition of Done:** A tenant admin can tune their AI chatbot's FAQ content and pull an accurate leads report without engineering involvement.

### Sprint 10 — Tenant Onboarding & Hardening
**Goal:** The platform is genuinely multi-tenant-ready and secure.
- Tenant & Branding Settings (`04-api-spec.md` §15); custom domain resolution (`02-architecture.md` §7, `10-deployment-devops.md` §8).
- Full security pass: rate limiting on AI endpoints (`10-deployment-devops.md` §6), secrets audit, RLS test coverage audit across every table.
- Load testing against the performance/scalability NFRs (`12-srs.md` §3.1–3.2).
- **Test cases:**
  - `TC-TENANT-03`: a second full tenant can be onboarded end-to-end (branding, first property, first lead) with zero cross-tenant leakage.
  - `TC-PERF-01`: AI Search/Chat/Recommendation meet their latency targets under simulated pilot-scale load.
  - `TC-SEC-01`: rate limits correctly throttle abusive request patterns on `/ai/*` endpoints without blocking normal usage.
- **Definition of Done:** A second tenant can be onboarded by a non-engineer following documented steps, with security/perf sign-off.

### Sprint 11 — Pilot Prep
**Goal:** Ready for real pilot tenants.
- Full regression pass across all golden test sets (chat, search, recommendation).
- UAT with actual pilot-candidate content (real property data, real tenant branding).
- Bug bash against the full `01-prd.md` acceptance criteria list, module by module.
- Finalize monitoring/alerting (`10-deployment-devops.md` §5) and backup verification (§7).
- **Test cases:** Full traceability sweep — every `NFR` and `UC` in `12-srs.md` Section 6's matrix gets a final pass/fail check.
- **Definition of Done:** Every PRD module's acceptance criteria (`01-prd.md`) passes against real data, in the staging environment, with a pilot tenant's actual content loaded.

---

## 5. Test Case Summary Table (Quick Reference)

| Category | Sample IDs | Traces To |
|---|---|---|
| Auth & Tenancy | `TC-AUTH-*`, `TC-TENANT-*` | `08-auth-roles-spec.md`, `12-srs.md` NFR-SEC-1/2 |
| Property Management | `TC-PROP-*` | `01-prd.md` Module 9 |
| Listing/Details | `TC-LIST-*`, `TC-DETAILS-*` | `01-prd.md` Modules 4–5 |
| Leads/CRM | `TC-LEAD-*` | `01-prd.md` Module 10 |
| AI Search | `TC-SEARCH-*` | `06-ai-search-spec.md` §9 |
| AI Chatbot | `TC-CHAT-*` | `05-ai-chatbot-spec.md` §12 |
| AI Recommendation | `TC-REC-*` | `07-ai-recommendation-spec.md` §9 |
| Dashboard/Roles | `TC-DASH-*`, `TC-ROLE-*` | `01-prd.md` Modules 8, 11 |
| AI Config/Reports | `TC-AICONFIG-*`, `TC-REPORT-*` | `01-prd.md` Modules 13, 15 |
| Performance/Security | `TC-PERF-*`, `TC-SEC-*` | `12-srs.md` Sections 3.1, 3.4 |

This table is a map, not a full test plan — expand each `TC-*` ID into a real pytest/Vitest test as it's implemented, and keep this table updated with actual test file locations once they exist.

---

## 6. Open Questions / Assumptions to Confirm

- [ ] Actual team size/velocity — the 12-sprint (~24 week) estimate assumes a small team working with Claude Code, not a solo developer; adjust sprint count to your real pace.
- [ ] Whether golden test sets (chat/search/recommendation) are built incrementally per sprint or as a dedicated effort before Sprint 11 — recommend building them incrementally, alongside each AI feature's sprint, so evaluation isn't rushed at the end.
- [ ] Whether a staging pilot tenant's real data is available early enough to inform Sprint 10–11 testing, or if synthetic data needs to carry those sprints too.

---

**This is the final planning document.** From here, work moves into `backend/`, `public-site/`, and `admin-portal/` themselves — Claude Code in VS Code, guided by `CLAUDE.md` and this sprint plan, sprint by sprint.
