# Page: Customer Portal — My Inquiries

> **Route:** `/portal/inquiries` · **PRD Module:** 7 · **App:** `public-site/` → `pages/CustomerPortal/Inquiries`
> Part of [Doc 16 — Customer Spec](README.md). Read [`README.md` §4](README.md#4-cross-cutting-rules-for-every-customer-page) first.

---

## 1. Purpose & Traceability

The customer-side mirror of the admin's lead pipeline. It answers: *"I asked about a property — did anyone actually see it?"*

This page is the **only place the CRM's internal state is exposed to the person it's about**, which makes it the most sensitive translation job in the customer surface. Get the vocabulary wrong here and you tell a buyer they've been categorised as `closed_lost`.

| Requirement | Source |
|---|---|
| FR7.1 Dashboard showing inquiry history | `01-prd.md` §8 |
| FR6.4 Every lead has a traceable source | `01-prd.md` §7 |
| Data scoped strictly to the logged-in user and tenant | `01-prd.md` §8 acceptance |

---

## 2. Entry & Exit Points

**Entry:** portal nav; "See all →" from the [dashboard](07-portal-dashboard.md); an "an agent replied" notification; a post-inquiry confirmation link ("track this inquiry").

**Exit:** the related property → [Property Details](03-property-details.md). Or "follow up" → a new message on the existing inquiry.

---

## 3. Layout & Regions

```
┌───────────────┬──────────────────────────────────────────────┐
│ PORTAL NAV    │  My inquiries (2)                            │
│               │                                              │
│   Overview    │  ┌────────────────────────────────────────┐  │
│   Favorites   │  │ ┌───┐ Sunview Residences               │  │
│   Requirements│  │ │img│ ₹78,00,000 · 3BHK · Whitefield   │  │
│ ▸ Inquiries 2 │  │ └───┘                                  │  │
│   Notifications│ │                                        │  │
│               │  │  Status:  [ ● An agent is on it ]      │  │
│               │  │  Sent:    12 Jul 2026                  │  │
│               │  │  Via:     Property page                │  │
│               │  │                                        │  │
│               │  │  Your message:                         │  │
│               │  │  "Is this available for a Nov move-in?"│  │
│               │  │                                        │  │
│               │  │  ── Timeline ──────────────────────    │  │
│               │  │  ● 12 Jul  Inquiry received            │  │
│               │  │  ● 13 Jul  Anjali picked this up       │  │
│               │  │  ○          Site visit                 │  │
│               │  │                                        │  │
│               │  │  [ Send a follow-up ]  [ View property]│  │
│               │  └────────────────────────────────────────┘  │
│               │  ┌────────────────────────────────────────┐  │
│               │  │ Palm Grove Villa   [ ● Received ]      │  │
│               │  └────────────────────────────────────────┘  │
└───────────────┴──────────────────────────────────────────────┘
```

| Region | Contents |
|---|---|
| Inquiry card | The property (if any), the customer's own message, when it was sent, and how (source) |
| Status pill | The **translated** stage — see §5. Never the raw enum |
| Timeline | Derived from `lead_activities` stage changes — but heavily filtered (§9) |
| Actions | "Send a follow-up" (appends a message), "View property" |

---

## 4. Workflow

```
Customer opens /portal/inquiries
   │
   ▼
GET /portal/inquiries  → their leads + current stage + property
   │
   ▼
Cards render, newest first
   │
   ├─→ Clicks "View property"  → /property/:id
   │
   ├─→ Clicks "Send a follow-up"
   │        │
   │        ▼
   │   Message box → submits
   │        │
   │        ▼
   │   ⚠ NO ENDPOINT EXISTS for a customer to append to a lead.
   │     POST /admin/leads/{id}/notes is admin-only and must stay that way.
   │     See §11 — this needs to be specified before the action can ship.
   │     Interim: the button opens the standard lead-capture form and
   │     creates a NEW lead referencing the same property (ugly but honest),
   │     or the button is hidden for MVP.
   │
   └─→ Agent moves the lead in the admin pipeline
            │
            ▼
       Status pill here updates on the customer's next load
       (no realtime push in MVP)
```

---

## 5. States & the Stage Translation

**This table is the most important content on this page.** The `leads.stage` enum is written by and for agents. It must be translated before it ever reaches a customer.

| `leads.stage` (internal) | Shown to the customer | Rationale |
|---|---|---|
| `new` | **Received** | Honest, non-committal |
| `contacted` | **An agent is on it** | The agent has reached out |
| `site_visit_scheduled` | **Visit scheduled** | Factual |
| `negotiation` | **In discussion** | Never say "negotiation" — it frames the relationship adversarially |
| `closed_won` | **Completed** | |
| `closed_lost` | **Closed** | **Never** "Lost". And never explain *why* — the agent's reason is internal |

| State | Behavior |
|---|---|
| Loading | Skeleton cards |
| **Empty** | "You haven't asked about anything yet." + Browse properties CTA |
| Inquiry with no property (general contact form) | Card renders without the property block — the message is the content |
| Property since sold/unpublished | Show it, greyed, with "This property is no longer available" |
| Lead was soft-deleted by an admin | **Do not show it.** But also don't 404 the page — filter it out |
| Long agent silence | If a lead has sat in `new` for >N days, the copy should not pretend progress. Consider surfacing "Still waiting? Contact us directly" rather than a stale "Received" |

---

## 6. API Calls

| Trigger | Call | Notes |
|---|---|---|
| Mount | `GET /portal/inquiries` | Returns the customer's leads and their status. `04-api-spec.md` §6 |
| View property | *(navigation only)* | |
| Send a follow-up | *(none exists)* | See §11 |

---

## 7. Data Touched

| Table | Access |
|---|---|
| `leads` | Read — **the rows belonging to this customer** (see §8 — this linkage does not currently exist) |
| `lead_activities` | Read (stage-change timeline) |
| `properties`, `property_media` | Read (the inquired-about property) |
| `lead_notes` | **Must NOT be exposed.** These are internal agent notes ("lowball offer, not serious"). They are not customer-visible under any circumstance |

---

## 8. Permissions & Tenancy — ⚠ Blocking Gap

**`leads` has no `user_id` column.** (`03-database-schema.md` §3.7: `id`, `tenant_id`, `property_id`, `customer_name`, `customer_phone`, `customer_email`, `source`, `stage`, `assigned_agent_id`, timestamps.)

So there is **no reliable way to answer "which leads belong to this logged-in customer?"** — which is the entire premise of this page (FR7.1).

The available workarounds are all bad:

| Approach | Why it fails |
|---|---|
| Match on `customer_email` | `customer_email` is **nullable** (phone is the required field). And a visitor can type *any* email into an anonymous form — including someone else's. **Matching leads to accounts by email is a data-leak vector**: register with `victim@example.com`, and you'd be shown their inquiries. |
| Match on `customer_phone` | Same problem, unverified input. |
| Match on `session_id` | `leads` has no `session_id` either. |

**The fix is a schema change:** add `user_id UUID NULL REFERENCES users(id)` and `session_id text NULL` to `leads`, set on creation, and migrated on registration exactly like `favorites` (`08-auth-roles-spec.md` §4). Then this page filters on `user_id = me`, and the ownership question has an actual answer.

**This must be resolved in `03-database-schema.md` before Sprint 4 (lead capture).** Retrofitting ownership onto leads after they exist in production is significantly worse.

Other rules:
- `lead_notes` and internal `lead_activities` metadata (who the agent is, why it was lost) are **never** returned by `/portal/inquiries`. The response schema for the portal must be a separate Pydantic `LeadOut` variant from the admin one — do not reuse the admin schema and hope the frontend hides the fields (`.claude/rules/backend.md`: never reuse one schema when the shapes differ).

---

## 9. Validation & Edge Cases

- **The timeline must be filtered, not dumped.** `lead_activities` records every stage change including reversals (an agent moving a lead back from `negotiation` to `contacted`). Showing a customer that their inquiry went *backwards* is confusing and unflattering. Show forward progress and current state only.
- **Agent identity:** showing "Anjali picked this up" is good for trust, but exposes staff names. Show first name only, never email/phone/role — and confirm with the tenant that they want agent names public at all.
- **A customer inquires about the same property twice:** both leads show. Consider grouping by `property_id`.
- **Anonymous inquiry, later registration:** the lead should appear here after registering (that's the whole point of the migration) — impossible today, per §8.

---

## 10. Acceptance Criteria

| ID | Case | Source |
|---|---|---|
| TC-LEAD-01 | An inquiry submitted anonymously, then followed by registration, appears in the customer's inquiry list | FR7.1 (**blocked by §8**) |
| TC-LEAD-03 | Stage changes made by an agent are reflected in the customer's status | Sprint 4 |
| — | Internal `lead_notes` never appear in any customer-facing response | Security test |
| — | Customer A cannot read Customer B's inquiries — including by lead ID | Security test |

---

## 11. Open Questions

- [ ] **BLOCKING — leads have no owner.** `leads` needs `user_id` + `session_id` (see §8). Nothing on this page is correct or safe until that's decided. Fix `03-database-schema.md` first.
- [ ] **No customer follow-up endpoint.** FR7.1 implies a customer can track an inquiry, but the "send a follow-up" action has no API. Options: a `POST /portal/inquiries/{id}/message` (needs adding to `04-api-spec.md`), or drop the action for MVP and route follow-ups through the chatbot instead — which is arguably the better product answer, since the bot can already escalate to the assigned agent.
- [ ] Whether the customer sees the assigned agent's name at all (tenant preference — some brokerages won't want it).
- [ ] Whether stage changes push a notification (FR3.4 covers new *matches*, not inquiry updates). Ties to **Gap G1**.
