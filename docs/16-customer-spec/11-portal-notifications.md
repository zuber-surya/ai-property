# Page: Customer Portal — Notifications & Preferences

> **Route:** `/portal/notifications` · **PRD Modules:** 7, 15 · **App:** `public-site/` → `pages/CustomerPortal/Notifications`
> Part of [Doc 16 — Customer Spec](README.md). Read [`README.md` §4](README.md#4-cross-cutting-rules-for-every-customer-page) first.

> ## ⚠ This page cannot be built as specified.
> `GET /portal/notifications` and `PUT /portal/notifications/preferences` exist in `04-api-spec.md` §6, and FR7.1/FR7.2 require them — but **`03-database-schema.md` defines no `notifications` table and no preference storage.** The only related table is `notification_rules`, which is the *admin's* event-routing config (PRD Module 15), not a per-customer inbox.
>
> **Gaps G1 and G2 must be closed in `03-database-schema.md` before this page is implemented** (`.claude/rules/workflow.md` — update the doc first, then build). §12 proposes the schema.

---

## 1. Purpose & Traceability

The retention loop. A customer who saved a requirement profile and then never hears from us has no reason to come back. This page — and the emails behind it — are what make FR3.4 ("saved profiles trigger notifications when new matching properties are added") real.

| Requirement | Source |
|---|---|
| FR7.1 Dashboard showing notifications | `01-prd.md` §8 |
| FR7.2 Notification preferences (email/SMS/in-app) for new matches | `01-prd.md` §8 |
| FR3.4 Saved profiles trigger notifications on new matching properties | `01-prd.md` §4 |
| FR15.2 Configurable notification rules (admin side) | `01-prd.md` §16 |

---

## 2. Entry & Exit Points

**Entry:** portal nav (with an unread badge); the "What's new" panel on the [dashboard](07-portal-dashboard.md); a link at the bottom of a notification email ("manage your alerts").

**Exit:** each notification **deep-links to its subject** — a new match → [Property Details](03-property-details.md); an inquiry update → [Inquiries](10-portal-inquiries.md). A notification that doesn't go anywhere is just noise.

---

## 3. Layout & Regions

```
┌───────────────┬──────────────────────────────────────────────┐
│ PORTAL NAV    │  Notifications          [ Mark all as read ] │
│               │                                              │
│   Overview    │  ┌────────────────────────────────────────┐  │
│   Favorites   │  │ ● 2 new homes match your requirements  │  │
│   Requirements│  │   Sunview Residences + 1 more    2h ago│  │
│   Inquiries   │  └────────────────────────────────────────┘  │
│ ▸ Notifications│ ┌────────────────────────────────────────┐  │
│      ● 3      │  │ ● An agent replied to your inquiry     │  │
│               │  │   Sunview Residences             1d ago│  │
│               │  └────────────────────────────────────────┘  │
│               │  ┌────────────────────────────────────────┐  │
│               │  │   Price dropped on a saved property    │  │
│               │  │   Palm Grove Villa · ₹1.2Cr → ₹1.1Cr   │  │
│               │  │                                  4d ago│  │
│               │  └────────────────────────────────────────┘  │
│               │                                              │
│               │  ── PREFERENCES ───────────────────────────  │
│               │                                              │
│               │                  Email   SMS   In-app        │
│               │  New matches      [x]    [ ]    [x]          │
│               │  Inquiry updates  [x]    [ ]    [x]          │
│               │  Price changes    [ ]    [ ]    [x]          │
│               │                                              │
│               │  [ Save preferences ]                        │
└───────────────┴──────────────────────────────────────────────┘
```

| Region | Contents |
|---|---|
| Notification list | Newest first. Unread = a dot + bolder weight. Each row is a link |
| Mark all as read | One click; no confirmation |
| Preferences grid | Event type × channel (FR7.2). **Email/SMS delivery providers have been chosen** (SendGrid for email, Twilio for SMS per 02-architecture.md §3 and 03-database-schema.md §3.21) — see §11 |

### 3.1 Notification Types (proposed — needs PRD confirmation)

| Type | Trigger | Deep-links to |
|---|---|---|
| `new_match` | A newly published property matches a saved requirement profile (FR3.4) | Property Details |
| `inquiry_update` | The agent moved the customer's lead to a new stage | Inquiries |
| `price_change` | A favorited property's price changed | Property Details |
| `property_unavailable` | A favorited property was marked Sold | Favorites |

Only `new_match` is explicitly required by the PRD (FR3.4). The rest are proposals and **must be added to `01-prd.md` before being built** — they are exactly the kind of scope that quietly appears in code without ever being specified.

---

## 4. Workflow

```
Customer opens /portal/notifications
   │
   ▼
GET /portal/notifications  → list (read + unread)
   │
   ▼
List renders; unread count clears from the nav badge
   │
   ├─→ Clicks a notification
   │        │
   │        ▼
   │   Marked read → deep-link to its subject
   │
   ├─→ Mark all as read → all marked, badge clears
   │
   └─→ Changes a preference toggle → [ Save preferences ]
            │
            ▼
       PUT /portal/notifications/preferences

Background — how a notification gets created (FR3.4):

   Admin publishes a property                [→ 17-admin-spec/04]
        │
        ▼
   Property is embedded + indexed             (06-ai-search-spec.md §4.2)
        │
        ▼
   Matched against every saved requirement_profile in the tenant
        │                                     (07-ai-recommendation-spec.md §6)
        ▼
   Above the match threshold?
        │
        ├─ no  → nothing happens
        │
        └─ yes → write requirement_matches row
                     │
                     ▼
                 create a notification for the profile's owner
                     │
                     ▼
                 respect the customer's channel preferences (FR7.2):
                   in-app → always written
                   email  → queued if enabled
                   SMS    → queued if enabled
```

---

## 5. States

| State | Behavior |
|---|---|
| Loading | Skeleton rows |
| **Empty** | "Nothing yet. Save a requirement profile and we'll tell you when something matches." → wizard CTA. Same conversion logic as every other empty portal state |
| All read | List still renders (history has value), just without dots |
| Preferences saving | Button disabled; on success a quiet "Saved" — no modal |
| Email/SMS channel unavailable | **Grey out and disable the toggle with a reason**, rather than letting the customer enable a channel that silently never delivers. A preference that does nothing is worse than an absent one |
| Notification whose subject was deleted | Keep the row, disable the link, mark it "no longer available" |

---

## 6. API Calls

| Trigger | Call | Notes |
|---|---|---|
| Mount | `GET /portal/notifications` | `04-api-spec.md` §6. Backed by `notifications` (`03-database-schema.md` §3.20) |
| Save preferences | `PUT /portal/notifications/preferences` | `04-api-spec.md` §6. Backed by `notification_preferences` (`03-database-schema.md` §3.21) |
| Mark read / mark all read | *(none exists)* | Not in the API spec. Needs adding, or fold into `GET` semantics (bad) |

---

## 7. Data Touched

| Table | Access |
|---|---|
| `notifications` | Read + mark-read (`03-database-schema.md` §3.20). Ownership is per-`user_id`, not per-tenant |
| `notification_preferences` | Read + write (`03-database-schema.md` §3.21). `UNIQUE (user_id, event_type)` |
| `requirement_matches` | Read (the source of `new_match` notifications) |
| `leads`, `lead_activities` | Read (the source of `inquiry_update` notifications) |
| `notification_rules` | **Not this.** This is the *admin's* rule config (Module 15), a different concern with a different owner |

---

## 8. Permissions & Tenancy

- Auth required; scoped to `user_id = me` **and** `tenant_id`.
- **A notification is per-user, not per-tenant.** Its ownership check must be on `user_id` — the same IDOR risk as everywhere else in the portal.
- **Unsubscribe links in emails must work without a login.** That means a signed, single-purpose token in the URL — not a session. Getting this wrong (requiring login to unsubscribe) is a compliance problem, not just a UX one.
- Anonymous sessions get **no** notifications — there's nowhere to send them. This is one of the few things genuinely gated behind registration, and it's the honest reason to register.

---

## 9. Validation & Edge Cases

- **Notification storms:** a tenant bulk-uploads 200 properties (FR9.2) and every one matches Priya's profile → 200 notifications. **Batch by profile per time window** ("12 new homes match your requirements") rather than one per property. This must be designed in, not patched later — the bulk-upload feature makes it inevitable.
- **Duplicate notifications:** re-running a match must not re-notify about a property the customer was already told about. Dedupe on `(profile_id, property_id)`.
- **Deleted requirement profile:** kill its pending notifications ([09-portal-requirements.md](09-portal-requirements.md) §9).
- **Email deliverability:** a real transactional provider (SendGrid) **has been chosen** (02-architecture.md §3 and 03-database-schema.md §3.21). Not missing from `10-deployment-devops.md`.
- **Preference defaults:** new accounts default to in-app + email **on** for `new_match` (it's why they registered) and everything else off. Do not default-enable SMS — it costs money per send and it annoys people.

---

## 10. Acceptance Criteria

| ID | Case | Source |
|---|---|---|
| TC-REC-* | Publishing a property that matches a saved profile produces a notification for that customer | FR3.4 |
| — | The customer's channel preferences are respected on send | FR7.2 |
| — | 200 matching properties published at once produce **one batched** notification, not 200 | §9 |
| — | Customer A never receives a notification about Customer B's profile | Security test |

---

## 11. Open Questions

- [x] ~~**Gap G1** — no `notifications` table.~~ **Closed** — `03-database-schema.md` §3.20 (`GAPS.md` §5).
- [x] ~~**Gap G2** — no preference storage.~~ **Closed** — `03-database-schema.md` §3.21 (`GAPS.md` §5).
- [x] ~~**No email/SMS provider is chosen.**~~ **This was never true** — it is the false gap ~~G9b~~ (`GAPS.md` §5A). Providers were decided 2026-07-13 and are named in `03-database-schema.md` §3.21: email → **SendGrid**, SMS → **Twilio**, in-app → the `notifications` table. All three ship at MVP. ⚠️ Indian SMS needs **DLT registration** — a calendar lead-time item, not an engineering one.
- [ ] Which notification types are actually in scope (§3.1) — only `new_match` is in the PRD today.
- [ ] Whether in-app notifications need realtime push (Supabase Realtime) or poll-on-load is sufficient. **Poll-on-load is sufficient for MVP**; a property alert is not time-critical.

---

## 12. Proposed Schema (for `03-database-schema.md`)

Offered so the gap can be closed quickly. **Add it to the schema doc and an Alembic migration — do not implement from here.**

```
notifications                       (tenant-owned)
  id            UUID PK
  tenant_id     UUID NOT NULL REFERENCES tenants(id)
  user_id       UUID NOT NULL REFERENCES users(id)
  type          text        -- new_match | inquiry_update | price_change | ...
  title         text
  body          text
  entity_type   text        -- property | lead | requirement_profile
  entity_id     UUID        -- deep-link target
  read_at       timestamptz NULL
  created_at    timestamptz DEFAULT now()

notification_preferences            (tenant-owned)
  id            UUID PK
  tenant_id     UUID NOT NULL REFERENCES tenants(id)
  user_id       UUID NOT NULL REFERENCES users(id)
  event_type    text        -- new_match | inquiry_update | ...
  email_enabled boolean DEFAULT true
  sms_enabled   boolean DEFAULT false
  in_app_enabled boolean DEFAULT true
  updated_at    timestamptz DEFAULT now()
  UNIQUE (user_id, event_type)
```

Both are tenant-owned → both need RLS via the standard helper, and both need a cross-tenant-access test (`.claude/rules/database.md`, `rules/security.md`).
