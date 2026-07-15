"""The reusable RLS macro.

ADR-0003: tenant isolation is enforced at the DB layer via Postgres RLS, as the
PRIMARY control — not application filtering. Every tenant-owned table applies
its policy through THIS ONE helper, never hand-written per-table SQL, so the
policy is identical everywhere and cannot be subtly wrong on one table.

The policy reads a per-request session variable, `app.current_tenant_id`, set at
the start of every request in core/tenancy.py. A row is visible only when its
tenant_id matches that variable.
"""

from __future__ import annotations

from alembic import op


def enable_tenant_rls(table: str) -> None:
    """Turn on RLS for a tenant-owned table. Call from a migration's upgrade()."""
    op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;")
    op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY;")
    # FORCE so the table owner is subject to the policy too — otherwise the
    # migration/admin role would silently bypass isolation.
    # `nullif(..., '')` matters: when the session variable is unset,
    # current_setting(..., true) returns '' — and ''::uuid ERRORS. Coercing the
    # empty string to NULL makes an unset tenant match NO rows (fail closed,
    # cleanly) instead of throwing. Proven by test_no_tenant_context_sees_nothing.
    op.execute(
        f"""
        CREATE POLICY tenant_isolation ON {table}
            USING (
                tenant_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid
            )
            WITH CHECK (
                tenant_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid
            );
        """
    )


def disable_tenant_rls(table: str) -> None:
    """Reverse of enable_tenant_rls, for a migration's downgrade()."""
    op.execute(f"DROP POLICY IF EXISTS tenant_isolation ON {table};")
    op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY;")
