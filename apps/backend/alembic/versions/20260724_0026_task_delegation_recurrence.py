"""M8.2: task delegation (assignee_id) + recurrence (RRULE string)

Revision ID: 20260724_0026
Revises: 20260724_0025
Create Date: 2026-07-24 10:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "20260724_0026"
down_revision: Union[str, None] = "20260724_0025"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("tasks") as batch_op:
        batch_op.add_column(sa.Column("assignee_id", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("recurrence_rule", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("delegated_at", sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column("delegation_seen_at", sa.DateTime(timezone=True), nullable=True))
        batch_op.create_foreign_key("fk_tasks_assignee_id_users", "users", ["assignee_id"], ["id"])
        batch_op.create_index("ix_tasks_assignee_id", ["assignee_id"])


def downgrade() -> None:
    with op.batch_alter_table("tasks") as batch_op:
        batch_op.drop_index("ix_tasks_assignee_id")
        batch_op.drop_constraint("fk_tasks_assignee_id_users", type_="foreignkey")
        batch_op.drop_column("delegation_seen_at")
        batch_op.drop_column("delegated_at")
        batch_op.drop_column("recurrence_rule")
        batch_op.drop_column("assignee_id")
