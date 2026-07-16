# Admin Portal — Detailed Spec (Index)

> **Doc 17 of the PropVista CRM documentation set.** The full, page-by-page specification for the **admin portal** — the CRM used by agents, tenant admins, and the platform super admin. Implementation-level companion to `01-prd.md` (Modules 8–16).
>
> **Status:** Draft v1.0 · **Last updated:** July 2026
> Implemented in: `frontend/` — the admin routes (`src/routes/admin/`, lazy-loaded). See `02-architecture.md` §5.2, ADR-0020.
> Depends on: `01-prd.md`, `03-database-schema.md`, `04-api-spec.md`, `08-auth-roles-spec.md`, `13-ui-ux-flows.md`, `14-screen-workflows.md`
> Customer counterpart: `docs/16-customer-spec/`

---

## 1. How to Use This Doc Set

One file per screen. Each follows the same 11-section template as the customer set, plus a mandatory **Roles** section — because in the admin portal, *who is looking* changes what the page does.

| Section | Answers |
|---|---|
| 1. Purpose & Traceability | Why the screen exists; PRD module + FR numbers |
| 2. Entry & Exit Points | Navigation in and out |
| 3. Layout & Regions | Wireframe + region breakdown |
| 4. Workflow | The click-by-click sequence |
| 5. States | Loading, empty, error, permission-denied |
| 6. API Calls | Every request, and when |
| 7. Data Touched | Tables read/written |
| 8. **Roles & Permissions** | agent vs. admin vs. super_admin — **enforced server-side** |
| 9. Validation & Edge Cases | Input rules and failure modes |
| 10. Acceptance Criteria | `TC-*` cases from `docs/15-development-plan.md` |
| 11. Open Questions | Unresolved — do not guess |

---

## 2. Page Index

### 2.1 Access

| # | File | Route | PRD Module |
|---|---|---|---|
| 01 | [`01-login-and-invite.md`](01-login-and-invite.md) | `/admin/login`, invite accept | 11 |

### 2.2 Core CRM

| # | File | Route | PRD Module |
|---|---|---|---|
| 02 | [`02-dashboard.md`](02-dashboard.md) | `/admin/dashboard` | 8 |
| 03 | [`03-properties-list.md`](03-properties-list.md) | `/admin/properties` | 9 |
| 04 | [`04-property-add-edit.md`](04-property-add-edit.md) | `/admin/properties/new`, `/:id/edit` | 9 |
| 05 | [`05-property-bulk-upload.md`](05-property-bulk-upload.md) | `/admin/properties/bulk-upload` | 9 |
| 06 | [`06-property-approvals-status.md`](06-property-approvals-status.md) | `/admin/properties?status=pending` | 9 |
| 07 | [`07-leads-kanban.md`](07-leads-kanban.md) | `/admin/leads` | 10 |
| 08 | [`08-lead-detail.md`](08-lead-detail.md) | `/admin/leads/:id` (panel) | 10 |
| 09 | [`09-leads-table-and-assignment.md`](09-leads-table-and-assignment.md) | `/admin/leads?view=table` | 10 |

### 2.3 People

| # | File | Route | PRD Module |
|---|---|---|---|
| 10 | [`10-agents.md`](10-agents.md) | `/admin/agents` | 12 |
| 11 | [`11-users-roles.md`](11-users-roles.md) | `/admin/users` | 11 |
| 12 | [`12-audit-log.md`](12-audit-log.md) | `/admin/users/audit-log` | 11 |

### 2.4 AI Configuration (Module 13)

| # | File | Route |
|---|---|---|
| 13 | [`13-ai-config-chatbot.md`](13-ai-config-chatbot.md) | `/admin/ai-config/chatbot` |
| 14 | [`14-ai-config-recommendation.md`](14-ai-config-recommendation.md) | `/admin/ai-config/recommendation` |
| 15 | [`15-ai-config-chat-logs.md`](15-ai-config-chat-logs.md) | `/admin/ai-config/chat-logs` |
| 16 | [`16-ai-config-search-insights.md`](16-ai-config-search-insights.md) | `/admin/ai-config/search-insights` |
| **22** | [**`22-agent-chat-console.md`**](22-agent-chat-console.md) | **`/admin/chat`** — live handoff. **The only real-time screen in the portal** (FR1.7; closed gap G7) |

### 2.5 Content, Reporting & Settings

| # | File | Route | PRD Module |
|---|---|---|---|
| 17 | [`17-cms.md`](17-cms.md) | `/admin/cms` | 14 |
| 18 | [`18-reports.md`](18-reports.md) | `/admin/reports` | 15 |
| 19 | [`19-notification-rules.md`](19-notification-rules.md) | `/admin/settings/notifications` | 15 |
| 20 | [`20-tenant-branding.md`](20-tenant-branding.md) | `/admin/settings` | 16 |
| 21 | [`21-superadmin-tenants.md`](21-superadmin-tenants.md) | `/platform/tenants` | 16 |

---

## 3. Site Map

Authoritative version: `13-ui-ux-flows.md` §3.2.

```
/admin/dashboard
├── /admin/properties            list · add/edit · bulk upload · approvals
├── /admin/leads                 Kanban + table
├── /admin/agents                profiles · performance · leaderboard
├── /admin/users                 roles · invites · audit log
├── /admin/ai-config             chatbot · recommendation · chat logs · search insights
├── /admin/cms                   pages · SEO
├── /admin/reports               builder · exports
├── /admin/settings              tenant branding · notification rules
└── /platform/tenants            super_admin only
```

**Navigation principle** (`13-ui-ux-flows.md` §2.4): the left nav must reach **every** module in one click from anywhere. Admins jump between modules non-linearly; they do not follow a sequence.

---

## 4. Cross-Cutting Rules for Every Admin Page

### 4.1 The three roles change everything

| Role | Sees |
|---|---|
| `agent` | Their **assigned** leads. Their own performance. Properties (read + limited update). **No** users, AI config, CMS, reports, settings, or tenants |
| `admin` | Everything within their tenant |
| `super_admin` | Tenant management (`/platform/tenants`); not scoped to one tenant |

**Permissions are enforced server-side via `require_role`/`require_permission` dependencies** (`08-auth-roles-spec.md` §5). Hiding a nav item is a *courtesy*, not a security boundary. Every restricted endpoint must return **403** when called directly by an out-of-scope role — and each one needs a test that proves it (`TC-ROLE-01`, `TC-SEC-01`).

**Agents are additionally scoped to their own rows.** An agent calling `GET /admin/leads/{id}` for a lead assigned to someone else gets a 403 — a role check alone is not sufficient, there's an ownership check too (`08-auth-roles-spec.md` §5).

### 4.2 Tenant isolation
Tenant is resolved from the **authenticated user's tenant association**, never from a request parameter (`04-api-spec.md` §1). Everything an admin sees is their tenant's. `super_admin` is the sole exception and is scoped to platform-level tables.

### 4.3 Every write is audited
Per FR11.3 / PRD Module 11: **all admin-portal write actions are logged** (actor, action, entity, timestamp). This is not optional and not per-screen — it's a cross-cutting concern implemented once, at the service layer, and every mutating endpoint participates. See [`12-audit-log.md`](12-audit-log.md).

### 4.4 Soft delete, always
Properties, leads, and users are **soft-deleted** (`deleted_at`), never hard-deleted (`.claude/rules/database.md`). CRM history has to survive. "Delete" in the UI means "archive" in the database — and the copy should be honest about that.

### 4.5 Design system — and no tenant branding
The admin portal uses the design system directly: **[`docs/DESIGN.md`](../DESIGN.md)**. No tenant logo, no tenant colors. It's a tool, not a storefront.

> ⚠️ `13-ui-ux-flows.md` §4.1–§4.5 used to hold a parallel system (brass/teal/Fraunces/IBM Plex Mono). **It is deleted.** Any page in this set still citing it for a color, font or badge is stale — go to `DESIGN.md`. Doc 13 §4.6–§4.8 (iconography, breakpoints, accessibility) is still live.

Neither surface is tenant-branded in the MVP (decided 2026-07-13 — the public site isn't either, see PRD FR16.2). Every tenant gets the same tokens.

Two `DESIGN.md` rules bite hardest in the admin portal:
- **The `tertiary` family marks AI output and nothing else.** Legitimate uses: the AI-derived lead sources (Chatbot, AI Search), the AI-config screens' model output, chat-log transcripts. **Not** legitimate: focus rings (those are `primary`), nav highlights, or any chart series that isn't AI-derived.
- **Status uses the semantic ramp**, never `primary`/`secondary` — see `DESIGN.md` → Semantic Status Colors. This is a denser, more table-heavy surface than the public site, and status legibility at chip size is the thing most likely to break.

### 4.6 Desktop-first, and that's a decision
Agents and admins work at desks. `13-ui-ux-flows.md` §5 flags mobile parity as an open question; this doc set assumes **desktop-first with a usable read-only mobile view**, and calls it out where it matters (the Kanban board in particular is not a mobile experience).

---

## 5. Known Spec Gaps

Found while writing this set. **Fix the owning doc before building the affected screen** (`.claude/rules/workflow.md`).

### ✅ Closed in `03-database-schema.md` v1.1

| # | Gap | Resolution |
|---|---|---|
| A1 | No `audit_log` table, despite FR11.3, `GET /admin/audit-log`, and `.claude/rules/security.md` all requiring one | `audit_log` added (§3.23), **append-only enforced by `REVOKE UPDATE, DELETE`**. Build it with the *first* write endpoint — a log added late has no history |
| A4 | Configurable stages (FR10.1) vs. the fixed `leads.stage` enum | **Decided: fixed enum for MVP.** ⚠️ `01-prd.md` FR10.1 still promises configurability and must be updated to match |
| A5 | No `reports` table, though `GET /admin/reports/{id}/export` implied one | **Decided: reports are stateless** — export re-runs the query with the same params. ⚠️ `04-api-spec.md` §14 needs updating to a parameterized export endpoint |
| A6 | No `bulk_uploads` table, though FR9.2 requires per-row error reporting | `bulk_uploads` + `bulk_upload_rows` added (§3.25) |
| A7 | `properties` had no `created_by`, so agent ownership-scoping was inexpressible | `created_by` added (§3.4) |
| A8 | Property views weren't tracked (FR8.2) | `property_views` added (§3.7). **Cannot be backfilled** — must ship with the first published property |
| A10 | `leads` had no `user_id` | Added, plus `session_id`, `requirement_profile_id`, `chat_conversation_id`, `deal_value` (§3.8) |
| — | Ownership changes were unrecorded, making per-agent attribution (FR12.2) uncomputable | `lead_activities.activity_type` + `from_agent_id`/`to_agent_id` (§3.10) |
| — | Chat-log flagging (FR13.2) had no column; abandoned conversations stayed `active` forever | `chat_conversations.flagged`, `flag_reason`, `status = 'abandoned'`, `last_message_at` (§3.13) |
| — | The per-tenant "approval required" flag (FR9.3) had no home; dated KPIs had no timezone | `tenants.requires_property_approval`, `tenants.timezone` (§3.1) |
| — | FR13.4 search insights had no data source | `search_queries` added (§3.24) — **must exist before Sprint 5** |
| — | Homepage banners (FR14.1) couldn't be a `cms_pages` row | `cms_banners` added (§3.17) |
| — | `listing_expiring` (FR15.2) could never fire | `properties.expires_at` added |

### ⛔ Still open

| # | Gap | Affects | Owning doc |
|---|---|---|---|
| A2 | **No agent-reply path for escalated chats.** A chat escalates to a human (FR1.7), but no endpoint lets an agent *send* a message into that conversation, and no delivery channel exists. The loop never closes. | [`08`](08-lead-detail.md), [`15`](15-ai-config-chat-logs.md) | `04-api-spec.md`, `05-ai-chatbot-spec.md` |
| A3 | **Lead auto-assignment (FR10.2) is undecided** — round-robin, rules-based, or manual claim? Determines whether new leads have an owner, hence whether anyone works them. Recommend **round-robin**; the schema already models system-initiated assignment. | [`07`](07-leads-kanban.md), [`09`](09-leads-table-and-assignment.md) | `01-prd.md` |
| A9 | **"Site visitors" KPI (FR8.1) has no data source** — no analytics/traffic tracking specified. Drop the card rather than shipping a fake number. | [`02`](02-dashboard.md) | `01-prd.md` / `10-deployment-devops.md` |
| ~~A11~~ | ✅ **CLOSED — never real.** `02-architecture.md` **§4.4**: `pg_cron` + a `jobs` table + a Python worker, decided **2026-07-13**, with `mark_stale_leads()` listed by name. Follow-up reminders, stale-lead alerts, listing expiry and abandoned-chat cleanup are all buildable. This entry was a stale summary (`GAPS.md` §5A). | — | — |
| A12 | **No email/SMS provider chosen.** In-app notifications now work; email/SMS remain dead toggles. | [`19`](19-notification-rules.md) | `10-deployment-devops.md` |
| A13 | **What `tenants.status = suspended`/`trial` actually *do*** — three values, no defined behavior. | [`21`](21-superadmin-tenants.md) | `01-prd.md` |
| A14 | **No public CMS read endpoint** — the module publishes into a void. Plus missing endpoints: property reject, bulk operations, chatbot/weights preview, resend/revoke invite, tenant-settings `GET`, domain verification, usage stats. | [`17`](17-cms.md), [`06`](06-property-approvals-status.md), [`13`](13-ai-config-chatbot.md), [`20`](20-tenant-branding.md) | `04-api-spec.md` |
| A15 | **No per-tenant SSL provisioning** for custom domains. | [`20`](20-tenant-branding.md) | `10-deployment-devops.md` |

---

## 6. Build Order

Per `15-development-plan.md`: Auth/roles (Sprint 1) → Property management (Sprint 2–3) → Lead pipeline (Sprint 4) → AI config (Sprints 5–7, alongside each AI feature) → Dashboard/reports/CMS/tenant settings (Phase 3, Sprints 8–11).

The audit log (A1) is cross-cutting and should be built with the **first** write endpoint, not retrofitted at the end.
