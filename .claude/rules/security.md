# Rule: Security & Tenant Isolation

Applies to: every request path and query. Source: `docs/02-architecture.md` §3/§7/§10, `docs/08-auth-roles-spec.md`.

## Tenant isolation (non-negotiable)
- **Enforced at the DB layer via Postgres RLS**, not only application filtering. RLS is the primary safety net; app-level `tenant_id` filtering is a second layer, never the only one.
- `tenant_id` is resolved at the very start of the request lifecycle (`app/core/tenancy.py`) and set for the duration of the request (e.g. a Postgres session variable read by RLS policies):
  - **Admin portal:** from the authenticated user's tenant association (a user belongs to exactly one tenant; super admins excepted).
  - **Public site:** from the request's domain/subdomain mapped to a tenant — independent of whether the visitor is logged in.
- AI modules must pass `tenant_id` into every embeddings query and Bedrock context (see `rules/ai.md`).
- Every new tenant-owned table requires an explicit test that a Tenant A user cannot read/write Tenant B rows — failing at the **DB layer**, not just the API layer.

## Auth
- **Supabase Auth** issues JWTs for both customer and admin users. `app/core/security.py` verifies the JWT per request and extracts `user_id` + role claims.
- The application's own `users` table (not the JWT) is the source of truth for role/tenant, so role changes take effect immediately.
- Role permissions are enforced **server-side** via a `require_role`/permission dependency — never rely on hiding UI. A restricted role calling an out-of-scope API gets a 403.
- Anonymous visitors browse/search/chat/inquire with a lightweight `X-Session-Id` (not an account); session data migrates to the account on registration/login.

## Secrets
- Supabase service key and AWS/Bedrock credentials come from env vars (via `app/core/config.py`) / a secrets manager. Never hardcoded, never committed. `.env.example` lists required vars with placeholders.

## Auditing & abuse
- Log all admin-portal write actions (actor, action, entity, timestamp) — PRD Module 11.
- Rate-limit public `ai/*` endpoints to control Bedrock cost exposure from abuse.
