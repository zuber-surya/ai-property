# Auth & Roles Specification — PropVista CRM

> **Doc 08 of the PropVista CRM documentation set.** Covers authentication flows and role/permission logic. Tenant data isolation (RLS policies) is already specified in `03-database-schema.md` Section 4 and `02-architecture.md` Section 3 — this doc does not repeat that; it focuses on *who* a user is and *what* they're allowed to do once authenticated.
>
> **Status:** Draft v1.0 · **Last updated:** July 2026
> Depends on: `01-prd.md` (Module 11), `02-architecture.md` (Section 7), `03-database-schema.md` (`users`, `roles_permissions`)

---

## 1. Authentication Provider

**Supabase Auth** is the identity provider for all users — customers, agents, admins, and super admins alike. FastAPI does not implement its own password/session storage; it verifies Supabase-issued JWTs on incoming requests.

```
Client (React) ──login/register──► Supabase Auth ──JWT──► Client
Client ──Authorization: Bearer <JWT>──► FastAPI ──verify──► request proceeds
```

- `core/security.py` (per `02-architecture.md`) verifies the JWT signature/expiry and extracts `auth_user_id`.
- The backend then looks up the corresponding row in the application's `users` table (`03-database-schema.md`) via `auth_user_id` to get `role`, `tenant_id`, and profile info — the JWT itself is not the source of truth for role/permissions, the `users` table is (so role changes take effect immediately, not only after a new token is issued).

---

## 2. Auth Flows

### 2.1 Customer Registration & Login
- Standard email/password (and optionally social login, e.g. Google — nice-to-have, not MVP-required) via Supabase Auth.
- On first registration, a corresponding `users` row is created with `role = 'customer'`.
- Anonymous browsing remains fully supported (Section 4) — registration is only required to persist favorites/requirement profiles/inquiry history across sessions (PRD Module 7).

### 2.2 Admin-Portal User Invitation (Agent/Admin)
- Admin-portal users are **not self-registered** — they're invited (`POST /admin/users/invite`, `04-api-spec.md` Section 10) by an existing admin or super admin.
- Invite flow: backend creates a Supabase Auth invite (or a pending `users` row + email link), the invitee sets a password on first login, and their `users` row is pre-populated with `role` and tenant association set by the inviter.

### 2.3 Password Reset / Email Verification
- Delegated to Supabase Auth's built-in flows (magic link / reset email) — no custom implementation needed at the FastAPI layer beyond redirect/callback handling.

### 2.4 Token Refresh & Expiry
- Supabase-issued JWTs are short-lived with a refresh token pattern, handled client-side by the Supabase JS client in the React app — FastAPI only ever validates the current access token per request, it does not manage refresh logic.

---

## 3. Role Model

Four base roles (per `03-database-schema.md` `users.role`):

| Role | Scope | Summary |
|---|---|---|
| `customer` | Public site / Customer Portal | Browses, searches, chats, saves favorites/requirements, tracks own inquiries |
| `agent` | Admin Portal | Manages assigned leads, updates own profile, views own performance |
| `admin` | Admin Portal (tenant-level) | Full access within their tenant: properties, leads, users, reports, AI config, branding |
| `super_admin` | Admin Portal (platform-level) | Manages tenants themselves (`tenants` table); not scoped to a single tenant |

### 3.1 Granular Permissions (Optional Layer)

Per PRD Module 11 / `roles_permissions` table (`03-database-schema.md`), tenants can optionally define custom sub-roles (e.g. "Marketing" or "Support") with a feature-level permission map (`{"properties.edit": true, "reports.view": false}`), layered **on top of** the base role, not replacing it. MVP can ship with just the four fixed roles and defer custom sub-roles if it simplifies initial delivery (flagged as an open question, Section 6).

---

## 4. Anonymous (Unauthenticated) Access

Per PRD FR — visitors must be able to browse, search, use the chatbot, and submit inquiries without an account:
- No `users` row or JWT required for these actions.
- A client-generated `session_id` (sent via `X-Session-Id` header, per `04-api-spec.md` Section 1) tracks favorites, chat conversation, and requirement profile for the duration of the anonymous session.
- On registration/login, anonymous session data (favorites, chat history, requirement profile) is migrated to the new `user_id` — favorites/`requirement_profiles`/`chat_conversations` rows get their `session_id`-matched records reassigned to `user_id` (implementation detail for the registration flow).

---

## 5. Permission Enforcement (Backend)

- Enforcement happens **server-side, at the API layer**, via FastAPI dependencies — never relying on the frontend hiding UI elements as the actual security boundary.
- Pattern (conceptual):
  ```python
  @router.post("/admin/properties")
  def create_property(payload: PropertyCreate, user: User = Depends(require_role(["admin"]))):
      ...
  ```
- A `require_role([...])` (and, where needed, a more granular `require_permission("properties.edit")`) dependency checks the resolved `users.role` (and `roles_permissions` map, if used) before the route body executes.
- Agents are further scoped to **their own assigned leads/properties** where relevant (e.g. an agent can update notes only on leads assigned to them) — enforced as an additional ownership check within the service layer, not just a role check.

### 5.1 Route Protection Matrix (Representative)

| Endpoint Group | `customer` | `agent` | `admin` | `super_admin` |
|---|---|---|---|---|
| Public site (search/chat/browse) | ✅ (own session) | – | – | – |
| Customer Portal | ✅ (own data) | – | – | – |
| Admin Dashboard/Reports | – | Partial (own performance only) | ✅ | ✅ (cross-tenant view, if applicable) |
| Property Management | – | Read + limited update (assigned) | ✅ | ✅ |
| Lead/CRM Pipeline | – | ✅ (assigned leads) | ✅ (all tenant leads) | ✅ |
| User & Role Management | – | – | ✅ | ✅ |
| AI Config | – | – | ✅ | ✅ |
| Tenant Management (`/platform/tenants`) | – | – | – | ✅ only |

This table is representative — the authoritative, enforced definition lives in code via the `require_role`/`require_permission` dependencies, not this document; keep this table updated as a human-readable reference when routes change.

---

## 6. Open Questions / Assumptions to Confirm

- [ ] Whether granular `roles_permissions` (custom sub-roles) ship at MVP or are deferred in favor of just the four fixed roles.
- [ ] Whether social login (Google, etc.) is included for customer registration at MVP or deferred.
- [ ] Exact ownership-scoping rules for agents beyond leads (e.g. can an agent edit a property they didn't create, or only view it) — needs product input.
- [ ] Session-to-account data migration edge cases (e.g. visitor already has a registered account's favorites and also anonymous-session favorites — merge behavior on login).

---

**Next document:** `09-coding-standards.md` — conventions for Claude Code to follow consistently across the backend and both frontend apps.
