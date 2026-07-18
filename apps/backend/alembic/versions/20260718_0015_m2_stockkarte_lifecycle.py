"""m2 stockkarte and colony lifecycle

Revision ID: 20260718_0015
Revises: 20260713_0014
Create Date: 2026-07-18 10:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "20260718_0015"
down_revision: Union[str, None] = "20260713_0014"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("hives", sa.Column("stock_number", sa.String(), nullable=True))
    op.add_column(
        "hives",
        sa.Column("colony_kind", sa.String(), nullable=False, server_default="wirtschaftsvolk"),
    )
    op.add_column("hives", sa.Column("established_at", sa.Date(), nullable=True))
    op.add_column("hives", sa.Column("tags", sa.JSON(), nullable=True))

    op.create_table(
        "varroa_checks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("hive_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("method", sa.String(), nullable=True),
        sa.Column("mite_count", sa.Integer(), nullable=True),
        sa.Column("mites_per_day", sa.Float(), nullable=True),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["hive_id"], ["hives.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_varroa_checks_hive_id", "varroa_checks", ["hive_id"])
    op.create_index("ix_varroa_checks_owner_id", "varroa_checks", ["owner_id"])


def downgrade() -> None:
    op.drop_index("ix_varroa_checks_owner_id", table_name="varroa_checks")
    op.drop_index("ix_varroa_checks_hive_id", table_name="varroa_checks")
    op.drop_table("varroa_checks")
    op.drop_column("hives", "tags")
    op.drop_column("hives", "established_at")
    op.drop_column("hives", "colony_kind")
    op.drop_column("hives", "stock_number")
