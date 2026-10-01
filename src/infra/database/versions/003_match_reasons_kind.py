"""matches.reasons: de text[] para jsonb [{kind, text}]

Revision ID: 003
Revises: 002
Create Date: 2026-10-01

Os textos antigos foram gerados pelo ScoreJob (determinístico), então dá para
recuperar a polaridade pelo prefixo de cada mensagem. O que não casar com
nenhum prefixo conhecido vira "info" (neutro) — nada é chutado.
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None

_KIND_BY_PREFIX = """
    CASE
        WHEN r LIKE 'Vaga menciona stack principal:%' THEN 'pro'
        WHEN r LIKE 'Vaga menciona stack secundária:%' THEN 'pro'
        WHEN r = 'Senioridade compatível' THEN 'pro'
        WHEN r = 'Vaga remota' THEN 'pro'
        WHEN r LIKE 'Localização compatível:%' THEN 'pro'
        WHEN r LIKE 'Stack exigida incompatível:%' THEN 'con'
        WHEN r LIKE 'Senioridade incompatível:%' THEN 'con'
        WHEN r = 'Localização/modo de trabalho fora das preferências' THEN 'con'
        ELSE 'info'
    END
"""


def upgrade() -> None:
    op.add_column("matches", sa.Column("reasons_v2", postgresql.JSONB, nullable=True))
    op.execute(
        f"""
        UPDATE matches SET reasons_v2 = COALESCE(
            (SELECT jsonb_agg(jsonb_build_object('kind', {_KIND_BY_PREFIX}, 'text', r) ORDER BY ord)
             FROM unnest(reasons) WITH ORDINALITY AS t(r, ord)),
            '[]'::jsonb
        )
        """
    )
    op.drop_column("matches", "reasons")
    op.alter_column("matches", "reasons_v2", new_column_name="reasons", nullable=False)


def downgrade() -> None:
    op.add_column("matches", sa.Column("reasons_v1", postgresql.ARRAY(sa.String), nullable=True))
    op.execute(
        """
        UPDATE matches SET reasons_v1 = COALESCE(
            ARRAY(SELECT elem->>'text' FROM jsonb_array_elements(reasons) AS elem),
            '{}'
        )
        """
    )
    op.drop_column("matches", "reasons")
    op.alter_column("matches", "reasons_v1", new_column_name="reasons", nullable=False)
