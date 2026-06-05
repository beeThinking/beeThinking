"""initial schema

Revision ID: 20260605_0001
Revises: 
Create Date: 2026-06-05 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260605_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

hive_type = sa.Enum("langstroth", "dadant", "zander", "other", name="hivetype")
hive_status = sa.Enum("active", "inactive", "lost", name="hivestatus")


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("is_verified", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "apiaries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("address", sa.String(), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_apiaries_id"), "apiaries", ["id"], unique=False)

    op.create_table(
        "hives",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("location", sa.String(), nullable=True),
        sa.Column("type", hive_type, nullable=False),
        sa.Column("status", hive_status, nullable=False),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("apiary_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["apiary_id"], ["apiaries.id"]),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_hives_id"), "hives", ["id"], unique=False)

    op.create_table(
        "inspections",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("hive_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("queen_seen", sa.Boolean(), nullable=False),
        sa.Column("brood_strength", sa.Integer(), nullable=True),
        sa.Column("varroa_count", sa.Float(), nullable=True),
        sa.Column("food_stores", sa.Integer(), nullable=True),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(["hive_id"], ["hives.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_inspections_id"), "inspections", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_inspections_id"), table_name="inspections")
    op.drop_table("inspections")
    op.drop_index(op.f("ix_hives_id"), table_name="hives")
    op.drop_table("hives")
    op.drop_index(op.f("ix_apiaries_id"), table_name="apiaries")
    op.drop_table("apiaries")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_table("users")
    hive_status.drop(op.get_bind(), checkfirst=True)
    hive_type.drop(op.get_bind(), checkfirst=True)
