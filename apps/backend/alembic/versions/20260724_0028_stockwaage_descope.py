"""M8.10: Stockwaage descope — scale_enabled toggle + weight_readings table

Revision ID: 20260724_0028
Revises: 20260724_0027
Create Date: 2026-07-24 12:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "20260724_0028"
down_revision: Union[str, None] = "20260724_0027"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("hives", sa.Column("scale_enabled", sa.Boolean(), nullable=False, server_default=sa.false()))

    op.create_table(
        "weight_readings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("hive_id", sa.Integer(), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("weight_kg", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.ForeignKeyConstraint(["hive_id"], ["hives.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_weight_readings_hive_id", "weight_readings", ["hive_id"])


def downgrade() -> None:
    op.drop_index("ix_weight_readings_hive_id", table_name="weight_readings")
    op.drop_table("weight_readings")
    op.drop_column("hives", "scale_enabled")
