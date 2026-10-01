"""matches.work_mode: modalidade extraída da vaga (remote/hybrid/onsite/not_informed)

Revision ID: 004
Revises: 003
Create Date: 2026-10-01

Avaliações antigas ficam NULL: o fato não foi guardado na época e só
reavaliando a vaga com o LLM daria para recuperá-lo.
"""
import sqlalchemy as sa
from alembic import op

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("matches", sa.Column("work_mode", sa.String(16), nullable=True))


def downgrade() -> None:
    op.drop_column("matches", "work_mode")
