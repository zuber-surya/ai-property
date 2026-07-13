# Pages: Register & Login

> **Routes:** `/register`, `/login` (+ password reset callback) · **PRD Module:** 7 · **App:** `public-site/` → `pages/Auth/`
> Part of [Doc 16 — Customer Spec](README.md). Read [`README.md` §4](README.md#4-cross-cutting-rules-for-every-customer-page) first.
> Spec: `08-auth-roles-spec.md`

---

## 1. Purpose & Traceability

Registration exists for exactly one reason: **to persist things across sessions.** It is never a gate. A visitor who never registers can still search, chat, favorite, run the wizard, and inquire.

That framing dictates the design: the signup form is small, appears in context (a modal, right after the action that motivated it), and returns the visitor to exactly where they were.

| Requirement | Source |
|---|---|
| Customer registration/login via Supabase Auth | `08-auth-roles-spec.md` §2.1 |
| Anonymous session data migrates to the account on register/login | `08-auth-roles-spec.md` §4 |
| Favoriting prompts registration *after* the action, not before | `13-ui-ux-flows.md` §2.1, FR4.4 |
| Admin users are **invited**, never self-registered | `08-auth-roles-spec.md` §2.2 |

**Critical:** this page registers `customer` role users **only**. Agents and admins are invited into the [admin portal](../17-admin-spec/01-login-and-invite.md) — there must be no path from this form to an elevated role.

---

## 2. Entry & Exit Points

**Entry (in rough order of frequency):**

| Trigger | Presented as |
|---|---|
| Favorited a property, wants to keep it | **Modal**, over the current page |
| Finished the requirement wizard, wants alerts | **Modal**, over the results |
| Clicked "Login" in the header | Full page `/login` |
| Clicked a "view your inquiry" link in an email | Full page `/login?next=/portal/inquiries` |
| Tried to open `/portal/*` while logged out | Redirect to `/login?next=<original>` |

**Exit:** back to `next` if present, else `/portal`. **A modal signup never navigates away** — it closes and the underlying page updates (the heart is now persisted).

---

## 3. Layout & Regions

```
┌───────────────────────── modal / page ──────────────────────┐
│                                                       [ × ] │
│   Save your favorites                                       │
│   Create an account to keep this — it takes 20 seconds.     │
│   ─────────────────────────────────────────────────────     │
│                                                             │
│   Full name                                                 │
│   [_______________________________________]                 │
│                                                             │
│   Email                                                     │
│   [_______________________________________]                 │
│                                                             │
│   Phone (optional)                                          │
│   [_______________________________________]                 │
│                                                             │
│   Password                                                  │
│   [_______________________________________] 👁              │
│   ▪▪▪▪▫▫  Strong enough                                     │
│                                                             │
│              [      Create account      ]                   │
│                                                             │
│   Already have an account?  Log in                          │
│   ─────────────────────────────────────────────────────     │
│   By continuing you agree to the Terms and Privacy Policy.  │
└─────────────────────────────────────────────────────────────┘
```

**Login is the same shell, two fields:** email + password, a "Forgot password?" link, and a "Create one" link.

| Region | Contents |
|---|---|
| Contextual headline | **Changes based on entry point** — "Save your favorites", "Get alerts for new matches", or a neutral "Welcome back". The headline should name the thing they're about to keep |
| Fields | Name, email, phone (optional), password |
| Password strength | Live meter; enforce a minimum, don't enforce baroque character rules |
| Legal | Terms/Privacy links → [CMS pages](12-static-cms-pages.md) |

---

## 4. Workflow

### 4.1 Registration

```
Visitor submits the register form
   │
   ▼
React app calls Supabase Auth (signUp) directly via the Supabase JS client
   │   — FastAPI does not store passwords (08-auth-roles-spec.md §1)
   │
   ├─ Email already registered → "That email already has an account. Log in?"
   │                              (do NOT reveal more than the user already knows)
   │
   ▼
Supabase returns a JWT + auth_user_id
   │
   ▼
POST /auth/register  { auth_user_id-bearing JWT, full_name, phone, session_id }
   │
   │   Backend:
   │     1. Create a `users` row: role = 'customer',
   │        tenant_id = the domain-resolved tenant, auth_user_id = <from JWT>
   │     2. MIGRATE the anonymous session (08-auth-roles-spec.md §4):
   │          favorites             where session_id = X → set user_id
   │          requirement_profiles  where session_id = X → set user_id
   │          chat_conversations    where session_id = X → set user_id
   │     3. Return the user profile
   │
   ▼
Client stores the session (Supabase JS handles refresh)
   │
   ▼
Modal closes → the underlying page re-renders as logged-in
(or: redirect to `next`, else /portal)
```

### 4.2 Login

```
Submit → Supabase Auth (signInWithPassword) → JWT
   │
   ▼
GET /auth/me  → { user_id, full_name, role, tenant_id }
   │
   ├─ role != 'customer'  → this is an admin/agent on the public site.
   │                        Allowed (they may also browse), but the header
   │                        should offer a link to the admin portal.
   │                        The customer portal must still only show
   │                        THEIR OWN data — role does not grant extra
   │                        visibility here.
   │
   ▼
Session-data migration runs again (a returning user may have
anonymous favorites from this device — see §9, merge behavior)
   │
   ▼
Redirect to `next` or /portal
```

### 4.3 Password Reset
Fully delegated to Supabase Auth's built-in reset email / magic link (`08-auth-roles-spec.md` §2.3). The app only handles the redirect/callback route and shows a "set a new password" form.

---

## 5. States

| State | Behavior |
|---|---|
| Default | Empty form, contextual headline |
| Submitting | Button disabled + spinner; fields locked |
| Email taken (register) | Inline error + a one-click switch to Login, **carrying the email over** |
| Bad credentials (login) | Generic "Email or password is incorrect" — never "no such user" (that's a user-enumeration oracle) |
| Email unverified | Depends on whether Supabase email confirmation is enabled — see §11 |
| Rate-limited | Supabase enforces its own auth rate limits; surface them as "Too many attempts, try again shortly" |
| Network failure mid-migration | **The dangerous one.** The Supabase account now exists but the `users` row / migration may not. See §9 |
| Already logged in | `/login` and `/register` redirect straight to `/portal` |

---

## 6. API Calls

| Trigger | Call | Notes |
|---|---|---|
| Register (step 1) | Supabase Auth `signUp` (client SDK) | Not a FastAPI call |
| Register (step 2) | `POST /auth/register` | Creates the `users` row + migrates session data. `04-api-spec.md` §2 |
| Login (step 1) | Supabase Auth `signInWithPassword` (client SDK) | Not a FastAPI call |
| Login (step 2) | `GET /auth/me` | Returns role + tenant; **the `users` table is the source of truth, not the JWT claims** (`08-auth-roles-spec.md` §1) |
| Logout | `POST /auth/logout` | Plus clearing the client session |

---

## 7. Data Touched

| Table | Access |
|---|---|
| `users` | Write (create the `customer` row, linked to `auth_user_id`) |
| `favorites` | Update (`session_id` → `user_id`) |
| `requirement_profiles` | Update (`session_id` → `user_id`) |
| `chat_conversations` | Update (`session_id` → `user_id`) |
| `tenants` | Read (which tenant this customer belongs to — from the domain) |
| Supabase `auth.users` | Write (managed by Supabase, not by us) |

---

## 8. Permissions & Tenancy

- **A customer belongs to exactly one tenant** — the one whose domain they registered on. `users.tenant_id` is set from the domain, never from client input.
- **The same email registering on two tenants' sites** creates a *single* Supabase auth identity but needs *two* `users` rows (one per tenant), or it breaks the "one user, one tenant" model. **This is unresolved** — see §11. It is a real scenario (a buyer shopping across two brokerages) and it will surface in testing.
- **Role escalation is impossible from this form:** `POST /auth/register` hardcodes `role = 'customer'`. It must ignore any client-supplied role field entirely — not validate it, *ignore* it.
- **`next` redirect must be validated** — only allow same-origin relative paths, or it's an open-redirect phishing vector.

---

## 9. Validation & Edge Cases

- **Name:** required, trimmed. **Email:** required, well-formed, lowercased before storage. **Phone:** optional here (unlike lead capture, where it's the point), but it's what an agent will actually use — worth asking for.
- **Password:** minimum length enforced by Supabase policy; show the rule *before* they fail it.
- **The partial-registration hole:** if Supabase `signUp` succeeds but `POST /auth/register` fails, the user has an auth identity with no `users` row — they can "log in" and every authenticated call 500s. **Mitigation:** `GET /auth/me` must create the missing `users` row on demand (idempotent, self-healing) rather than assuming it exists. Do not rely on the registration call having succeeded.
- **Merge behavior on login (`08-auth-roles-spec.md` §6, open):** a returning user logs in on a device that has anonymous favorites. Recommended: **union** the anonymous session's favorites into the account (deduplicated on `property_id`), and for `requirement_profiles`, keep both — the account's existing one and the new anonymous one — rather than overwriting. Silently destroying a saved profile is much worse than showing two.
- **Chat history migration:** an anonymous conversation that was already **escalated** and picked up by an agent must keep its lead linkage when re-keyed to the user. Don't orphan it.

---

## 10. Acceptance Criteria

| ID | Case | Source |
|---|---|---|
| TC-AUTH-01 | A customer can register and log in; a `users` row is created with `role = customer` | Sprint 1 |
| TC-AUTH-02 | Role/tenant is read from the `users` table, not the JWT — a role change takes effect immediately | Sprint 1 |
| TC-TENANT-01 | A customer registered on tenant A's domain is scoped to tenant A only | Sprint 1 |
| — | Favoriting anonymously, then registering, preserves the favorite | FR4.4, `13-ui-ux-flows.md` §2.1 |
| TC-SEC-01 | A customer cannot reach any admin endpoint (403) regardless of what they send | Sprint 11 |

---

## 11. Open Questions

- [ ] **Same email across two tenants.** Does that person get two `users` rows sharing one `auth_user_id`? (That breaks the current lookup, which assumes `auth_user_id` → one user.) Or are customer accounts strictly per-tenant with separate credentials? **This needs a decision in `08-auth-roles-spec.md` before Sprint 1** — it's a schema-level constraint, not a UI choice.
- [ ] Whether email verification is required before the account is usable, or whether the account works immediately and verification is a nudge. (Requiring it will hurt the "favorite → register" conversion flow this whole design is built around.)
- [ ] Social login (Google) at MVP — open in `08-auth-roles-spec.md` §6.
- [ ] The exact merge rules in §9 need product sign-off; they're currently my recommendation, not a decision.
