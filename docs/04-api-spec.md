# API Specification — PropVista CRM

> **Doc 04 of the PropVista CRM documentation set.** REST API surface for the public site, customer portal, and admin portal, served by the FastAPI backend. Built directly on the entities in `03-database-schema.md` and the modules in `01-prd.md`.
>
> **Status:** Draft v1.0 · **Last updated:** July 2026
> Depends on: `01-prd.md`, `02-architecture.md`, `03-database-schema.md`

---

## 1. Conventions

- **Base path:** `/api/v1/`
- **Format:** JSON request/response bodies.
- **Auth:** `Authorization: Bearer <supabase_jwt>` header. Anonymous endpoints (browsing, search, chat, contact) work without it, using a `X-Session-Id` header for anonymous session tracking instead.
- **Tenant resolution:** For public-site requests, tenant is resolved server-side from the request's origin domain — not passed explicitly by the client. For admin-portal requests, tenant is resolved from the authenticated user's tenant association. No endpoint accepts a client-supplied `tenant_id` directly (prevents cross-tenant spoofing).
- **Pagination:** `?page=1&page_size=20` query params; responses include `{ "items": [...], "total": N, "page": 1, "page_size": 20 }`.
- **Error format:**
  ```json
  { "error": { "code": "PROPERTY_NOT_FOUND", "message": "Property not found." } }
  ```
- **Standard HTTP status codes**: 200/201 success, 400 validation error, 401 unauthenticated, 403 unauthorized (role/permission), 404 not found, 429 rate-limited, 500 server error.
- **Rate limiting:** Applied per session/IP on all `ai/*` endpoints (Section 3) to control Bedrock cost exposure — specific limits defined in `10-deployment-devops.md`.

---

## 2. Auth Endpoints

| Method | Path | Purpose | Auth |
|---|---|---|---|
| POST | `/auth/register` | Register a new customer account | None |
| POST | `/auth/login` | Login (delegates to Supabase Auth) | None |
| POST | `/auth/logout` | Logout / invalidate session | Bearer |
| GET | `/auth/me` | Current user profile + role + tenant | Bearer |
| POST | `/auth/invite` | Invite a new admin-portal user (agent/admin) | Bearer (admin) |

---

## 3. AI Endpoints (Public Site) — Core USP

### 3.1 AI Search

| Method | Path | Purpose |
|---|---|---|
| POST | `/ai/search` | Natural-language property search |

**Request:**
```json
{ "query": "3BHK under 80 lakhs near tech park", "filters": { "listing_type": "sale" }, "page": 1, "page_size": 20 }
```
**Response:**
```json
{
  "items": [ { "property_id": "...", "title": "...", "price": 7800000, "match_score": 0.91, "thumbnail_url": "..." } ],
  "parsed_query": { "property_type": "apartment", "bedrooms": 3, "budget_max": 8000000, "location_hint": "tech park" },
  "total": 12, "page": 1, "page_size": 20
}
```

### 3.2 AI Chatbot

| Method | Path | Purpose |
|---|---|---|
| POST | `/ai/chat/message` | Send a message, get bot response |
| GET | `/ai/chat/history/{conversation_id}` | Retrieve conversation history |
| POST | `/ai/chat/escalate` | Force escalate current conversation to a human agent |

**Request (`/ai/chat/message`):**
```json
{ "conversation_id": "optional-existing-id", "message": "Is this property still available?", "property_id": "optional-context" }
```
**Response:**
```json
{
  "conversation_id": "...",
  "reply": "Yes, this property is still available. Would you like to schedule a visit?",
  "actions": [ { "type": "show_property_card", "property_id": "..." } ],
  "escalated": false
}
```

### 3.3 AI Recommendation (Requirement Analysis)

| Method | Path | Purpose |
|---|---|---|
| POST | `/ai/recommend` | Submit requirement profile, get matched shortlist |
| GET | `/ai/recommend/{requirement_profile_id}` | Retrieve saved profile + latest matches |
| PUT | `/ai/recommend/{requirement_profile_id}` | Update a saved requirement profile |

**Request:**
```json
{
  "budget_min": 5000000, "budget_max": 8000000,
  "preferred_locations": ["Tech Park Area", "City Center"],
  "property_type": "apartment", "purpose": "self_use", "timeline": "3_months",
  "must_have_amenities": ["parking", "gym"]
}
```
**Response:**
```json
{
  "requirement_profile_id": "...",
  "matches": [ { "property_id": "...", "match_score": 0.87, "match_reason": "Matches your budget and location; missing gym." } ]
}
```

---

## 4. Property Endpoints (Public)

| Method | Path | Purpose | Auth |
|---|---|---|---|
| GET | `/properties` | Browse/filter/sort listings | None |
| GET | `/properties/{id}` | Property details | None |
| GET | `/properties/{id}/similar` | Similar properties (reuses recommendation engine) | None |
| POST | `/properties/{id}/favorite` | Favorite a property (session or user) | None (session) |
| DELETE | `/properties/{id}/favorite` | Unfavorite | None (session) |

`GET /properties` query params: `listing_type, property_type, price_min, price_max, bedrooms, location, amenities[], sort, view (grid/list/map), page, page_size`.

---

## 5. Contact / Lead Capture Endpoints (Public)

| Method | Path | Purpose | Auth |
|---|---|---|---|
| POST | `/leads` | Create a lead from a contact form | None |
| POST | `/leads/callback-request` | Request a callback with a time slot | None |

**Request (`/leads`):**
```json
{ "customer_name": "...", "customer_phone": "...", "customer_email": "...", "message": "...", "property_id": "optional", "source": "contact_form" }
```

---

## 6. Customer Portal Endpoints (Authenticated Customer)

| Method | Path | Purpose |
|---|---|---|
| GET | `/portal/favorites` | List saved properties |
| GET | `/portal/requirements` | List saved requirement profiles |
| DELETE | `/ai/recommend/{requirement_profile_id}` | **Delete a saved requirement profile** (FR7.3) — soft-delete; also stops its alerts |
| GET | `/portal/inquiries` | List submitted leads/inquiries and their status |
| GET | `/portal/notifications` | List notifications |
| POST | `/portal/notifications/read` | Mark one or all notifications read |
| PUT | `/portal/notifications/preferences` | Update notification preferences (email/SMS/in-app per event) |
| GET | `/unsubscribe?token=...` | **Unauthenticated** — a signed, single-purpose token. Requiring a login to unsubscribe is a compliance problem |

**Two filters, both mandatory, on every `/portal/*` query: `tenant_id` (RLS) *and* `user_id = <caller>` (application layer).** RLS gives tenant isolation; it does **not** stop Customer A reading Customer B's favorites within the same tenant. Every by-ID fetch (`GET /ai/recommend/{id}`, `DELETE /properties/{id}/favorite`) must verify ownership — this is the most likely IDOR class in the product.

**Customer-facing lead responses use a separate schema from the admin's.** `lead_notes` are internal agent commentary ("lowballing, not serious") and must never appear in a `/portal/*` response. And the raw `stage` enum is never shown — `negotiation` renders as "In discussion", `closed_lost` as "Closed", never "Lost".

---

## 7. Admin — Dashboard & Analytics

| Method | Path | Purpose |
|---|---|---|
| GET | `/admin/dashboard/summary` | KPI cards: total listings, active leads, conversion rate, traffic |
| GET | `/admin/dashboard/charts` | Lead-source breakdown, property views over time |
| GET | `/admin/dashboard/activity` | Recent activity feed |

---

## 8. Admin — Property Management

| Method | Path | Purpose |
|---|---|---|
| GET | `/admin/properties` | List all tenant properties (incl. drafts) |
| POST | `/admin/properties` | Create property |
| GET | `/admin/properties/{id}` | Get property (admin view) |
| PUT | `/admin/properties/{id}` | Update property |
| DELETE | `/admin/properties/{id}` | Soft-delete property |
| POST | `/admin/properties/bulk-upload` | CSV/Excel bulk upload |
| POST | `/admin/properties/{id}/approve` | Approve pending listing → publish |
| POST | `/admin/properties/{id}/reject` | **Send back to draft with a reason.** An approval gate that can only say "yes" isn't one |
| PATCH | `/admin/properties/{id}/status` | Change status (Featured/Sold/On Hold/Archived) |
| POST | `/admin/properties/bulk-status` | Bulk status/approve — avoids 200 sequential calls |
| POST | `/admin/properties/{id}/media` | Upload media (photo/video/floor plan/document) |

**Publishing is an event, not a status flip.** Every path that publishes (form, list, approval, bulk import) enqueues the **same** `jobs` pipeline: embed → index → match saved requirement profiles → notify (batched). Implement it once in the service layer, or the four paths will drift and "why isn't my property in search?" becomes a recurring ticket.

**Sold / archived / on-hold / soft-deleted properties must be *de-indexed*** (`deindex_property` job). A sold listing left in `property_embeddings` keeps being recommended and keeps being offered by the chatbot.

> ⚠️ **All media is stored in a single public bucket, including `media_type = 'document'`** (accepted risk, 2026-07-13 — `03-database-schema.md` §10.2). Anyone with the URL can read it. The upload UI must say so.

---

## 9. Admin — Lead & CRM Pipeline

| Method | Path | Purpose | Auth |
|---|---|---|---|
| GET | `/admin/leads` | List leads (filterable by stage, agent, source, date, **unclaimed**) | agent (read-only on others') / admin |
| POST | `/admin/leads` | Manually create a lead (`source = walk_in`) | agent / admin |
| GET | `/admin/leads/{id}` | Lead detail incl. notes & activity timeline | agent (read-only on others') / admin |
| **POST** | **`/admin/leads/{id}/claim`** | **Claim an unassigned lead for the calling agent** | agent / admin |
| PATCH | `/admin/leads/{id}/stage` | Move lead to a new pipeline stage | Owner or admin |
| PATCH | `/admin/leads/{id}/assign` | Assign/reassign a lead to an agent | **admin only** |
| POST | `/admin/leads/{id}/notes` | Add a note / follow-up reminder | Owner or admin |
| GET | `/admin/leads/pipeline-view` | Kanban-ready grouped-by-stage payload | agent / admin |

### 9.1 Claiming (manual claim — decided 2026-07-13)

Leads are **not auto-assigned**. `POST /leads` creates them with `assigned_agent_id = NULL`, and they appear in a **shared "New" column visible to every agent in the tenant**. `GET /admin/leads/pipeline-view` must therefore return, for an agent, **their own leads plus every unclaimed lead** — a strict "assigned to me" filter would make the shared queue invisible and nothing would ever be claimed.

**`POST /admin/leads/{id}/claim`** — the atomic claim. Two agents will race for the same lead.

```
200 → { "lead_id": "...", "assigned_agent_id": "<caller>", "claimed_at": "..." }
409 → { "error": { "code": "LEAD_ALREADY_CLAIMED",
                   "message": "Anjali claimed this lead a moment ago." } }
```

**409, not a silent overwrite.** The service performs a conditional update guarded on `assigned_agent_id IS NULL` (`03-database-schema.md` §3.8.1); zero rows affected → 409, and the client refreshes the card.

`PATCH /admin/leads/{id}/assign` is the **admin** reassignment path and is *not* guarded on NULL — an admin may take a lead off an agent. An `agent` calling it gets a **403**.

---

## 10. Admin — User & Role Management

| Method | Path | Purpose |
|---|---|---|
| GET | `/admin/users` | List admin-portal users for the tenant |
| POST | `/admin/users/invite` | Invite new user |
| PUT | `/admin/users/{id}/role` | Change role/permissions |
| DELETE | `/admin/users/{id}` | Deactivate user |
| GET | `/admin/audit-log` | Retrieve audit log entries |

---

## 11. Admin — Agent/Broker Management

| Method | Path | Purpose |
|---|---|---|
| GET | `/admin/agents` | List agents with summary stats |
| GET | `/admin/agents/{id}` | Agent profile detail |
| GET | `/admin/agents/{id}/performance` | Performance metrics (leads closed, response time) |
| GET | `/admin/agents/leaderboard` | Ranked leaderboard view |

---

## 12. Admin — AI Configuration

| Method | Path | Purpose |
|---|---|---|
| GET | `/admin/ai-config` | Get current tenant AI config (chatbot + recommendation weights) |
| PUT | `/admin/ai-config/chatbot` | Update greeting/FAQ/escalation rules |
| PUT | `/admin/ai-config/recommendation-weights` | Update requirement-analysis weighting |
| GET | `/admin/ai-config/chat-logs` | Browse/flag chatbot conversation logs |
| GET | `/admin/ai-config/search-insights` | Queries with low/no results, for tenant visibility |

---

## 12A. Admin — Live Chat Handoff *(closes gap G7)*

**The problem these close:** `POST /ai/chat/escalate` (§6) let the bot hand a conversation to a human — and **nothing let that human reply.** FR1.7 promises human handoff and its acceptance criterion requires escalations be *"visible to an agent in real time or near-real time"*. Without these four endpoints the bot promises an agent who cannot answer, and the escalation is a dead end.

**No migration is needed.** `chat_messages.sender` already accepts `agent` (§3.14) and `chat_conversations` already carries `status`, `escalated_at` and `assigned_agent_id` (§3.13). The schema was built for this.

| Method | Path | Purpose | Auth |
|---|---|---|---|
| GET | `/admin/chat/queue` | Escalated conversations — unclaimed, plus those assigned to me. **Sorted by wait time, longest first.** | Bearer (agent/admin) |
| POST | `/admin/chat/{conversation_id}/claim` | Claim an escalated conversation. **Atomic** — see below. | Bearer (agent/admin) |
| POST | `/admin/chat/{conversation_id}/reply` | Post a message as the human agent. Writes `chat_messages` with `sender = 'agent'`. | Bearer (agent/admin) |
| POST | `/admin/chat/{conversation_id}/close` | End the conversation. `status → closed`. | Bearer (agent/admin) |

### 12A.1 The claim must be atomic

Two agents clicking "Take this chat" at the same instant must result in **exactly one owner** — the loser gets `409 Conflict`, not a silently shared conversation.

This is the **same constraint as the lead claim** (FR10.2a, `03-database-schema.md` §3.8.1). **Reuse that pattern.** Do not invent a second concurrency mechanism for the same problem.

```
UPDATE chat_conversations
   SET assigned_agent_id = :agent_id
 WHERE id = :conversation_id
   AND status = 'escalated'
   AND assigned_agent_id IS NULL   -- the whole race is decided here
```
Zero rows updated → someone else won → `409`.

### 12A.2 ⚠️ Once escalated, the bot goes silent

**This is a rule on an existing endpoint, and it is the most important line in this section.**

`POST /ai/chat/message` (§6) on a conversation whose `status = 'escalated'` must:

- **persist the visitor's message** (`sender = 'user'`), and
- **return without invoking Bedrock.**

If the bot keeps answering after handoff, the visitor gets **two voices** — a human and a machine talking over each other — which is worse than no handoff at all. It also stops paying Bedrock for every message in an escalated conversation.

### 12A.3 Delivery back to the visitor — polling, not a realtime channel

The agent's reply reaches the open chat widget by **polling the existing `GET /ai/chat/history/{conversation_id}`** (§6) roughly every 4 seconds while `status = 'escalated'`. **No new customer-facing endpoint.**

Supabase Realtime would be nicer, and it is already in the stack — but **ADR-0005** restricts the Supabase client to Auth and Storage, never data access. A human agent types with 10–30 seconds of natural latency; 4-second polling is invisible against that. See **ADR-0017**.

### 12A.4 Response shapes

`GET /admin/chat/queue`
```json
{
  "items": [
    {
      "conversation_id": "…",
      "escalated_at": "2026-07-14T09:12:00Z",
      "waiting_seconds": 840,
      "assigned_agent_id": null,
      "visitor": { "name": "Priya S.", "phone": "+91…", "is_registered": true },
      "last_message_preview": "I want to speak to someone about Sunview",
      "message_count": 7,
      "property_id": "…"
    }
  ]
}
```
`waiting_seconds` is computed, not stored. **It is the most important field on the screen** — an escalated chat is the only genuinely real-time obligation in the CRM.

`POST /admin/chat/{id}/reply` → `201` with the created message. `POST …/claim` → `200`, or **`409`** if already claimed.

### 12A.5 Tenancy

All four are tenant-scoped like every other admin endpoint. An agent may only see and reply to conversations **in their own tenant**. `conversation_id` is a UUID from the path — **verify it belongs to the caller's tenant before acting on it**, or this becomes a cross-tenant read of a customer's chat transcript (`19-security-and-privacy.md` T1).

---

## 13. CMS

### 13.1 Public (no auth) — **the module is inert without these**

Admin CRUD existed with no public read route, so a tenant could publish content the public site had no way to fetch.

| Method | Path | Purpose | Auth |
|---|---|---|---|
| GET | `/cms/pages/{slug}` | Fetch a **published** page for the domain's tenant | None |
| GET | `/cms/pages` | List published pages (footer nav, blog index; filter `?type=post`) | None |
| GET | `/cms/banners` | Active homepage banners for the domain's tenant | None |

Both must return **only** `published = true` rows for the domain-resolved tenant. An unpublished page **404s** — never reveal that the slug exists.

### 13.2 Admin

| Method | Path | Purpose |
|---|---|---|
| GET | `/admin/cms/pages` | List CMS pages (incl. drafts) |
| POST | `/admin/cms/pages` | Create page |
| PUT | `/admin/cms/pages/{id}` | Edit page content/SEO |
| DELETE | `/admin/cms/pages/{id}` | **Soft**-delete page |
| GET/POST/PUT/DELETE | `/admin/cms/banners[/{id}]` | Homepage banner CRUD (FR14.1) |

> ⚠️ `content` is tenant-authored HTML rendered on the public site — **sanitize on write and on render** (strict allowlist; no `<script>`, no `on*`, no `javascript:`). This is the product's most dangerous stored-XSS surface.

---

## 14. Admin — Reports & Notifications

**Reports are synchronous and stateless** (decided 2026-07-13). There is **no saved-report entity and no report ID** — export re-runs the same query with the same parameters. The earlier `GET /admin/reports/{id}/export` shape is removed.

| Method | Path | Purpose |
|---|---|---|
| POST | `/admin/reports/generate` | Generate a report (leads/sales/inventory) with filters. Returns rows **synchronously**, row-capped |
| GET | `/admin/reports/export` | Re-run the same query and stream a **PDF/Excel** file. Takes the *same* filter params as `generate`, plus `format=pdf\|xlsx` |
| GET | `/admin/notification-rules` | List notification rules |
| POST | `/admin/notification-rules` | Create rule |
| PUT | `/admin/notification-rules/{id}` | Update rule |
| POST | `/admin/notification-rules/{id}/test` | Send a test notification to the rule's recipients |

**Row cap:** if the requested range exceeds the cap, return `400 REPORT_TOO_LARGE` with the row count and a suggestion to narrow the range. **Never silently truncate** — a truncated report that looks complete is worse than a refused one.

**Report figures must come from `metrics_service`** — the same code the Dashboard and Agents leaderboard call (`03-database-schema.md` §6). FR15.1's acceptance criterion ("exports match dashboard figures") is only true by construction, never by coincidence.

**Every export is written to the audit log** — it carries customer PII (names, phones) out of the system on someone's laptop. "Who downloaded the full customer list, and when" must be answerable.

---

## 15. Super Admin — Tenant & Branding

| Method | Path | Purpose | Auth |
|---|---|---|---|
| GET | `/platform/tenants` | List all tenants | Bearer (super_admin) |
| POST | `/platform/tenants` | Create new tenant | Bearer (super_admin) |
| PUT | `/platform/tenants/{id}` | Update tenant status/plan | Bearer (super_admin) |
| PUT | `/admin/tenant/branding` | Update own tenant's branding (logo, colors, domain) | Bearer (admin) |

---

## 16. Endpoint-to-Module Traceability

Every endpoint group above maps 1:1 to a PRD module (`01-prd.md`, Section 1 Module Map) — this API spec should not introduce functionality not already scoped there. If a new endpoint is needed during implementation, the corresponding PRD module should be updated first.

---

## 17. Open Questions / Assumptions to Confirm

- [ ] Whether OpenAPI-generated TypeScript types (from FastAPI's auto schema) are consumed directly by the React app, per the shared-types recommendation in `02-architecture.md`.
- [ ] Exact rate-limit thresholds per AI endpoint — deferred to `10-deployment-devops.md` (`GAPS.md` X1).
- [x] ~~Whether report generation (`/admin/reports/generate`) is synchronous or should return a job ID for async generation on large date ranges.~~ **DECIDED 2026-07-13 — synchronous and row-capped, see §14.** There is no report ID and no `reports` table; an over-cap range returns `400 REPORT_TOO_LARGE` rather than a silent truncation.
  > This checkbox sat open for three days *after* §14 answered it, and `GAPS.md` P3 cited that contradiction as evidence §14 was stale — when §14 was correct and this line was the residue. **An answered open-question is a lie with a checkbox** (`GAPS.md` §5A rule 2). Close the question in the same commit as the decision.

---

**Next document:** `05-ai-chatbot-spec.md` — chatbot conversation design, tool-calling, and Bedrock/Claude integration detail.
