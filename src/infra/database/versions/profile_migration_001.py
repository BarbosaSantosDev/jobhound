"""add profiles table

Revision ID: 001
Revises:
Create Date: 2026-08-03

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "001"
down_revision = "71a4f221ba5a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "profiles",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("slug", sa.String(64), nullable=False, unique=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("headline", sa.String(255), nullable=False, server_default=""),
        sa.Column("seniority", sa.String(16), nullable=False),
        sa.Column("primary_stack", postgresql.ARRAY(sa.String), nullable=False),
        sa.Column("secondary_stack", postgresql.ARRAY(sa.String), nullable=False, server_default="{}"),
        sa.Column("preferred_locations", postgresql.ARRAY(sa.String), nullable=False, server_default="{}"),
        sa.Column("accepts_remote", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("summary", sa.Text, nullable=False, server_default=""),
        sa.Column("search", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_profiles_slug", "profiles", ["slug"])


def downgrade() -> None:
    op.drop_index("ix_profiles_slug", table_name="profiles")
    op.drop_table("profiles")