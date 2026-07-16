# Route Map — PropVista CRM

> **Master reference for all routes and endpoints in the PropVista CRM system.** Organized by surface (public site, customer portal, admin portal) and API layer. Cross-references PRD modules, spec docs, and implementation files.

---

## Navigation

- **[1. Public Site Routes](#1-public-site-routes)** — Customer-facing, no auth required
- **[2. Customer Portal Routes](#2-customer-portal-routes)** — Authenticated customer
- **[3. Admin Portal Routes](#3-admin-portal-routes)** — Agents, admins, super-admins
- **[4. API Endpoints](#4-api-endpoints)** — Backend REST API (`/api/v1/`)
- **[5. Route Hierarchy & Flows](#5-route-hierarchy--flows)** — Visual sitemap
- **[6. Tenant Scoping Rules](#6-tenant-scoping-rules)** — Data isolation per route
- **[7. Implementation Status](#7-implementation-status)** — MVP scope vs. post-MVP

---

## 1. Public Site Routes

**Auth:** None (anonymous visitors; session-tracked via `X-Session-Id`). Registration prompt appears *after* a persist-worthy action, never before.

**Tenant:** Resolved server-side from request origin domain.

**Spec:** `docs/16-customer-spec/`

| Route | Purpose | Page File | PRD Module | Status |
|---|---|---|---|---|
| `/` | Homepage with hero AI search bar | `01-homepage.md` | 2, 4 | MVP |
| `/search` | AI-powered property search results + filters | `02-property-listing.md` | 4 | MVP |
| `/property/:id` | Property detail view + lead capture | `03-property-details.md` | 5 | MVP |
| `/requirement-analysis` | Requirement wizard (AI Recommendation) | `04-requirement-wizard.md` | 3 | MVP |
| `/contact` | Contact form / lead capture | `05-contact-page.md` | 6 | MVP |
| `/login` | Customer login modal | `06-auth-register-login.md` | 7 | MVP |
| `/register` | Customer registration modal | `06-auth-register-login.md` | 7 | MVP |
| `/:slug` | CMS static pages (About, Terms, Careers, blog) | `12-static-cms-pages.md` | 14 | Post-MVP (Gap G5) |

**Overlays (not routes):**
- **Chat Widget** — Appears on every public page, not a route | `14-feature-ai-chatbot.md` | 1 | MVP
- **Favorites Session** — LocalStorage-backed hearts on all pages | `16-feature-favorites-session.md` | 4, 7 | MVP

**Key Behaviors:**
- Anonymous visitors can browse, search, chat, favorite, fill the requirement wizard, and submit inquiries
- Favorites stored in `session_id` until register/login (then migrated to `user_id`)
- AI features degrade on failure/rate-limit rather than error out
- Design system from `DESIGN.md`; tertiary color marks AI output only

---

## 2. Customer Portal Routes

**Auth:** Bearer token (Supabase JWT) required. Anonymous visitors bounced to `/login`.

**Tenant:** Resolved from authenticated user's tenant association.

**Spec:** `docs/16-customer-spec/` (files 07–11, 16)

| Route | Purpose | Page File | PRD Module | Status |
|---|---|---|---|---|
| `/portal` | Dashboard + "What's New" + recent activity | `07-portal-dashboard.md` | 7 | MVP |
| `/portal/favorites` | Saved properties with action buttons | `08-portal-favorites.md` | 7 | MVP |
| `/portal/requirements` | Saved requirement profiles + AI matches | `09-portal-requirements.md` | 7, 3 | MVP |
| `/portal/inquiries` | Submitted leads + status timeline | `10-portal-inquiries.md` | 7 | MVP |
| `/portal/notifications` | Notification list + preferences | `11-portal-notifications.md` | 7, 15 | MVP |

**Key Behaviors:**
- Shares header and design system with public site (authenticated upsell of the same UI)
- All list queries enforce `tenant_id` (RLS) + `user_id` (application layer) — prevents IDOR
- Empty states designed, not defaulted
- "AI match" chips on recommendation output only
- No email/SMS channels yet (Gap G9); in-app only
- Data filtering: RLS at DB layer, app-layer user_id check on every by-ID fetch

---

## 3. Admin Portal Routes

**Auth:** Bearer token + role check. Routes check `agent` / `admin` / `super_admin` roles server-side per route.

**Tenant:** Resolved from authenticated user's tenant association. Super-admin routes (`/platform/*`) are tenant-agnostic.

**Spec:** `docs/17-admin-spec/`

**Navigation:** Left sidebar nav reaches every module in one click. No sequence; admins jump between areas.

### 3.1 Access & Auth

| Route | Purpose | Page File | Roles | Status |
|---|---|---|---|---|
| `/admin/login` | Admin/agent login | `01-login-and-invite.md` | none | MVP |
| `/admin/invite-accept` | Accept invite link (email) | `01-login-and-invite.md` | none | MVP |

### 3.2 Core CRM — Properties

| Route | Purpose | Page File | Roles | Status |
|---|---|---|---|---|
| `/admin/properties` | Properties list with filtering/sorting | `03-properties-list.md` | agent, admin | MVP |
| `/admin/properties/new` | Add new property | `04-property-add-edit.md` | admin | MVP |
| `/admin/properties/:id/edit` | Edit existing property | `04-property-add-edit.md` | admin | MVP |
| `/admin/properties/bulk-upload` | CSV bulk property upload | `05-property-bulk-upload.md` | admin | MVP |
| `/admin/properties?status=pending` | Approvals queue (draft → published) | `06-property-approvals-status.md` | admin | MVP |

### 3.3 Core CRM — Leads

| Route | Purpose | Page File | Roles | Status |
|---|---|---|---|---|
| `/admin/leads` | Leads Kanban board by stage | `07-leads-kanban.md` | agent, admin | MVP |
| `/admin/leads/:id` | Lead detail panel (slide-in) | `08-lead-detail.md` | agent, admin | MVP |
| `/admin/leads?view=table` | Leads table view + bulk assignment | `09-leads-table-and-assignment.md` | admin | MVP |

### 3.4 People & Roles

| Route | Purpose | Page File | Roles | Status |
|---|---|---|---|---|
| `/admin/agents` | Agent profiles + performance + leaderboard | `10-agents.md` | admin | MVP |
| `/admin/users` | User management + roles + invites | `11-users-roles.md` | admin | MVP |
| `/admin/users/audit-log` | Audit trail of all admin actions | `12-audit-log.md` | admin, super_admin | MVP |

### 3.5 AI Configuration

| Route | Purpose | Page File | Roles | Status |
|---|---|---|---|---|
| `/admin/ai-config/chatbot` | Chatbot system prompt + model selection | `13-ai-config-chatbot.md` | admin | MVP |
| `/admin/ai-config/recommendation` | Rec engine weights + matching thresholds | `14-ai-config-recommendation.md` | admin | MVP |
| `/admin/ai-config/chat-logs` | Chatbot transcript viewer + evals | `15-ai-config-chat-logs.md` | admin | MVP |
| `/admin/ai-config/search-insights` | Search query analytics + insights | `16-ai-config-search-insights.md` | admin | MVP |
| `/admin/chat` | **Live agent chat console** (handoff from chatbot) | `22-agent-chat-console.md` | agent, admin | MVP (Gap G7) |

### 3.6 Content, Reporting & Settings

| Route | Purpose | Page File | Roles | Status |
|---|---|---|---|---|
| `/admin/cms` | CMS page editor + SEO | `17-cms.md` | admin | Post-MVP (Gap G5) |
| `/admin/reports` | Report builder + exports | `18-reports.md` | admin | Post-MVP |
| `/admin/settings/notifications` | Notification rule engine + templates | `19-notification-rules.md` | admin | MVP (partial; Gap G9) |
| `/admin/settings` | Tenant branding (post-MVP, disabled in MVP) | `20-tenant-branding.md` | admin | Post-MVP (FR16.2) |

### 3.7 Platform-Level (Super-Admin Only)

| Route | Purpose | Page File | Roles | Status |
|---|---|---|---|---|
| `/platform/tenants` | Tenant management (create, edit, suspend) | `21-superadmin-tenants.md` | super_admin | Post-MVP |

**Key Behaviors:**
- Sidebar nav is sticky and reaches every module in one click
- All queries enforce tenant scoping (RLS + app-layer filter)
- Status badges use semantic colors from `DESIGN.md` (success/warning/error/neutral)
- No tertiary color on buttons or non-AI badges
- Role enforcement is server-side on every endpoint
- Agents see only leads assigned to them (+ shared team leads if configured)

---

## 4. API Endpoints

**Base path:** `/api/v1/`

**Auth:** `Authorization: Bearer <supabase_jwt>` header. Anonymous endpoints use `X-Session-Id` instead.

**Format:** JSON request/response bodies. Error format: `{ "error": { "code": "...", "message": "..." } }`

**Rate limiting:** `ai/*` endpoints limited per session/IP to cap Bedrock cost.

**Pagination:** `?page=1&page_size=20` query params. Response: `{ "items": [...], "total": N, "page": 1, "page_size": 20 }`

**Spec:** `docs/04-api-spec.md`

### 4.1 Auth Endpoints

| Method | Path | Purpose | Auth | PRD Module |
|---|---|---|---|---|
| POST | `/auth/register` | Register customer account | None | 7 |
| POST | `/auth/login` | Login (delegates to Supabase Auth) | None | 7 |
| POST | `/auth/logout` | Logout / invalidate session | Bearer | 7 |
| GET | `/auth/me` | Current user profile + role + tenant | Bearer | 7 |
| POST | `/auth/invite` | Invite admin/agent user (admin only) | Bearer (admin) | 11 |

### 4.2 AI Endpoints (Public Site) — Core USP

**Rate-limited per session/IP.**

#### AI Search

| Method | Path | Purpose | Auth |
|---|---|---|---|
| POST | `/ai/search` | Natural-language property search | None (session) |

**Request:**
```json
{
  "query": "3BHK under 80 lakhs near tech park",
  "filters": { "listing_type": "sale" },
  "page": 1,
  "page_size": 20
}
```

**Response:**
```json
{
  "items": [
    {
      "property_id": "...",
      "title": "...",
      "price": 7800000,
      "match_score": 0.91,
      "thumbnail_url": "..."
    }
  ],
  "parsed_query": {
    "property_type": "apartment",
    "bedrooms": 3,
    "budget_max": 8000000,
    "location_hint": "tech park"
  },
  "total": 12,
  "page": 1,
  "page_size": 20
}
```

**Failure mode:** Fall back to standard keyword search on raw query.

#### AI Chatbot

| Method | Path | Purpose | Auth |
|---|---|---|---|
| POST | `/ai/chat/message` | Send message, get bot response | None (session) |
| GET | `/ai/chat/history/{conversation_id}` | Retrieve conversation history | None (session) |
| POST | `/ai/chat/escalate` | Escalate to human agent | None (session) |

**Request (`/ai/chat/message`):**
```json
{
  "conversation_id": "optional-existing-id",
  "message": "Is this property still available?",
  "property_id": "optional-context"
}
```

**Response:**
```json
{
  "conversation_id": "...",
  "reply": "Yes, this property is still available. Would you like to schedule a visit?",
  "actions": [
    { "type": "show_property_card", "property_id": "..." }
  ],
  "escalated": false
}
```

**Failure mode:** Show "connect to an agent" path; never a dead chat window.

#### AI Recommendation (Requirement Analysis)

| Method | Path | Purpose | Auth |
|---|---|---|---|
| POST | `/ai/recommend` | Submit requirement profile, get shortlist | None (session) |
| GET | `/ai/recommend/{requirement_profile_id}` | Retrieve saved profile + matches | Bearer |
| PUT | `/ai/recommend/{requirement_profile_id}` | Update saved requirement profile | Bearer |

**Request:**
```json
{
  "budget_min": 5000000,
  "budget_max": 8000000,
  "preferred_locations": ["Tech Park Area", "City Center"],
  "property_type": "apartment",
  "purpose": "self_use",
  "timeline": "3_months",
  "must_have_amenities": ["parking", "gym"]
}
```

**Response:**
```json
{
  "requirement_profile_id": "...",
  "matches": [
    {
      "property_id": "...",
      "match_score": 0.87,
      "match_reason": "Matches your budget and location; missing gym."
    }
  ]
}
```

**Failure mode:** Fall back to closest-match list; never empty state.

### 4.3 Property Endpoints (Public)

| Method | Path | Purpose | Auth | Tenant |
|---|---|---|---|---|
| GET | `/properties` | Browse/filter/sort listings | None | Server-side |
| GET | `/properties/{id}` | Property details | None | Server-side |
| GET | `/properties/{id}/similar` | Similar properties (rec engine) | None | Server-side |
| POST | `/properties/{id}/favorite` | Favorite a property | None (session) or Bearer | Server-side |
| DELETE | `/properties/{id}/favorite` | Unfavorite | None (session) or Bearer | Server-side |

**`GET /properties` query params:** `listing_type, property_type, price_min, price_max, bedrooms, location, amenities[], sort, view (grid/list/map), page, page_size`

### 4.4 Contact / Lead Capture (Public)

| Method | Path | Purpose | Auth | Source |
|---|---|---|---|---|
| POST | `/leads` | Create lead from contact form | None (session) | contact_form |
| POST | `/leads/callback-request` | Request callback with time slot | None (session) | contact_form |

**Request (`/leads`):**
```json
{
  "customer_name": "...",
  "customer_phone": "...",
  "customer_email": "...",
  "message": "...",
  "property_id": "optional",
  "source": "contact_form"
}
```

### 4.5 Customer Portal Endpoints (Authenticated)

**All enforce `tenant_id` (RLS) + `user_id = <caller>` (app-layer).** Every by-ID fetch must verify ownership — IDOR prevention.

| Method | Path | Purpose | Data Touched |
|---|---|---|---|
| GET | `/portal/favorites` | List saved properties | favorites |
| GET | `/portal/requirements` | List saved requirement profiles | requirement_profiles |
| DELETE | `/ai/recommend/{requirement_profile_id}` | Delete requirement profile (soft-delete + stop alerts) | requirement_profiles |
| GET | `/portal/inquiries` | List inquiries + their status | inquiries, inquiry_timeline |
| GET | `/portal/notifications` | List notifications | notifications |
| POST | `/portal/notifications/read` | Mark notification(s) read | notifications |
| PUT | `/portal/notifications/preferences` | Update notification preferences (email/SMS/in-app per event type) | notification_preferences |
| GET | `/unsubscribe?token=...` | **Unauthenticated** — signed single-purpose token to unsubscribe | notification_preferences |

### 4.6 Admin Portal Endpoints (Authenticated Admin/Agent)

**Implementation:** Routers call Service → Repository. Repositories enforce `tenant_id` scoping. Services enforce role permissions.

**Spec:** `docs/17-admin-spec/`, per-screen pages.

| Method | Path | Purpose | Roles |
|---|---|---|---|
| GET | `/admin/properties` | List properties + filters + sort | agent, admin |
| POST | `/admin/properties` | Create property | admin |
| GET | `/admin/properties/{id}` | Get property details | agent, admin |
| PUT | `/admin/properties/{id}` | Update property | admin |
| DELETE | `/admin/properties/{id}` | Delete property (soft) | admin |
| POST | `/admin/properties/bulk-upload` | Bulk property import | admin |
| GET | `/admin/properties/approvals` | List draft → pending → published pipeline | admin |
| POST | `/admin/properties/{id}/approve` | Move property to published | admin |
| POST | `/admin/properties/{id}/reject` | Move property to rejected | admin |
| — | — | — | — |
| GET | `/admin/leads` | List leads + filter by stage | agent, admin |
| GET | `/admin/leads/{id}` | Lead detail + timeline | agent, admin |
| PUT | `/admin/leads/{id}` | Update lead (status, notes, assignment) | agent, admin (self) or admin |
| POST | `/admin/leads/{id}/assign` | Assign lead to agent | admin |
| — | — | — | — |
| GET | `/admin/agents` | List agents + performance | admin |
| GET | `/admin/agents/{id}` | Agent profile + leaderboard rank | admin |
| — | — | — | — |
| GET | `/admin/users` | List users + roles + invite status | admin |
| POST | `/admin/users` | Invite new user (agent/admin) | admin |
| GET | `/admin/users/{id}` | User detail | admin |
| PUT | `/admin/users/{id}` | Update user role | admin |
| DELETE | `/admin/users/{id}` | Revoke user access | admin |
| — | — | — | — |
| GET | `/admin/audit-log` | Audit trail (all admin writes) | admin, super_admin |
| — | — | — | — |
| GET | `/admin/ai-config/chatbot` | Get chatbot settings (system prompt, model) | admin |
| PUT | `/admin/ai-config/chatbot` | Update chatbot settings | admin |
| GET | `/admin/ai-config/recommendation` | Get rec engine weights + thresholds | admin |
| PUT | `/admin/ai-config/recommendation` | Update rec engine settings | admin |
| GET | `/admin/ai-config/chat-logs` | List chatbot transcripts | admin |
| GET | `/admin/ai-config/search-insights` | Query analytics + trending searches | admin |
| — | — | — | — |
| GET | `/admin/cms` | List CMS pages | admin |
| POST | `/admin/cms` | Create CMS page | admin |
| PUT | `/admin/cms/{id}` | Update CMS page | admin |
| DELETE | `/admin/cms/{id}` | Delete CMS page | admin |
| — | — | — | — |
| GET | `/admin/reports` | List saved reports | admin |
| POST | `/admin/reports` | Run report (builder) | admin |
| — | — | — | — |
| GET | `/admin/settings/notifications` | Get notification rules | admin |
| POST | `/admin/settings/notifications` | Create notification rule | admin |
| PUT | `/admin/settings/notifications/{id}` | Update notification rule | admin |
| DELETE | `/admin/settings/notifications/{id}` | Delete notification rule | admin |
| — | — | — | — |
| GET | `/platform/tenants` | List all tenants (super-admin) | super_admin |
| POST | `/platform/tenants` | Create tenant | super_admin |
| GET | `/platform/tenants/{id}` | Tenant details | super_admin |
| PUT | `/platform/tenants/{id}` | Update tenant settings | super_admin |
| DELETE | `/platform/tenants/{id}` | Suspend/delete tenant | super_admin |

---

## 5. Route Hierarchy & Flows

### 5.1 Public Site Sitemap

```
/ (Homepage)
├── /search                          Property Listing
├── /property/:id                    Property Details
├── /requirement-analysis            Requirement Wizard
├── /contact                         Contact Form
├── /login                           Auth (modal)
├── /register                        Auth (modal)
├── /:slug                           CMS Pages (static)
│
└── Overlays (every page):
    ├── Chat Widget (bottom-right)   AI Chatbot
    ├── Favorites Heart              Session favorites
    ├── AI Search Bar                AI Search (homepage header)
```

### 5.2 Customer Portal Sitemap

```
/portal (requires Bearer token)
├── /portal/dashboard                Overview
├── /portal/favorites                Saved Properties
├── /portal/requirements             Requirement Profiles + Matches
├── /portal/inquiries                Lead Status Timeline
└── /portal/notifications            Notification Center
```

**Entry points:**
- Login from public site (`/login`)
- Upsell banner on public pages (after persist-worthy action)
- Chat widget escalation (agent says "I'll connect you to an account")

### 5.3 Admin Portal Sitemap

```
/admin/ (requires Bearer token + role check)

Access:
├── /admin/login
└── /admin/invite-accept

Core CRM:
├── /admin/properties
│   ├── /admin/properties/new
│   ├── /admin/properties/:id/edit
│   ├── /admin/properties/bulk-upload
│   └── /admin/properties?status=pending
├── /admin/leads
│   ├── /admin/leads/:id
│   └── /admin/leads?view=table
├── /admin/agents
└── /admin/users
    └── /admin/users/audit-log

AI Configuration:
├── /admin/ai-config/chatbot
├── /admin/ai-config/recommendation
├── /admin/ai-config/chat-logs
├── /admin/ai-config/search-insights
└── /admin/chat

Content & Settings:
├── /admin/cms
├── /admin/reports
├── /admin/settings/notifications
└── /admin/settings

Platform (super-admin only):
└── /platform/tenants
```

### 5.4 Session → Authenticated Transition

**Favorites migration on register/login:**
1. Visitor browses anonymously; favorites stored in `session_id` (localStorage)
2. Visitor clicks "Ask about this" on property details → forced to `/register`
3. On successful register/login, backend re-keys all `session_id` rows to `user_id`
4. Customer portal now shows all favorites

**Spec:** `docs/16-feature-favorites-session.md` §5 (migration contract)

---

## 6. Tenant Scoping Rules

**Golden rule:** Every data fetch is filtered by `tenant_id` at the DB layer (RLS policy) *and* by app-layer filter (second layer of defense).

### 6.1 Public Site Routes

- **Tenant resolved:** From request origin domain/subdomain (server-side)
- **Identity:** `session_id` (client-generated, stored in `localStorage`)
- **Data isolation:** All GET/POST operations implicitly scoped to the tenant's domain
- **RLS:** `tenant_id = current_tenant_id()` enforced on `properties`, `requirement_profiles`, `inquiries`, `favorites` (session-keyed)

### 6.2 Customer Portal Routes

- **Tenant resolved:** From authenticated user's `tenant_id` (in JWT claims)
- **Identity:** `user_id` (in JWT)
- **Data isolation:** RLS enforces `tenant_id` AND app-layer check enforces `user_id` on every by-ID fetch (IDOR prevention)
- **Example:** `GET /portal/favorites` must return only `favorites` where `user_id = <caller>` **and** `property.tenant_id = <caller.tenant_id>` (RLS)

### 6.3 Admin Portal Routes

- **Tenant resolved:** From authenticated user's `tenant_id` (in JWT claims)
- **Identity:** `user_id` + `role` (in JWT and `users` table)
- **Data isolation:** RLS enforces `tenant_id`. App-layer enforces role + ownership (e.g., agent can only edit leads assigned to them).
- **Super-admin routes:** `/platform/*` have no tenant scoping (operate across all tenants)

### 6.4 IDOR Prevention Pattern

Every by-ID fetch must verify the caller owns the object:

```python
# Backend service layer
def get_favorite(favorite_id: str, user_id: str, tenant_id: str) -> Favorite:
    # DB layer (RLS) + app-layer check
    fav = repo.get_favorite(favorite_id, tenant_id=tenant_id)
    if fav.user_id != user_id:
        raise PermissionDenied("Not your favorite")
    return fav
```

---

## 7. Implementation Status

### MVP Scope (Sprint 0–4)

| Category | Routes | Status | Notes |
|---|---|---|---|
| **Public Site** | `/`, `/search`, `/property/:id`, `/requirement-analysis`, `/contact`, `/login`, `/register`, chat widget | ✅ MVP | Route `/:slug` (CMS) is Gap G5 |
| **Portal** | `/portal`, `/portal/favorites`, `/portal/requirements`, `/portal/inquiries`, `/portal/notifications` | ✅ MVP | Email/SMS channels Gap G9 |
| **Admin** | `/admin/*` (core CRM + AI config) except CMS | ✅ MVP | CMS is Gap G5 |
| **API** | Auth, AI search/chat/recommend, properties, leads, portal | ✅ MVP | All endpoints above |

### Post-MVP / Blocked by Gaps

| Feature | Route | Blocker | Issue |
|---|---|---|---|
| CMS Pages | `/:slug`, `/admin/cms` | Gap G5 | No public read endpoint. *(The scheduler exists — `02-architecture.md` §4.4.)* |
| Tenant Branding | `/admin/settings` | FR16.2 decision | Post-MVP; no themeeable UI in MVP |
| Email/SMS Notifications | `/portal/notifications`, `/admin/settings/notifications` | ~~G9~~ ✅ | **Buildable.** SendGrid + Twilio (`02-architecture.md` §3); `pg_cron` + jobs worker (§4.4). See `GAPS.md` §5A |
| Super-Admin Tenants | `/platform/tenants` | Gap G10 | No tenant creation flow in MVP |
| Reports | `/admin/reports` | Gap G11 | No stateless report definition API |
| Agent Chat Handoff | `/admin/chat` | Gap G7 (closed) | Now in MVP via new spec file `22-agent-chat-console.md` |

**Gaps:** See `docs/00-project-overview.md` §9.1 and respective spec files' `README.md` §5 for details.

---

## Quick Reference

### By PRD Module

| Module | Routes | Auth | Spec File |
|---|---|---|---|
| 1. AI Chatbot | `/`, `/ai/chat/*` | None (session) | `docs/05-ai-chatbot-spec.md` |
| 2. AI Search | `/search`, `/ai/search` | None (session) | `docs/06-ai-search-spec.md` |
| 3. Requirement Wizard | `/requirement-analysis`, `/ai/recommend` | None (session) | `docs/07-ai-recommendation-spec.md` |
| 4. Browse & Filter | `/`, `/search`, `/property/:id` | None | `docs/01-prd.md` §2–5 |
| 5. Property Details | `/property/:id` | None | `docs/16-customer-spec/03-property-details.md` |
| 6. Lead Capture | `/contact`, `/property/:id`, `/api/v1/leads` | None | `docs/16-customer-spec/15-feature-lead-capture.md` |
| 7. Customer Portal | `/portal/*` | Bearer | `docs/16-customer-spec/07–11` |
| 8. Dashboard (Admin) | `/admin/dashboard` | Bearer (admin) | `docs/17-admin-spec/02-dashboard.md` |
| 9. Property Management | `/admin/properties/*` | Bearer (admin) | `docs/17-admin-spec/03–06` |
| 10. Lead CRM | `/admin/leads*` | Bearer (agent/admin) | `docs/17-admin-spec/07–09` |
| 11. Users & Access | `/admin/users`, `/auth/invite` | Bearer (admin) | `docs/08-auth-roles-spec.md` |
| 12. Agent Leaderboard | `/admin/agents` | Bearer (admin) | `docs/17-admin-spec/10-agents.md` |
| 13. AI Configuration | `/admin/ai-config/*` | Bearer (admin) | `docs/17-admin-spec/13–16` |
| 14. Content / CMS | `/:slug`, `/admin/cms` | Mixed | Gap G5 |
| 15. Reports & Auditing | `/admin/reports`, `/admin/users/audit-log` | Bearer (admin) | `docs/17-admin-spec/18, 12` |
| 16. Branding & Settings | `/admin/settings`, `/platform/tenants` | Bearer (admin/super-admin) | `docs/17-admin-spec/20–21` |

### By Implementation Folder

| Folder | Routes | Files |
|---|---|---|
| `public-site/` | `/`, `/search`, `/property/:id`, `/requirement-analysis`, `/contact`, `/login`, `/register`, `/:slug` | `pages/`, `components/`, `hooks/`, `api/` |
| `admin-portal/` | `/admin/*`, `/platform/*` | `pages/`, `components/`, `hooks/`, `api/` |
| `backend/` | `/api/v1/*` | `app/api/v1/`, `app/services/`, `app/repositories/`, `app/ai_clients/` |

---

## Keeping This Doc Current

**Owner:** This file is NOT a source of truth for routes — it is a **convenience reference** derived from the owning docs.

**Owning docs (source of truth):**
- Public site routes: `docs/16-customer-spec/README.md` §2–3
- Admin portal routes: `docs/17-admin-spec/README.md` §2–3
- API endpoints: `docs/04-api-spec.md` §2–6
- PRD module mappings: `docs/01-prd.md`

**How to update:**
1. Change the owning doc first
2. Run `python scripts/check_drift.py` to verify no conflicts
3. Update this file to match
4. Commit together

**Last verified:** 2026-07-14 against `docs/16-customer-spec/README.md`, `docs/17-admin-spec/README.md`, `docs/04-api-spec.md`, and `docs/01-prd.md`.
