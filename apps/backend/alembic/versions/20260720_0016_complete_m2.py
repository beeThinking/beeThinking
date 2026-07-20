"""complete m2 stock card fields

Revision ID: 20260720_0016
Revises: 20260718_0016
"""

from alembic import op
import sqlalchemy as sa


revision = "20260720_0016"
down_revision = "20260718_0016"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("hives") as batch_op:
        batch_op.add_column(sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"))
    with op.batch_alter_table("queens") as batch_op:
        batch_op.add_column(sa.Column("marking_code", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("introduced_at", sa.Date(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("queens") as batch_op:
        batch_op.drop_column("introduced_at")
        batch_op.drop_column("marking_code")
    with op.batch_alter_table("hives") as batch_op:
        batch_op.drop_column("sort_order")
