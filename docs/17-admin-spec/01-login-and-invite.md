# Page: Admin Login & Invite Acceptance

> **Routes:** `/admin/login`, `/admin/accept-invite?token=…` · **PRD Module:** 11 · **App:** `admin-portal/`
> Part of [Doc 17 — Admin Spec](README.md). Read [`README.md` §4](README.md#4-cross-cutting-rules-for-every-admin-page) first.
> Spec: `08-auth-roles-spec.md`

---

## 1. Purpose & Traceability

The door to the CRM. Two entry paths, and the distinction matters:

- **Login** — an existing agent/admin/super_admin.
- **Invite acceptance** — a new admin-portal user setting their password for the first time.

**There is no self-registration.** Admin-portal users are *invited* by an existing admin or super admin (`08-auth-roles-spec.md` §2.2). A public "create an admin account" form would be a privilege-escalation hole with a nice UI.

| Requirement | Source |
|---|---|
| FR11.2 Invite flow for new admin-portal users | `01-prd.md` §12 |
| Supabase Auth is the identity provider for all users | `08-auth-roles-spec.md` §1 |
| The `users` table — not the JWT — is the source of truth for role/tenant | `08-auth-roles-spec.md` §1 |
| Role permissions enforced server-side | `08-auth-roles-spec.md` §5 |

---

## 2. Entry & Exit Points

**Entry:** direct visit to the admin domain; a session expiring mid-work (→ login, then back to where they were); an invite email link.

**Exit:** `/admin/dashboard` — or, for an `agent`, straight to `/admin/leads` filtered to "assigned to me". **Send each role where their work actually is.** An agent has no use for a KPI dashboard they can barely see.

---

## 3. Layout & Regions

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│                  PropVista                          │  ← platform brand,
│                  ──────────                         │    NOT tenant brand
│                                                     │    (README §4.5)
│         Sign in to your workspace                   │
│                                                     │
│    Email                                            │
│    [_____________________________________]          │
│                                                     │
│    Password                                         │
│    [_____________________________________] 👁       │
│                                                     │
│    [           Sign in            ]                 │
│                                                     │
│    Forgot your password?                            │
│                                                     │
│    ───────────────────────────────────────          │
│    Need access? Ask your administrator              │
│    to invite you.       ← no self-signup link.      │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Invite acceptance** is the same shell: the email is pre-filled and locked, and the user sets a password. The invite's role and tenant were fixed by the inviter and are **not** shown as editable fields — not even disabled ones. They aren't the invitee's business.

---

## 4. Workflow

### 4.1 Login

```
Submit email + password
   │
   ▼
Supabase Auth signInWithPassword (client SDK) → JWT
   │   FastAPI never sees the password (08-auth-roles-spec.md §1)
   │
   ▼
GET /auth/me   (Authorization: Bearer <jwt>)
   │
   │   Backend: verify the JWT → extract auth_user_id →
   │            look up the `users` row → return role + tenant_id
   │            ← the users TABLE is authoritative, not the JWT claims,
   │              so a revoked role takes effect on the next request,
   │              not on the next token refresh
   ▼
Role check
   │
   ├─ role = 'customer'  → ❌ REJECT. "This account doesn't have admin
   │                         access." Sign them out of the admin app.
   │                         A customer JWT is a valid JWT — the admin
   │                         portal must check the ROLE, not just the
   │                         signature.
   │
   ├─ is_active = false  → ❌ REJECT. A deactivated user holding a still
   │                         -valid JWT must be locked out immediately.
   │                         This is exactly why the users table is
   │                         authoritative.
   │
   ├─ role = 'agent'       → /admin/leads?assigned=me
   ├─ role = 'admin'       → /admin/dashboard
   └─ role = 'super_admin' → /platform/tenants
```

### 4.2 Invite (the admin's side → [11-users-roles.md](11-users-roles.md))

```
Admin fills: email + role (+ tenant, if super_admin)
   │
   ▼
POST /admin/users/invite
   │
   │   Backend:
   │     1. Create a Supabase Auth invite (or a pending `users` row + token)
   │     2. Pre-populate the `users` row: role + tenant_id, set by the
   │        INVITER — never by the invitee
   │     3. Email the invite link
   ▼
Invitee clicks the link → /admin/accept-invite?token=…
   │
   ▼
Sets a password → Supabase Auth completes the signup
   │
   ▼
The `users` row activates with its pre-set role and tenant
   │
   ▼
Redirect to the role's landing page
```

**The security property:** the invitee never supplies their own role or tenant. Those come from the pre-created `users` row. If the accept-invite endpoint accepted a role from the request body, any invited agent could make themselves an admin.

---

## 5. States

| State | Behavior |
|---|---|
| Default | Empty form |
| Submitting | Button disabled + spinner |
| Bad credentials | **Generic** "Email or password is incorrect." Never "no such user" — that's a user-enumeration oracle, and on an admin portal it tells an attacker which emails are staff |
| Customer account on the admin portal | Clear rejection + a link to the public site |
| Deactivated user (`is_active = false`) | "This account has been deactivated. Contact your administrator." |
| Invite expired | "This invite has expired. Ask your administrator to send a new one." Never auto-extend it |
| Invite already used | Redirect to normal login |
| Session expired mid-work | Return to login with a `next` param, and **preserve unsaved form state where feasible** — losing 20 minutes of a property listing to a token expiry is a genuine, avoidable insult |
| Rate-limited | Supabase's own auth throttling; surface it plainly |

---

## 6. API Calls

| Trigger | Call | Notes |
|---|---|---|
| Sign in | Supabase Auth `signInWithPassword` (client SDK) | Not a FastAPI call |
| Post-login | `GET /auth/me` | Returns role + tenant from the `users` table. `04-api-spec.md` §2 |
| Sign out | `POST /auth/logout` | Plus clearing the client session |
| Send an invite | `POST /admin/users/invite` | Admin-only. `04-api-spec.md` §10 |
| Password reset | Supabase built-in flow | `08-auth-roles-spec.md` §2.3 |

---

## 7. Data Touched

| Table | Access |
|---|---|
| `users` | Read (role, tenant, `is_active`); Write on invite |
| `tenants` | Read (which tenant the user belongs to) |
| Supabase `auth.users` | Managed by Supabase |
| *`audit_log`* | Should record invites sent and role assignments — **table doesn't exist (Gap A1)** |

---

## 8. Roles & Permissions

| Action | `agent` | `admin` | `super_admin` |
|---|---|---|---|
| Log in to the admin portal | ✅ | ✅ | ✅ |
| Invite a user | ❌ | ✅ (within their tenant) | ✅ (any tenant) |
| Assign the `admin` role | ❌ | ✅ | ✅ |
| Assign `super_admin` | ❌ | **❌ — must be impossible** | ✅ |

**A tenant admin must not be able to mint a `super_admin`.** That's a platform-wide privilege escalation from a tenant-level account. `POST /admin/users/invite` must reject `role = 'super_admin'` unless the caller *is* one. Test it explicitly — it's the kind of check that's obvious in review and absent in code.

---

## 9. Validation & Edge Cases

- **A customer's email is later invited as an agent.** Same person, same Supabase identity, now needs a *second* `users` row with a different role — which collides with the "one `users` row per `auth_user_id`" assumption. **Same unresolved problem as the customer side** (`16-customer-spec/06` §11). It will come up: brokerage staff browse their own listings.
- **Invite token security:** single-use, expiring, cryptographically random. It's a credential that grants a role — treat it like one.
- **Never leak tenant membership:** the login form must not reveal, before authentication, whether an email exists or which tenant it belongs to.
- **Deactivation must be immediate.** Because role/status is read from `users` on **every** request (not from the JWT), a deactivated user is locked out on their next call. This is a real benefit of the design and it should be tested (`TC-AUTH-02`).
- **Session length:** agents work all day. A short JWT + silent refresh (handled by the Supabase JS client) is right; a hard 1-hour re-login is not.

---

## 10. Acceptance Criteria

| ID | Case | Source |
|---|---|---|
| TC-AUTH-01 | An invited admin/agent can accept, set a password, and log in | Sprint 1 |
| TC-AUTH-02 | A role change in the `users` table takes effect **immediately**, without a new token | Sprint 1 |
| TC-ROLE-01 | An `agent` calling an admin-only endpoint gets a 403 | Sprint 8 |
| TC-SEC-01 | A `customer` JWT cannot access any `/admin/*` endpoint | Sprint 11 |
| — | A tenant `admin` cannot invite a `super_admin` | Security test |
| — | A deactivated user with a valid JWT is refused | Security test |

---

## 11. Open Questions

- [ ] **One person, two roles** (customer on the public site + agent in the portal) — the `auth_user_id` → single `users` row assumption breaks. Needs a decision in `08-auth-roles-spec.md`, and it's the same open item as the customer side.
- [ ] **Granular sub-roles** (Marketing, Support) via `roles_permissions` — ship at MVP or defer to the four fixed roles? Open in `08-auth-roles-spec.md` §6. **Recommend deferring**; the four roles cover every flow in this doc set, and the granular layer adds a permission-check surface to get wrong.
- [ ] Whether admin login should require **2FA**. It's a CRM holding customer PII across tenants — Supabase Auth supports MFA. Not mentioned anywhere in the doc set, and it should be at least a deliberate deferral rather than an oversight.
- [ ] Invite expiry window (48h? 7 days?) — unspecified.
