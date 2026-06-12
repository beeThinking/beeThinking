"""apiary stock number

Revision ID: 20260611_0010
Revises: 20260611_0009
Create Date: 2026-06-11
"""

from alembic import op
import sqlalchemy as sa


revision = "20260611_0010"
down_revision = "20260611_0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("apiaries") as batch_op:
        batch_op.add_column(sa.Column("stock_number", sa.String(), nullable=True))

    op.execute("UPDATE apiaries SET stock_number = COALESCE(NULLIF(name, ''), 'Stand #' || id)")

    with op.batch_alter_table("apiaries") as batch_op:
        batch_op.alter_column("stock_number", nullable=False)
        batch_op.alter_column("name", existing_type=sa.String(), nullable=True)


def downgrade() -> None:
    op.execute("UPDATE apiaries SET name = stock_number WHERE name IS NULL OR name = ''")

    with op.batch_alter_table("apiaries") as batch_op:
        batch_op.alter_column("name", existing_type=sa.String(), nullable=False)
        batch_op.drop_column("stock_number")
