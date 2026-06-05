"""add hive lifecycle and events

Revision ID: 20260605_0005
Revises: 20260605_0004
Create Date: 2026-06-05 13:30:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260605_0005"
down_revision: Union[str, None] = "20260605_0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

old_status = sa.Enum("active", "inactive", "lost", name="hivestatus")
new_status = sa.Enum(
    "active",
    "archived",
    "dissolved",
    "merged",
    "sold",
    "dead",
    "inactive",
    "lost",
    "created_by_mistake",
    name="hivestatus",
)


def upgrade() -> None:
    if op.get_context().dialect.name == "postgresql":
        op.execute("ALTER TYPE hivestatus ADD VALUE IF NOT EXISTS 'archived'")
        op.execute("ALTER TYPE hivestatus ADD VALUE IF NOT EXISTS 'dissolved'")
        op.execute("ALTER TYPE hivestatus ADD VALUE IF NOT EXISTS 'merged'")
        op.execute("ALTER TYPE hivestatus ADD VALUE IF NOT EXISTS 'sold'")
        op.execute("ALTER TYPE hivestatus ADD VALUE IF NOT EXISTS 'dead'")
        op.execute("ALTER TYPE hivestatus ADD VALUE IF NOT EXISTS 'created_by_mistake'")

    op.add_column("hives", sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.add_column("hives", sa.Column("archived_at", sa.Date(), nullable=True))
    op.add_column("hives", sa.Column("merged_into_hive_id", sa.Integer(), nullable=True))
    if op.get_context().dialect.name != "sqlite":
        op.create_foreign_key("fk_hives_merged_into_hive_id", "hives", "hives", ["merged_into_hive_id"], ["id"])

    op.create_table(
        "hive_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("hive_id", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(), nullable=False),
        sa.Column("event_date", sa.Date(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("related_entity_type", sa.String(), nullable=True),
        sa.Column("related_entity_id", sa.Integer(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["hive_id"], ["hives.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_hive_events_id"), "hive_events", ["id"], unique=False)
    op.create_index("ix_hive_events_user_hive_date", "hive_events", ["user_id", "hive_id", "event_date"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_hive_events_user_hive_date", table_name="hive_events")
    op.drop_index(op.f("ix_hive_events_id"), table_name="hive_events")
    op.drop_table("hive_events")
    if op.get_context().dialect.name != "sqlite":
        op.drop_constraint("fk_hives_merged_into_hive_id", "hives", type_="foreignkey")
    op.drop_column("hives", "merged_into_hive_id")
    op.drop_column("hives", "archived_at")
    op.drop_column("hives", "is_active")
