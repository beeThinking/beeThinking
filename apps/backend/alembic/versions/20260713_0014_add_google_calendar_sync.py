"""add google calendar sync

Revision ID: 20260713_0014
Revises: 20260713_0013
Create Date: 2026-07-13 14:30:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "20260713_0014"
down_revision: Union[str, None] = "20260713_0013"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "google_calendar_connections",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("refresh_token_encrypted", sa.Text(), nullable=False),
        sa.Column("calendar_id", sa.String(), nullable=False),
        sa.Column("calendar_name", sa.String(), nullable=False),
        sa.Column("connected_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("last_sync_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index("ix_google_calendar_connections_user_id", "google_calendar_connections", ["user_id"])
    op.create_table(
        "google_calendar_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("google_event_id", sa.String(), nullable=False),
        sa.Column("synced_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "google_event_id", name="uq_google_calendar_event_user_google"),
        sa.UniqueConstraint("user_id", "task_id", name="uq_google_calendar_event_user_task"),
    )
    op.create_index("ix_google_calendar_events_task_id", "google_calendar_events", ["task_id"])
    op.create_index("ix_google_calendar_events_user_id", "google_calendar_events", ["user_id"])
    op.create_table(
        "google_oauth_states",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("state_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_google_oauth_states_expires_at", "google_oauth_states", ["expires_at"])
    op.create_index("ix_google_oauth_states_state_hash", "google_oauth_states", ["state_hash"], unique=True)
    op.create_index("ix_google_oauth_states_user_id", "google_oauth_states", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_google_oauth_states_user_id", table_name="google_oauth_states")
    op.drop_index("ix_google_oauth_states_state_hash", table_name="google_oauth_states")
    op.drop_index("ix_google_oauth_states_expires_at", table_name="google_oauth_states")
    op.drop_table("google_oauth_states")
    op.drop_index("ix_google_calendar_events_user_id", table_name="google_calendar_events")
    op.drop_index("ix_google_calendar_events_task_id", table_name="google_calendar_events")
    op.drop_table("google_calendar_events")
    op.drop_index("ix_google_calendar_connections_user_id", table_name="google_calendar_connections")
    op.drop_table("google_calendar_connections")
