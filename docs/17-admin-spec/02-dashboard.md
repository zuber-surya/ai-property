# Page: Admin Dashboard & Analytics

> **Route:** `/admin/dashboard` · **PRD Module:** 8 · **App:** `admin-portal/` → `pages/Dashboard/`
> Part of [Doc 17 — Admin Spec](README.md). Read [`README.md` §4](README.md#4-cross-cutting-rules-for-every-admin-page) first.

---

## 1. Purpose & Traceability

The owner's morning glance: *is the business healthy, and what needs me today?* It is a **launchpad, not a destination** — every number and every activity row is a link into the module where the work actually happens (Vikram's non-linear flow, `13-ui-ux-flows.md` §2.4).

| Requirement | Source |
|---|---|
| FR8.1 KPI cards: total listings, active leads, conversion rate, site visitors | `01-prd.md` §9 |
| FR8.2 Charts: lead-source breakdown, property views over time | `01-prd.md` §9 |
| FR8.3 Recent activity feed (new leads, listing changes, chatbot escalations) | `01-prd.md` §9 |
| Acceptance: **all metrics tenant-scoped; numbers reconcile with the underlying CRM data** | `01-prd.md` §9 |
| Screen workflow | `14-screen-workflows.md` §6 |

---

## 2. Entry & Exit Points

**Entry:** the post-login landing for `admin` (agents land on their leads instead — see [01](01-login-and-invite.md) §2). The logo/home link from anywhere.

**Exit:** everything here is a link.

| Element | Goes to |
|---|---|
| "Active leads" KPI | [Lead Pipeline](07-leads-kanban.md) |
| "Total listings" KPI | [Properties](03-properties-list.md) |
| "Pending approval" | [Approvals](06-property-approvals-status.md) |
| Activity: new lead | [Lead Pipeline](07-leads-kanban.md), deep-linked to that lead |
| Activity: property published | [Properties](03-properties-list.md), deep-linked |
| Activity: chatbot escalation | [Chat Logs](15-ai-config-chat-logs.md) / the lead |
| Chart: lead source | [Reports](18-reports.md), pre-filtered |

---

## 3. Layout & Regions

```
┌──────────┬───────────────────────────────────────────────────────┐
│ SIDEBAR  │  Dashboard                        [ Last 30 days ▾ ]  │
│          │                                                       │
│ ▸Dashboard  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐     │
│  Properties │ LISTINGS│ │  ACTIVE │ │ CONVER- │ │ VISITORS│     │
│  Leads   │  │         │ │  LEADS  │ │  SION   │ │         │     │
│  Agents  │  │   142   │ │   38    │ │  12.4%  │ │  ⚠ no   │     │
│  Users   │  │  ▲ 6    │ │  ▲ 12   │ │  ▼ 1.2  │ │  source │     │
│  AI Config  │  3 pending│ │ 5 unassigned│      │ │ (A9)   │     │
│  CMS     │  └─────────┘ └─────────┘ └─────────┘ └─────────┘     │
│  Reports │      ↑ each card is a link into its module            │
│  Settings│                                                       │
│          │  ┌── LEAD SOURCES ─────┐ ┌── PROPERTY VIEWS ────────┐│
│          │  │                     │ │                          ││
│          │  │  Chatbot      ████ 42│ │   ⚠ not tracked (A8)    ││
│          │  │  AI search    ███  31│ │                          ││
│          │  │  Contact form ██   18│ │   no table records a     ││
│          │  │  Requirement  █    12│ │   property view          ││
│          │  │  Walk-in      ▌     4│ │                          ││
│          │  └─────────────────────┘ └──────────────────────────┘│
│          │                                                       │
│          │  ┌── RECENT ACTIVITY ──────────────────────────────┐ │
│          │  │ ● New lead from AI Chatbot — Sunview      2m ago│ │
│          │  │ ⚠ Chatbot escalation — visitor wants an   8m ago│ │
│          │  │   agent                                         │ │
│          │  │ ● Property #204 published by Vikram      1h ago │ │
│          │  │ ● Lead moved to Negotiation by Anjali    2h ago │ │
│          │  └─────────────────────────────────────────────────┘ │
└──────────┴───────────────────────────────────────────────────────┘
```

| Region | Contents |
|---|---|
| Sidebar | Every module, one click, from anywhere (`13-ui-ux-flows.md` §2.4) |
| Date range | Applies to KPIs and charts. Default: last 30 days |
| KPI cards | Value + trend vs. the previous period + a **secondary actionable line** ("3 pending approval") — the number tells you the state, the second line tells you what to *do* |
| Lead sources | Bar/donut of `leads.source` (FR8.2) |
| Property views | **Cannot be built — Gap A8** |
| Activity feed | Newest first. Escalations are visually flagged (`color-coral`) — they're the only genuinely time-sensitive item |

---

## 4. Workflow

```
Admin logs in → Dashboard
   │
   ├─→ GET /admin/dashboard/summary   → KPI cards
   ├─→ GET /admin/dashboard/charts    → lead sources, property views
   └─→ GET /admin/dashboard/activity  → activity feed
        │  3 parallel calls; each section renders as it lands.
        │  The activity feed is the most valuable and often the slowest —
        │  don't gate the KPIs behind it.
        ▼
   Renders (tenant-scoped)
        │
        ├─→ Changes the date range → summary + charts re-query
        │                             (the activity feed does NOT — it's
        │                              always "recent", not range-bound)
        │
        ├─→ Clicks a KPI card → the relevant module, pre-filtered
        │
        └─→ Clicks an activity row → deep-links to that entity
              e.g. "New lead from AI Chatbot" → /admin/leads?lead=<id>
                   with the detail panel already open
```

**The deep link must land on the thing, not the list.** Clicking "New lead from AI Chatbot" and being dropped on an unfiltered Kanban board is a failure — the admin then has to *find* the lead they just clicked.

---

## 5. States

| State | Behavior |
|---|---|
| Loading | Skeleton cards + chart placeholders. The sidebar is immediately usable |
| **New tenant, zero data** | The day-one state, and it must be designed. Not four zeros and two empty charts — an **onboarding checklist**: "① Add your first property ② Invite your team ③ Configure your chatbot". This is the tenant's first impression of the product |
| Zero leads but properties exist | KPIs render; the lead chart shows an empty state with "leads will appear here as visitors inquire" |
| A section fails | Inline retry **in that section only**. A broken chart must not take down the KPIs |
| `agent` role | Should not land here at all (see [01](01-login-and-invite.md) §2). If they navigate here directly, show **only their own** performance — never tenant-wide KPIs. FR8.1 numbers are business-level data, and an agent seeing tenant-wide conversion rates is a permissions leak, not a feature |
| Stale/cached figures | If any KPI is cached, label the freshness. An admin making decisions on numbers of unknown age is worse off than one who knows they're an hour old |

---

## 6. API Calls

| Trigger | Call | Notes |
|---|---|---|
| Mount | `GET /admin/dashboard/summary` | KPI cards. `04-api-spec.md` §7 |
| Mount / date change | `GET /admin/dashboard/charts` | Lead sources, property views |
| Mount | `GET /admin/dashboard/activity` | Recent activity feed |

All are `admin`-scoped and tenant-scoped from the authenticated user.

---

## 7. Data Touched

| Table | Access |
|---|---|
| `properties` | Read (counts by status) |
| `leads` | Read (counts by stage/source; conversion) |
| `lead_activities` | Read (stage-change events for the feed + conversion timing) |
| `chat_conversations` | Read (escalations for the feed) |
| `users` | Read (actor names in the feed) |
| *`audit_log`* | The natural source for "listing changes" in the feed — **doesn't exist (A1)** |
| *property views* | **Doesn't exist (A8)** |
| *site traffic* | **Doesn't exist (A9)** |

---

## 8. Roles & Permissions

| | `agent` | `admin` | `super_admin` |
|---|---|---|---|
| Tenant-wide KPIs | ❌ | ✅ | ✅ |
| Own performance only | ✅ | ✅ | ✅ |
| Activity feed (tenant-wide) | ❌ | ✅ | ✅ |

Per `08-auth-roles-spec.md` §5.1, an agent gets "Partial (own performance only)". **The cleanest implementation is a separate agent-facing view** rather than one endpoint that silently returns different numbers depending on the caller's role — an endpoint whose *meaning* changes by role is a bug factory. Either way, the filtering is server-side.

---

## 9. Validation & Edge Cases

- **"Conversion rate" is undefined.** Closed-won ÷ total leads? ÷ leads in a terminal state? Over what window — leads *created* in the period, or *closed* in it? **These give materially different numbers**, and FR8.1's acceptance criterion is that the dashboard reconciles with [Reports](18-reports.md). Two screens computing "conversion" differently is the classic way to destroy trust in a CRM's numbers. **Define it once, in one service, used by both.**
- **"Active leads"** — presumably any lead not in `closed_won`/`closed_lost`. Same rule: define it once.
- **Division by zero:** zero leads → conversion is "—", not "0%" and definitely not `NaN%`.
- **Trend arrows** need a previous period. For a tenant less than 30 days old, there isn't one — show the value with no arrow, not a misleading "▲ 100%".
- **Soft-deleted rows** (`deleted_at`) must be excluded from every count. Easy to forget in an aggregate query, and it makes numbers silently wrong.
- **Timezone:** "last 30 days" in whose timezone? The tenant's, not UTC, and definitely not the browser's — otherwise two admins in the same company see different numbers. There's no tenant timezone column (see §11).

---

## 10. Acceptance Criteria

| ID | Case | Source |
|---|---|---|
| TC-DASH-01 | KPI figures are correct and **reconcile with the underlying lead/property data** | Sprint 8 |
| TC-TENANT-01 | All metrics are strictly tenant-scoped — no other tenant's leads or listings contribute to any number | Sprint 1 |
| TC-ROLE-01 | An agent cannot retrieve tenant-wide dashboard data | Sprint 8 |
| — | Dashboard "conversion rate" equals the Reports module's for the same range | FR8.1 acceptance |

---

## 11. Open Questions

- [ ] **Gap A8 — property views aren't tracked**, so FR8.2's "property views over time" chart cannot be built. Needs a `property_views` table (or an analytics integration). Cheap to add now; annoying later, since you can't backfill history that was never recorded.
- [ ] **Gap A9 — "site visitors" (FR8.1) has no data source.** No analytics is specified anywhere in the doc set. Options: a lightweight self-hosted counter, or a third-party analytics tool (which has privacy/consent implications and belongs in `10-deployment-devops.md`). **Until it's resolved, drop the KPI card rather than shipping a fake number.**
- [ ] **Define "conversion rate" precisely** (§9) — a one-line definition in `01-prd.md` prevents a class of trust-destroying bugs.
- [ ] **Gap A1 — no `audit_log`**, so "listing changes" in the activity feed has no clean source. It could be reconstructed from `properties.updated_at`, but that can't tell you *who* changed *what*.
- [ ] **No tenant timezone.** `tenants` has no timezone column, so every date-ranged number is ambiguous.
- [ ] Whether the dashboard is real-time or refresh-on-load. **Refresh-on-load is fine**; a CRM dashboard doesn't need websockets. But escalations are time-sensitive — a polled unread badge on the sidebar may be worth it.
