"""add batches table and harvests.batch_id

Revision ID: 20260723_0019
Revises: 20260723_0018
Create Date: 2026-07-23 12:30:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "20260723_0019"
down_revision: Union[str, None] = "20260723_0018"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "batches",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("lot_number", sa.String(), nullable=False),
        sa.Column("best_before", sa.Date(), nullable=True),
        sa.Column("total_amount_kg", sa.Float(), nullable=False),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("owner_id", "lot_number", name="uq_batches_owner_id_lot_number"),
    )
    op.create_index(op.f("ix_batches_id"), "batches", ["id"], unique=False)
    with op.batch_alter_table("harvests") as batch_op:
        batch_op.add_column(sa.Column("batch_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key("fk_harvests_batch_id_batches", "batches", ["batch_id"], ["id"])


def downgrade() -> None:
    with op.batch_alter_table("harvests") as batch_op:
        batch_op.drop_constraint("fk_harvests_batch_id_batches", type_="foreignkey")
        batch_op.drop_column("batch_id")
    op.drop_index(op.f("ix_batches_id"), table_name="batches")
    op.drop_table("batches")
