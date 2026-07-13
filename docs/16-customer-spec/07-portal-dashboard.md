# Page: Customer Portal — Dashboard

> **Route:** `/portal` · **PRD Module:** 7 · **App:** `public-site/` → `pages/CustomerPortal/`
> Part of [Doc 16 — Customer Spec](README.md). Read [`README.md` §4](README.md#4-cross-cutting-rules-for-every-customer-page) first.

---

## 1. Purpose & Traceability

The logged-in home. It answers one question: *"what's happened since I was last here?"* — new matches against my requirements, replies to my inquiries, price changes on things I saved.

The portal is an **authenticated view of the public site**, not a separate product (`02-architecture.md` §5.1). Same app, same header, same branding — just more of it.

| Requirement | Source |
|---|---|
| FR7.1 Dashboard: saved properties, requirement profile, inquiry history, notifications | `01-prd.md` §8 |
| FR7.2 Notification preferences | `01-prd.md` §8 |
| FR7.3 Edit/delete saved requirement profile | `01-prd.md` §8 |
| Data is scoped strictly to the logged-in user *and* their tenant | `01-prd.md` §8 acceptance |

---

## 2. Entry & Exit Points

**Entry:** header "My Portal" after login; a post-login redirect; a notification email deep link.

**Exit:** into the four sub-pages ([Favorites](08-portal-favorites.md), [Requirements](09-portal-requirements.md), [Inquiries](10-portal-inquiries.md), [Notifications](11-portal-notifications.md)), or back out to a [Property Details](03-property-details.md) page.

**Guard:** `/portal/*` while logged out → redirect to `/login?next=/portal/...`. Never render a shell with empty data.

---

## 3. Layout & Regions

```
┌──────────────────────────────────────────────────────────────┐
│ HEADER  [logo]              Search  Contact   [Priya ▾]      │
├───────────────┬──────────────────────────────────────────────┤
│ PORTAL NAV    │  Welcome back, Priya.                        │
│               │                                              │
│ ▸ Overview    │  ┌──────── WHAT'S NEW ─────────────────────┐ │
│   Favorites 4 │  │ ● 2 new homes match your requirements   │ │
│   Requirements│  │   → View matches                        │ │
│   Inquiries 2 │  │ ● Agent replied to your inquiry on      │ │
│   Notifications│ │   Sunview Residences                    │ │
│               │  └─────────────────────────────────────────┘ │
│               │                                              │
│               │  SAVED PROPERTIES                 See all →  │
│               │  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐        │
│               │  │  ♥   │ │  ♥   │ │  ♥   │ │  ♥   │        │
│               │  └──────┘ └──────┘ └──────┘ └──────┘        │
│               │                                              │
│               │  MY REQUIREMENTS                    Edit →   │
│               │  ┌─────────────────────────────────────────┐ │
│               │  │ 3BHK apartment · ₹50–80L · Whitefield   │ │
│               │  │ Self-use · within 3 months              │ │
│               │  │ 6 current matches            View →     │ │
│               │  └─────────────────────────────────────────┘ │
│               │                                              │
│               │  RECENT INQUIRIES                 See all →  │
│               │  ┌─────────────────────────────────────────┐ │
│               │  │ Sunview Residences   [Contacted]  2d ago│ │
│               │  │ Palm Grove Villa     [New]        5d ago│ │
│               │  └─────────────────────────────────────────┘ │
└───────────────┴──────────────────────────────────────────────┘

Mobile: portal nav collapses to a horizontal tab strip under the header.
```

| Region | Contents |
|---|---|
| Portal nav | Four sections + counts. Counts are the point — they tell the user where to look |
| What's new | Unread notifications, condensed. The reason this page exists |
| Saved properties | First 4 favorites, newest first → [Favorites](08-portal-favorites.md) |
| My requirements | A plain-language summary of the saved profile + live match count → [Requirements](09-portal-requirements.md) |
| Recent inquiries | Last 2–3 leads with their current **stage** shown as a customer-friendly status → [Inquiries](10-portal-inquiries.md) |

---

## 4. Workflow

```
Logged-in customer lands on /portal
   │
   ├─→ GET /portal/favorites      (first page only)
   ├─→ GET /portal/requirements
   ├─→ GET /portal/inquiries      (first page only)
   └─→ GET /portal/notifications  (unread only)
        │  4 parallel calls; each section renders as its own data lands.
        │  A slow section never blocks the others.
        ▼
Dashboard renders
   │
   ├─→ "View matches"  → /portal/requirements
   ├─→ Clicks a saved property card → /property/:id
   ├─→ Clicks an inquiry row → /portal/inquiries (expanded)
   ├─→ Unfavorites from the card → DELETE /properties/{id}/favorite
   │                                → the card disappears optimistically
   └─→ Notification clicked → marked read → deep-links to its target
```

**No aggregate "dashboard summary" endpoint exists** (unlike the admin side, which has `/admin/dashboard/summary`). This page composes itself from the four portal endpoints. That's fine at this scale and avoids inventing an endpoint that isn't in `04-api-spec.md` — but if the four calls prove slow, add a summary endpoint *to the spec first*.

---

## 5. States

| State | Behavior |
|---|---|
| Loading | Per-section skeletons; the nav and header render immediately |
| **First-time user** (registered, but has nothing saved) | This is the most common state on day one and must be designed, not defaulted. Show a genuine onboarding: "Start by telling us what you're looking for →" (wizard) and "Or browse listings →". Do **not** show three empty boxes |
| No favorites | Section shows a single prompt card linking to `/search` |
| No requirement profile | Section shows the wizard CTA — this is the highest-value empty state on the page |
| No inquiries | Section hidden entirely (an empty "inquiries" box has no value) |
| Nothing new | "What's new" collapses to a quiet "You're all caught up" |
| A section errors | That section shows an inline retry; **the rest of the page still works** |
| Logged out | Redirect to login before any of this renders |

---

## 6. API Calls

| Trigger | Call | Notes |
|---|---|---|
| Mount | `GET /portal/favorites` | `04-api-spec.md` §6 |
| Mount | `GET /portal/requirements` | |
| Mount | `GET /portal/inquiries` | Returns the customer's leads + their current stage |
| Mount | `GET /portal/notifications` | **Gap G1** — no `notifications` table exists to serve this |
| Unfavorite | `DELETE /properties/{id}/favorite` | |

All require `Authorization: Bearer <jwt>`.

---

## 7. Data Touched

| Table | Access |
|---|---|
| `favorites` | Read (where `user_id = me`) |
| `requirement_profiles` | Read |
| `requirement_matches` | Read (match count) |
| `leads` | Read — **only rows belonging to this customer** |
| `properties`, `property_media` | Read (cards) |
| *notifications* | **Table does not exist — Gap G1** |

---

## 8. Permissions & Tenancy

**Two filters, both mandatory:** `tenant_id = <domain tenant>` **AND** `user_id = <authenticated user>`. Tenant scoping alone is not enough here — it would show Priya every *other* customer's favorites within the same tenant.

- The `/portal/*` endpoints must resolve the user from the JWT and filter by `user_id` in the repository layer. RLS gives tenant isolation; **user isolation within a tenant is an application-layer responsibility** and needs its own explicit test.
- **Linking a lead back to a customer is not currently possible.** `leads` has `customer_name`, `customer_phone`, `customer_email` — but **no `user_id` FK**. So `GET /portal/inquiries` has no reliable way to know which leads belong to the logged-in user. Matching on email is fragile (a visitor can inquire with any email; emails are nullable). **This is a blocking schema gap** — see [10-portal-inquiries.md](10-portal-inquiries.md) §11.
- An `agent` or `admin` who logs into the public site sees **their own** customer data here — never elevated visibility. Role does not widen the portal.

---

## 9. Validation & Edge Cases

- **Deleted/unpublished property in favorites:** show the card greyed with "No longer available" rather than 404ing the whole section or silently dropping it. The customer saved it; tell them what happened.
- **Multiple requirement profiles:** the schema allows many per user. The dashboard shows the most recent; the [Requirements page](09-portal-requirements.md) shows all. The UI copy ("My requirements", singular) should not assume there's exactly one.
- **Stale match counts:** the count comes from `requirement_matches`, which is only regenerated when the profile is re-run or a new property is published. It can be stale; don't present it as live.
- **Customer-facing stage names:** never show the raw pipeline stage (`negotiation`, `closed_lost`) to the customer. Map to friendly statuses — see [10-portal-inquiries.md](10-portal-inquiries.md) §5.

---

## 10. Acceptance Criteria

| ID | Case | Source |
|---|---|---|
| TC-AUTH-01 | Only an authenticated customer can load `/portal` | Sprint 1 |
| — | All data shown is scoped to the logged-in user *and* tenant (FR7.1 acceptance) | `01-prd.md` §8 |
| — | Customer A cannot see Customer B's favorites/inquiries within the same tenant | Needs its own test |
| TC-TENANT-01/02 | No cross-tenant data appears | Sprint 1 |

---

## 11. Open Questions

- [ ] **Gap G1/G2:** notifications have no table and preferences have no storage (see [11-portal-notifications.md](11-portal-notifications.md)).
- [ ] **Blocking:** `leads` has no `user_id` — the inquiry history in FR7.1 cannot be built correctly without it.
- [ ] **Gap G4:** "Saved Searches" appears in Raj's persona flow (`13-ui-ux-flows.md` §2.2) and would naturally live on this dashboard, but it exists in no module, table, or endpoint. Either scope it into the PRD or remove it from the persona flow.
- [ ] Whether a `GET /portal/summary` aggregate endpoint is worth adding (4 calls → 1). Defer until measured.
