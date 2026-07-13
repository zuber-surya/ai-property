# Page: Audit Log

> **Route:** `/admin/users/audit-log` · **PRD Module:** 11 · **App:** `admin-portal/` → `pages/Users/AuditLog`
> Part of [Doc 17 — Admin Spec](README.md). Read [`README.md` §4](README.md#4-cross-cutting-rules-for-every-admin-page) first.

> ## ⚠ This page cannot be built as specified.
> FR11.3 requires an audit log. `GET /admin/audit-log` is specified in `04-api-spec.md` §10. `.claude/rules/security.md` states plainly: *"Log all admin-portal write actions (actor, action, entity, timestamp) — PRD Module 11."*
>
> **But `03-database-schema.md` defines no `audit_log` table.** (Gap A1.)
>
> §12 proposes the schema. Add it to `03-database-schema.md` and an Alembic migration first (`.claude/rules/workflow.md`).

---

## 1. Purpose & Traceability

Who did what, when. In a multi-tenant CRM holding other people's customer data, this is the difference between "we can tell you exactly what happened" and "we don't know."

**It is not a feature of this page — it is a cross-cutting service-layer concern** that this page merely *reads*. Every mutating endpoint in the admin portal writes to it. Build it with the **first** write endpoint, not as a Phase 3 catch-up: an audit log added late has no history, and history is the only thing it's for.

| Requirement | Source |
|---|---|
| FR11.3 Audit log of admin actions (actor, action, entity, timestamp) | `01-prd.md` §12 |
| "Log all admin-portal write actions" | `.claude/rules/security.md` |
| Acceptance (PRD §18): admin actions and lead-stage changes are logged with timestamps for reporting and accountability | `01-prd.md` §18 |

---

## 2. Entry & Exit Points

**Entry:** the "Audit log" button on [Users](11-users-roles.md); a compliance/incident investigation ("who published that listing?", "who changed Ravi's role?").

**Exit:** each entry deep-links to the entity it touched, where that entity still exists.

---

## 3. Layout & Regions

```
┌──────────┬────────────────────────────────────────────────────────────┐
│ SIDEBAR  │  ← Users                                                   │
│          │  Audit log                                                 │
│          │                                                            │
│          │  Actor:[All ▾] Action:[All ▾] Entity:[All ▾]              │
│          │  Date:[Last 30 days ▾]                    [ Export CSV ]   │
│          │                                                            │
│          │  ┌──────────────────────────────────────────────────────┐  │
│          │  │ When       │ Who    │ Did what                       │  │
│          │  ├──────────────────────────────────────────────────────┤  │
│          │  │ 13 Jul     │ Vikram │ granted ADMIN to meera@t.com   │  │
│          │  │ 14:22      │        │ (was: agent)              🔴   │  │
│          │  ├──────────────────────────────────────────────────────┤  │
│          │  │ 13 Jul     │ Vikram │ published property             │  │
│          │  │ 11:05      │        │ "Palm Grove Villa"       →     │  │
│          │  ├──────────────────────────────────────────────────────┤  │
│          │  │ 13 Jul     │ Anjali │ moved lead "Priya Sharma"      │  │
│          │  │ 09:47      │        │ Contacted → Site Visit    →    │  │
│          │  ├──────────────────────────────────────────────────────┤  │
│          │  │ 12 Jul     │ Vikram │ deactivated user ravi@t.com 🔴 │  │
│          │  │ 17:30      │        │                                │  │
│          │  ├──────────────────────────────────────────────────────┤  │
│          │  │ 12 Jul     │ Anjali │ updated chatbot greeting       │  │
│          │  │ 16:12      │        │                           →    │  │
│          │  └──────────────────────────────────────────────────────┘  │
│          │                                     ‹ 1 2 3 … 40 ›         │
└──────────┴────────────────────────────────────────────────────────────┘
```

| Element | Notes |
|---|---|
| Human-readable action | "granted ADMIN to meera@t.com (was: agent)" — **not** `UPDATE users SET role='admin' WHERE id=...`. An audit log nobody can read is an audit log nobody reads |
| 🔴 High-risk flag | Role grants, deactivations, and tenant-settings changes are visually distinct. These are the entries an investigation is looking for |
| Filters | Actor, action type, entity type, date range |
| Deep link | → the entity, where it still exists |
| Export | For compliance requests |

---

## 4. What Gets Logged

**Every write in the admin portal.** Not a curated subset — a curated subset is one someone forgot to add to.

| Module | Actions |
|---|---|
| Properties | create · update · **publish** · approve · reject · status change · archive · delete · bulk import |
| Leads | stage change · **reassign** · note added · manual create |
| Users | **invite · role change · deactivate** ← the highest-value entries in the log |
| AI Config | greeting/FAQ/escalation-rule changes · recommendation-weight changes |
| CMS | page create/edit/publish/delete |
| Tenant settings | branding · domain · **anything a super_admin does to a tenant** |
| Reports | (generation — arguably a read, but it exports customer PII, so log it) |

**Explicitly not logged:** ordinary reads. Logging every `GET` produces a log too noisy to use and a table that outgrows the data it describes.

### 4.1 Implementation

**One place, not thirty.** A service-layer decorator/dependency that every mutating service method passes through — not a manual `audit_log.write(...)` call sprinkled into each endpoint. The manual approach is guaranteed to be incomplete within a month, and the gaps will be exactly the endpoints someone added in a hurry.

```
Router → Service ──┬──► Repository → DB
                   └──► AuditService.record(actor, action, entity, before, after)
```

**The audit write must be in the same transaction as the change.** Otherwise you get changes with no log entry (worse) or log entries for changes that rolled back (also bad).

---

## 5. States

| State | Behavior |
|---|---|
| Loading | Skeleton rows |
| Empty (new tenant) | "No admin activity yet." Fine and expected |
| Filtered to nothing | "No matching entries" |
| Entity since deleted | The entry **remains** and still names the entity ("property 'Palm Grove Villa'"), with a dead link. **The log is the record of what happened — it must survive the thing it describes.** An audit log that loses entries when a row is deleted is not an audit log |
| Very large log | Paginate. Consider a retention policy (§9) |

---

## 6. API Calls

| Trigger | Call | Notes |
|---|---|---|
| Mount / filter | `GET /admin/audit-log` | `04-api-spec.md` §10. **No table backs it (A1)** |
| Export | *(none)* | Not specified |

**There is deliberately no write endpoint and no delete endpoint.** The log is written by the service layer as a side effect of other actions, and **nothing may modify or delete an entry** — not an admin, not a super_admin, not the API. An audit log that can be edited by the people it audits is theatre.

---

## 7. Data Touched

| Table | Access |
|---|---|
| *`audit_log`* | Read (append-only) — **doesn't exist (A1)** |
| `users` | Read (actor names) |

---

## 8. Roles & Permissions

| Action | `agent` | `admin` | `super_admin` |
|---|---|---|---|
| View the tenant's audit log | ❌ | ✅ | ✅ |
| View across tenants | ❌ | ❌ | ✅ |
| Modify / delete an entry | ❌ | ❌ | **❌ — nobody, ever** |

- The log is **tenant-owned** → RLS applies, and a tenant admin sees only their tenant's entries.
- **A super_admin's actions on a tenant must appear in that tenant's log.** If platform staff change a tenant's settings, that tenant deserves to see it. A log that hides the platform operator's actions from the customer is exactly the kind of thing that destroys trust when discovered.

---

## 9. Validation & Edge Cases

- **Actor is required.** Every entry has one. If a system/background job (the publish pipeline, an auto-assignment) mutates data, the actor is `system` — explicitly, not null.
- **Store enough to be useful.** "updated property" is nearly worthless. "changed price ₹78,00,000 → ₹75,00,000" is what an investigation needs. Capture a `before`/`after` diff (jsonb) for the fields that changed. But **do not dump entire row snapshots** — that bloats the table and duplicates PII into a second place you now have to protect.
- **PII in the log:** entries will contain customer names and emails. It's tenant-owned data under RLS, subject to the same protections as the source table.
- **Retention:** undefined. `03-database-schema.md` §6 already flags retention as open for `chat_messages` and `lead_activities`. **The audit log has the strongest case for long retention and the strongest case for growing without bound.** Decide.
- **Failure to write the audit entry** must fail the whole transaction. A change that silently escapes the log is the exact failure this system exists to prevent.
- **`lead_activities` overlaps with this.** Stage changes are already recorded there. Either treat `lead_activities` as a specialized audit table and have the audit log point at it, or accept the duplication — but **decide deliberately**, because two half-complete histories are worse than one complete one.

---

## 10. Acceptance Criteria

| ID | Case | Source |
|---|---|---|
| — | Every admin write action produces an audit entry with actor, action, entity, and timestamp (FR11.3) | `01-prd.md` §12 |
| — | A role change is logged, including the old and new role | §4 |
| — | Deleting a property does **not** remove its audit entries | §5 |
| — | No API can modify or delete an audit entry | Security test |
| TC-TENANT-01 | Tenant A's admin cannot read tenant B's audit log | Sprint 1 |
| — | A super_admin's action on a tenant appears in **that tenant's** log | §8 |

---

## 11. Open Questions

- [ ] **Gap A1 — the table doesn't exist.** Blocking. §12 proposes it.
- [ ] **Retention policy** (§9).
- [ ] **`lead_activities` vs. `audit_log` overlap** (§9) — resolve deliberately.
- [ ] Whether the audit log needs export (compliance requests generally require it).
- [ ] Whether failed/denied actions are logged too. **They should be** — repeated 403s from one agent against `/admin/users` is precisely the signal an audit log exists to surface, and it's invisible if you only log successes.

---

## 12. Proposed Schema (for `03-database-schema.md`)

```
audit_log                              (tenant-owned, append-only)
  id           UUID PK
  tenant_id    UUID NOT NULL REFERENCES tenants(id)
  actor_id     UUID NULL REFERENCES users(id)   -- NULL only when actor_type='system'
  actor_type   text NOT NULL DEFAULT 'user'     -- user | system | super_admin
  action       text NOT NULL                    -- property.publish, user.role_change, …
  entity_type  text NOT NULL                    -- property | lead | user | ai_config | cms_page | tenant
  entity_id    UUID NULL                        -- nullable: the entity may be gone
  entity_label text NULL                        -- denormalized name, so the log stays
                                                --   readable after the entity is deleted
  changes      jsonb NULL                       -- {"price": {"from": 7800000, "to": 7500000}}
  ip_address   inet NULL
  created_at   timestamptz NOT NULL DEFAULT now()

  INDEX (tenant_id, created_at DESC)
  INDEX (tenant_id, actor_id)
  INDEX (tenant_id, entity_type, entity_id)
```

Notes:
- **No `updated_at`, no `deleted_at`.** Append-only by design.
- `entity_label` is deliberately denormalized — it's what keeps an entry readable after the property it describes is gone.
- Tenant-owned → RLS via the standard helper + a cross-tenant-access test (`.claude/rules/database.md`).
- Enforce append-only **at the database level** (a `REVOKE UPDATE, DELETE` on the app's role), not merely by not writing an update endpoint. The application will eventually have a bug; the grant won't.
