# Page: Reports

> **Route:** `/admin/reports` · **PRD Module:** 15 · **App:** `admin-portal/` → `pages/Reports/`
> Part of [Doc 17 — Admin Spec](README.md). Read [`README.md` §4](README.md#4-cross-cutting-rules-for-every-admin-page) first.

---

## 1. Purpose & Traceability

Filterable, exportable reports on leads, sales, and inventory — for the owner who wants the numbers in a spreadsheet, or in a PDF for a partner meeting.

**The acceptance criterion is the whole design constraint:** *"exported reports match dashboard figures for the same filter/date range."* That sounds obvious and is routinely violated, because the dashboard and the report get written months apart by different people, each defining "conversion" their own way. **One metrics service, used by both.** Not two queries that happen to agree today.

| Requirement | Source |
|---|---|
| FR15.1 Report builder: leads, sales, inventory reports with filters and export (PDF/Excel) | `01-prd.md` §16 |
| Acceptance: **exported reports match dashboard figures for the same filter/date range** | `01-prd.md` §16 |

---

## 2. Entry & Exit Points

**Entry:** sidebar; a Dashboard chart drill-down ("Leads by source" → the full report, pre-filtered — Vikram's flow, `13-ui-ux-flows.md` §2.4).

**Exit:** a downloaded file. Or a drill-through into the [lead table](09-leads-table-and-assignment.md) with the same filters applied.

---

## 3. Layout & Regions

```
┌──────────┬────────────────────────────────────────────────────────────┐
│ SIDEBAR  │  Reports                                                   │
│          │                                                            │
│          │  ┌── BUILD A REPORT ──────────────────────────────────┐    │
│          │  │  Type      (•) Leads  ( ) Sales  ( ) Inventory      │    │
│          │  │                                                     │    │
│          │  │  Period    [ 1 Jun 2026 ] → [ 30 Jun 2026 ]         │    │
│          │  │                                                     │    │
│          │  │  Group by  [ Source ▾ ]                             │    │
│          │  │  Filters   Agent:[All ▾]  Stage:[All ▾]             │    │
│          │  │            Property type:[All ▾]                    │    │
│          │  │                                                     │    │
│          │  │            [ Generate ]                             │    │
│          │  └─────────────────────────────────────────────────────┘    │
│          │                                                            │
│          │  ── Leads by source · 1–30 Jun 2026 ───────────────────    │
│          │                                                            │
│          │  ┌──────────────────────────────────────────────────────┐  │
│          │  │ Source          │ Leads │ Won │ Lost │ Open │ Conv.  │  │
│          │  ├──────────────────────────────────────────────────────┤  │
│          │  │ 💬 AI Chatbot   │  142  │ 18  │  41  │  83  │ 12.7%  │  │
│          │  │ 🔍 AI Search    │   98  │ 14  │  30  │  54  │ 14.3%  │  │
│          │  │ 📝 Contact form │   61  │  6  │  22  │  33  │  9.8%  │  │
│          │  │ 📋 Requirement  │   44  │  9  │  11  │  24  │ 20.5%  │  │
│          │  │ 🚶 Walk-in      │   12  │  3  │   4  │   5  │ 25.0%  │  │
│          │  ├──────────────────────────────────────────────────────┤  │
│          │  │ TOTAL           │  357  │ 50  │ 108  │ 199  │ 14.0%  │  │
│          │  └──────────────────────────────────────────────────────┘  │
│          │        ↑ this is the report that proves (or disproves)     │
│          │          the AI features are worth what they cost          │
│          │                                                            │
│          │  [ ⬇ Excel ]  [ ⬇ PDF ]                                    │
└──────────┴────────────────────────────────────────────────────────────┘
```

### 3.1 The Three Report Types

| Type | Rows | Answers |
|---|---|---|
| **Leads** | Grouped by source / agent / stage / month | Where do leads come from, and which convert? |
| **Sales** | Closed-won leads, with property + value + agent | What did we actually sell? |
| **Inventory** | Properties by status / type / price band / age-on-market | What are we sitting on, and what's stale? |

---

## 4. Workflow

```
Admin picks type + period + grouping + filters
   │
   ▼
[ Generate ]
   │
   ▼
POST /admin/reports/generate  { type, date_from, date_to, group_by, filters }
   │
   ├─ SYNCHRONOUS  → returns the rows → render
   │
   └─ ASYNCHRONOUS → returns a job id → poll → render
        │
        └─ ⚠ Which one? 04-api-spec.md §17 flags this as open, and
           GET /admin/reports/{id}/export implies a PERSISTED report
           with an id — which implies async, and implies a table
           that doesn't exist (Gap A5).
   ▼
Report renders on screen
   │
   ├─→ [ ⬇ Excel ] / [ ⬇ PDF ]
   │        → GET /admin/reports/{id}/export?format=xlsx|pdf
   │
   └─→ Clicks a row ("AI Chatbot: 142 leads")
            → the lead table, filtered to source=chatbot + the same dates
            → the SAME numbers, drillable to the SAME rows.
              If the table shows 138 leads where the report said 142,
              the report is dead to this admin forever.
```

---

## 5. States

| State | Behavior |
|---|---|
| Idle | The builder, with sensible defaults (Leads, last 30 days, grouped by source) |
| Generating | Progress. A wide date range on a large tenant is genuinely slow |
| Empty result | "No leads in this period." Not an error |
| Exporting | Spinner on the button; the file downloads |
| Large report | 50,000 rows will not render in the browser. Paginate on screen; **the export gets everything** |
| Timeout | The exact reason async matters (§11) |

---

## 6. API Calls

| Trigger | Call | Notes |
|---|---|---|
| Generate | `POST /admin/reports/generate` | `04-api-spec.md` §14 |
| Export | `GET /admin/reports/{id}/export` | Implies a persisted report — **no table exists (A5)** |

---

## 7. Data Touched

| Table | Access |
|---|---|
| `leads` | Read (the core of leads + sales reports) |
| `lead_activities` | Read (**stage-change timestamps — where conversion and time-to-close actually come from**) |
| `properties` | Read (inventory; the property on a sale) |
| `users` | Read (agent attribution) |
| *`reports`* | **Doesn't exist (A5)** — nothing to hold a generated report or its ID |

---

## 8. Roles & Permissions

| Action | `agent` | `admin` | `super_admin` |
|---|---|---|---|
| Generate tenant-wide reports | ❌ | ✅ | ✅ |
| Own performance only | ✅ (via [Agents](10-agents.md)) | ✅ | ✅ |
| Export | ❌ | ✅ | ✅ |

**Exports contain customer PII** — names, phones, emails — leaving the system as a file on someone's laptop. Two consequences:
1. Admin-only, always. `08-auth-roles-spec.md` §5.1 gives agents "Partial (own performance only)"; a full lead export is not that.
2. **Log every export in the audit log** ([12](12-audit-log.md)). "Who downloaded the full customer list, and when" is precisely the question that gets asked after an incident — and it's unanswerable without the log that doesn't exist (Gap A1).

---

## 9. Validation & Edge Cases

- **⚠ The metric-consistency trap.** The acceptance criterion demands the report match the dashboard. That only holds if **one service computes each metric**, consumed by [Dashboard](02-dashboard.md), [Agents](10-agents.md), and Reports. If each screen writes its own SQL, they *will* diverge — over the boundary condition, the timezone, whether soft-deleted rows are excluded, whether "conversion" is over created-in-period or closed-in-period leads. **Build `metrics_service.py` once. Make the three screens call it.** This is the single most important implementation note in this file.
- **Date boundaries:** inclusive or exclusive of the end date? In whose timezone? Off-by-one-day is the classic reason a report and a dashboard disagree by 3 leads and everyone loses faith in both.
- **Soft-deleted rows** must be excluded consistently — everywhere, not just where someone remembered.
- **Reassigned leads:** attributed to the current owner, or the one who closed it? ([10](10-agents.md) §9 — and there's no reassignment history to compute it either way.)
- **Sales value:** a "sales report" needs a **sale price**, and there is nowhere to store one. `leads` has no value/amount column, and `properties.price` is the *asking* price, not what it sold for. **So the sales report can only report asking prices — which is not what "sales" means.** See §11.
- **PDF generation** needs a library and, for charts, a rendering step. Not chosen in `10-deployment-devops.md`.
- **Excel** — a real `.xlsx`, not a CSV with a misleading extension.

---

## 10. Acceptance Criteria

| ID | Case | Source |
|---|---|---|
| TC-REPORT-01 | A report generates with filters and exports to PDF/Excel | Sprint 8 |
| — | **Exported figures match the Dashboard for the same filters and date range** (FR15.1 acceptance) | `01-prd.md` §16 |
| — | Drilling from a report row into the lead table shows exactly the same rows and count | §4 |
| TC-TENANT-01 | A report contains only the caller's tenant's data | Sprint 1 |
| TC-ROLE-01 | An agent cannot generate or export a tenant-wide report (403) | Sprint 8 |
| — | Every export is recorded in the audit log | §8 |

---

## 11. Open Questions

- [ ] **Gap A5 — no `reports` table / job model**, but `GET /admin/reports/{id}/export` implies a persisted report with an ID. Either make export stateless (re-run the query with the same params, no ID needed) or add the table. **Recommend stateless re-run** — it's simpler, has no storage or cleanup, and there's no requirement to keep report history.
- [ ] **Sync or async?** Open in `04-api-spec.md` §17. **Same question as [bulk upload](05-property-bulk-upload.md) — solve it once, for both.** Recommend: sync with a row cap, async only if it proves necessary.
- [ ] **The sales report has no sale price** (§9). `leads` needs a `deal_value` (set on `closed_won`), or "sales" reporting is really just "closed-won lead counts". **Decide in `01-prd.md`** — a real-estate CRM that can't report what it sold for is a strange thing.
- [ ] **Define each metric once** (§9), shared with the Dashboard and Agents. The most consequential open item on this page.
- [ ] PDF/Excel library choice — belongs in `10-deployment-devops.md`.
- [ ] Whether scheduled/emailed reports ("email me the weekly lead report") are in scope. They aren't in the PRD; they're the first thing an owner will ask for.
