# Page: Customer Portal — Favorites

> **Route:** `/portal/favorites` · **PRD Module:** 7 (with 4) · **App:** `public-site/` → `pages/CustomerPortal/Favorites`
> Part of [Doc 16 — Customer Spec](README.md). Read [`README.md` §4](README.md#4-cross-cutting-rules-for-every-customer-page) first.
> The favoriting *mechanism* (session vs. account, migration) is specified in [`16-feature-favorites-session.md`](16-feature-favorites-session.md). This file covers the **page** that lists them.

---

## 1. Purpose & Traceability

The shortlist. A buyer's favorites are the properties they're actually deciding between — so this page is really a **comparison surface**, not just a saved list.

| Requirement | Source |
|---|---|
| FR7.1 Dashboard showing saved properties | `01-prd.md` §8 |
| FR4.4 Favorites saved anonymously migrate to the account | `01-prd.md` §5 |
| Data scoped strictly to the logged-in user and tenant | `01-prd.md` §8 acceptance |

---

## 2. Entry & Exit Points

**Entry:** portal nav; the "See all →" link on the [dashboard](07-portal-dashboard.md); the "Sign up to keep this" flow, which lands here after registration to show the visitor their favorite survived.

**Exit:** a card → [Property Details](03-property-details.md). Or "Ask about these" → [lead capture](15-feature-lead-capture.md) with the property list attached.

---

## 3. Layout & Regions

```
┌───────────────┬──────────────────────────────────────────────┐
│ PORTAL NAV    │  Saved properties (4)                        │
│               │                          Sort: [ Recent ▾ ]  │
│   Overview    │                                              │
│ ▸ Favorites 4 │  ┌────────────────────────────────────────┐  │
│   Requirements│  │ ┌────┐ Sunview Residences         ♥   │  │
│   Inquiries   │  │ │img │ ₹78,00,000 · 3BHK · 1,200sqft  │  │
│   Notifications│ │ └────┘ Whitefield        [Published]   │  │
│               │  │        Saved 3 days ago                │  │
│               │  │        [ Ask about this ]  [ Remove ]  │  │
│               │  └────────────────────────────────────────┘  │
│               │  ┌────────────────────────────────────────┐  │
│               │  │ ┌────┐ Palm Grove Villa           ♥   │  │
│               │  │ │img │ ₹1,20,00,000 · 4BHK            │  │
│               │  │ └────┘             [ Sold ] ← greyed   │  │
│               │  │        No longer available             │  │
│               │  └────────────────────────────────────────┘  │
│               │                                              │
│               │       [ Compare selected ]  (see §11)        │
└───────────────┴──────────────────────────────────────────────┘
```

| Region | Contents |
|---|---|
| Header | Count + sort (Recently saved / Price ↑ / Price ↓) |
| Favorite row | Larger than a grid card — this is a considered list, not a browse grid. Shows price, key specs, status badge, saved date |
| Per-row actions | **Ask about this** (creates a lead with `property_id`) and **Remove** |
| Unavailable rows | Greyed, badge shows Sold/On Hold, actions replaced with "See similar" |

---

## 4. Workflow

```
Customer opens /portal/favorites
   │
   ▼
GET /portal/favorites  → list of saved properties (with current status)
   │
   ├─→ Clicks a card → /property/:id
   │
   ├─→ Clicks ♥ / Remove
   │        │
   │        ▼
   │   Optimistic removal (row fades out immediately)
   │   DELETE /properties/{id}/favorite
   │        │
   │        ├─ success → done
   │        └─ failure → row returns + "Couldn't remove that" toast
   │                     (never leave the UI lying about the server state)
   │
   ├─→ Clicks "Ask about this"
   │        │
   │        ▼
   │   Lead-capture modal, pre-filled from the user's profile
   │   → POST /leads { property_id, source: "contact_form" }
   │   → the inquiry appears in /portal/inquiries
   │
   └─→ Changes sort → client-side re-sort (the list is small; no re-query)
```

---

## 5. States

| State | Behavior |
|---|---|
| Loading | 2–3 skeleton rows |
| **Empty** | The default state for most new accounts. "Nothing saved yet — tap the ♥ on any listing to keep it here." + a prominent **Browse properties** button. This empty state gets real design attention; it's seen more often than the populated one |
| Just migrated (post-registration) | A one-time confirmation banner: "Your 2 saved properties are now in your account." This closes the loop on the promise that got them to register |
| Property no longer published | Row is greyed, marked "No longer available", kept in the list. **Do not silently delete it** — the customer saved it deliberately |
| Property sold | Same, badge = Sold, with a "See similar" action |
| Removal failed | Row restored + error toast |

---

## 6. API Calls

| Trigger | Call | Notes |
|---|---|---|
| Mount | `GET /portal/favorites` | Auth required. `04-api-spec.md` §6 |
| Remove | `DELETE /properties/{id}/favorite` | Same endpoint the public pages use; resolves the user from the JWT |
| Ask about this | `POST /leads` | With `property_id` |

---

## 7. Data Touched

| Table | Access |
|---|---|
| `favorites` | Read / Delete (where `user_id = me` **and** `tenant_id = domain tenant`) |
| `properties` | Read (join — including status, so sold/unpublished can be shown correctly) |
| `property_media` | Read (thumbnails) |
| `leads` | Write ("Ask about this") |

---

## 8. Permissions & Tenancy

- Auth required. Both `user_id = me` **and** `tenant_id` filters apply (see [dashboard](07-portal-dashboard.md) §8 — user isolation within a tenant is an app-layer job).
- `DELETE /properties/{id}/favorite` must verify the favorite **belongs to the caller**. Deleting by `property_id` alone, without scoping to the caller's `user_id`/`session_id`, would let one user delete another's favorite. Not theoretical — it's the obvious implementation and it's wrong.

---

## 9. Validation & Edge Cases

- **Favoriting the same property twice** (e.g. once anonymously, again after login): `favorites` needs a uniqueness constraint on `(tenant_id, property_id, coalesce(user_id, session_id))`, or migration will produce duplicate rows. The schema does not currently define one — see §11.
- **A favorite whose property was hard-deleted:** shouldn't happen (properties are soft-deleted), but the join must tolerate it rather than dropping a row silently.
- **Large lists:** paginate at 20. Most users will have <10.
- **Removal is not undoable** in MVP; a brief "Removed — Undo" toast is cheap and prevents a mis-tap from destroying a shortlist. Recommended.

---

## 10. Acceptance Criteria

| ID | Case | Source |
|---|---|---|
| — | Favoriting anonymously → registering → the favorite appears here | FR4.4, `13-ui-ux-flows.md` §2.1 |
| — | Data is scoped to the logged-in user and tenant | FR7.1 acceptance |
| — | Customer A cannot delete Customer B's favorite by property ID | Security test |
| TC-TENANT-02 | A cross-tenant property can never be favorited or listed here | Sprint 1 |

---

## 11. Open Questions

- [ ] **Uniqueness constraint on `favorites`** is not defined in `03-database-schema.md`. Without it, the session→account migration will create duplicates. Add it.
- [ ] Whether a **compare view** (side-by-side spec table of 2–3 favorites) is in scope. It's the natural next step for this page and a genuine differentiator for buyers, but it's in **no PRD module** — so it needs to be scoped in `01-prd.md` before it can be built.
- [ ] Whether removing a favorite should be undoable (recommended) — a soft `deleted_at` on `favorites` would support it, but the schema has no such column on this table.
