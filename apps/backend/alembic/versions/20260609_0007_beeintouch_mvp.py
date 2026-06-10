"""beeintouch inspired mvp

Revision ID: 20260609_0007
Revises: 20260605_0006
Create Date: 2026-06-09 14:30:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "20260609_0007"
down_revision: Union[str, None] = "20260605_0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


ARTICLE_CATEGORY_VALUES = ("honey", "material", "feed", "other")
TASK_KIND_VALUES = ("todo", "appointment")


def _enum(name: str, values: tuple[str, ...]):
    if op.get_bind().dialect.name == "postgresql":
        return postgresql.ENUM(*values, name=name, create_type=False)
    return sa.Enum(*values, name=name)


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        postgresql.ENUM(*ARTICLE_CATEGORY_VALUES, name="articlecategory").create(bind, checkfirst=True)
        postgresql.ENUM(*TASK_KIND_VALUES, name="taskkind").create(bind, checkfirst=True)

    op.add_column("tasks", sa.Column("start_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("tasks", sa.Column("end_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("tasks", sa.Column("kind", _enum("taskkind", TASK_KIND_VALUES), nullable=False, server_default="todo"))

    op.create_table(
        "feedings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("apiary_id", sa.Integer(), nullable=True),
        sa.Column("hive_id", sa.Integer(), nullable=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("feed_type", sa.String(), nullable=False),
        sa.Column("amount_kg_or_l", sa.Float(), nullable=False),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["apiary_id"], ["apiaries.id"]),
        sa.ForeignKeyConstraint(["hive_id"], ["hives.id"]),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_feedings_id"), "feedings", ["id"], unique=False)

    op.create_table(
        "articles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("category", _enum("articlecategory", ARTICLE_CATEGORY_VALUES), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("sku", sa.String(), nullable=True),
        sa.Column("weight_kg", sa.Float(), nullable=True),
        sa.Column("unit", sa.String(), nullable=False),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_articles_id"), "articles", ["id"], unique=False)

    op.create_table(
        "inventory_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("article_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Float(), nullable=False),
        sa.Column("unit", sa.String(), nullable=False),
        sa.Column("price", sa.Float(), nullable=True),
        sa.Column("best_before", sa.Date(), nullable=True),
        sa.Column("batch_code", sa.String(), nullable=True),
        sa.Column("archived", sa.Boolean(), nullable=False),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["article_id"], ["articles.id"]),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_inventory_items_id"), "inventory_items", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_inventory_items_id"), table_name="inventory_items")
    op.drop_table("inventory_items")
    op.drop_index(op.f("ix_articles_id"), table_name="articles")
    op.drop_table("articles")
    op.drop_index(op.f("ix_feedings_id"), table_name="feedings")
    op.drop_table("feedings")
    op.drop_column("tasks", "kind")
    op.drop_column("tasks", "end_at")
    op.drop_column("tasks", "start_at")
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        postgresql.ENUM(*TASK_KIND_VALUES, name="taskkind").drop(bind, checkfirst=True)
        postgresql.ENUM(*ARTICLE_CATEGORY_VALUES, name="articlecategory").drop(bind, checkfirst=True)
