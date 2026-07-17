# Project Overview — PropVista CRM

> **Doc 00 of the PropVista CRM documentation set.** This is the entry point — read this first. It links out to every other document that will be built for this project.
>
> **Status:** Draft v1.0 · **Last updated:** July 2026
> Note: "PropVista CRM" is a placeholder name — rename throughout once finalized.

---

## 1. What This Application Is

PropVista CRM is an **AI-first, multi-tenant real estate CRM SaaS platform**. It has two faces:

- A **public-facing website** where property seekers (customers) discover listings using AI-powered search, chat with an AI assistant, and get AI-matched recommendations based on their requirements.
- An **admin portal** where real estate businesses (admins, agents, brokers) manage listings, track leads through a CRM pipeline, and configure the AI features.

The platform is **multi-tenant**: each real estate business gets its own branded instance (public site + admin portal), backed by a shared application and shared AI services.

---

## 2. Core USP (What Makes This Different)

Three AI capabilities are the heart of the product — everything else in the app supports them:

| Capability | What It Does |
|---|---|
| **AI Chatbot** | Conversational assistant on the public site — answers questions, qualifies leads, schedules visits, escalates to a human agent when needed. |
| **AI Search** | Natural-language property search (e.g. *"3BHK under 80 lakhs near tech park"*) instead of manual filter-based search. |
| **AI Recommendation** | A guided requirement-analysis flow that captures buyer/renter needs and returns a ranked, matched shortlist of properties. |

These three are documented in their own dedicated specs (see [Document Index](#8-document-index)) because they carry the most product risk and the most engineering complexity.

---

## 3. Users & Roles

| User Type | Where They Work | Summary |
|---|---|---|
| **Customer (Visitor)** | Public site | Browses/search properties, uses AI chat, gets recommendations, submits inquiries. No login required for browsing; login unlocks saved searches/favorites. |
| **Customer (Registered)** | Customer Portal | Logged-in area: saved properties, requirement profile, inquiry history, notifications. |
| **Sales Agent** | Admin Portal | Manages assigned leads through the CRM pipeline, logs notes, schedules follow-ups. |
| **Admin / Owner** | Admin Portal | Manages listings, team, reports, and AI configuration for their tenant (business). |
| **Super Admin** | Admin Portal (platform-level) | Manages tenants (onboarding, plans, branding) across the whole SaaS platform. |

Full role/permission breakdown lives in `08-auth-roles-spec.md`.

---

## 4. Application Scope

### In Scope (MVP and near-term)
- Public site: homepage, AI search, AI chatbot, requirement-analysis wizard, property listing/browse, property details, contact/lead capture, customer portal (saved items, inquiries).
- Admin portal: dashboard/analytics, property management, lead/CRM pipeline, user & role management, agent management, chatbot & search configuration, basic CMS, reports & notifications, tenant/branding settings.
- Multi-tenancy: tenant-isolated data, tenant-specific branding.

### Out of Scope (for now — revisit post-MVP)
- Payment/subscription billing flows (pricing model intentionally excluded from planning docs at this stage).
- Third-party listing portal syndication (e.g. auto-posting to external portals).
- Native mobile apps (mobile-responsive web only for MVP).
- Advanced BI/data-warehouse-style reporting (basic reports only for MVP).

---

## 5. Tech Stack

| Layer | Choice | Notes |
|---|---|---|
| **Frontend** | React | Public site, customer portal, and admin portal — likely as separate apps or route groups within one React codebase (decided in `02-architecture.md`). |
| **Backend** | Python + **FastAPI** | API layer, business logic, AI orchestration. FastAPI chosen for native async support (important for streaming chat responses and concurrent Bedrock calls). |
| **Database** | Supabase (Postgres) | Primary relational data store. Supabase also provides Auth and Storage, which we plan to leverage rather than building custom (confirm in `02-architecture.md` and `08-auth-roles-spec.md`). |
| **Vector Store** | Supabase Postgres + `pgvector` | For AI search and recommendation embeddings — avoids introducing a separate vector database for MVP. Embedding model still to be chosen (see Open Questions). |
| **LLM Provider** | Amazon Bedrock — **Anthropic Claude models** | Powers the AI chatbot, AI search query understanding, and AI recommendation reasoning. Specific Claude model version (e.g. Sonnet vs. Haiku, per task/cost tradeoff) to be finalized in `05-ai-chatbot-spec.md` / `06-ai-search-spec.md` / `07-ai-recommendation-spec.md`. |
| **Hosting/Infra** | TBD | Covered in `10-deployment-devops.md`. |

> These choices will be elaborated with concrete versions, libraries, and folder structure in `02-architecture.md`. This overview just fixes the high-level stack so every later document is consistent.

---

## 6. High-Level System Shape

```
                        ┌─────────────────────────┐
                        │      Amazon Bedrock       │
                        │  (LLM: chat, search NLU,  │
                        │   recommendation logic)   │
                        └────────────┬───────────┘
                                     │
   ┌───────────────┐        ┌───────▼────────┐        ┌───────────────┐
   │  React (Public │        │  Python Backend │        │  React (Admin  │
   │  Site + Cust.  │◄──────►│      API        │◄──────►│    Portal)     │
   │    Portal)     │        │  (business logic,│        │                │
   └───────────────┘        │  AI orchestration)│        └───────────────┘
                             └───────┬─────────┘
                                     │
                        ┌────────────▼─────────────┐
                        │   Supabase (Postgres +    │
                        │   pgvector + Auth +        │
                        │   Storage)                 │
                        │   — tenant-isolated data   │
                        └────────────────────────────┘
```

One Python backend serves both the public-facing React app and the admin React app, with tenant context resolved on every request (see `02-architecture.md` for the multi-tenancy strategy).

---

## 7. Success Criteria (MVP)

- A visitor can describe what they want in plain language and get relevant property results (AI Search).
- A visitor can complete a chatbot conversation that ends in either an answered question or a scheduled callback/visit.
- A visitor can complete the requirement-analysis flow and receive a matched shortlist.
- An admin can add a property, see it appear correctly on the public site, and receive a lead when a visitor inquires about it.
- An agent can move a lead through the CRM pipeline and see accurate status at every stage.
- Two different tenants can use the platform simultaneously with zero data leakage between them.

---

## 8. Document Index

This is the full planned documentation set. Documents are created one at a time; links will go live as each is completed.

| # | Document | Purpose | Status |
|---|---|---|---|
| 00 | `00-project-overview.md` | This document | ✅ Done |
| 01 | `01-prd.md` | Detailed functional requirements per module | ✅ Done |
| 02 | `02-architecture.md` | System architecture, multi-tenancy, folder structure | ✅ Done |
| 03 | `03-database-schema.md` | Entities, tables, relationships | ✅ Done |
| 04 | `04-api-spec.md` | REST API endpoints for public + admin | ✅ Done |
| 05 | `05-ai-chatbot-spec.md` | Chatbot conversation design & Bedrock integration | ✅ Done |
| 06 | `06-ai-search-spec.md` | NL search pipeline, ranking, indexing | ✅ Done |
| 07 | `07-ai-recommendation-spec.md` | Requirement-analysis matching engine | ✅ Done |
| 08 | `08-auth-roles-spec.md` | Auth, tenant isolation, role permissions | ✅ Done |
| 09 | `09-coding-standards.md` | Conventions for Claude Code to follow consistently | ✅ Done |
| 10 | `10-deployment-devops.md` | Environments, CI/CD, hosting | ✅ Done |

**Supplementary documents** (created after the core set, as follow-on needs arose):

| # | Document | Purpose | Status |
|---|---|---|---|
| 11 | `11-stitch-design-prompts.md` | Copy-paste Stitch prompts + shared design direction, per priority screen | ✅ Done |
| 12 | `12-srs.md` | Formal non-functional requirements, use cases, traceability matrix | ✅ Done |
| 13 | `13-ui-ux-flows.md` | Persona-based user flow diagrams + written-up design system | ✅ Done |
| 14 | `14-screen-workflows.md` | Within-screen interaction sequences for the 8 priority screens | ✅ Done |
| 15 | `15-development-plan.md` | Sprint-by-sprint build order + per-module `TC-*` test cases | ✅ Done |

**Detailed per-screen specs** (implementation-level; one file per page/feature):

| # | Document | Purpose | Status |
|---|---|---|---|
| 16 | `16-customer-spec/` | **Customer surface** — public site + customer portal. One file per page (homepage, listing, details, wizard, contact, auth, the 4 portal pages, CMS pages) and per cross-page feature (AI search, chatbot, lead capture, favorites/session). Index: `16-customer-spec/README.md` | ✅ Done |
| 17 | `17-admin-spec/` | **Admin portal** — one file per screen (dashboard, properties, bulk upload, approvals, lead Kanban/detail/table, agents, users, audit log, the 4 AI-config screens, CMS, reports, notifications, branding, super-admin tenants). Index: `17-admin-spec/README.md` | ✅ Done |

> Docs 16 and 17 sit *below* `01-prd.md` (what must exist) and `04-api-spec.md` (the contract): they specify what each screen contains, how it behaves click-by-click, which endpoints it calls, which tables it touches, and which `TC-*` cases it must pass. Each file ends with an **Open Questions** section, and each index has a **Known Spec Gaps** table listing requirements that cannot currently be built because the schema or API spec doesn't support them — see Section 9 below.

---

## 9. Open Questions / Assumptions to Confirm

These will get resolved as we build out the later documents — flagging them here so nothing gets lost:

- [x] Python web framework → **FastAPI**.
- [x] LLM provider/model family → **Anthropic Claude models via Amazon Bedrock**, for chat, search-query-understanding, and recommendation reasoning.
- [x] Supabase Auth usage → **used as-is** as the identity provider for all users (customer, agent, admin, super_admin); the application's own `users` table (not the JWT) remains the source of truth for role/tenant, so role changes take effect immediately. See `08-auth-roles-spec.md` Section 1.
- [ ] Confirm specific Claude model version per task (e.g. a lighter/faster model for quick search-query parsing vs. a stronger model for chatbot conversation and recommendation reasoning) — to be decided in the respective AI spec docs, with cost/latency tradeoffs in mind.
- [x] Embedding model for `pgvector` → **Amazon Titan Text Embeddings V2, 1024 dimensions** (via Bedrock). See `06-ai-search-spec.md` and `03-database-schema.md`.
- [x] Hosting target → **AWS-native** (App Runner or ECS for the backend, S3/CloudFront for the React app), confirmed directionally to keep Bedrock latency/cost low. Exact service (App Runner vs. ECS) remains open — see `10-deployment-devops.md` Section 9.
- [x] ORM/data-access layer → **SQLAlchemy + Alembic**, per `02-architecture.md`.

### 9.1 Blocking Spec Gaps (surfaced by docs 16 & 17)

Writing the per-screen specs exposed requirements that **cannot be built** because the schema or API spec doesn't support them. These are documentation gaps, not implementation choices — fix the owning doc first (`.claude/rules/workflow.md`). Full lists: `16-customer-spec/README.md` §5 and `17-admin-spec/README.md` §5.

#### ✅ Closed in `03-database-schema.md` v1.1

All schema-owned gaps are resolved. See that doc's [§8 Changelog](03-database-schema.md#8-changelog-v10--v11) for the full diff and [§7](03-database-schema.md#7-open-questions--assumptions-to-confirm) for the product decisions baked in.

| Gap | Resolution |
|---|---|
| `leads` had no `user_id` / `session_id` — inquiries couldn't be tied to a customer, and the `customer_email` workaround was **exploitable** | Both columns added, plus `requirement_profile_id`, `chat_conversation_id`, `deal_value`, `idempotency_key`, `requested_callback_at` |
| No `notifications` table, no customer preference storage | `notifications` + `notification_preferences` added — the **in-app** channel is now fully buildable |
| No `audit_log` table | Added, append-only, enforced by `REVOKE UPDATE, DELETE` |
| No canonical amenity vocabulary | `amenities` lookup table added; `properties.amenities` and `requirement_profiles.must_have_amenities` now store codes, not free text |
| No search-query log | `search_queries` added — **must exist before the first AI search runs (Sprint 5)** |
| No property-view tracking (FR8.2) | `property_views` added — **cannot be backfilled**, so it must ship with the first published property |
| `source = property_details` was not a valid enum value | Added; `14-screen-workflows.md` and the schema now agree |
| Pipeline stages: FR10.1 promised configurable, the enum was fixed | **Decided: fixed enum for MVP.** ⚠️ `01-prd.md` FR10.1 still promises configurability and needs updating to match |
| Homepage banners, blog posts, bulk-upload jobs, tenant timezone/approval-flag/contact-info | `cms_banners`, `cms_pages.page_type`, `bulk_uploads`/`bulk_upload_rows`, `tenants.*` all added |

#### ⛔ Still blocking — owned by other docs

| Gap | Owning doc | Blocks |
|---|---|---|
| ~~No job scheduler~~ ✅ **RESOLVED — and it never was a gap.** `02-architecture.md` **§4.4** has specified `pg_cron` + a `jobs` table + a Python worker since **2026-07-13**, with `mark_stale_leads()` explicitly listed. This line was a stale summary that was copied into eight other documents and caused a *mandatory* requirement (FR10.2b) to be planned as unbuildable for a sprint. See `GAPS.md` §5A. | `02-architecture.md` §4.4 | FR10.3, FR15.2 — **both buildable** |
| **No public CMS read endpoint** — a tenant can publish content the public site has no way to fetch. Module 14 is inert. (`GAPS.md` **G5**) | `04-api-spec.md` | FR14.1/FR14.2 |
| **No per-tenant SSL provisioning** for custom domains. Post-MVP with branding (ADR-0010), but it carries infrastructure lead time. (`GAPS.md` **A15**) | `10-deployment-devops.md` | FR16.2 |
| Missing endpoints: requirement-profile delete (the column exists — `GAPS.md` **G8**), autosuggest (**G3**), chatbot/weights preview, resend/revoke invite. | `04-api-spec.md` | Various |

#### ✅ Closed — this table was wrong for three days

**Everything below was closed or decided on 2026-07-13/14 and left sitting under "⛔ Still blocking" until 2026-07-16** — in the document `CLAUDE.md` tells every new reader to open *first*. That is the worst possible place for a stale gap list, and it is why `OWNERSHIP.md` §4 says the sweep ships in the same commit as the fix.

| Was listed as blocking | The truth |
|---|---|
| ~~*"Email/SMS providers"*~~ — the row even contradicted itself, saying providers **were** chosen and then recommending "in-app only … rather than switches that do nothing" | ✅ **SendGrid + Twilio, decided 2026-07-13** (`02-architecture.md` §3). All three channels ship at MVP. The "no provider" version of this claim was the false gap ~~G9b~~ (`GAPS.md` §5A). ⚠️ Indian SMS needs **DLT registration** — regulatory lead time |
| ~~*"Lead auto-assignment undecided — recommend round-robin"*~~ | ✅ **Decided 2026-07-13: manual claim from a shared queue, no auto-assignment** (`01-prd.md` FR10.2, ADR-0014). The recommendation here was overruled. Safety net: the **mandatory** stale-lead alert (FR10.2b), which is buildable (`02-architecture.md` §4.4) |
| ~~*"No agent-reply path for escalated chats"*~~ | ✅ **Closed 2026-07-14** (`GAPS.md` G7). `04-api-spec.md` §12A + `05-ai-chatbot-spec.md` §10A + `17-admin-spec/22`. No migration needed |
| ~~*"What `tenants.status = suspended`/`trial` do — no defined behavior"*~~ | ✅ **Defined 2026-07-13**: `01-prd.md` FR16.1, `03-database-schema.md` §3.1. `suspended` = public site serving, admin login blocked |
| ~~*"Missing: property reject, bulk operations"*~~ | ✅ **Both exist**: `04-api-spec.md` §8 — `POST /admin/properties/{id}/reject`, `POST /admin/properties/bulk-status` |
| ~~*"No job scheduler"*~~ | ✅ **Never real** — see the row already recorded below |

---

**Next document:** `01-prd.md` — detailed functional requirements per module, built from the business plan's feature list but written for engineering use.
