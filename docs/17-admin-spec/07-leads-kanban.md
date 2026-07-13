# Page: Lead Pipeline — Kanban Board

> **Route:** `/admin/leads` · **PRD Module:** 10 · **App:** `admin-portal/` → `pages/Leads/`
> Part of [Doc 17 — Admin Spec](README.md). Read [`README.md` §4](README.md#4-cross-cutting-rules-for-every-admin-page) first.

---

## 1. Purpose & Traceability

**The agent's home screen.** Anjali opens this in the morning and lives in it all day (`13-ui-ux-flows.md` §2.3). Every other admin screen is visited occasionally; this one is *inhabited*.

That has a design consequence: **optimize for the hundredth use, not the first.** Drag-and-drop instead of an edit form. Keyboard-reachable. Fast. A single extra click here is paid dozens of times a day, by the person whose productivity the entire CRM exists to serve.

| Requirement | Source |
|---|---|
| FR10.1 Kanban: New → Contacted → Site Visit Scheduled → Negotiation → Closed/Lost (**stage names configurable**) | `01-prd.md` §11 |
| FR10.2 Manual or automatic (round-robin/rules-based) assignment | `01-prd.md` §11 |
| FR10.3 Notes, call logs, follow-up reminders | `01-prd.md` §11 → [08](08-lead-detail.md) |
| FR10.4 Lead source tracking | `01-prd.md` §11 |
| FR10.5 Table view as an alternative | `01-prd.md` §11 → [09](09-leads-table-and-assignment.md) |
| Acceptance: **every lead has a non-null source and an owner (or explicit "unassigned"); stage changes are timestamped** | `01-prd.md` §11 |
| Screen workflow | `14-screen-workflows.md` §8 |

---

## 2. Entry & Exit Points

**Entry:** the post-login landing **for agents** (filtered to "assigned to me"); the sidebar; the "Active leads" KPI or an activity row on the [Dashboard](02-dashboard.md), deep-linked to a specific lead.

**Exit:** a card → the [lead detail panel](08-lead-detail.md) (a slide-over, **not** a navigation — leaving the board to read a lead and coming back is exactly the friction to avoid). Or toggle to the [table view](09-leads-table-and-assignment.md).

---

## 3. Layout & Regions

```
┌──────────┬──────────────────────────────────────────────────────────────────┐
│ SIDEBAR  │ Leads    [Kanban][Table]   Agent:[Me ▾] Source:[All ▾] [+ Lead]  │
│          │                                                                  │
│          │ ┌─ NEW (5) ─┐ ┌CONTACTED│ ┌ VISIT   │ ┌NEGOTIAT.│ ┌ CLOSED   ┐  │
│          │ │           │ │  (12)   │ │  (4)    │ │  (3)    │ │  (28)    │  │
│          │ │ ┌───────┐ │ │┌───────┐│ │┌───────┐│ │┌───────┐│ │┌────────┐│  │
│          │ │ │Priya S│ │ ││Ravi K ││ ││Meera ││ ││Arun P ││ ││Deepa M ││  │
│          │ │ │💬 chat│ │ ││🔍 srch││ ││📝 form││ ││💬 chat││ ││ WON ✓  ││  │
│          │ │ │Sunview│ │ ││Palm G.││ ││Lake V.││ ││Sunview││ ││        ││  │
│          │ │ │ 2m ago│ │ ││  🔴 3d││ ││ 📅 Fri││ ││       ││ │└────────┘│  │
│          │ │ │  ⚠ un-│ │ │└───────┘│ │└───────┘│ │└───────┘│ │┌────────┐│  │
│          │ │ │ assign│ │ │┌───────┐│ │         │ │         │ ││Ajay R  ││  │
│          │ │ └───────┘ │ ││...    ││ │         │ │         │ ││ LOST ✗ ││  │
│          │ │ ┌───────┐ │ │└───────┘│ │         │ │         │ │└────────┘│  │
│          │ │ │...    │ │ │         │ │         │ │         │ │          │  │
│          │ │ └───────┘ │ │         │ │         │ │         │ │          │  │
│          │ └───────────┘ └─────────┘ └─────────┘ └─────────┘ └──────────┘  │
│          │       ↑ drag a card between columns to change stage             │
└──────────┴──────────────────────────────────────────────────────────────────┘
```

| Element | Contents |
|---|---|
| Column | A stage + its count. **Closed** merges won/lost visually but keeps them distinguishable |
| Card | Customer name · **source icon** (chatbot 💬 / search 🔍 / form 📝 / requirement / walk-in) · the property · time in stage |
| 🔴 Staleness | A lead sitting in a stage too long. **The most valuable pixel on the board** — the pipeline's job is to stop leads rotting silently |
| ⚠ Unassigned | Nobody owns it. A lead in `new` with no owner is a lead nobody is working |
| 📅 | A follow-up reminder is set (FR10.3) |
| Filters | Agent (default: **me**, for agents), source, date |

---

## 4. Workflow

```
Agent opens /admin/leads
   │
   ▼
GET /admin/leads/pipeline-view   → grouped-by-stage payload
   │   (a purpose-built endpoint — the board doesn't paginate a flat list)
   ▼
Board renders, filtered to "assigned to me" by default
   │
   ├─→ Clicks a card → the detail panel slides in from the right    [→ 08]
   │        · the board stays visible behind it. Context is not lost.
   │
   ├─→ DRAGS a card to the next column
   │        │
   │        ▼
   │   Optimistic move (the card is already there — no waiting)
   │        │
   │        ▼
   │   PATCH /admin/leads/{id}/stage  { to_stage }
   │        │
   │        ├─ success → a lead_activities row is written:
   │        │            from_stage, to_stage, changed_by, changed_at
   │        │            ← this timestamped trail is what every
   │        │              conversion metric in Reports is built on
   │        │
   │        └─ failure → the card SNAPS BACK + an error toast.
   │                     Never leave the board showing a state the
   │                     server didn't accept.
   │
   ├─→ Drags a lead to Closed → asks Won or Lost
   │        · closed_won and closed_lost are different outcomes and
   │          both feed reporting. Don't make the agent guess which
   │          one a single "Closed" column means.
   │
   └─→ [+ Lead] → manually add a walk-in (source = walk_in)         [FR10.4]
```

---

## 5. States

| State | Behavior |
|---|---|
| Loading | Skeleton columns |
| **Empty (new tenant)** | "No leads yet. They'll appear here as visitors inquire through your site." + a link to check that the public site is live. This is a *waiting* state, not a failure |
| Empty column | The column stays visible (drop targets must exist). A quiet "Nothing here" |
| Agent with no assigned leads | "Nothing assigned to you." + a switch to "All leads" — **if** the tenant lets agents self-claim (open, see §11) |
| Dragging | The origin column dims; valid drop targets highlight |
| Drag failed | Snap back + a toast |
| Huge column (200 closed leads) | **Virtualize or cap it.** The Closed column grows forever and will eventually make the board unusable. Show recent + "see all in Table view" |
| Stale lead | 🔴 after N days in stage (N per stage — 2 days in `new` is bad; 2 weeks in `negotiation` is normal) |
| Mobile | **The Kanban board is not a mobile experience.** Drag-and-drop on a 5-column board on a phone is a bad idea. On mobile, default to the [table view](09-leads-table-and-assignment.md) with a stage dropdown. `13-ui-ux-flows.md` §5 leaves admin mobile parity open — **this is the concrete answer for this screen** |

---

## 6. API Calls

| Trigger | Call | Notes |
|---|---|---|
| Mount | `GET /admin/leads/pipeline-view` | Kanban-ready, grouped by stage. `04-api-spec.md` §9 |
| Drag | `PATCH /admin/leads/{id}/stage` | Writes a `lead_activities` row |
| Reassign | `PATCH /admin/leads/{id}/assign` | See [09](09-leads-table-and-assignment.md) |
| Open a card | `GET /admin/leads/{id}` | Full detail + notes + timeline |
| + Lead | *(no endpoint)* | ⚠ `POST /leads` is the **public** endpoint. There's no admin-side lead-create route, but FR10.4 explicitly lists `walk_in` as a source that's "manually added". See §11 |

---

## 7. Data Touched

| Table | Access |
|---|---|
| `leads` | Read / Update (`stage`, `assigned_agent_id`) |
| `lead_activities` | **Write on every stage change** — from, to, by, when |
| `lead_notes` | Read (a note-count indicator on the card) |
| `properties` | Read (the property on the card) |
| `users` | Read (agent names/avatars) |

---

## 8. Roles & Permissions

| Action | `agent` | `admin` | `super_admin` |
|---|---|---|---|
| View **assigned** leads | ✅ | ✅ | ✅ |
| View **all tenant** leads | ⚠ open (§11) | ✅ | ✅ |
| Move a stage on an assigned lead | ✅ | ✅ | ✅ |
| Move a stage on **someone else's** lead | ❌ | ✅ | ✅ |
| Reassign a lead | ❌ | ✅ | ✅ |

**Ownership scoping is enforced in the service layer, not just the role check** (`08-auth-roles-spec.md` §5). An agent calling `PATCH /admin/leads/{id}/stage` for a lead assigned to a colleague gets a **403** — not a silent success, and not merely a hidden button. This needs its own test; a role-only check will pass a naive review and still be wrong.

---

## 9. Validation & Edge Cases

- **Stage skipping** (New → Negotiation, straight past Contacted): **allow it.** Real deals skip steps, and a CRM that fights the agent's reality gets abandoned for a spreadsheet.
- **Backwards moves** (Negotiation → Contacted): allow, and record in `lead_activities`. But **do not show reversals to the customer** ([customer 10](../16-customer-spec/10-portal-inquiries.md) §9).
- **Reopening a closed lead:** allow. Deals come back from the dead.
- **Two agents drag the same lead simultaneously:** last write wins. Log both attempts in `lead_activities`, so the history is honest about what happened.
- **A lead with a deleted property:** properties are soft-deleted, so the reference survives. Show the property name with a "no longer listed" note rather than a broken card.
- **Every lead must have a source (FR10.4 acceptance).** `POST /leads` sets it; a manually added walk-in must too. **A lead with a null source is a reporting hole** — the lead-source chart on the Dashboard is a headline metric.
- **Unassigned leads must not be invisible.** If an agent's board defaults to "assigned to me", the `new` unassigned column is empty for everyone, and nobody works the new leads. **Either auto-assign on creation, or make the unassigned queue prominent.** This is the practical consequence of Gap A3 being unresolved — and it's how a CRM quietly loses leads.

---

## 10. Acceptance Criteria

| ID | Case | Source |
|---|---|---|
| TC-LEAD-01 | A lead created from the public site appears in the `new` column with the correct source | Sprint 4 |
| TC-LEAD-02 | Dragging a card changes the stage and **writes a timestamped `lead_activities` row** | Sprint 4 |
| TC-LEAD-03 | An agent sees only their assigned leads; an admin sees all tenant leads | Sprint 4 |
| TC-ROLE-01 | An agent cannot change the stage of another agent's lead (403) | Sprint 8 |
| TC-TENANT-01 | No cross-tenant lead ever appears | Sprint 1 |
| TC-CHAT-04 | A chatbot escalation is visible to an agent here | Sprint 6 |

---

## 11. Open Questions

- [ ] **Gap A4 — FR10.1 says stage names are configurable, but `leads.stage` is a fixed enum** in `03-database-schema.md`. Both can't be true. Either (a) drop configurability for MVP (**recommended** — it's a nice-to-have that complicates every query, report, and board render), or (b) add a `pipeline_stages` table per tenant and make `leads.stage` an FK. **Decide before Sprint 4.**
- [ ] **Gap A3 — lead auto-assignment (FR10.2) is unresolved.** Round-robin, rules-based, or manual claim? This is not a small UI question: it determines whether new leads have an owner, which determines whether the board's default filter shows them, which determines **whether anyone works them**. Open in `01-prd.md` and `14-screen-workflows.md` §10.
- [ ] **No admin-side lead-create endpoint**, despite FR10.4 listing `walk_in` as a manually-added source. Add `POST /admin/leads` to `04-api-spec.md`.
- [ ] **Can agents see (and claim) unassigned leads?** Depends on the answer to A3.
- [ ] **Staleness thresholds** (the 🔴 flag) — per stage, per tenant, or hardcoded? Not specified anywhere, and it's the board's most useful signal.
