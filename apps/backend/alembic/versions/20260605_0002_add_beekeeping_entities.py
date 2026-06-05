"""add beekeeping entities

Revision ID: 20260605_0002
Revises: 20260605_0001
Create Date: 2026-06-05 01:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260605_0002"
down_revision: Union[str, None] = "20260605_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

task_priority = sa.Enum("low", "medium", "high", "urgent", name="taskpriority")
task_status = sa.Enum("open", "done", "cancelled", name="taskstatus")
task_source = sa.Enum("manual", "inspection", "system", name="tasksource")


def upgrade() -> None:
    op.create_table(
        "queens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("hive_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("origin", sa.String(), nullable=True),
        sa.Column("marking_color", sa.String(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["hive_id"], ["hives.id"]),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_queens_id"), "queens", ["id"], unique=False)

    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("hive_id", sa.Integer(), nullable=True),
        sa.Column("apiary_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("priority", task_priority, nullable=False),
        sa.Column("status", task_status, nullable=False),
        sa.Column("source", task_source, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["apiary_id"], ["apiaries.id"]),
        sa.ForeignKeyConstraint(["hive_id"], ["hives.id"]),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_tasks_id"), "tasks", ["id"], unique=False)

    op.create_table(
        "treatments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("hive_id", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.Date(), nullable=False),
        sa.Column("ended_at", sa.Date(), nullable=True),
        sa.Column("product", sa.String(), nullable=False),
        sa.Column("method", sa.String(), nullable=True),
        sa.Column("dosage", sa.String(), nullable=True),
        sa.Column("reason", sa.String(), nullable=True),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["hive_id"], ["hives.id"]),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_treatments_id"), "treatments", ["id"], unique=False)

    op.create_table(
        "harvests",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("apiary_id", sa.Integer(), nullable=True),
        sa.Column("hive_id", sa.Integer(), nullable=True),
        sa.Column("harvest_date", sa.Date(), nullable=False),
        sa.Column("crop_type", sa.String(), nullable=True),
        sa.Column("amount_kg", sa.Float(), nullable=False),
        sa.Column("batch_code", sa.String(), nullable=True),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["apiary_id"], ["apiaries.id"]),
        sa.ForeignKeyConstraint(["hive_id"], ["hives.id"]),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_harvests_id"), "harvests", ["id"], unique=False)

    op.create_table(
        "photos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("hive_id", sa.Integer(), nullable=True),
        sa.Column("inspection_id", sa.Integer(), nullable=True),
        sa.Column("object_key", sa.String(), nullable=False),
        sa.Column("filename", sa.String(), nullable=False),
        sa.Column("content_type", sa.String(), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("caption", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(["hive_id"], ["hives.id"]),
        sa.ForeignKeyConstraint(["inspection_id"], ["inspections.id"]),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_photos_id"), "photos", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_photos_id"), table_name="photos")
    op.drop_table("photos")
    op.drop_index(op.f("ix_harvests_id"), table_name="harvests")
    op.drop_table("harvests")
    op.drop_index(op.f("ix_treatments_id"), table_name="treatments")
    op.drop_table("treatments")
    op.drop_index(op.f("ix_tasks_id"), table_name="tasks")
    op.drop_table("tasks")
    op.drop_index(op.f("ix_queens_id"), table_name="queens")
    op.drop_table("queens")
    task_source.drop(op.get_bind(), checkfirst=True)
    task_status.drop(op.get_bind(), checkfirst=True)
    task_priority.drop(op.get_bind(), checkfirst=True)
