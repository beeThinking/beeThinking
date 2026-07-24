"""sales and cashbook sale_id link

Revision ID: 20260723_0024
Revises: 20260723_0023
Create Date: 2026-07-23 16:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "20260723_0024"
down_revision: Union[str, None] = "20260723_0023"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "sales",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("partner_id", sa.Integer(), sa.ForeignKey("office_partners.id"), nullable=True),
        sa.Column("sale_date", sa.Date(), nullable=False),
        sa.Column("vat_rate", sa.Float(), nullable=False),
        sa.Column("amount_gross", sa.Float(), nullable=False, server_default="0"),
        sa.Column("amount_net", sa.Float(), nullable=False, server_default="0"),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("cashbook_entry_id", sa.Integer(), sa.ForeignKey("cashbook_entries.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "sale_items",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("sale_id", sa.Integer(), sa.ForeignKey("sales.id", ondelete="CASCADE"), nullable=False),
        sa.Column("inventory_item_id", sa.Integer(), sa.ForeignKey("inventory_items.id"), nullable=False),
        sa.Column("quantity", sa.Float(), nullable=False),
        sa.Column("unit_price_gross", sa.Float(), nullable=False),
        sa.Column("line_total_gross", sa.Float(), nullable=False),
    )

    with op.batch_alter_table("cashbook_entries") as batch_op:
        batch_op.add_column(sa.Column("sale_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key("fk_cashbook_entries_sale_id_sales", "sales", ["sale_id"], ["id"])


def downgrade() -> None:
    with op.batch_alter_table("cashbook_entries") as batch_op:
        batch_op.drop_constraint("fk_cashbook_entries_sale_id_sales", type_="foreignkey")
        batch_op.drop_column("sale_id")

    op.drop_table("sale_items")
    op.drop_table("sales")
