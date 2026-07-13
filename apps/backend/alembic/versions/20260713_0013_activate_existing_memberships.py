"""activate existing apiary memberships

Revision ID: 20260713_0013
Revises: 20260612_0012
Create Date: 2026-07-13 13:10:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "20260713_0013"
down_revision: Union[str, None] = "20260612_0012"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        sa.text(
            "UPDATE apiary_members "
            "SET accepted_at = COALESCE(created_at, CURRENT_TIMESTAMP) "
            "WHERE accepted_at IS NULL"
        )
    )


def downgrade() -> None:
    op.execute(sa.text("UPDATE apiary_members SET accepted_at = NULL"))
