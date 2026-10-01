"""pipeline_runs: histórico de execuções do pipeline, com relatório por fonte

Revision ID: 007
Revises: 006
Create Date: 2026-10-01

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "007"
down_revision = "006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "pipeline_runs",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "profile_id",
            sa.Integer,
            sa.ForeignKey("profiles.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("profile_slug", sa.String(64), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("error", sa.Text, nullable=True),
        sa.Column("report", postgresql.JSONB, nullable=False),
    )
    op.create_index("ix_pipeline_runs_profile_id", "pipeline_runs", ["profile_id"])
    op.create_index("ix_pipeline_runs_finished_at", "pipeline_runs", ["finished_at"])


def downgrade() -> None:
    op.drop_index("ix_pipeline_runs_finished_at", table_name="pipeline_runs")
    op.drop_index("ix_pipeline_runs_profile_id", table_name="pipeline_runs")
    op.drop_table("pipeline_runs")
