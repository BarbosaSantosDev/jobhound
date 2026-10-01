"""profiles.enabled_sources: fontes ligadas por perfil

Revision ID: 005
Revises: 004
Create Date: 2026-10-01

Perfis existentes ficam com todas as fontes ligadas — é o comportamento que
eles já tinham (as fontes eram derivadas só da stack).
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "profiles",
        sa.Column(
            "enabled_sources",
            postgresql.ARRAY(sa.String),
            nullable=False,
            server_default="{gupy,nerdin,remoteok}",
        ),
    )


def downgrade() -> None:
    op.drop_column("profiles", "enabled_sources")
