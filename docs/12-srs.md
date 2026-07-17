# Software Requirements Specification (SRS) — PropVista CRM

> **Doc 12 of the PropVista CRM documentation set.** Formal engineering requirements specification — non-functional requirements, use-case descriptions, external interfaces, and a traceability matrix back to `01-prd.md`. This document does not repeat the functional requirements themselves (see `01-prd.md`); it complements them with what a PRD typically leaves out.
>
> **Status:** Draft v1.0 · **Last updated:** July 2026
> Depends on: `00-project-overview.md`, `01-prd.md`, `02-architecture.md`, `03-database-schema.md`, `08-auth-roles-spec.md`

---

## 1. Introduction

### 1.1 Purpose
This SRS defines the non-functional requirements, formal use cases, and external interface requirements for PropVista CRM, complementing the functional requirements already specified in `01-prd.md`. It exists to give engineering and QA a rigorous, testable basis beyond "what feature does what" — covering performance, security, reliability, and system boundaries.

### 1.2 Scope
Covers the full platform: public site, customer portal, admin portal, and the three core AI capabilities (chatbot, search, recommendation), as scoped in `00-project-overview.md` Section 4.

### 1.3 Definitions & References
See `00-project-overview.md` for the glossary of terms (tenant, multi-tenant, lead pipeline, requirement analysis). This document assumes familiarity with `01-prd.md` (module/FR numbering, reused below) and `03-database-schema.md` (entity names, reused below).

### 1.4 Document Conventions
- Non-functional requirements are numbered `NFR-<category>-<n>` (e.g. `NFR-PERF-1`).
- Use cases are numbered `UC-<n>`.
- Every requirement in this document is traceable to a PRD module via the matrix in Section 6.

---

## 2. Overall Description

### 2.1 Product Perspective
PropVista CRM is a new, standalone multi-tenant SaaS platform (not an extension of an existing system). Its major external dependency is Amazon Bedrock for all AI reasoning/embedding, and Supabase for data, auth, and storage — both treated as managed external services, not components this SRS specifies the internals of.

### 2.2 Product Functions (Summary)
See `01-prd.md` Section 1 (Module Map) for the full functional breakdown across 16 modules. This SRS does not restate them.

### 2.3 User Classes and Characteristics
See `08-auth-roles-spec.md` Section 3 for the formal role model (customer, agent, admin, super_admin). Characteristics relevant to non-functional design:
- **Customers** are largely non-technical, mobile-first, and impatient with slow AI responses — this directly informs the performance NFRs (Section 3.1).
- **Agents/Admins** are daily, repeat users working inside the admin portal for extended sessions — this informs usability and session-length NFRs (Section 3.5).

### 2.4 Operating Environment
Per `02-architecture.md` Section 8: local, staging, and production environments, AWS-hosted backend (App Runner/ECS), Supabase-hosted database, React SPAs served via S3/CloudFront.

### 2.5 Constraints
- Must use the confirmed stack: React, Python/FastAPI, Supabase (Postgres + pgvector), Amazon Bedrock (Claude models + Titan Embeddings) — per `00-project-overview.md` Section 5.
- Multi-tenant data isolation is mandatory (RLS-based, per `03-database-schema.md` Section 4) and is treated as a hard constraint on every requirement below, not an optional feature.
- No payment/billing system in scope (per `00-project-overview.md` Section 4).

### 2.6 Assumptions and Dependencies
- Amazon Bedrock model availability in the target AWS region is assumed sufficient for both Claude conversation models and Titan Embeddings at launch (flagged as an open item in `05`/`06`).
- Supabase's managed Postgres/Auth/Storage services are assumed to meet the availability targets in Section 3.3 — this SRS does not specify Supabase's internals, only how PropVista CRM depends on them.

---

## 3. Non-Functional Requirements

### 3.1 Performance

| ID | Requirement |
|---|---|
| `NFR-PERF-1` | Standard (non-AI) page data requests (property listing, property details, lead list) must return within a target of ~500ms server-side processing time under normal load. |
| `NFR-PERF-2` | AI Search (`/ai/search`) must return results within the latency budget defined in `06-ai-search-spec.md` Section 7 — parsing and embedding calls run in parallel to meet this. |
| `NFR-PERF-3` | AI Chatbot (`/ai/chat/message`) must begin streaming a response within a short perceived-latency window (target to be set from real Bedrock streaming measurements) — full response time is less important than time-to-first-token given the streaming UI (`05-ai-chatbot-spec.md` Section 6). |
| `NFR-PERF-4` | AI Recommendation (`/ai/recommend`) must return a ranked shortlist within a latency budget suitable for a form-submission wait (a few seconds is acceptable here, unlike search/chat, since it's a deliberate one-time submission, not a live-typing interaction). |
| `NFR-PERF-5` | The system must support the concurrent load of an initial pilot cohort of tenants (exact figure TBD — see Section 7) without measurable degradation across the above targets. |

### 3.2 Scalability

| ID | Requirement |
|---|---|
| `NFR-SCALE-1` | The backend (FastAPI on App Runner/ECS) must scale horizontally with tenant/traffic growth without requiring architectural changes to the modular monolith (per `02-architecture.md` Section 1). |
| `NFR-SCALE-2` | The `property_embeddings` table's `hnsw` vector index must remain performant as property count grows per tenant and across tenants — index strategy revisited if a single tenant's catalog grows beyond typical scale assumptions (no specific number fixed yet; flagged for load testing). |
| `NFR-SCALE-3` | Background job processing (embedding generation, notification dispatch, bulk import) runs in a **separate worker process polling the `jobs` table**, scheduled by **`pg_cron`** — per `02-architecture.md` §4.4. It must scale by **adding worker instances** without changing the public API contract; `FOR UPDATE SKIP LOCKED` is what makes concurrent workers safe. |

### 3.3 Availability & Reliability

| ID | Requirement |
|---|---|
| `NFR-AVAIL-1` | Core browsing/search/property-details functionality must degrade gracefully, not fail entirely, if Bedrock is unavailable — falls back to standard filter search (per `06-ai-search-spec.md` Section 8). |
| `NFR-AVAIL-2` | The chatbot must show a clear fallback message and offer human escalation if Bedrock times out (per `05-ai-chatbot-spec.md` Section 6), rather than leaving the UI hanging. |
| `NFR-AVAIL-3` | No single tenant's outage-causing behavior (e.g. a malformed bulk upload) should be able to degrade service for other tenants — reinforces the tenant-isolation requirement (`03-database-schema.md` Section 4) as also a reliability property, not just a security one. |

### 3.4 Security

| ID | Requirement |
|---|---|
| `NFR-SEC-1` | All tenant-owned data access is enforced via Postgres RLS at the database layer, not only application-level filtering (per `03-database-schema.md` Section 4) — this is the primary tenant-isolation control. |
| `NFR-SEC-2` | All API endpoints requiring authentication must reject requests with missing/invalid/expired JWTs (per `08-auth-roles-spec.md` Section 1) — no endpoint infers identity from client-supplied, unverified data. |
| `NFR-SEC-3` | Role/permission checks are enforced server-side on every protected route (per `08-auth-roles-spec.md` Section 5) — the UI hiding a control is never the actual security boundary. |
| `NFR-SEC-4` | Secrets (Supabase service key, AWS/Bedrock credentials) are stored via environment variables/secrets manager and never logged or committed (per `09-coding-standards.md` Section 7, `10-deployment-devops.md` Section 1). |
| `NFR-SEC-5` | AI-facing endpoints (chat, search, recommend) apply input validation and prompt-injection hygiene per `05-ai-chatbot-spec.md` Section 9 before constructing any model prompt. |
| `NFR-SEC-6` | Rate limiting is applied to public AI endpoints to prevent abuse-driven cost exposure (per `04-api-spec.md` Section 1, `10-deployment-devops.md` Section 6). |

### 3.5 Usability

| ID | Requirement |
|---|---|
| `NFR-USE-1` | All public-site and customer-portal screens are usable on mobile viewports (per `01-prd.md` Section 18). |
| `NFR-USE-2` | The admin portal supports efficient repeat use for daily sessions — e.g. the lead Kanban board must support drag-and-drop stage changes without a full page reload. |
| `NFR-USE-3` | AI chatbot and AI search interactions follow standard, familiar UI conventions (chat bubbles, typing indicators, autosuggest) so no onboarding/explanation is needed for a first-time visitor (ties to `11-stitch-design-prompts.md`'s design direction). |

### 3.6 Maintainability

| ID | Requirement |
|---|---|
| `NFR-MAINT-1` | Codebase follows the layering discipline and folder structure in `02-architecture.md`/`09-coding-standards.md` — routers/services/repositories are not conflated. |
| `NFR-MAINT-2` | AI prompts are versioned and isolated in `ai_clients/prompts/`, never inlined, so behavior changes are traceable (per `09-coding-standards.md` Section 2.7). |
| `NFR-MAINT-3` | All schema changes go through Alembic migrations — no manual production schema edits (per `09-coding-standards.md` Section 2.6). |

### 3.7 Compliance & Data Privacy

| ID | Requirement |
|---|---|
| `NFR-COMP-1` | Customer PII (name, phone, email) collected via chatbot, contact forms, or requirement profiles is stored only as needed for CRM purposes and not exposed across tenant boundaries (ties to `NFR-SEC-1`). |
| `NFR-COMP-2` | A retention policy exists and is enforced. **Defined 2026-07-13 in `03-database-schema.md` §8** (chat transcripts 24 months, audit log 7 years, raw telemetry 90 days → rollups), enforced by nightly `pg_cron` jobs. This SRS requires the policy to exist and be enforced; §8 owns the durations and this row must not restate them. |

### 3.8 Interoperability

| ID | Requirement |
|---|---|
| `NFR-INTEROP-1` | The API is documented via FastAPI's OpenAPI schema (auto-generated) and kept accurate, enabling frontend type generation (per `04-api-spec.md` Section 17, `09-coding-standards.md` Section 3.4). |
| `NFR-INTEROP-2` | Third-party integrations are abstracted behind a service interface (`app/notifiers/`) so the provider can change without touching calling code. Email and SMS are **decided** (SendGrid / Twilio — `02-architecture.md` §3); the **maps** provider is still open (§9). |

---

## 4. Use Case Descriptions

### UC-1: Visitor Searches for a Property (AI Search)
- **Actor:** Customer (anonymous or registered)
- **Preconditions:** Visitor is on the public site; tenant has at least one published property.
- **Main Flow:**
  1. Visitor enters a natural-language query in the search bar.
  2. System parses the query and generates results (per `06-ai-search-spec.md` Section 2).
  3. System displays ranked results.
  4. Visitor selects a property to view details (→ UC-4 style navigation, not a separate use case).
- **Alternate Flow:** AI parsing fails → system falls back to semantic-only or standard filter search (`06-ai-search-spec.md` Section 8); visitor is not shown an error.
- **Postconditions:** Search query and result interaction may be logged for evaluation purposes (`06-ai-search-spec.md` Section 9).

### UC-2: Visitor Converses with the AI Chatbot and Becomes a Lead
- **Actor:** Customer (anonymous or registered)
- **Preconditions:** Visitor opens the chat widget on any public page.
- **Main Flow:**
  1. Visitor sends a message.
  2. System responds, using tool calls to fetch live property data as needed (`05-ai-chatbot-spec.md` Section 4).
  3. Visitor expresses interest; bot offers to capture contact info and/or schedule a visit.
  4. Visitor provides contact info; system creates a lead record (source = `chatbot`).
- **Alternate Flow:** Bot cannot resolve the query or visitor requests a human → conversation is escalated (`05-ai-chatbot-spec.md` Section 10); a notification is created for an available agent.
- **Postconditions:** A `leads` row exists with `source = 'chatbot'`; conversation is persisted in `chat_messages` for admin review.

### UC-3: Visitor Completes Requirement Analysis
- **Actor:** Customer (anonymous or registered)
- **Preconditions:** Visitor starts the guided requirement wizard.
- **Main Flow:**
  1. Visitor answers each step (budget, location, type, purpose, timeline, amenities).
  2. On submission, system generates a ranked shortlist with match reasons (`07-ai-recommendation-spec.md` Section 3).
  3. Visitor may save the profile (if registered) or register to save it.
- **Alternate Flow:** No strong matches found → system returns closest-match fallback, never an empty state (`07-ai-recommendation-spec.md` Section 7).
- **Postconditions:** A `requirement_profiles` row and associated `requirement_matches` rows exist; if saved, future property publishes are checked against this profile (`07-ai-recommendation-spec.md` Section 6).

### UC-4: Admin Publishes a New Property
- **Actor:** Admin (or Agent, if permitted)
- **Preconditions:** Admin is authenticated and has `properties.edit` permission.
- **Main Flow:**
  1. Admin fills out the multi-step property form (Basic Info, Media, Pricing, Amenities, Location).
  2. Admin saves/submits; if tenant requires approval, status = `pending_approval`, else `published` directly (`01-prd.md` FR9.3).
  3. On save, a background job generates the property's embedding and indexes it (`06-ai-search-spec.md` Section 4.2).
  4. Saved requirement profiles are checked for new matches (`07-ai-recommendation-spec.md` Section 6).
- **Postconditions:** Property is queryable via AI Search and eligible for AI Recommendation matching once published.

### UC-5: Agent Manages a Lead Through the Pipeline
- **Actor:** Agent
- **Preconditions:** A lead exists and is assigned to the agent (or is unassigned and claimable, depending on tenant configuration).
- **Main Flow:**
  1. Agent views the lead in the Kanban board or table view (`01-prd.md` FR10.1).
  2. Agent logs a call/meeting note and sets a follow-up reminder.
  3. Agent moves the lead to the next pipeline stage.
  4. Stage change is recorded in `lead_activities` with a timestamp.
- **Postconditions:** Lead's current stage and full activity history are accurately reflected for reporting (`01-prd.md` Module 15).

### UC-6: Super Admin Onboards a New Tenant
- **Actor:** Super Admin
- **Preconditions:** Super admin is authenticated at the platform level.
- **Main Flow:**
  1. Super admin creates a new tenant record (name, domain).
  2. Tenant admin is invited and sets up branding (logo, colors, custom domain).
  3. Tenant's public site becomes reachable at its configured domain, resolving `tenant_id` per request (`02-architecture.md` Section 7).
- **Postconditions:** New tenant operates with fully isolated data (`NFR-SEC-1`); no visibility into other tenants' data.

---

## 5. External Interface Requirements

| Interface | Direction | Notes |
|---|---|---|
| Amazon Bedrock (Converse API) | Outbound | Chat, search-query parsing, recommendation reasoning, match-reason generation — all via `ai_clients/bedrock_client.py` (`02-architecture.md` Section 4.2) |
| Amazon Bedrock (Titan Embeddings) | Outbound | Property and query/requirement embeddings — via `ai_clients/embeddings_client.py` |
| Supabase Auth | Bi-directional | User registration/login, JWT issuance; verified by FastAPI on each request |
| Supabase Postgres (+ pgvector) | Bi-directional | Primary data store, RLS-enforced |
| Supabase Storage | Bi-directional | Property media (photos, floor plans, documents) |
| Maps provider (**TBD**) | Outbound | Property location display, map view (`02-architecture.md` §9). Genuinely undecided |
| **Twilio** (SMS) | Outbound | Notification delivery, callback confirmations. Decided 2026-07-13 (`02-architecture.md` §3). Indian SMS needs DLT registration |
| **SendGrid** (email) | Outbound | Transactional email. Decided 2026-07-13 (`02-architecture.md` §3) |

---

## 6. Requirements Traceability Matrix

| PRD Module (`01-prd.md`) | Related NFRs | Related Use Case(s) |
|---|---|---|
| 1. AI Chatbot | NFR-PERF-3, NFR-AVAIL-2, NFR-SEC-5 | UC-2 |
| 2. AI Search | NFR-PERF-2, NFR-AVAIL-1 | UC-1 |
| 3. AI Recommendation | NFR-PERF-4 | UC-3 |
| 4. Property Listing | NFR-PERF-1, NFR-USE-1 | UC-1 |
| 5. Property Details | NFR-PERF-1, NFR-USE-1 | UC-1 |
| 6. Contact/Lead Capture | NFR-SEC-1 | UC-2 |
| 7. Customer Portal | NFR-SEC-1, NFR-SEC-2 | UC-3 |
| 8. Admin Dashboard | NFR-PERF-1, NFR-SEC-1 | — |
| 9. Property Management | NFR-SCALE-2, NFR-MAINT-3 | UC-4 |
| 10. Lead & CRM Pipeline | NFR-USE-2, NFR-SEC-3 | UC-5 |
| 11. User & Role Management | NFR-SEC-2, NFR-SEC-3 | — |
| 12. Agent/Broker Management | NFR-SEC-3 | UC-5 |
| 13. AI Configuration | NFR-MAINT-2 | — |
| 14. CMS | NFR-USE-1 | — |
| 15. Reports & Notifications | NFR-COMP-2 | — |
| 16. Tenant & Branding | NFR-SEC-1, NFR-INTEROP-2 | UC-6 |

This matrix should be updated whenever a PRD module or NFR changes — it's the fastest way to check "did we forget a non-functional angle on this feature?" during implementation review.

---

## 7. Open Questions / Assumptions to Confirm

- [ ] Exact concurrent-user/tenant target for `NFR-PERF-5` and `NFR-SCALE-2` — needs a business-side estimate (expected pilot cohort size) before load testing can be meaningful.
- [ ] Exact latency numbers for `NFR-PERF-2`/`NFR-PERF-3`/`NFR-PERF-4` — currently qualitative; to be pinned down after initial Bedrock latency measurements (same open item as in `05`/`06`/`07`).
- [ ] Data retention policy duration for `NFR-COMP-2` — needs a business/legal decision, not just an engineering one.
- [ ] Whether any regional data-residency requirements apply (not yet raised — worth confirming given customer PII is involved).

---

**Next document:** `13-ui-ux-flows.md` — persona-based user flow diagrams and a written-up design system/style guide.
