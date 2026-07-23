"""add batch remaining_kg, inventory_items.batch_id, extend article category

Revision ID: 20260723_0023
Revises: 20260723_0022
Create Date: 2026-07-23 15:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "20260723_0023"
down_revision: Union[str, None] = "20260723_0022"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("batches") as batch_op:
        batch_op.add_column(sa.Column("remaining_kg", sa.Float(), nullable=True))

    op.execute("UPDATE batches SET remaining_kg = total_amount_kg")

    with op.batch_alter_table("inventory_items") as batch_op:
        batch_op.add_column(sa.Column("batch_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key("fk_inventory_items_batch_id_batches", "batches", ["batch_id"], ["id"])

    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("ALTER TYPE articlecategory ADD VALUE IF NOT EXISTS 'finished_product'")

    op.execute("UPDATE articles SET category = 'material' WHERE category = 'other'")


def downgrade() -> None:
    op.execute("UPDATE articles SET category = 'material' WHERE category = 'finished_product'")

    with op.batch_alter_table("inventory_items") as batch_op:
        batch_op.drop_constraint("fk_inventory_items_batch_id_batches", type_="foreignkey")
        batch_op.drop_column("batch_id")

    with op.batch_alter_table("batches") as batch_op:
        batch_op.drop_column("remaining_kg")
