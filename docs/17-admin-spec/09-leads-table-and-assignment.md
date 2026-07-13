# Page: Lead Table View & Assignment

> **Route:** `/admin/leads?view=table` · **PRD Module:** 10 · **App:** `admin-portal/` → `pages/Leads/TableView`
> Part of [Doc 17 — Admin Spec](README.md). Read [`README.md` §4](README.md#4-cross-cutting-rules-for-every-admin-page) first.

---

## 1. Purpose & Traceability

The Kanban board is for **working** leads one at a time. The table is for **managing** them in bulk — the manager's view, not the agent's.

It's where you answer "who's got what?", "what's gone cold?", and "Ravi is on leave, move his 14 leads to Meera." The board cannot answer those questions; a table can.

| Requirement | Source |
|---|---|
| FR10.5 Table view as an alternative to Kanban | `01-prd.md` §11 |
| FR10.2 Manual or automatic (round-robin/rules-based) lead assignment | `01-prd.md` §11 |
| FR10.4 Lead source tracking | `01-prd.md` §11 |
| Acceptance: every lead has a non-null source and an owner (or an explicit unassigned state) | `01-prd.md` §11 |

---

## 2. Entry & Exit Points

**Entry:** the Kanban/Table toggle; the **default view on mobile** (a 5-column drag board is not a phone experience — see [07](07-leads-kanban.md) §5); a Reports drill-down.

**Exit:** a row → the [lead detail panel](08-lead-detail.md) (the same panel the board opens). Or export to CSV.

---

## 3. Layout & Regions

```
┌──────────┬───────────────────────────────────────────────────────────────┐
│ SIDEBAR  │ Leads   [Kanban][▪Table]                    [ Export CSV ]    │
│          │                                                               │
│          │ [Search name/phone] Stage:[All▾] Agent:[All▾] Source:[All▾]   │
│          │ Created:[Last 30d ▾]                                          │
│          │                                                               │
│          │ ┌───────────────────────────────────────────────────────────┐ │
│          │ │☐│ Name     │Source │Property │Stage      │Owner │ Age  │⋯│ │
│          │ ├───────────────────────────────────────────────────────────┤ │
│          │ │☑│Priya S.  │💬 chat│Sunview  │[Contacted]│Anjali│  2d  │⋯│ │
│          │ │☑│Ravi K.   │🔍 srch│Palm G.  │[New]      │  —   │🔴 5d │⋯│ │
│          │ │☐│Meera N.  │📝 form│Lake V.  │[Visit]    │Ravi  │  1d  │⋯│ │
│          │ │☐│Arun P.   │💬 chat│Sunview  │[Negotiat.]│Anjali│ 12d  │⋯│ │
│          │ │☐│Deepa M.  │  walk │  —      │[Won ✓]    │Meera │ 30d  │⋯│ │
│          │ └───────────────────────────────────────────────────────────┘ │
│          │                                                               │
│          │ ┌── 2 selected ────────────────────────────────────────────┐  │
│          │ │  Assign to: [ Meera ▾ ]  [Apply]   [Change stage] [×]    │  │
│          │ └──────────────────────────────────────────────────────────┘  │
│          │                                        ‹ 1 2 3 … 12 ›         │
└──────────┴───────────────────────────────────────────────────────────────┘
```

| Column | Notes |
|---|---|
| Name | + phone on hover/expand |
| Source | FR10.4 — the icon + label. **Filterable**, which is how you answer "is the chatbot actually producing leads?" |
| Property | The listing, or "—" for a general inquiry |
| Stage | Badge, matching the board's colors |
| Owner | Or a **highlighted "—"** for unassigned. Unassigned must be visually loud |
| **Age** | Days since creation, or days in the current stage. 🔴 when stale. **This is the column a manager sorts by**, and it's the one that surfaces the leads quietly rotting |

---

## 4. Workflow

```
Manager opens the table view
   │
   ▼
GET /admin/leads?stage=&agent=&source=&date=&page=
   │
   ▼
Table renders (sortable, filterable, paginated — URL params, so a view
                like "all unassigned, sorted by age" is a shareable link)
   │
   ├─→ Clicks a row → the same detail panel as the board          [→ 08]
   │
   ├─→ Sorts by Age → the stale leads rise to the top.
   │        This is the "what's rotting?" query, and it's the whole
   │        reason a manager opens this screen.
   │
   ├─→ Filters to Owner = "—" (unassigned)
   │        │
   │        ▼
   │   The leads nobody is working. If auto-assignment isn't
   │   implemented (Gap A3), THIS IS EVERY NEW LEAD, and the only
   │   thing stopping them from being lost is a human remembering
   │   to check this filter.
   │
   ├─→ Selects rows → bulk assign
   │        │
   │        ▼
   │   PATCH /admin/leads/{id}/assign   (per row — no bulk endpoint)
   │        │
   │        ▼
   │   Owner changes. ⚠ Is this written to lead_activities?
   │      The table only models stage changes (from_stage/to_stage) —
   │      there's nowhere to record "reassigned from Ravi to Meera."
   │      See §9.
   │
   └─→ [ Export CSV ] → ⚠ no endpoint (§6)
```

---

## 5. Assignment (FR10.2) — the unresolved core

FR10.2 allows "manual or automatic (round-robin/rules-based)". **Nothing decides which**, and `14-screen-workflows.md` §10 flags it as open. The choice has real consequences:

| Model | What happens | Cost |
|---|---|---|
| **Manual claim** | New leads land unassigned; agents pull from a shared queue | Nobody owns a lead until someone chooses to. Off-hours leads sit. **Leads get lost.** |
| **Round-robin** | Each new lead is auto-assigned to the next agent in rotation | Simple, fair, always-owned. Ignores expertise, workload, and who's on leave |
| **Rules-based** | Assign by property type, locality, or price band | Best fit; most machinery; needs rules config that isn't in the schema |

**Recommendation: round-robin at MVP, with manual reassignment from this screen.** It guarantees FR10.1's acceptance criterion ("every lead has an assigned owner or an explicit unassigned state") is met with a *real* owner rather than a permanent "—", and it's a day's work versus a sprint. Rules-based can come later — it's an optimization on top, not a different architecture.

But it needs deciding **in `01-prd.md`**, not in code.

---

## 6. API Calls

| Trigger | Call | Notes |
|---|---|---|
| Mount / filter / sort | `GET /admin/leads` | Filterable by stage, agent, source, date. `04-api-spec.md` §9 |
| Row → detail | `GET /admin/leads/{id}` | |
| Assign / reassign | `PATCH /admin/leads/{id}/assign` | One call per lead |
| Bulk assign | *(no bulk endpoint)* | The client loops. Fine for 14 leads; poor for 200 |
| Export CSV | *(none)* | Not in the API spec. [Reports](18-reports.md) has export — this could route there instead of adding a second export path |

---

## 7. Data Touched

| Table | Access |
|---|---|
| `leads` | Read / Update (`assigned_agent_id`) |
| `lead_activities` | Read (age-in-stage). ⚠ **Write? See §9** |
| `users` | Read (the agent dropdown; only `role = 'agent'` and `is_active`) |
| `properties` | Read |

---

## 8. Roles & Permissions

| Action | `agent` | `admin` | `super_admin` |
|---|---|---|---|
| View the table (own leads) | ✅ | ✅ | ✅ |
| View **all** tenant leads | ⚠ open | ✅ | ✅ |
| **Assign / reassign** | ❌ | ✅ | ✅ |
| Bulk assign | ❌ | ✅ | ✅ |
| Export | ❌ | ✅ | ✅ |

**Reassignment is a management action.** An agent who could reassign leads could hand off every hard lead and keep the easy ones — or, more simply, take their colleague's. 403 for agents, server-side.

---

## 9. Validation & Edge Cases

- **Reassignment isn't recorded anywhere.** `lead_activities` models *stage* changes (`from_stage`, `to_stage`) — there is no equivalent for ownership. So "who reassigned this, and when?" is unanswerable, which matters both for accountability and for agent-performance metrics ([10](10-agents.md)): if a lead is closed by Meera after Ravi did all the work, whose number is it? **Either extend `lead_activities` to a generic activity type, or lean on the (missing) `audit_log` (Gap A1).**
- **Assigning to an inactive/deleted agent:** filter the dropdown to `is_active` agents only.
- **Deactivating an agent with 14 open leads:** they must be reassigned or explicitly unassigned. **Do not orphan them silently** — this is exactly how a CRM loses a quarter's pipeline. Prompt on deactivation ([11](11-users-roles.md) §9).
- **Bulk assigning 200 leads:** 200 sequential PATCHes will be slow and can partially fail. Report which succeeded.
- **Sorting by "age":** age-since-created or age-in-current-stage? **They answer different questions** — the second is the one that finds neglect. Offer both, and label them unambiguously.
- **Every lead has a source (FR10.4 acceptance)** — a null source breaks the source filter and the Dashboard chart.

---

## 10. Acceptance Criteria

| ID | Case | Source |
|---|---|---|
| TC-LEAD-03 | The table filters correctly by stage, agent, and source | Sprint 4 |
| — | Reassigning a lead changes the owner and the agent sees it on their board | FR10.2 |
| — | Every lead has a non-null source and either an owner or an explicit unassigned state | FR10.1 acceptance |
| TC-ROLE-01 | An agent calling `PATCH /admin/leads/{id}/assign` gets a 403 | Sprint 8 |
| TC-TENANT-01 | No cross-tenant lead appears | Sprint 1 |

---

## 11. Open Questions

- [ ] **Gap A3 — the assignment model (FR10.2) is undecided.** See §5. **Recommend round-robin at MVP.** It must be decided in `01-prd.md` before Sprint 4, because "manual claim" and "auto-assign" produce different default board filters, different empty states, and a different answer to "who is responsible for this lead right now?"
- [ ] **Ownership changes aren't audited** (§9). Extend `lead_activities` or build the audit log.
- [ ] **No bulk-assign endpoint**, and no CSV-export endpoint for leads.
- [ ] Whether agents can view the full tenant lead table read-only (open in `08-auth-roles-spec.md` §6).
- [ ] Rules-based assignment (FR10.2's third option) has no config schema. If it's genuinely wanted, it needs a `assignment_rules` table — otherwise cut it from the PRD explicitly rather than leaving it as an unbuilt option.
