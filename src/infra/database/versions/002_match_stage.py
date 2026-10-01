"""matches.stage: etapa da vaga na triagem (new/saved/applied/discarded)

Revision ID: 002
Revises: 001
Create Date: 2026-10-01

"""
import sqlalchemy as sa
from alembic import op

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Avaliações existentes entram como "new": é o que eram antes da triagem existir.
    op.add_column(
        "matches",
        sa.Column("stage", sa.String(16), nullable=False, server_default="new"),
    )


def downgrade() -> None:
    op.drop_column("matches", "stage")
