"""add water content percent to harvests

Revision ID: 20260723_0018
Revises: 20260720_0017
Create Date: 2026-07-23 12:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "20260723_0018"
down_revision: Union[str, None] = "20260720_0017"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("harvests", sa.Column("water_content_percent", sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column("harvests", "water_content_percent")
