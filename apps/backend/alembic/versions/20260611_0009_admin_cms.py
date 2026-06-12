"""admin cms

Revision ID: 20260611_0009
Revises: 20260610_0008
Create Date: 2026-06-11
"""

from alembic import op
import sqlalchemy as sa


revision = "20260611_0009"
down_revision = "20260610_0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.false()))

    op.create_table(
        "app_texts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("key", sa.String(), nullable=False),
        sa.Column("locale", sa.String(), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("updated_by_user_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["updated_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key", "locale", name="uq_app_texts_key_locale"),
    )
    op.create_index(op.f("ix_app_texts_id"), "app_texts", ["id"], unique=False)
    op.create_index(op.f("ix_app_texts_key"), "app_texts", ["key"], unique=False)
    op.create_index(op.f("ix_app_texts_locale"), "app_texts", ["locale"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_app_texts_locale"), table_name="app_texts")
    op.drop_index(op.f("ix_app_texts_key"), table_name="app_texts")
    op.drop_index(op.f("ix_app_texts_id"), table_name="app_texts")
    op.drop_table("app_texts")
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("is_admin")
