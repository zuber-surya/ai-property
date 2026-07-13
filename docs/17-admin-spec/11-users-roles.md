# Page: User & Role Management

> **Route:** `/admin/users` · **PRD Module:** 11 · **App:** `admin-portal/` → `pages/Users/`
> Part of [Doc 17 — Admin Spec](README.md). Read [`README.md` §4](README.md#4-cross-cutting-rules-for-every-admin-page) first.

---

## 1. Purpose & Traceability

Who can get in, and what they can do once they're in. This is the **security-critical** screen of the admin portal: every other page's permission model is only as good as this one's correctness.

It manages *access* — the performance view of the same people lives in [Agents](10-agents.md).

| Requirement | Source |
|---|---|
| FR11.1 Role creation (Admin, Sales Agent, Marketing, Support, Super Admin) with granular per-feature permissions | `01-prd.md` §12 |
| FR11.2 Invite flow for new admin-portal users | `01-prd.md` §12 → [01](01-login-and-invite.md) |
| FR11.3 Audit log of admin actions | `01-prd.md` §12 → [12](12-audit-log.md) |
| Acceptance: **a restricted role cannot access or call APIs outside its permission set — enforced server-side, not just hidden in the UI** | `01-prd.md` §12 |

---

## 2. Entry & Exit Points

**Entry:** sidebar (admin only — the nav item should not even render for an agent); "Invite your team" from an empty [Agents](10-agents.md) list or the Dashboard onboarding checklist.

**Exit:** [Audit log](12-audit-log.md); an agent's name → their [performance profile](10-agents.md).

---

## 3. Layout & Regions

```
┌──────────┬───────────────────────────────────────────────────────────┐
│ SIDEBAR  │  Users                    [ Audit log ]  [ + Invite user ]│
│          │                                                           │
│          │  ┌─────────────────────────────────────────────────────┐  │
│          │  │ Name       │ Email          │ Role   │Status │  ⋯   │  │
│          │  ├─────────────────────────────────────────────────────┤  │
│          │  │ Vikram S.  │ vikram@t.com   │ Admin  │Active │  ⋯   │  │
│          │  │            │                │        │       │      │  │
│          │  │ Anjali M.  │ anjali@t.com   │ Agent  │Active │  ⋯   │  │
│          │  │ Ravi K.    │ ravi@t.com     │ Agent  │Active │  ⋯   │  │
│          │  │ Meera N.   │ meera@t.com    │ Agent  │Invited│  ⋯   │  │
│          │  │            │                │        │ ↳ resend     │  │
│          │  │ Old User   │ old@t.com      │ Agent  │Inactive  ⋯   │  │
│          │  └─────────────────────────────────────────────────────┘  │
│          │                                                           │
│          │  ┌─── Invite a user ────────────────────────────────┐     │
│          │  │  Email *   [_______________________________]     │     │
│          │  │                                                  │     │
│          │  │  Role *    ( ) Admin    — full access to         │     │
│          │  │                            everything in your    │     │
│          │  │                            workspace             │     │
│          │  │            (•) Agent    — their assigned leads   │     │
│          │  │                            only                  │     │
│          │  │                                                  │     │
│          │  │            ← NO super_admin option here, ever.   │     │
│          │  │                                                  │     │
│          │  │            [ Send invite ]                       │     │
│          │  └──────────────────────────────────────────────────┘     │
└──────────┴───────────────────────────────────────────────────────────┘
```

| Region | Contents |
|---|---|
| User table | Name, email, role, status (Active / Invited / Inactive), row menu |
| Row menu | Change role · Resend invite · **Deactivate** (never "Delete" — see §9) |
| Invite form | Email + role. **The role list a tenant admin sees must not contain `super_admin`** |
| Role descriptions | Written in plain language. An admin choosing a role from a bare enum will choose wrong |

---

## 4. Workflow

```
Admin opens /admin/users
   │
   ▼
GET /admin/users   → tenant's admin-portal users
   │                 (customers are NOT listed here — they're not
   │                  portal users, and mixing them in would make this
   │                  table useless the moment the tenant has 500 buyers)
   ▼
Table renders
   │
   ├─→ [ + Invite user ]
   │        │
   │        ▼
   │   Email + role → POST /admin/users/invite
   │        │
   │        │   Backend:
   │        │     · role and tenant are set BY THE INVITER
   │        │     · reject role = 'super_admin' unless the caller is one
   │        │     · create the pending users row + send the invite
   │        ▼
   │   Status = Invited → the invitee accepts → Active     [→ 01]
   │
   ├─→ Row → Change role
   │        │
   │        ▼
   │   PUT /admin/users/{id}/role
   │        │
   │        ▼
   │   ⚡ TAKES EFFECT IMMEDIATELY — the users table is the source of
   │      truth, not the JWT (08-auth-roles-spec.md §1). The user does
   │      not need to log out and back in. Demoting a compromised admin
   │      locks them out on their very next request.
   │      This is a real security property. Test it (TC-AUTH-02).
   │
   └─→ Row → Deactivate
            │
            ▼
        DELETE /admin/users/{id}   → is_active = false (soft)
            │
            ▼
        ⚠ FIRST: what happens to their 14 open leads?
          Prompt to reassign. Do NOT silently orphan them. (§9)
```

---

## 5. States

| State | Behavior |
|---|---|
| Loading | Skeleton rows |
| Only one user (the founding admin) | "Invite your team" is the primary CTA |
| Invited, not accepted | Status = Invited, with **Resend** and **Revoke** |
| Invite expired | Clearly marked; Resend generates a **new** token |
| Deactivated user | Muted row, still listed (their name appears on historical leads and must resolve) |
| **Last admin** | **Cannot be deactivated or demoted.** A tenant with zero admins is locked out of their own workspace and needs support intervention. Block it, with an explanation — this is a trivially reachable state and an entirely preventable support ticket |
| Self | An admin **cannot change their own role or deactivate themselves.** Same reason |
| `agent` role | This page must be **completely unreachable** — the nav item doesn't render, the route redirects, and every endpoint returns 403 |

---

## 6. API Calls

| Trigger | Call | Notes |
|---|---|---|
| Mount | `GET /admin/users` | Tenant's portal users. `04-api-spec.md` §10 |
| Invite | `POST /admin/users/invite` | |
| Change role | `PUT /admin/users/{id}/role` | |
| Deactivate | `DELETE /admin/users/{id}` | **Soft** — sets `is_active = false` |
| Audit log | `GET /admin/audit-log` | ⚠ **no table exists (Gap A1)** → [12](12-audit-log.md) |
| Resend / revoke invite | *(none)* | Not in the API spec; both are needed in practice |

---

## 7. Data Touched

| Table | Access |
|---|---|
| `users` | Read / Write (`role`, `is_active`) — **tenant-scoped** |
| `roles_permissions` | Read/Write **if** granular sub-roles ship (see §11) |
| `leads` | Read/Update (reassignment on deactivation) |
| Supabase `auth.users` | Write (invites) |
| *`audit_log`* | **Every action on this page must be logged — and the table doesn't exist (A1).** Of all the places to be missing an audit trail, "who granted whom admin access" is the worst |

---

## 8. Roles & Permissions

| Action | `agent` | `admin` | `super_admin` |
|---|---|---|---|
| View users | ❌ | ✅ (own tenant) | ✅ (any) |
| Invite `agent` | ❌ | ✅ | ✅ |
| Invite `admin` | ❌ | ✅ | ✅ |
| **Invite/grant `super_admin`** | ❌ | **❌ — must be impossible** | ✅ |
| Change a role | ❌ | ✅ (within tenant) | ✅ |
| Deactivate | ❌ | ✅ | ✅ |

**The two hard rules, both server-side:**

1. **A tenant admin can never create or promote to `super_admin`.** That's tenant → platform privilege escalation. `POST /admin/users/invite` and `PUT /admin/users/{id}/role` must both reject it unless the caller is already a `super_admin`. **Two endpoints, one rule — it is very easy to enforce it in one and forget the other.**
2. **A tenant admin can only touch users in their own tenant.** `PUT /admin/users/{id}/role` where the target belongs to another tenant → **404** (not 403 — don't confirm the user exists).

Per FR11.1's acceptance criterion, all of this is enforced by `require_role` dependencies, **never by hiding the UI**.

---

## 9. Validation & Edge Cases

- **Deactivating an agent with open leads.** Their 14 leads are still assigned to a user who can no longer log in. **They are now invisible on every board and nobody is working them.** Prompt: "Ravi has 14 open leads. Reassign to: [ ▾ ]" — and don't let the deactivation complete without an answer. This is the single most consequential edge case on the page.
- **Deactivating the last admin** — block (§5).
- **Self-demotion / self-deactivation** — block.
- **Re-inviting an existing email** — don't create a duplicate. Offer to resend or reactivate.
- **A customer's email invited as an agent** — the same `auth_user_id` → one `users` row collision as [01](01-login-and-invite.md) §9. Unresolved.
- **Role change while the user is mid-session:** takes effect on the next request. That's correct — and it means an agent could be looking at a screen their role no longer permits. The API returns 403; the frontend must handle that gracefully (redirect, don't crash).
- **Email is PII.** The user list is tenant-scoped, but that's a second layer — RLS on `users` is the first.

---

## 10. Acceptance Criteria

| ID | Case | Source |
|---|---|---|
| TC-AUTH-01 | An invited user can accept and log in with the role they were given | Sprint 1 |
| TC-AUTH-02 | **A role change takes effect immediately, without re-login** | Sprint 1 |
| TC-ROLE-01 | A restricted role cannot call APIs outside its permission set — **server-side** (FR11.1 acceptance) | Sprint 8 |
| — | A tenant admin cannot create a `super_admin` (via invite **or** role change) | Security test |
| — | A tenant admin cannot modify a user in another tenant | Security test |
| — | The last admin cannot be deactivated | §5 |
| TC-SEC-01 | An agent gets a 403 on every `/admin/users*` endpoint | Sprint 11 |

---

## 11. Open Questions

- [ ] **Gap A1 — no `audit_log` table**, yet FR11.3 requires one and `GET /admin/audit-log` is specified. This page's actions (role grants, deactivations, invites) are the **most important things in the entire product to audit**. See [12](12-audit-log.md).
- [ ] **Granular sub-roles (FR11.1: "Marketing", "Support") — ship or defer?** Open in `08-auth-roles-spec.md` §6. **Recommend defer.** The four fixed roles cover every flow in this doc set; `roles_permissions` adds a second permission system that must be checked *everywhere* the first one is, and a permission model with two sources of truth is a permission model with holes. If it ships, `require_permission` must be as rigorously tested as `require_role`.
- [ ] **No resend/revoke-invite endpoints**, though both are needed the first week.
- [ ] **The deactivation → lead reassignment flow** (§9) needs a product decision: block until reassigned, auto-unassign, or auto-redistribute?
- [ ] Whether 2FA is required for the `admin` role ([01](01-login-and-invite.md) §11).
