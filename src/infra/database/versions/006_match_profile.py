"""matches.profile_id: cada avaliação pertence a um perfil

Revision ID: 006
Revises: 005
Create Date: 2026-10-01

Avaliações existentes ficam com profile_id NULL ("legadas"): o pipeline usava
o perfil editado por último NA HORA do faro, então não dá para saber com qual
perfil cada uma foi feita. As legadas aparecem para qualquer perfil.
"""
import sqlalchemy as sa
from alembic import op

revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("matches", sa.Column("profile_id", sa.Integer, nullable=True))
    op.create_foreign_key(
        "fk_matches_profile_id", "matches", "profiles", ["profile_id"], ["id"], ondelete="CASCADE"
    )
    op.create_index("ix_matches_profile_id", "matches", ["profile_id"])
    # uma avaliação por vaga e perfil (NULLs não colidem entre si no Postgres)
    op.create_unique_constraint("uq_matches_job_profile", "matches", ["job_id", "profile_id"])


def downgrade() -> None:
    op.drop_constraint("uq_matches_job_profile", "matches", type_="unique")
    op.drop_index("ix_matches_profile_id", table_name="matches")
    op.drop_constraint("fk_matches_profile_id", "matches", type_="foreignkey")
    op.drop_column("matches", "profile_id")
