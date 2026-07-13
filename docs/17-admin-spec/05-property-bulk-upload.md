# Page: Property Bulk Upload (CSV / Excel)

> **Route:** `/admin/properties/bulk-upload` · **PRD Module:** 9 · **App:** `admin-portal/` → `pages/Properties/BulkUpload`
> Part of [Doc 17 — Admin Spec](README.md). Read [`README.md` §4](README.md#4-cross-cutting-rules-for-every-admin-page) first.

---

## 1. Purpose & Traceability

**This is the onboarding feature.** A new tenant does not arrive with an empty inventory — they arrive with 140 properties in a spreadsheet. If bulk upload doesn't work well, they either never finish onboarding or they hate the product for a week while typing.

It gets its own page because "upload a CSV" is the easy 10%; **validation and error reporting are the other 90%**, and that's what FR9.2 actually requires.

| Requirement | Source |
|---|---|
| FR9.2 Bulk upload via CSV/Excel **with validation and error reporting** | `01-prd.md` §10 |
| FR9.5 On save, listings are embedded/indexed for AI Search | `01-prd.md` §10 |

---

## 2. Entry & Exit Points

**Entry:** the "Bulk upload" button on the [property list](03-properties-list.md); the empty-state onboarding for a new tenant (**this should be the most prominent CTA there**).

**Exit:** back to the property list, with the imported rows visible as drafts. Or into the [add/edit form](04-property-add-edit.md) to fix a single failed row.

---

## 3. Layout & Regions

```
┌──────────┬─────────────────────────────────────────────────────────┐
│ SIDEBAR  │  ← Properties                                           │
│          │                                                         │
│          │  Bulk upload                                            │
│          │                                                         │
│          │  ① Download the template                                │
│          │     [ ⬇ property-template.csv ]                         │
│          │     Column definitions and allowed values included.     │
│          │                                                         │
│          │  ② Upload your file                                     │
│          │     ┌───────────────────────────────────────────────┐   │
│          │     │                                               │   │
│          │     │      Drop a .csv or .xlsx here                │   │
│          │     │      or [ browse ]                            │   │
│          │     │                                               │   │
│          │     └───────────────────────────────────────────────┘   │
│          │                                                         │
│          │  ③ Review                                               │
│          │  ┌─────────────────────────────────────────────────┐    │
│          │  │  142 rows · ✅ 128 valid · ⚠ 14 need attention  │    │
│          │  ├─────────────────────────────────────────────────┤    │
│          │  │ Row │ Title          │ Issue                    │    │
│          │  ├─────────────────────────────────────────────────┤    │
│          │  │  7  │ Palm Grove     │ ⚠ price is not a number: │    │
│          │  │     │                │   "on request"           │    │
│          │  │ 23  │ (empty)        │ ⚠ title is required      │    │
│          │  │ 41  │ Lake View      │ ⚠ unknown amenity:       │    │
│          │  │     │                │   "swiming pool"         │    │
│          │  │     │                │   did you mean           │    │
│          │  │     │                │   "swimming_pool"?       │    │
│          │  └─────────────────────────────────────────────────┘    │
│          │                                                         │
│          │  [ ⬇ Download the 14 failed rows ]                      │
│          │                                                         │
│          │  [ Import the 128 valid rows as drafts ]                │
│          │            ↑ partial import — don't make them fix       │
│          │              14 rows before they get ANY value          │
└──────────┴─────────────────────────────────────────────────────────┘
```

---

## 4. Workflow

```
Admin downloads the template
   │   · a real template: correct headers, one example row, and the
   │     allowed values for property_type / listing_type / amenities.
   │     Half of all import errors are prevented right here.
   ▼
Uploads a filled .csv / .xlsx
   │
   ▼
POST /admin/properties/bulk-upload
   │
   │   Backend:
   │     1. Parse (CSV and Excel — Excel is what they actually have)
   │     2. Validate EVERY row. Do not stop at the first error.
   │     3. Return a per-row result: valid | error(reason, column)
   │
   ▼
Review screen: N valid, M failed, with per-row reasons        [FR9.2]
   │
   ├─→ [ Download the failed rows ]
   │      A CSV containing ONLY the failed rows, plus an `error` column.
   │      They fix it in Excel — where they already live — and re-upload
   │      just that file. This one detail is the difference between a
   │      feature people use and a feature people give up on.
   │
   ▼
[ Import the valid rows ]
   │
   ▼
Rows are created as DRAFTS (never published directly)
   │   · Nobody should be able to push 142 unreviewed listings live
   │     from a spreadsheet in one click. Draft is the safe landing.
   ▼
Admin reviews in the property list → publishes (individually or in bulk)
   │
   ▼
On publish, EACH property runs the publish pipeline:           [FR9.5]
   embed → index → match against requirement_profiles → notify
   │
   ▼
   ⚠ 128 properties published at once = a notification storm.
     Batch per customer ("12 new homes match your requirements"),
     never one notification per property.
     (16-customer-spec/11-portal-notifications.md §9)
```

---

## 5. States

| State | Behavior |
|---|---|
| Idle | Template download + dropzone |
| Uploading | Progress bar |
| Parsing / validating | "Checking 142 rows…" — a large file takes real time |
| **Review** | The core state. Valid count, failed count, per-row reasons |
| All valid | Straight to "Import 142 properties" |
| All failed | Almost always a **structural** problem (wrong headers, wrong delimiter, a file that isn't really a CSV). Say *that*, don't list 142 identical row errors: "This file's columns don't match the template. Download the template?" |
| Importing | Progress. This is a long-running job — see §11 on sync vs. async |
| Import complete | "128 properties imported as drafts. [Review them →]" |
| Partial failure during import | Some rows inserted, some failed mid-flight. **Report exactly which** — and the successful ones stay imported. Do not roll back 127 good rows because row 128 hit a constraint |
| File too large | Reject with the actual limit, before upload |

---

## 6. API Calls

| Trigger | Call | Notes |
|---|---|---|
| Upload + validate | `POST /admin/properties/bulk-upload` | `04-api-spec.md` §8. **The spec defines one endpoint** — so validate-and-import are the same call, which forces a synchronous, all-or-nothing shape. See §11 |
| Confirm import | *(no separate endpoint)* | The two-phase "validate → review → import" flow in §4 **needs a second endpoint** that doesn't exist |
| Template download | *(static asset)* | |

---

## 7. Data Touched

| Table | Access |
|---|---|
| `properties` | Write (bulk, `status = 'draft'`) |
| `property_media` | ⚠ **How does a CSV carry photos?** See §9 |
| `property_embeddings` | Write (on publish, not on import) |
| *`bulk_uploads` / `bulk_upload_rows`* | **Don't exist — Gap A6.** Nothing models the job or its per-row results |

---

## 8. Roles & Permissions

| Action | `agent` | `admin` | `super_admin` |
|---|---|---|---|
| Bulk upload | ❌ | ✅ | ✅ |

**Admin-only, unambiguously.** Bulk-creating inventory is not an agent operation, and the blast radius of a bad import is large.

Every imported row is stamped with the **caller's tenant**. A CSV column named `tenant_id` must be **ignored**, not honored — that would be a trivially exploitable cross-tenant write, and it's exactly the sort of thing a naive "map the CSV columns to the model" implementation does by accident.

---

## 9. Validation & Edge Cases

The whole feature is this section.

| Case | Behavior |
|---|---|
| **Wrong headers** | Detect up front, don't emit 142 row errors. Suggest the template |
| **Excel, not CSV** | Must actually support `.xlsx` — FR9.2 says "CSV/Excel", and Excel is what tenants have |
| **Excel number formatting** | `₹78,00,000` / `78 L` / `7800000.00` / `1.2Cr` all appear in real files. Parse leniently, and **show what you parsed it as** in the review table |
| **Unknown amenity** | Don't silently drop it. Suggest the nearest canonical value ("swiming pool" → `swimming_pool`) — this needs the canonical vocabulary that doesn't exist yet ([04](04-property-add-edit.md) §11) |
| **Duplicate rows within the file** | Detect on title + address and flag them |
| **Duplicate against existing listings** | Warn, don't block. A tenant may genuinely have two identical flats |
| **Photos** | **A CSV cannot contain images.** Options: (a) a column of image URLs the backend fetches — which is an SSRF surface and needs an allowlist; (b) media added later per-property; (c) a ZIP upload with a filename convention. **Unspecified today** — and a bulk import with no photos produces 128 listings that won't convert |
| **Encoding** | UTF-8 with a BOM, Latin-1, smart quotes. Property names in a non-English market will break a naive parser |
| **Empty rows / trailing blank lines** | Skip silently, don't error |
| **Enormous file** | Cap the row count. 10,000 rows synchronously will time out the request and probably the browser |
| **`tenant_id` column present in the CSV** | **Ignore it.** See §8 |

---

## 10. Acceptance Criteria

| ID | Case | Source |
|---|---|---|
| TC-PROP-03 | A valid CSV imports; rows appear as drafts | Sprint 2 |
| — | An invalid row is reported with its **row number and reason**, and does not block the valid rows (FR9.2) | FR9.2 |
| — | The failed rows can be downloaded, fixed, and re-uploaded | §4 |
| — | An `.xlsx` file imports as well as a `.csv` | FR9.2 |
| — | A `tenant_id` column in the CSV cannot write to another tenant | Security test |
| — | Publishing 128 imported properties produces **batched** customer notifications, not 128 per customer | [Customer 11](../16-customer-spec/11-portal-notifications.md) §9 |

---

## 11. Open Questions

- [ ] **Gap A6 — nothing models the upload job or its per-row results.** FR9.2 requires "validation and error reporting", which implies persistence: the admin uploads, walks away, comes back. Add `bulk_uploads` + `bulk_upload_rows` to `03-database-schema.md`, or accept a purely in-request, non-resumable flow.
- [ ] **The API spec has one endpoint** (`POST /admin/properties/bulk-upload`) but the flow needs two phases (validate → review → confirm import). Either add `POST /admin/properties/bulk-upload/validate` + `/commit`, or accept a one-shot import with no review step — **which contradicts FR9.2's "validation and error reporting"**, since there'd be nothing to review before committing. Resolve in `04-api-spec.md`.
- [ ] **Sync or async?** A 500-row import with per-row validation will exceed a normal request timeout. This is the same open question `04-api-spec.md` §17 raises for report generation. **Recommend: async job + polling**, and solve it once for both features.
- [ ] **How do photos get in?** (§9). Without an answer, bulk upload produces listings that can't convert — which undercuts the whole point of the feature.
- [ ] **The canonical amenity vocabulary** — needed here for fuzzy-matching import values. Same gap as [04](04-property-add-edit.md) §11.
