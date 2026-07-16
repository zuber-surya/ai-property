# Page: Customer Portal — My Requirements

> **Route:** `/portal/requirements` · **PRD Modules:** 7, 3 · **App:** `public-site/` → `pages/CustomerPortal/Requirements`
> Part of [Doc 16 — Customer Spec](README.md). Read [`README.md` §4](README.md#4-cross-cutting-rules-for-every-customer-page) first.

---

## 1. Purpose & Traceability

The saved output of the [Requirement Wizard](04-requirement-wizard.md), plus its live matches. This page is what turns a one-off wizard run into an ongoing relationship: the profile sits here, and when the tenant lists a new matching property, the customer gets told (FR3.4).

| Requirement | Source |
|---|---|
| FR3.3 Registered users can save their requirement profile and revisit/edit it | `01-prd.md` §4 |
| FR3.4 Saved profiles trigger notifications when new matching properties are added | `01-prd.md` §4 |
| FR7.1 Dashboard shows the requirement profile | `01-prd.md` §8 |
| FR7.3 Ability to edit/delete the saved requirement profile | `01-prd.md` §8 |

---

## 2. Entry & Exit Points

**Entry:** portal nav; the "Edit →" / "View matches" links on the [dashboard](07-portal-dashboard.md); a "2 new matches" notification.

**Exit:** a match card → [Property Details](03-property-details.md). Or "Edit" → the [wizard](04-requirement-wizard.md), pre-filled.

---

## 3. Layout & Regions

```
┌───────────────┬──────────────────────────────────────────────┐
│ PORTAL NAV    │  My requirements                             │
│               │                                              │
│   Overview    │  ┌────────────────────────────────────────┐  │
│   Favorites   │  │ WHAT YOU'RE LOOKING FOR      [Edit]    │  │
│ ▸ Requirements│  │                              [Delete]  │  │
│   Inquiries   │  │  Budget      ₹50L – ₹80L               │  │
│   Notifications│ │  Location    Whitefield, Marathahalli  │  │
│               │  │  Type        Apartment                 │  │
│               │  │  Purpose     To live in                │  │
│               │  │  Timeline    Within 3 months           │  │
│               │  │  Must-haves  Parking, Gym              │  │
│               │  │                                        │  │
│               │  │  🔔 Alerts on  — we'll email you when  │  │
│               │  │     a new match is listed.  [Turn off] │  │
│               │  └────────────────────────────────────────┘  │
│               │                                              │
│               │  YOUR MATCHES (6)              Updated 2d ago│
│               │  ┌────────────────────────────────────────┐  │
│               │  │ ┌───┐ Sunview Residences    ★ 92%  NEW │  │
│               │  │ │img│ ₹78,00,000 · 3BHK              ♡ │  │
│               │  │ └───┘ ✓ Budget  ✓ Location  ✗ No gym   │  │
│               │  └────────────────────────────────────────┘  │
│               │  ┌────────────────────────────────────────┐  │
│               │  │ ...                            84%     │  │
│               │  └────────────────────────────────────────┘  │
└───────────────┴──────────────────────────────────────────────┘
```

| Region | Contents |
|---|---|
| Profile summary | The saved answers in plain language — **not** raw enum values (`self_use` → "To live in") |
| Edit / Delete | Edit reopens the wizard pre-filled; Delete removes the profile and its alerts (FR7.3) |
| Alerts toggle | Per-profile notification switch (FR3.4) — stored in `requirement_profiles.alerts_enabled` (`03-database-schema.md` §3.11) |
| Matches | The ranked shortlist, with the same ✓/✗ reason lines as the wizard results. New-since-last-visit matches get a **NEW** flag |
| Updated timestamp | When the matches were last regenerated — honest about staleness |

---

## 4. Workflow

```
Customer opens /portal/requirements
   │
   ▼
GET /portal/requirements  → the saved profile(s)
   │
   ▼
GET /ai/recommend/{requirement_profile_id}  → profile + latest matches
   │
   ▼
Profile + matches render
   │
   ├─→ Clicks a match → /property/:id
   ├─→ Favorites a match → POST /properties/{id}/favorite
   │
   ├─→ Clicks Edit
   │        │
   │        ▼
   │   Wizard opens pre-filled with the saved answers
   │        │
   │        ▼
   │   Re-submit → PUT /ai/recommend/{id}
   │        │       (updates in place — does NOT create a second profile)
   │        ▼
   │   Matches are regenerated → back to this page with fresh results
   │
   ├─→ Clicks Delete → confirm dialog → profile + its alerts removed
   │        │           ⚠ no DELETE endpoint exists yet — Gap G6
   │
   └─→ Toggles alerts → `requirement_profiles.alerts_enabled` (§3.11)
   │        ⚠ no endpoint writes it yet — Gap G8

Background (not on this page — triggered by the admin publishing a property):
   New property published → matched against every saved requirement_profile
   (07-ai-recommendation-spec.md §6) → match written → notification fired [FR3.4]
   → customer sees "2 new homes match your requirements" on next visit
```

---

## 5. States

| State | Behavior |
|---|---|
| Loading | Skeleton for both panels |
| **No profile saved** | The main empty state. A single, well-designed CTA: "Tell us what you're looking for and we'll match you — 5 questions, about a minute." → the wizard. This is the page's highest-value conversion |
| Profile saved, matches exist | The layout above |
| Profile saved, **zero matches** | Never a bare empty state (FR3.2). "Nothing matches exactly right now. We'll alert you the moment something does." + the closest-match list + a nudge to widen budget/location, with the *specific* constraint that's blocking most listings called out if it can be computed |
| Matches stale | "Updated 2 days ago" is shown honestly. Optionally offer a "Refresh matches" action (re-runs `PUT`) |
| Multiple profiles | The schema allows several per user. Render them as stacked cards, each with its own matches. Do **not** silently show only the first |
| Alerts unavailable | Storage exists (`alerts_enabled`, §3.11) but **no endpoint writes it — Gap G8.** Until that lands, hide the toggle rather than shipping a switch that does nothing |

---

## 6. API Calls

| Trigger | Call | Notes |
|---|---|---|
| Mount | `GET /portal/requirements` | Saved profiles for this user. `04-api-spec.md` §6 |
| Mount / expand | `GET /ai/recommend/{requirement_profile_id}` | Profile + latest matches. `04-api-spec.md` §3.3 |
| Edit → resubmit | `PUT /ai/recommend/{requirement_profile_id}` | Updates the profile and regenerates matches |
| Delete | *(none)* | **Gap G6** — FR7.3 requires delete; no endpoint exists. Add to `04-api-spec.md` first |
| Alerts toggle | *(none)* | **Gap G8** — `PUT /portal/notifications/preferences` is per-**event-type** (`04-api-spec.md` §6), not per-profile. Writing `requirement_profiles.alerts_enabled` needs its own endpoint; add it to `04-api-spec.md` first |

---

## 7. Data Touched

| Table | Access |
|---|---|
| `requirement_profiles` | Read / Update / Delete (`user_id = me`) |
| `requirement_matches` | Read |
| `properties`, `property_media` | Read (match cards) |
| `favorites` | Write (favoriting a match) |
| `ai_config` | Read (tenant weights, used when regenerating matches) |

---

## 8. Permissions & Tenancy

- Auth required; both `user_id = me` and `tenant_id` filters apply.
- **`PUT`/`GET`/`DELETE /ai/recommend/{id}` must verify the profile belongs to the caller.** The profile ID is a UUID in the URL — without an ownership check, any authenticated customer could read or overwrite another customer's requirement profile by ID. This is the single most likely IDOR in the customer surface. It needs an explicit test.
- Matches are drawn only from the domain tenant's published properties.

---

## 9. Validation & Edge Cases

- **Edit must update, not duplicate.** Re-running the wizard from this page uses `PUT`, not `POST`. Otherwise a user who tweaks their budget three times ends up with four profiles and four sets of alerts.
- **Deleting a profile must also stop its alerts** and clean up `requirement_matches`, or the customer keeps getting emailed about a profile they deleted — a trust-destroying bug.
- **Tenant changed their `recommendation_weights`** (FR3.5) after the matches were generated: the stored matches are now scored under the old weights. Regenerate on next view, or accept and label the staleness. Don't pretend they're current.
- **A matched property gets sold**: it must drop out of the match list (or show as unavailable) — a customer clicking a "92% match" and finding it sold is worse than not showing it.
- **Enum → human copy:** `self_use`, `3_months`, `closed_won` are database values. Never render them raw.

---

## 10. Acceptance Criteria

| ID | Case | Source |
|---|---|---|
| TC-REC-01 | Saved profile returns its ranked shortlist | Sprint 7 |
| TC-REC-02 | Zero-match profile shows the closest-match fallback, never an empty state | Sprint 7 |
| — | A registered user can revisit and edit their profile (FR3.3) | FR3.3 |
| — | Publishing a new matching property notifies the profile owner (FR3.4) | FR3.4 |
| — | Customer A cannot `GET`/`PUT` Customer B's profile by ID | Security test |

---

## 11. Open Questions

- [ ] **Gap G6:** no delete endpoint for a requirement profile, despite FR7.3 requiring it.
- [x] ~~**Gap G2:** the per-profile alerts toggle has no storage.~~ **Closed** — the store is `requirement_profiles.alerts_enabled` (§3.11), and always was. `notification_preferences` (§3.21) is per-event-type; `notification_rules` (§3.22) is the *admin's* rule table. What is still missing is the **endpoint** → **Gap G8**.
- [ ] Should a customer be allowed **multiple** requirement profiles (the schema permits it) or exactly one (which the singular UI copy in FR7.1/FR7.3 implies)? This changes the UI materially. **Recommend: allow multiple** — "a 3BHK to live in" and "a plot to invest in" are genuinely different searches — but the PRD should say so explicitly.
- [x] ~~How "NEW since last visit" is computed — needs a `last_viewed_at` per profile, which doesn't exist.~~ **It exists:** `requirement_profiles.last_viewed_at` (§3.11), added for exactly this flag.
