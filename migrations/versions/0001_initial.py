"""초기 스키마: 확장(vector, pg_trgm) + job_runs

Revision ID: 0001
Revises:
Create Date: 2026-10-29
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 운영 서버에서는 DB 소유자가 슈퍼유저가 아니면 확장을 미리 만들어 둬야 한다 (runbook 참고)
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    op.create_table(
        "job_runs",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("job", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
        sa.Column("items", sa.Integer()),
        sa.Column("error", sa.Text()),
        sa.Column("meta", postgresql.JSONB()),
    )
    op.create_index("ix_job_runs_job_started_at", "job_runs", ["job", "started_at"])


def downgrade() -> None:
    op.drop_index("ix_job_runs_job_started_at", table_name="job_runs")
    op.drop_table("job_runs")
