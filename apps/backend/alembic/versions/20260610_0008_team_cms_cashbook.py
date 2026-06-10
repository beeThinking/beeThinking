"""team cms cashbook

Revision ID: 20260610_0008
Revises: 20260609_0007
Create Date: 2026-06-10
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260610_0008"
down_revision = "20260609_0007"
branch_labels = None
depends_on = None


APIARY_MEMBER_ROLE_VALUES = ("owner", "admin", "member", "viewer")
CASHBOOK_DIRECTION_VALUES = ("income", "expense")
OCR_STATUS_VALUES = ("pending", "parsed", "confirmed", "failed")


def enum_type(bind, values: tuple[str, ...], name: str, create_type: bool = False) -> sa.Enum:
    if bind.dialect.name == "postgresql":
        return postgresql.ENUM(*values, name=name, create_type=create_type)
    return sa.Enum(*values, name=name, native_enum=False)


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        enum_type(bind, APIARY_MEMBER_ROLE_VALUES, "apiarymemberrole", create_type=True).create(bind, checkfirst=True)
        enum_type(bind, CASHBOOK_DIRECTION_VALUES, "cashbookdirection", create_type=True).create(bind, checkfirst=True)
        enum_type(bind, OCR_STATUS_VALUES, "ocrstatus", create_type=True).create(bind, checkfirst=True)

    apiary_member_role = enum_type(bind, APIARY_MEMBER_ROLE_VALUES, "apiarymemberrole")
    cashbook_direction = enum_type(bind, CASHBOOK_DIRECTION_VALUES, "cashbookdirection")
    ocr_status = enum_type(bind, OCR_STATUS_VALUES, "ocrstatus")

    op.create_table(
        "apiary_members",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("apiary_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("role", apiary_member_role, nullable=False),
        sa.Column("invited_by_user_id", sa.Integer(), nullable=True),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(["apiary_id"], ["apiaries.id"]),
        sa.ForeignKeyConstraint(["invited_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("apiary_id", "user_id", name="uq_apiary_members_apiary_user"),
    )
    op.create_index(op.f("ix_apiary_members_id"), "apiary_members", ["id"], unique=False)

    op.create_table(
        "content_pages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("locale", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("eyebrow", sa.String(), nullable=True),
        sa.Column("lead", sa.Text(), nullable=True),
        sa.Column("cta_label", sa.String(), nullable=True),
        sa.Column("cta_link", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("updated_by_user_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["updated_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug", "locale", name="uq_content_pages_slug_locale"),
    )
    op.create_index(op.f("ix_content_pages_id"), "content_pages", ["id"], unique=False)
    op.create_index(op.f("ix_content_pages_slug"), "content_pages", ["slug"], unique=False)

    op.create_table(
        "content_sections",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("page_id", sa.Integer(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("heading", sa.String(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["page_id"], ["content_pages.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_content_sections_id"), "content_sections", ["id"], unique=False)

    op.create_table(
        "cashbook_receipts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("file_object_key", sa.String(), nullable=True),
        sa.Column("filename", sa.String(), nullable=False),
        sa.Column("content_type", sa.String(), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("ocr_status", ocr_status, nullable=False),
        sa.Column("ocr_text", sa.Text(), nullable=True),
        sa.Column("ocr_provider", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_cashbook_receipts_id"), "cashbook_receipts", ["id"], unique=False)

    op.create_table(
        "cashbook_receipt_suggestions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("receipt_id", sa.Integer(), nullable=False),
        sa.Column("field_name", sa.String(), nullable=False),
        sa.Column("suggested_value", sa.String(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(["receipt_id"], ["cashbook_receipts.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_cashbook_receipt_suggestions_id"), "cashbook_receipt_suggestions", ["id"], unique=False)

    op.create_table(
        "cashbook_entries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("apiary_id", sa.Integer(), nullable=True),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("performed_by_user_id", sa.Integer(), nullable=False),
        sa.Column("booking_date", sa.Date(), nullable=False),
        sa.Column("direction", cashbook_direction, nullable=False),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("amount_gross", sa.Float(), nullable=False),
        sa.Column("tax_rate", sa.Float(), nullable=False),
        sa.Column("tax_amount", sa.Float(), nullable=False),
        sa.Column("amount_net", sa.Float(), nullable=False),
        sa.Column("counterparty", sa.String(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("payment_method", sa.String(), nullable=True),
        sa.Column("receipt_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["apiary_id"], ["apiaries.id"]),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["performed_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["receipt_id"], ["cashbook_receipts.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_cashbook_entries_id"), "cashbook_entries", ["id"], unique=False)

    with op.batch_alter_table("inspections") as batch_op:
        batch_op.add_column(sa.Column("performed_by_user_id", sa.Integer(), sa.ForeignKey("users.id", name="fk_inspections_performed_by_user_id"), nullable=True))
    with op.batch_alter_table("feedings") as batch_op:
        batch_op.add_column(sa.Column("performed_by_user_id", sa.Integer(), sa.ForeignKey("users.id", name="fk_feedings_performed_by_user_id"), nullable=True))
    with op.batch_alter_table("treatments") as batch_op:
        batch_op.add_column(sa.Column("performed_by_user_id", sa.Integer(), sa.ForeignKey("users.id", name="fk_treatments_performed_by_user_id"), nullable=True))
    with op.batch_alter_table("harvests") as batch_op:
        batch_op.add_column(sa.Column("performed_by_user_id", sa.Integer(), sa.ForeignKey("users.id", name="fk_harvests_performed_by_user_id"), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("harvests") as batch_op:
        batch_op.drop_column("performed_by_user_id")
    with op.batch_alter_table("treatments") as batch_op:
        batch_op.drop_column("performed_by_user_id")
    with op.batch_alter_table("feedings") as batch_op:
        batch_op.drop_column("performed_by_user_id")
    with op.batch_alter_table("inspections") as batch_op:
        batch_op.drop_column("performed_by_user_id")
    op.drop_index(op.f("ix_cashbook_entries_id"), table_name="cashbook_entries")
    op.drop_table("cashbook_entries")
    op.drop_index(op.f("ix_cashbook_receipt_suggestions_id"), table_name="cashbook_receipt_suggestions")
    op.drop_table("cashbook_receipt_suggestions")
    op.drop_index(op.f("ix_cashbook_receipts_id"), table_name="cashbook_receipts")
    op.drop_table("cashbook_receipts")
    op.drop_index(op.f("ix_content_sections_id"), table_name="content_sections")
    op.drop_table("content_sections")
    op.drop_index(op.f("ix_content_pages_slug"), table_name="content_pages")
    op.drop_index(op.f("ix_content_pages_id"), table_name="content_pages")
    op.drop_table("content_pages")
    op.drop_index(op.f("ix_apiary_members_id"), table_name="apiary_members")
    op.drop_table("apiary_members")

    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        enum_type(bind, OCR_STATUS_VALUES, "ocrstatus", create_type=True).drop(bind, checkfirst=True)
        enum_type(bind, CASHBOOK_DIRECTION_VALUES, "cashbookdirection", create_type=True).drop(bind, checkfirst=True)
        enum_type(bind, APIARY_MEMBER_ROLE_VALUES, "apiarymemberrole", create_type=True).drop(bind, checkfirst=True)
