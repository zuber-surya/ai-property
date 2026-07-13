# Page: Property — Add / Edit (Multi-Step Form)

> **Routes:** `/admin/properties/new`, `/admin/properties/:id/edit` · **PRD Module:** 9 · **App:** `admin-portal/` → `pages/Properties/PropertyForm`
> Part of [Doc 17 — Admin Spec](README.md). Read [`README.md` §4](README.md#4-cross-cutting-rules-for-every-admin-page) first.

---

## 1. Purpose & Traceability

Where inventory is created. This form's output feeds **everything**: the public listing page, the AI search index, the recommendation engine, and the chatbot's factual answers. A weak description here degrades all three AI features — the embedding is only as good as the text it's built from.

That's the thing to internalize: **this form is the training input for the product's USP.** Design it to elicit good text, not just valid text.

| Requirement | Source |
|---|---|
| FR9.1 CRUD with media (photos, video, floor plans, documents) | `01-prd.md` §10 |
| FR9.3 Draft → Pending Approval → Published | `01-prd.md` §10 |
| FR9.5 On save, content is embedded/indexed for AI Search | `01-prd.md` §10 |
| Screen workflow | `14-screen-workflows.md` §7 |

---

## 2. Entry & Exit Points

**Entry:** "+ Add property" on the [list](03-properties-list.md); a row click (edit); "Fix errors" from a [bulk upload](05-property-bulk-upload.md) row; a rejected-approval notification.

**Exit:** Save as Draft (→ back to the list) · Submit (→ Pending or Published, per tenant config) · Cancel (→ **confirm if dirty**).

---

## 3. Layout & Regions

```
┌──────────┬─────────────────────────────────────────────────────────┐
│ SIDEBAR  │  ← Properties                          [Save as draft]  │
│          │                                                         │
│          │  ●━━━━━●━━━━━●━━━━━○━━━━━○                              │
│          │  Basic  Media  Pricing Amenities Location               │
│          │                                                         │
│          │  ┌───────────────── PRICING ─────────────────────────┐  │
│          │  │                                                   │  │
│          │  │  Listing type *      ( ) For sale  (•) For rent   │  │
│          │  │                                                   │  │
│          │  │  Price *                                          │  │
│          │  │  [ ₹ 78,00,000            ]  ₹6,500 / sqft        │  │
│          │  │                             ↑ auto-computed       │  │
│          │  │  Area (sqft) *                                    │  │
│          │  │  [ 1,200                  ]                       │  │
│          │  │                                                   │  │
│          │  │  Bedrooms      Bathrooms                          │  │
│          │  │  [ 3      ▾]   [ 2      ▾]                        │  │
│          │  │                                                   │  │
│          │  └───────────────────────────────────────────────────┘  │
│          │                                                         │
│          │  [ ← Back ]                             [ Next → ]      │
│          │                                                         │
│          │  ⚠ Unsaved changes  ·  Draft autosaved 30s ago          │
└──────────┴─────────────────────────────────────────────────────────┘
```

### 3.1 The Five Steps

| Step | Fields | Table columns |
|---|---|---|
| **1. Basic info** | Title*, description*, property type*, assigned agent | `title`, `description`, `property_type`, `agent_id` |
| **2. Media** | Photos (drag-drop, reorderable), video, floor plan, documents | `property_media` (`media_type`, `url`, `sort_order`) |
| **3. Pricing** | Listing type*, price*, area*, bedrooms, bathrooms | `listing_type`, `price`, `area_sqft`, `bedrooms`, `bathrooms` |
| **4. Amenities** | Multi-select from the **canonical amenity vocabulary** | `amenities` (jsonb) |
| **5. Location** | Address*, map pin (lat/lng) | `location_address`, `location_lat`, `location_lng` |

**The description field deserves special treatment.** It is the primary input to the embedding (FR9.5). A three-word description produces a useless vector, and the AI search will quietly underperform for that listing forever. Show a character-count guide, a "what makes a good description" hint, and — worth considering — a quality warning below a threshold.

---

## 4. Workflow

```
Admin clicks "+ Add property"
   │
   ▼
Step 1 (Basic) → 2 (Media) → 3 (Pricing) → 4 (Amenities) → 5 (Location)
   │
   │  · "Save as draft" is available at EVERY step (status = draft)
   │  · Back is always available
   │  · Autosave as draft periodically — losing a half-built listing
   │    with 12 uploaded photos to a session timeout is unforgivable
   │
   ▼
Final step → Submit
   │
   ▼
Does the tenant require approval?                              [FR9.3]
   │   ⚠ this flag has no home in the schema — Gap, see §11
   │
   ├─ YES → status = pending_approval
   │          → the property does NOT go live
   │          → it appears in the admin's approval queue    [→ 06]
   │
   └─ NO  → status = published
              │
              ▼
        ┌── THE PUBLISH PIPELINE (the same one from every path) ──┐
        │                                                          │
        │  1. Generate the embedding from title + description      │
        │     + amenities + location  (Titan V2, 1024-dim)         │
        │     → property_embeddings, tagged tenant_id + property_id│
        │                            (06-ai-search-spec.md §4.2)   │
        │                                              [FR9.5]     │
        │  2. Match against saved requirement_profiles             │
        │                       (07-ai-recommendation-spec.md §6)  │
        │  3. Notify matching customers (batched)      [FR3.4]     │
        │                                                          │
        └──────────────────────────────────────────────────────────┘
              │
              ▼
        Live on the public site · searchable · recommendable ·
        answerable by the chatbot
```

**Editing a published property re-runs step 1 of the pipeline** if any embedded field changed (title, description, amenities, location). This is the easiest thing in the whole system to get wrong: the property looks updated everywhere *except* AI search, which silently serves the old vector. It won't throw an error. Nobody will notice for weeks.

---

## 5. States

| State | Behavior |
|---|---|
| New, empty | Step 1, nothing filled |
| Editing | All steps pre-filled; the admin can jump to **any** step (this is not a wizard for a novice — it's a form for a professional. Sequential-only navigation would be actively hostile here) |
| Dirty | "Unsaved changes" indicator; Cancel confirms |
| Autosaving | Quiet "Draft saved" — never a modal |
| Uploading media | Per-file progress. Other fields stay editable — do not block the form on an upload |
| Upload failed | Per-file retry. **Don't lose the other nine photos** because one failed |
| Validation error on submit | Jump to the **first** offending step and focus the field. Never show "some fields are invalid" without saying which |
| Pending approval (editing) | Editable, but the admin should know an edit may reset the approval |
| Published (editing) | A banner: "This listing is live. Changes appear on the public site immediately" |
| Re-indexing after an edit | Show it ("Updating search index…"). The window where the listing is live but stale is real |

---

## 6. API Calls

| Trigger | Call | Notes |
|---|---|---|
| Save draft / submit (new) | `POST /admin/properties` | `04-api-spec.md` §8 |
| Load for edit | `GET /admin/properties/{id}` | Admin view — includes drafts |
| Save (edit) | `PUT /admin/properties/{id}` | |
| Media upload | `POST /admin/properties/{id}/media` | → Supabase Storage; the URL is stored in `property_media` |
| Approve (if pending) | `POST /admin/properties/{id}/approve` | [06](06-property-approvals-status.md) |

**Media upload needs a property ID** — which doesn't exist until the first save. So step 2 (Media) requires the record to already be created. **Create the draft on entering step 1** (or on the first "Next"), so media has something to attach to. Otherwise you need a temp-file staging area, which is a lot of machinery to avoid a draft row.

---

## 7. Data Touched

| Table | Access |
|---|---|
| `properties` | Write |
| `property_media` | Write (each file) |
| `property_embeddings` | Write (on publish / content change) |
| `users` | Read (agent dropdown) |
| `requirement_profiles`, `requirement_matches` | Read/Write (match-on-publish) |
| *`audit_log`* | Should record create/update/publish — **doesn't exist (A1)** |

---

## 8. Roles & Permissions

| Action | `agent` | `admin` | `super_admin` |
|---|---|---|---|
| Create | ⚠ unresolved (see [03](03-properties-list.md) §8) | ✅ | ✅ |
| Edit any property | ❌ | ✅ | ✅ |
| Edit an assigned property | ⚠ "limited update" | ✅ | ✅ |
| Publish directly | ❌ | ✅ | ✅ |
| Submit for approval | ✅ (if they can create) | ✅ | ✅ |

The natural shape is: **agents can draft and submit for approval; only admins can publish.** That's what the approval workflow is *for*. But `08-auth-roles-spec.md` §6 leaves it open, and Gap A7 (no `created_by`) means "an agent's own drafts" isn't expressible today.

---

## 9. Validation & Edge Cases

- **Required:** title, description, property type, listing type, price, area, address. **Optional:** bedrooms/bathrooms (a plot has neither), media, amenities, lat/lng.
- **Cannot publish without media.** A published listing with zero photos will not convert and makes the tenant's site look broken. Block it at submit, or at minimum warn hard.
- **Amenities must come from the canonical vocabulary** shared with the [requirement wizard](../16-customer-spec/04-requirement-wizard.md) and the public filters. Free-text amenities silently break matching: a listing tagged "gymnasium" never matches a wizard asking for "gym". **This vocabulary is not defined anywhere in the doc set** — see §11 and the same flag on the customer side.
- **Price:** positive, sane bounds. Reject `0` (an admin will type it to mean "price on request" — if that's a real need, model it explicitly rather than letting `0` mean something).
- **Area:** positive; used for the per-sqft calculation, so guard the division.
- **Lat/lng:** optional, but without them the property can't appear in map view. Warn.
- **Description quality:** see §3.1. This is a **product** concern, not just validation.
- **Media file limits:** type allowlist (images/video/pdf), size cap, count cap. Uploads go to Supabase Storage — a public bucket URL means anyone with the URL can read the file. For *documents* (which may include ownership papers), that's a real consideration nobody has specified.
- **Losing work:** session expiry, a stray back button, an accidental tab close. Autosave, and warn on unload when dirty.

---

## 10. Acceptance Criteria

| ID | Case | Source |
|---|---|---|
| TC-PROP-01 | A property can be created with media and appears in the list | Sprint 2 |
| TC-PROP-02 | Draft → Pending → Published transitions work | Sprint 2 |
| TC-SEARCH-* | **A newly published property is searchable within the sync window** (FR9.5) | Sprint 5 |
| — | **Editing a published property's description updates its embedding** | FR9.5 (the easy one to miss) |
| TC-REC-* | Publishing a property that matches a saved profile notifies that customer | FR3.4 |
| TC-TENANT-01 | A property is created with the creator's tenant and is invisible to other tenants | Sprint 1 |

---

## 11. Open Questions

- [ ] **The "approval required" flag has no home.** FR9.3 says it's configurable per tenant, but `tenants` has no such column and `ai_config` is the wrong place. Add `requires_property_approval boolean` to `tenants` in `03-database-schema.md`.
- [ ] **The canonical amenity vocabulary is undefined** — and it silently breaks recommendation matching, search filters, and this form's multi-select. It should be a fixed enum/lookup in `03-database-schema.md`. **The single highest-leverage small fix in the doc set.**
- [ ] **Storage access control for property documents.** Supabase Storage buckets are public or signed. Which, and for which media types? Not specified in `02-architecture.md` or `10-deployment-devops.md`.
- [ ] **Is the embedding regenerated on every edit, or only on relevant field changes?** Regenerating on every save costs a Titan call per keystroke-batch; regenerating on none is a correctness bug. Recommend: hash the embedded text and regenerate only when the hash changes.
- [ ] Whether an edit to a published property should re-enter the approval queue (a tenant with approval enabled probably wants it to — otherwise the approval gate is trivially bypassed by publishing something innocuous and then editing it).
