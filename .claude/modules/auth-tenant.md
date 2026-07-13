# Module: Auth / Tenant / Roles

Covers PRD Module 11 (User & Role Management) and Module 16 (Tenant & Branding Settings). **Build this first** — every other module assumes auth and tenant scoping work (Sprint 1, `docs/15` §4).

**Read:** `docs/08-auth-roles-spec.md`, `docs/03-database-schema.md` §3.1–3.3, `docs/02-architecture.md` §3/§7.
**Rules:** `.claude/rules/security.md` (primary), plus `backend`, `database`, `testing`.

## Tables
`tenants` (platform-level, not tenant-scoped), `users`, `roles_permissions`.

## Key requirements
- Supabase Auth issues JWTs; `app/core/security.py` verifies them and extracts `user_id` + role.
- The `users` table (not the JWT) is the source of truth for role/tenant — role changes take effect immediately.
- `require_role` / permission dependency enforces access **server-side** (403 on out-of-scope API calls).
- `tenant_id` resolution: admin portal → user's tenant association; public site → request domain/subdomain (`app/core/tenancy.py`).
- Anonymous session handling via `X-Session-Id`; data migrates to the account on register/login.
- FR11.1 granular per-feature permissions; FR11.2 invite flow; FR11.3 audit log (actor, action, entity, timestamp).
- FR16.1 super admin manages tenants; FR16.2 tenant branding (logo, colors, custom domain) applies to that tenant's public site only.

## Acceptance / test cases (from `docs/15`)
- `TC-AUTH-01` valid JWT resolves the correct `users` row + role.
- `TC-AUTH-02` expired/invalid JWT rejected on a protected route.
- `TC-TENANT-01` Tenant A user cannot read/write Tenant B rows — for **every** tenant-owned table — failing at the DB layer.
- `TC-TENANT-02` anonymous session data scoped by `session_id`.
- Restricted role cannot call out-of-scope APIs (server-side, not just hidden UI).
