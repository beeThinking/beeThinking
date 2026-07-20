"""configurable inspection criteria

Revision ID: 20260718_0016
Revises: 20260718_0015
Create Date: 2026-07-18 16:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "20260718_0016"
down_revision: Union[str, None] = "20260718_0015"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "inspection_criteria",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("section", sa.String(length=50), nullable=False, server_default="verschiedenes"),
        sa.Column("value_type", sa.String(length=20), nullable=False, server_default="stars"),
        sa.Column("options", sa.JSON(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_inspection_criteria_owner_id", "inspection_criteria", ["owner_id"])

    op.add_column("inspections", sa.Column("hive_weight_kg", sa.Float(), nullable=True))
    op.add_column("inspections", sa.Column("criteria_values", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("inspections", "criteria_values")
    op.drop_column("inspections", "hive_weight_kg")
    op.drop_index("ix_inspection_criteria_owner_id", table_name="inspection_criteria")
    op.drop_table("inspection_criteria")
