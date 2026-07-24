"""M9 refresh tokens

Revision ID: 20260724_0029
Revises: 20260724_0028
"""
from alembic import op
import sqlalchemy as sa

revision = "20260724_0029"
down_revision = "20260724_0028"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("token_id", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("family_id", sa.String(length=64), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.Column("replaced_by_id", sa.Integer(), sa.ForeignKey("refresh_tokens.id")),
        sa.Column("reuse_detected", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.UniqueConstraint("token_id"),
    )
    for column in ("token_id", "user_id", "family_id", "expires_at"):
        op.create_index(f"ix_refresh_tokens_{column}", "refresh_tokens", [column])


def downgrade() -> None:
    op.drop_table("refresh_tokens")
