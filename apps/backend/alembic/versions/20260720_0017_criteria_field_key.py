"""link inspection criteria to fixed fields

Revision ID: 20260720_0017
Revises: 20260720_0016
Create Date: 2026-07-20 12:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "20260720_0017"
down_revision: Union[str, None] = "20260720_0016"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("inspection_criteria", sa.Column("field_key", sa.String(length=50), nullable=True))


def downgrade() -> None:
    op.drop_column("inspection_criteria", "field_key")
