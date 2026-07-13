# Rule: Database & Migrations

Applies to: all schema and data-access work. Source: `docs/03-database-schema.md`, `docs/09-coding-standards.md` §2.6.

Data access is **SQLAlchemy talking directly to the Supabase Postgres connection string.** Supabase's own client is used only for Auth and Storage — never for data access.

## Table conventions (every table)
- PK: `id UUID PRIMARY KEY DEFAULT gen_random_uuid()`.
- Timestamps: `created_at TIMESTAMPTZ DEFAULT now()`, `updated_at TIMESTAMPTZ DEFAULT now()`.
- Soft delete via `deleted_at TIMESTAMPTZ NULL` on user-facing entities (properties, leads, users) — preserve CRM history, don't hard-delete.
- Naming: `snake_case`, plural table names.

## Tenant-owned tables
- Include `tenant_id UUID NOT NULL REFERENCES tenants(id)`.
- `tenants` itself is platform-level and **not** tenant-scoped (it's the table `tenant_id` references).

## Migrations — Alembic only
- **Every schema change goes through an Alembic migration.** No manual edits against the Supabase Postgres instance, even in early dev, so `docs/03-database-schema.md` and the live DB never drift.
- After changing a SQLAlchemy model, generate and review a migration (`alembic revision --autogenerate`), then `alembic upgrade head`.

## RLS policies via a reusable helper
- Postgres Row-Level Security enforces `tenant_id = current_tenant_id()` at the DB layer — this is the **primary** tenant-isolation safety net, not app filtering (see `rules/security.md`).
- Apply RLS through **one repeatable migration macro/helper**, reused in each tenant-owned table's migration — do not hand-write per-table SQL.
- `property_embeddings` (pgvector) is tagged with `tenant_id` and `property_id`; it can be regenerated from `properties`, so it's not a single point of unrecoverable failure.
