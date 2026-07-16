# Page: Property Management — List

> **Route:** `/admin/properties` · **PRD Module:** 9 · **App:** `admin-portal/` → `pages/Properties/`
> Part of [Doc 17 — Admin Spec](README.md). Read [`README.md` §4](README.md#4-cross-cutting-rules-for-every-admin-page) first.

---

## 1. Purpose & Traceability

The inventory table. Unlike the public [Property Listing](../16-customer-spec/02-property-listing.md) — which is a *browsing* surface for buyers — this is an **operational** surface: dense, sortable, bulk-actionable, and it shows every status including drafts.

| Requirement | Source |
|---|---|
| FR9.1 CRUD for listings with media | `01-prd.md` §10 |
| FR9.2 Bulk upload (CSV/Excel) | `01-prd.md` §10 → [05](05-property-bulk-upload.md) |
| FR9.3 Approval workflow: Draft → Pending Approval → Published | `01-prd.md` §10 → [06](06-property-approvals-status.md) |
| FR9.4 Status flags: Featured, Sold, On Hold, Archived | `01-prd.md` §10 |
| FR9.5 On save, content is embedded/indexed for AI Search | `01-prd.md` §10 |
| Screen workflow | `14-screen-workflows.md` §7 |

---

## 2. Entry & Exit Points

**Entry:** sidebar; the "Total listings" / "3 pending approval" KPI card on the [Dashboard](02-dashboard.md); a deep link from the activity feed.

**Exit:** [Add/Edit](04-property-add-edit.md); [Bulk upload](05-property-bulk-upload.md); the public property page (a "View live →" link — an admin should be able to see exactly what a buyer sees, in one click).

---

## 3. Layout & Regions

```
┌──────────┬────────────────────────────────────────────────────────────┐
│ SIDEBAR  │  Properties (142)      [ Bulk upload ]  [ + Add property ] │
│          │                                                            │
│ Dashboard│  [ Search title/location…    ]  Status:[All ▾] Type:[All ▾]│
│▸Properties  Agent:[All ▾]                                             │
│  Leads   │                                                            │
│  Agents  │  ┌──────────────────────────────────────────────────────┐  │
│  ...     │  │ ☐ │ Property         │ Price │ Status    │ Agent │⋯ │  │
│          │  ├──────────────────────────────────────────────────────┤  │
│          │  │ ☑ │ ▪ Sunview Res.   │ ₹78L  │[Published]│ Anjali│⋯ │  │
│          │  │   │   3BHK · W'field │       │  ★featured│       │  │  │
│          │  ├──────────────────────────────────────────────────────┤  │
│          │  │ ☑ │ ▪ Palm Grove     │ ₹1.2Cr│[Pending]  │ Ravi  │⋯ │  │
│          │  ├──────────────────────────────────────────────────────┤  │
│          │  │ ☐ │ ▪ Lake View Plot │ ₹45L  │[Draft]    │  —    │⋯ │  │
│          │  ├──────────────────────────────────────────────────────┤  │
│          │  │ ☐ │ ▪ Green Acres    │ ₹92L  │[Sold]     │ Anjali│⋯ │  │
│          │  └──────────────────────────────────────────────────────┘  │
│          │                                                            │
│          │  ┌── 2 selected ───────────────────────────────────────┐   │
│          │  │ [Approve] [Feature] [Archive] [Assign agent] [×]    │   │  ← bulk bar,
│          │  └─────────────────────────────────────────────────────┘   │    appears on
│          │                                     ‹ 1 2 3 … 8 ›          │    selection
└──────────┴────────────────────────────────────────────────────────────┘
```

| Region | Contents |
|---|---|
| Search | Title / location, debounced |
| Filters | Status, type, agent. **Status is the one that matters** — "show me everything pending approval" is the daily query |
| Table | Thumbnail, title + specs, price, status badge, assigned agent, row menu |
| Status badge | Colors per `DESIGN.md` → **Semantic Status Colors** — Draft `neutral-container`, Pending Approval `warning-container`, Published `success-container`, Sold `inverse-surface`, Rejected `error-container`, Archived muted |
| Bulk bar | Appears on selection (FR9.1, FR9.4) — see §9 on confirmation |
| Row menu (⋯) | Edit · View live · Duplicate · Change status · Archive |

---

## 4. Workflow

```
Admin arrives at the property list
   │
   ▼
GET /admin/properties  → ALL statuses, including drafts
   │   (unlike the public GET /properties, which is published-only)
   ▼
Table renders
   │
   ├─→ Searches / filters → re-query (URL params, so the view is shareable)
   │
   ├─→ Clicks a row → /admin/properties/:id/edit
   │
   ├─→ Row menu → Change status → PATCH /admin/properties/{id}/status
   │
   ├─→ Selects rows → bulk bar appears
   │        │
   │        ├─ Approve  → POST /admin/properties/{id}/approve  (per row)
   │        ├─ Feature  → PATCH .../status
   │        ├─ Archive  → PATCH .../status   ← DESTRUCTIVE-ISH. Confirm. (§9)
   │        └─ Assign   → PATCH ... agent    (⚠ no bulk endpoint exists — §11)
   │
   └─→ [+ Add property] → the multi-step form  → [04]

When a property becomes `published` (from here or the form):
   │
   ▼
Background job: generate the embedding + index it   (06-ai-search-spec.md §4.2)
   │                                                          [FR9.5]
   ▼
Match it against saved requirement_profiles  (07-ai-recommendation-spec.md §6)
   │
   ▼
Notify matching customers                                    [FR3.4]
   │   ⚠ batch these — a bulk upload of 200 properties must not
   │      fire 200 notifications per customer
   │      (16-customer-spec/11 §9)
   ▼
The property is now searchable, recommendable, and visible on the public site
```

**Publishing is not a status flip — it's an event with three consequences** (index, match, notify). Every path that publishes (this list, the form, bulk upload, approval) must trigger the same pipeline. Implement it **once** in the service layer, or the three paths will drift and "why isn't my property showing in search?" becomes a recurring support ticket.

---

## 5. States

| State | Behavior |
|---|---|
| Loading | Skeleton rows |
| **Empty (new tenant)** | The day-one state. A real onboarding: "Add your first property" + "Bulk upload from a spreadsheet" side by side. Most tenants arrive with existing inventory in a spreadsheet — **lead with bulk upload**, don't bury it |
| Empty (filters too narrow) | "No properties match" + Clear filters |
| Bulk action in progress | Progress indicator; the table locks. A 50-row bulk approve is not instant |
| Bulk action partial failure | **Show which rows failed and why.** "3 of 5 approved" with per-row reasons — never a generic "Some items failed" |
| Property with no images | Placeholder thumbnail. Flag it — a published property with no photos will not convert, and the admin should be told |
| Indexing in progress | A published property whose embedding hasn't generated yet is **live but not searchable**. That window should be visible ("Indexing…") rather than silently confusing |
| `agent` role | Read + limited update on properties (`08-auth-roles-spec.md` §5.1). No bulk actions, no Add, no Archive. See §8 |

---

## 6. API Calls

| Trigger | Call | Notes |
|---|---|---|
| Mount / filter | `GET /admin/properties` | All statuses incl. drafts. `04-api-spec.md` §8 |
| Row → status change | `PATCH /admin/properties/{id}/status` | Featured / Sold / On Hold / Archived (FR9.4) |
| Row / bulk → approve | `POST /admin/properties/{id}/approve` | FR9.3 |
| Row → soft delete | `DELETE /admin/properties/{id}` | Soft delete (`deleted_at`) |
| Bulk anything | *(no bulk endpoints exist)* | The client loops per-row. **Fine at 5 rows, bad at 200** — see §11 |

---

## 7. Data Touched

| Table | Access |
|---|---|
| `properties` | Read / Update (status) / Soft delete |
| `property_media` | Read (thumbnails) |
| `property_embeddings` | Write (regenerated on publish/content change — FR9.5) |
| `users` | Read (assigned agent names) |
| `requirement_profiles` / `requirement_matches` | Read/Write (match-on-publish) |
| *`audit_log`* | Should record every status change — **doesn't exist (A1)** |

---

## 8. Roles & Permissions

| Action | `agent` | `admin` | `super_admin` |
|---|---|---|---|
| View the list | ✅ | ✅ | ✅ |
| Create a property | ⚠ open — see §11 | ✅ | ✅ |
| Edit a property | ⚠ "limited update (assigned)" | ✅ | ✅ |
| Approve | ❌ | ✅ | ✅ |
| Change status / Feature | ❌ | ✅ | ✅ |
| Archive / delete | ❌ | ✅ | ✅ |
| Bulk actions | ❌ | ✅ | ✅ |

**The agent scope is genuinely unresolved.** `08-auth-roles-spec.md` §5.1 says "Read + limited update (assigned)" and §6 flags the exact rules as an open question. And **`properties` has no `created_by` column (Gap A7)** — only `agent_id` (the assigned agent). So "properties an agent created" is not expressible in the current schema. Until this is decided, the safe default is: **agents get read-only on properties**, and the UI hides every mutating control while the API returns 403 regardless.

---

## 9. Validation & Edge Cases

- **Bulk actions need confirmation.** Archiving 40 listings in one click, with no confirm step, is a support incident waiting to happen. `14-screen-workflows.md` §10 flags this as open — **the answer is yes, confirm, and name the count**: "Archive 40 properties?" Approve is safe enough to skip confirmation; Archive and Delete are not.
- **Deleting a property with active leads:** the leads reference `property_id`. Soft delete keeps the FK valid — this is exactly why hard deletes are banned (`.claude/rules/database.md`). The lead's history must survive the listing.
- **Un-publishing a live property** with pending inquiries: allowed, but warn ("3 open leads reference this listing").
- **The embedding must regenerate on a *content* change** (title, description, amenities, location), not only on publish. An admin who fixes a typo in the description and finds search results unchanged has hit a stale-index bug that is very hard to notice and very easy to introduce (FR9.5).
- **Archived properties must leave the search index.** Otherwise the AI keeps recommending a listing the buyer can't see. The de-index path is as important as the index path and is easier to forget.
- **Concurrent edits:** two admins editing the same listing — last write wins, silently. Acceptable for MVP; worth an `updated_at` check if it bites.

---

## 10. Acceptance Criteria

| ID | Case | Source |
|---|---|---|
| TC-PROP-01 | CRUD works; a created property appears in the list | Sprint 2 |
| TC-PROP-02 | The approval workflow moves Draft → Pending → Published correctly | Sprint 2 |
| TC-PROP-03 | Status flags (Featured/Sold/On Hold/Archived) apply and are reflected publicly | Sprint 2 |
| TC-SEARCH-* | **A newly published property becomes searchable within the sync window** (FR9.5) | Sprint 5 |
| TC-TENANT-01 | An admin sees only their own tenant's properties | Sprint 1 |
| TC-ROLE-01 | An agent calling `POST /admin/properties/{id}/approve` gets a 403 | Sprint 8 |

---

## 11. Open Questions

- [ ] **Gap A7 — `properties` has no `created_by`**, so agent ownership-scoping (`08-auth-roles-spec.md` §6) can't be expressed. Add the column, or settle on "agents are read-only on properties."
- [ ] **No bulk endpoints.** `04-api-spec.md` §8 offers only per-ID operations, so a 200-row bulk approve is 200 HTTP calls. Add `POST /admin/properties/bulk-status` / `bulk-approve` to the spec — or accept the loop and cap the selection size.
- [ ] **Bulk-action confirmation** — flagged open in `14-screen-workflows.md` §10. Recommend: confirm on Archive/Delete, not on Approve/Feature.
- [ ] **Is approval required per tenant?** FR9.3 says the approval step is "configurable per tenant whether approval is required" — but `tenants` has no such column and `ai_config` isn't the right home. Where does that flag live? See [06](06-property-approvals-status.md).
- [ ] Whether "Duplicate listing" is in scope. It isn't in the PRD, but for an agent listing 12 near-identical flats in one building it's the difference between an hour and a day. Would need scoping in `01-prd.md` first.
