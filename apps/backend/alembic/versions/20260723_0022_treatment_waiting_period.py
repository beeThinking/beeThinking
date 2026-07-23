"""add waiting_period_days to treatments

Revision ID: 20260723_0022
Revises: 20260723_0019
Create Date: 2026-07-23 14:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "20260723_0022"
down_revision: Union[str, None] = "20260723_0019"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("treatments") as batch_op:
        batch_op.add_column(sa.Column("waiting_period_days", sa.Integer(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("treatments") as batch_op:
        batch_op.drop_column("waiting_period_days")
