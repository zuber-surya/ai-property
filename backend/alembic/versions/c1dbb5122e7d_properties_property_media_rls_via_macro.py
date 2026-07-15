"""properties + property_media, RLS via macro

Revision ID: c1dbb5122e7d
Revises: 
Create Date: 2026-07-15 10:26:45.430724
"""
import sqlalchemy as sa

from alembic import op
from app.core.rls import disable_tenant_rls, enable_tenant_rls

revision = 'c1dbb5122e7d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Extensions first: gen_random_uuid() needs pgcrypto; pgvector for embeddings.
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # The application connects as this NON-SUPERUSER role, so RLS actually
    # applies to it. Migrations/admin tooling connect as the superuser and
    # bypass RLS by design (ADR-0005). A superuser app connection would make
    # tenant isolation silently non-existent — this is the highest-risk detail
    # in the whole data layer (02-architecture.md §4.4).
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_user') THEN
                CREATE ROLE app_user LOGIN PASSWORD 'app_password' NOSUPERUSER NOBYPASSRLS;
            END IF;
        END
        $$;
        """
    )
    op.execute("GRANT USAGE ON SCHEMA public TO app_user;")

    op.create_table('properties',
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('property_type', sa.String(length=50), nullable=False),
    sa.Column('listing_type', sa.String(length=10), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('price', sa.Numeric(precision=14, scale=2), nullable=True),
    sa.Column('bedrooms', sa.Integer(), nullable=True),
    sa.Column('bathrooms', sa.Integer(), nullable=True),
    sa.Column('area_sqft', sa.Integer(), nullable=True),
    sa.Column('locality', sa.String(length=120), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_properties_tenant_id'), 'properties', ['tenant_id'], unique=False)
    op.create_table('property_media',
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('property_id', sa.UUID(), nullable=False),
    sa.Column('url', sa.Text(), nullable=False),
    sa.Column('sort_order', sa.Integer(), nullable=False),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['property_id'], ['properties.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_property_media_tenant_id'), 'property_media', ['tenant_id'], unique=False)

    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON properties, property_media TO app_user;")

    # RLS — the primary tenant-isolation control (ADR-0003), applied through
    # the ONE reusable macro, never hand-written per table.
    enable_tenant_rls('properties')
    enable_tenant_rls('property_media')


def downgrade() -> None:
    disable_tenant_rls('property_media')
    disable_tenant_rls('properties')
    op.drop_index(op.f('ix_property_media_tenant_id'), table_name='property_media')
    op.drop_table('property_media')
    op.drop_index(op.f('ix_properties_tenant_id'), table_name='properties')
    op.drop_table('properties')
    # ### end Alembic commands ###
