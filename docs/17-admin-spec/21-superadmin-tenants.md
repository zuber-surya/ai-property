# Page: Super Admin — Tenant Management

> **Route:** `/platform/tenants` · **PRD Module:** 16 · **App:** `admin-portal/` → `pages/TenantSettings/Platform`
> Part of [Doc 17 — Admin Spec](README.md). Read [`README.md` §4](README.md#4-cross-cutting-rules-for-every-admin-page) first.

---

## 1. Purpose & Traceability

The platform operator's console: onboard a new real-estate business, suspend one that hasn't paid, see who's actually using the product.

**This is the only screen in the system that intentionally crosses tenant boundaries.** Everything else in this codebase is built to make cross-tenant access impossible; this page is the deliberate, tightly-guarded exception. It deserves proportional care.

| Requirement | Source |
|---|---|
| FR16.1 Super admin: create/manage tenant accounts, view tenant status/usage | `01-prd.md` §17 |
| `super_admin` is platform-level, not scoped to a single tenant | `08-auth-roles-spec.md` §3 |
| `tenants` is platform-level and **not** tenant-scoped | `.claude/rules/database.md` |

---

## 2. Entry & Exit Points

**Entry:** the post-login landing for `super_admin` ([01](01-login-and-invite.md) §4.1). The route must be **completely unreachable** for every other role.

**Exit:** a tenant's detail view. Possibly an "impersonate" / "view as" flow — which is a genuinely dangerous feature and is discussed in §11.

---

## 3. Layout & Regions

```
┌──────────┬────────────────────────────────────────────────────────────┐
│ PLATFORM │  Tenants (14)                            [ + New tenant ]  │
│          │                                                            │
│ ▸Tenants │  Status:[All ▾]                                            │
│  Health  │                                                            │
│          │  ┌──────────────────────────────────────────────────────┐  │
│          │  │ Business      │ Domain        │Status │Props│Leads│⋯ │  │
│          │  ├──────────────────────────────────────────────────────┤  │
│          │  │ Sharma Estates│sharmaestates. │Active │ 142 │ 357 │⋯ │  │
│          │  │               │com            │       │     │     │  │  │
│          │  │ Nova Realty   │nova.propvista │Trial  │  18 │  12 │⋯ │  │
│          │  │               │.com           │ 3d    │     │     │  │  │
│          │  │               │               │ left  │     │     │  │  │
│          │  │ Old Brokers   │oldbrokers.com │Susp-  │  88 │ 210 │⋯ │  │
│          │  │               │               │ended🔴│     │     │  │  │
│          │  └──────────────────────────────────────────────────────┘  │
│          │                                                            │
│          │  ┌─ New tenant ────────────────────────────────────────┐   │
│          │  │  Business name  [ ____________________________ ]    │   │
│          │  │  Subdomain      [ nova ].propvista.com              │   │
│          │  │  Status         [ Trial ▾ ]                         │   │
│          │  │                                                     │   │
│          │  │  First admin                                        │   │
│          │  │  Email          [ ____________________________ ]    │   │
│          │  │  ↑ they get an invite and become the tenant's       │   │
│          │  │    first admin. A tenant with no admin is an        │   │
│          │  │    empty workspace nobody can get into.             │   │
│          │  │                                                     │   │
│          │  │                          [ Create tenant ]          │   │
│          │  └─────────────────────────────────────────────────────┘   │
└──────────┴────────────────────────────────────────────────────────────┘
```

| Region | Maps to |
|---|---|
| Tenant list | `tenants` (`name`, `domain`, `status`: `active`/`trial`/`suspended`) |
| Usage columns | Property and lead counts — the "view tenant status/usage" half of FR16.1 |
| Create form | Tenant + **its first admin user**, in one step |
| Row menu | Edit · Suspend · Reactivate · View as (§11) |

---

## 4. Workflow

### 4.1 Onboarding a tenant

```
Super admin fills: business name, subdomain, plan/status, first-admin email
   │
   ▼
POST /platform/tenants
   │
   │   Backend, in ONE transaction:
   │     1. Create the `tenants` row (name, domain, status)
   │     2. Create a default `ai_config` row for the tenant
   │        ← without it the chatbot has no greeting and no FAQ,
   │          and the recommendation engine has no weights.
   │          A tenant created without ai_config has a BROKEN bot
   │          on day one, and nobody will know why.
   │     3. Seed default notification_rules ("new lead → email → agent")
   │        ← without this, their leads arrive and nobody is told
   │          (19-notification-rules.md §5)
   │     4. Seed starter CMS pages as drafts (About/Terms/Privacy)
   │     5. Invite the first admin (role = admin, tenant = this one)
   │
   ▼
The tenant admin gets an invite → sets a password → lands in an
empty-but-functional workspace                              [→ 01]
```

**Steps 2–4 are the difference between a tenant that works on day one and a tenant that files three support tickets in week one.** They aren't in any doc — they're the practical consequence of every "first-time state" in this doc set. Provision defaults, don't provision emptiness.

### 4.2 Suspension

```
Super admin suspends a tenant (non-payment, abuse, offboarding)
   │
   ▼
PUT /platform/tenants/{id}  { status: 'suspended' }
   │
   ▼
What does "suspended" actually DO? Nothing in the doc set says.
   │
   ├─ Does the public site go dark? (Their customers see... what?)
   ├─ Can admins still log in and export their data?
   ├─ Do the AI endpoints stop? (They cost us money per call.)
   └─ Is the data retained, and for how long?
   │
   ▼
⚠ `tenants.status` exists as a column with three values and NO
   defined behavior anywhere. See §11 — this needs deciding before
   anyone can be suspended, and it will be needed the first time
   someone doesn't pay.
```

---

## 5. States

| State | Behavior |
|---|---|
| Loading | Skeleton |
| Empty (no tenants) | Only true on day zero of the platform |
| Trial expiring | Highlight. Billing is out of scope (`00-project-overview.md` §4) — but a *trial status* that nothing acts on is a column that lies |
| Suspended | Red. And the behavior must be defined (§4.2) |
| Creating | The multi-step provisioning above; a partial failure leaves a broken tenant — **it must be one transaction** |

---

## 6. API Calls

| Trigger | Call | Notes |
|---|---|---|
| List | `GET /platform/tenants` | `super_admin` only. `04-api-spec.md` §15 |
| Create | `POST /platform/tenants` | |
| Update status/plan | `PUT /platform/tenants/{id}` | |
| Usage stats | *(none)* | FR16.1 says "view tenant status/usage" — no endpoint returns usage |
| Delete a tenant | *(none)* | Deliberately absent, and that's correct — see §9 |

---

## 7. Data Touched

| Table | Access |
|---|---|
| `tenants` | Read / Write — **platform-level, outside the RLS pattern** |
| `users` | Write (the first admin invite) |
| `ai_config` | Write (defaults on provision) |
| `notification_rules`, `cms_pages` | Write (seeded defaults) |
| Everything else | Read (usage counts across tenants) |
| *`audit_log`* | **Every super_admin action must be logged — into the affected tenant's log** ([12](12-audit-log.md) §8). A platform operator touching a customer's workspace is exactly what an audit trail is for |

---

## 8. Roles & Permissions

| Action | `customer` | `agent` | `admin` | `super_admin` |
|---|---|---|---|---|
| Anything on `/platform/*` | ❌ | ❌ | ❌ | ✅ |

**This is the most sensitive permission boundary in the system.**

- `08-auth-roles-spec.md` §5.1: `/platform/tenants` is `super_admin` **only**. Not "admin can see their own row" — **only**.
- **`tenants` sits outside RLS** (`.claude/rules/database.md`: it's the table `tenant_id` references, and is not itself tenant-scoped). **So there is no database backstop here.** Every other table in the system has RLS catching an application bug; this one does not. The `require_role(["super_admin"])` dependency is the *only* thing standing between an authenticated user and every tenant's row.
- **A tenant admin must never be able to become a `super_admin`** ([11](11-users-roles.md) §8) — that's the escalation path *into* this page, and it must be closed at both the invite and role-change endpoints.
- Every action here is cross-tenant by nature, which makes the audit log (Gap A1) more important on this screen than anywhere else in the product.

---

## 9. Validation & Edge Cases

- **Subdomain/domain uniqueness** — the tenant resolver's key. Must be `UNIQUE` at the database level ([20](20-tenant-branding.md) §9). Two tenants on one domain is not a validation error; it's a data breach.
- **Reserved subdomains:** `www`, `app`, `admin`, `api`, `mail`, `platform`.
- **Creating a tenant with no admin** produces an inaccessible workspace. Require the first admin's email at creation (§4.1).
- **The first-admin email already exists** (they're an admin of another tenant, or a customer) — the same one-`auth_user_id`-per-`users`-row collision as [01](01-login-and-invite.md) §9. **A consultant who admins two brokerages is a completely ordinary case**, and the current model can't represent it.
- **Deleting a tenant** must not be possible from the UI. It would cascade into every table in the system — properties, leads, chat transcripts, and other people's personal data. Offboarding is `suspended` + an explicit, deliberate, out-of-band data-retention process. **Not a button.**
- **Usage counts across all tenants** are the one legitimate cross-tenant query in the system. They must be aggregate-only. A super admin browsing an individual tenant's *leads* is a different and much more invasive thing than counting them (§11).
- **Suspension behavior is undefined** (§4.2).

---

## 10. Acceptance Criteria

| ID | Case | Source |
|---|---|---|
| TC-TENANT-03 | A super admin can create a tenant, and it's fully isolated from every existing tenant | Sprint 9 |
| — | A newly created tenant has a working chatbot config, notification rules, and starter CMS pages | §4.1 |
| TC-SEC-01 | A tenant `admin` calling any `/platform/*` endpoint gets a **403** | Sprint 11 |
| — | A tenant admin cannot escalate themselves to `super_admin` | Security test |
| — | Two tenants cannot share a domain | Security test |
| — | Every super_admin action appears in the affected tenant's audit log | [12](12-audit-log.md) §8 |

---

## 11. Open Questions

- [ ] **What does `status = 'suspended'` actually do?** (§4.2). The column exists with no defined behavior. Public site dark? Admin login blocked? AI endpoints disabled (they cost real money per call)? Data retained how long? **Decide in `01-prd.md` before the first non-paying customer forces the question.**
- [ ] **What does `trial` do?** Same problem. Billing is out of scope, so a trial that expires into... nothing... is a column that lies to whoever reads it.
- [ ] **No usage endpoint**, though FR16.1 requires "view tenant status/usage". What counts as usage — properties, leads, **AI calls** (the actual cost driver)? If the platform is paying for Bedrock per tenant, **per-tenant AI cost is the number that matters most on this page** and nothing currently records it. (The proposed `search_queries` table in [16](16-ai-config-search-insights.md) §11 would give you half of it.)
- [ ] **"View as tenant" / impersonation** — enormously useful for support, and enormously dangerous. If it ships: it must be **audited into the tenant's own log**, time-limited, read-only by default, and the tenant should arguably be *told* it happened. If it doesn't ship, support has no way to reproduce a tenant's bug. Not mentioned anywhere in the doc set; it will be requested in month two.
- [ ] **One person administering two tenants** is unrepresentable today (§9).
- [ ] **Cross-tenant platform health** (aggregate AI latency, error rates, search-fallback rates) would be genuinely valuable here — it's how you'd catch a prompt regression affecting every tenant at once. Currently there's no such view.
