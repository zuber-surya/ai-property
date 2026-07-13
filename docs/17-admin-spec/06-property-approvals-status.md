# Page: Property Approvals & Status Management

> **Route:** `/admin/properties?status=pending_approval` (a filtered view of the [list](03-properties-list.md)) · **PRD Module:** 9
> Part of [Doc 17 — Admin Spec](README.md). Read [`README.md` §4](README.md#4-cross-cutting-rules-for-every-admin-page) first.

---

## 1. Purpose & Traceability

The quality gate. In a brokerage where agents create listings but the owner is accountable for what appears on the company website, someone has to say yes before it goes live.

It's not a separate page so much as **a mode of the property list** — but the workflow around it is distinct enough to specify on its own, because the approval *decision* has consequences (publish pipeline, notifications) that a plain status change doesn't.

| Requirement | Source |
|---|---|
| FR9.3 Approval workflow: Draft → Pending Approval → Published (**configurable per tenant whether approval is required**) | `01-prd.md` §10 |
| FR9.4 Status flags: Featured, Sold, On Hold, Archived | `01-prd.md` §10 |
| Screen workflow | `14-screen-workflows.md` §7 |

---

## 2. The Status Model

`properties.status` (`03-database-schema.md` §3.4): `draft` · `pending_approval` · `published` · `sold` · `on_hold` · `archived`

```
                  ┌──────────────────────────────────────┐
                  │                                      │
    ┌─────────┐   │   ┌──────────────────┐   ┌───────────▼──┐
    │  DRAFT  │───┼──►│ PENDING APPROVAL │──►│  PUBLISHED   │
    └─────────┘   │   └──────────────────┘   └──┬───┬───┬───┘
         ▲        │            │                │   │   │
         │        │            │ rejected       │   │   │
         └────────┼────────────┘                │   │   │
                  │                             │   │   │
                  │  (approval NOT required:    │   │   │
                  │   draft ──────────────────► │   │   │
                  │   published directly)       │   │   │
                  │                             │   │   │
                  │        ┌────────────────────┘   │   │
                  │        ▼                        ▼   ▼
                  │   ┌─────────┐            ┌──────────┐  ┌──────────┐
                  │   │ ON HOLD │            │   SOLD   │  │ ARCHIVED │
                  │   └────┬────┘            └──────────┘  └──────────┘
                  │        │                       │             │
                  └────────┘                       │             │
                    (back to published)            └─────────────┘
                                                   terminal-ish;
                                                   both leave the
                                                   public site AND
                                                   the search index

    `is_featured` is a BOOLEAN, orthogonal to status — a featured
    property must also be `published` to appear anywhere.
```

### 2.1 What Each Status Means Publicly

| Status | Public site | AI search index | Chatbot can quote it |
|---|---|---|---|
| `draft` | ❌ (404) | ❌ | ❌ |
| `pending_approval` | ❌ (404) | ❌ | ❌ |
| `published` | ✅ | ✅ | ✅ |
| `sold` | ⚠ page renders with a "Sold" badge, **CTAs removed** | ❌ **de-indexed** | It can say "that one's sold" |
| `on_hold` | ❌ | ❌ | ❌ |
| `archived` | ❌ | ❌ | ❌ |

**De-indexing is as important as indexing.** A sold property left in `property_embeddings` keeps getting recommended, and the chatbot keeps offering it. That's a bad experience *and* it makes the AI look broken.

---

## 3. Layout

The [property list](03-properties-list.md) filtered to `pending_approval`, plus a review panel:

```
┌──────────┬─────────────────────────────────────────────────────────┐
│ SIDEBAR  │  Properties  ›  Pending approval (3)                    │
│          │                                                         │
│          │  ┌───────────────────────────────────────────────────┐  │
│          │  │ ▪ Palm Grove Villa                                │  │
│          │  │   ₹1,20,00,000 · 4BHK · 2,400 sqft                │  │
│          │  │   Submitted by Ravi · 2 days ago                  │  │
│          │  │                                                   │  │
│          │  │   ⚠ No floor plan uploaded                        │  │
│          │  │   ⚠ Description is 12 words (short — this weakens │  │
│          │  │      AI search results for this listing)          │  │
│          │  │                                                   │  │
│          │  │   [ Preview as a buyer ]                          │  │
│          │  │                                                   │  │
│          │  │   [ ✓ Approve & publish ]  [ ✗ Send back ]        │  │
│          │  └───────────────────────────────────────────────────┘  │
└──────────┴─────────────────────────────────────────────────────────┘
```

The **automated quality warnings** are the value-add. An approver skimming 12 listings won't notice a thin description — but that thin description degrades the AI search this whole product is sold on. Surface it at the moment of decision.

---

## 4. Workflow

```
Agent/admin submits a listing → status = pending_approval        [FR9.3]
   │
   ▼
It appears in the approval queue (+ the Dashboard's "3 pending" KPI)
   │
   ▼
Approver opens it
   │
   ├─→ [ Preview as a buyer ] → renders the public property page
   │      exactly as a visitor would see it. The single most useful
   │      control on this screen — approving something you've only
   │      seen as a form is how bad listings go live.
   │
   ├─→ [ ✓ Approve & publish ]
   │        │
   │        ▼
   │   POST /admin/properties/{id}/approve
   │        │
   │        ▼
   │   status = published
   │        │
   │        ▼
   │   ┌── THE PUBLISH PIPELINE (identical from every path) ──┐
   │   │  embed → index → match saved profiles → notify        │
   │   └───────────────────────────────────────────────────────┘
   │        │
   │        ▼
   │   Live · searchable · recommendable
   │
   └─→ [ ✗ Send back ]
            │
            ▼
        status = draft, with a rejection reason
            │
            ▼
        ⚠ NO ENDPOINT EXISTS for rejection, and no column stores
          the reason. Only `approve` is specified (§6). The submitter
          currently gets sent back with no explanation — or, worse,
          rejection isn't implementable at all. See §11.
```

---

## 5. States

| State | Behavior |
|---|---|
| Empty queue | "Nothing waiting for approval." Not an error — it's the *good* state, and it should feel like one |
| Approving | Button spinner; the row leaves the queue on success |
| Approval fails validation | E.g. no media. **Block it and say why** — a published listing with no photos is exactly what this gate exists to prevent |
| Indexing after approval | "Publishing… indexing for search" — the property is live but not yet searchable for a few seconds |
| Tenant doesn't require approval | **This whole screen is hidden.** Not shown-and-empty — hidden. A tenant that publishes directly should never see an approval queue in their nav |
| Bulk approve from the list | Allowed (see [03](03-properties-list.md)), but it skips the per-listing review — which somewhat defeats the purpose. Fine for a trusted-agent tenant |

---

## 6. API Calls

| Trigger | Call | Notes |
|---|---|---|
| Load the queue | `GET /admin/properties?status=pending_approval` | `04-api-spec.md` §8 |
| Approve | `POST /admin/properties/{id}/approve` | The only approval endpoint that exists |
| **Reject / send back** | *(none)* | **Missing.** Could be `PATCH .../status` back to `draft`, but there's nowhere to put the reason |
| Change status | `PATCH /admin/properties/{id}/status` | Featured / Sold / On Hold / Archived (FR9.4) |

---

## 7. Data Touched

| Table | Access |
|---|---|
| `properties` | Read / Update (`status`, `is_featured`) |
| `property_embeddings` | **Write on publish, DELETE on sold/archived/on_hold** (the de-index path) |
| `requirement_profiles`, `requirement_matches` | Read/Write (match-on-publish) |
| *`audit_log`* | Should record who approved what, and when — **doesn't exist (A1)**, and for an approval workflow that's a genuine accountability hole |

---

## 8. Roles & Permissions

| Action | `agent` | `admin` | `super_admin` |
|---|---|---|---|
| Submit for approval | ✅ (if they can create) | ✅ | ✅ |
| **Approve** | ❌ | ✅ | ✅ |
| Reject / send back | ❌ | ✅ | ✅ |
| Change status (Sold/Featured/Archived) | ❌ | ✅ | ✅ |

**An agent must never be able to approve — including their own submission.** That is the entire point of the gate, and `POST /admin/properties/{id}/approve` must 403 for `agent` (`TC-ROLE-01`).

Whether an admin can approve *their own* submission is a policy question. In a small brokerage, requiring a second admin would just deadlock. **Recommend: allow it, and log it** (which needs the audit log).

---

## 9. Validation & Edge Cases

- **Approving a listing with no media** — block or hard-warn (§5).
- **The submitter edits it while it's pending** — the approver may be looking at a stale version. Either lock it during review, or re-check on approve. Silently approving a version the approver never saw is the failure mode.
- **Approve → immediately mark Sold:** the publish pipeline fires, then the de-index fires. They must not race. If the embedding job is async and the de-index is sync, you can end up with a **sold property permanently in the search index** — a real, subtle bug worth an explicit test.
- **Un-publishing (Published → On Hold):** must de-index, and should warn if open leads reference the listing.
- **`is_featured` on a non-published property:** meaningless. Either block it or ignore it, but don't let it produce a featured listing that 404s on the homepage.
- **Archived is not deleted.** `archived` (a status) and `deleted_at` (a soft delete) are **two different things** and the schema has both. The UI must not conflate them. Right now the doc set doesn't clearly say what distinguishes them — see §11.

---

## 10. Acceptance Criteria

| ID | Case | Source |
|---|---|---|
| TC-PROP-02 | Draft → Pending → Published works, and only an admin can approve | Sprint 2 |
| TC-PROP-03 | Status flags apply and are correctly reflected on the public site | Sprint 2 |
| TC-ROLE-01 | An agent calling the approve endpoint gets a 403 | Sprint 8 |
| TC-SEARCH-* | An approved property becomes searchable within the sync window | Sprint 5 |
| — | **A property marked Sold is removed from the search index and stops being recommended** | §2.1 |

---

## 11. Open Questions

- [ ] **No rejection endpoint and no rejection-reason column.** FR9.3 implies a gate, and a gate that can only say "yes" isn't one. Add `PATCH /admin/properties/{id}/reject` (with a reason) to `04-api-spec.md`, and a column to hold it.
- [ ] **The "approval required" tenant flag has no home** — same gap as [04](04-property-add-edit.md) §11. Add `requires_property_approval` to `tenants`.
- [ ] **`archived` (status) vs. `deleted_at` (soft delete)** — what's the difference, and what does each mean for the public site, the search index, and reports? The schema has both; nothing explains the distinction.
- [ ] **Gap A1 — no audit log.** For an approval workflow, "who approved this and when" is not optional; it's the workflow's entire accountability story.
- [ ] Whether an admin may approve their own submission (§8).
