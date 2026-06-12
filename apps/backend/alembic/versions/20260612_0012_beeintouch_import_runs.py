"""beeintouch import runs

Revision ID: 20260612_0012
Revises: 20260611_0011
Create Date: 2026-06-12 17:30:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "20260612_0012"
down_revision: Union[str, None] = "20260611_0011"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "beeintouch_import_runs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=True),
        sa.Column("source_name", sa.String(), nullable=False),
        sa.Column("source_hash", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("imported_count", sa.Integer(), nullable=False),
        sa.Column("error_count", sa.Integer(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("error_text", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("source_name", "source_hash", name="uq_beeintouch_import_source_hash"),
    )
    op.create_index(op.f("ix_beeintouch_import_runs_id"), "beeintouch_import_runs", ["id"], unique=False)
    op.create_index(op.f("ix_beeintouch_import_runs_owner_id"), "beeintouch_import_runs", ["owner_id"], unique=False)

    op.create_table(
        "beeintouch_import_errors",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("run_id", sa.Integer(), nullable=False),
        sa.Column("source_name", sa.String(), nullable=False),
        sa.Column("page_number", sa.Integer(), nullable=True),
        sa.Column("row_number", sa.Integer(), nullable=True),
        sa.Column("target_type", sa.String(), nullable=True),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("raw_text", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(["run_id"], ["beeintouch_import_runs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_beeintouch_import_errors_id"), "beeintouch_import_errors", ["id"], unique=False)
    op.create_index(op.f("ix_beeintouch_import_errors_run_id"), "beeintouch_import_errors", ["run_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_beeintouch_import_errors_run_id"), table_name="beeintouch_import_errors")
    op.drop_index(op.f("ix_beeintouch_import_errors_id"), table_name="beeintouch_import_errors")
    op.drop_table("beeintouch_import_errors")
    op.drop_index(op.f("ix_beeintouch_import_runs_owner_id"), table_name="beeintouch_import_runs")
    op.drop_index(op.f("ix_beeintouch_import_runs_id"), table_name="beeintouch_import_runs")
    op.drop_table("beeintouch_import_runs")
