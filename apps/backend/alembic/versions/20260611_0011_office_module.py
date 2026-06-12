"""office module

Revision ID: 20260611_0011
Revises: 20260611_0010
Create Date: 2026-06-11
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260611_0011"
down_revision = "20260611_0010"
branch_labels = None
depends_on = None


PARTNER_TYPE_VALUES = ("customer", "supplier")
DOCUMENT_TYPE_VALUES = ("receipt", "invoice", "offer", "report")
DOCUMENT_STATUS_VALUES = ("draft", "sent", "accepted", "paid", "cancelled")


def enum_type(bind, values: tuple[str, ...], name: str, create_type: bool = False) -> sa.Enum:
    if bind.dialect.name == "postgresql":
        return postgresql.ENUM(*values, name=name, create_type=create_type)
    return sa.Enum(*values, name=name, native_enum=False)


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        enum_type(bind, PARTNER_TYPE_VALUES, "officepartnertype", create_type=True).create(bind, checkfirst=True)
        enum_type(bind, DOCUMENT_TYPE_VALUES, "officedocumenttype", create_type=True).create(bind, checkfirst=True)
        enum_type(bind, DOCUMENT_STATUS_VALUES, "officedocumentstatus", create_type=True).create(bind, checkfirst=True)

    partner_type = enum_type(bind, PARTNER_TYPE_VALUES, "officepartnertype")
    document_type = enum_type(bind, DOCUMENT_TYPE_VALUES, "officedocumenttype")
    document_status = enum_type(bind, DOCUMENT_STATUS_VALUES, "officedocumentstatus")

    op.create_table(
        "office_partners",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("partner_type", partner_type, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("phone", sa.String(), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("tax_id", sa.String(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_office_partners_id"), "office_partners", ["id"], unique=False)
    op.create_index(op.f("ix_office_partners_owner_id"), "office_partners", ["owner_id"], unique=False)

    op.create_table(
        "office_documents",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("partner_id", sa.Integer(), nullable=True),
        sa.Column("document_type", document_type, nullable=False),
        sa.Column("status", document_status, nullable=False),
        sa.Column("document_number", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("document_date", sa.Date(), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("amount_gross", sa.Float(), nullable=False),
        sa.Column("tax_rate", sa.Float(), nullable=False),
        sa.Column("tax_amount", sa.Float(), nullable=False),
        sa.Column("amount_net", sa.Float(), nullable=False),
        sa.Column("line_items_json", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("receipt_id", sa.Integer(), nullable=True),
        sa.Column("cashbook_entry_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["cashbook_entry_id"], ["cashbook_entries.id"]),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["partner_id"], ["office_partners.id"]),
        sa.ForeignKeyConstraint(["receipt_id"], ["cashbook_receipts.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_office_documents_id"), "office_documents", ["id"], unique=False)
    op.create_index(op.f("ix_office_documents_owner_id"), "office_documents", ["owner_id"], unique=False)

    with op.batch_alter_table("cashbook_entries") as batch_op:
        batch_op.add_column(sa.Column("title", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("invoice_number", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("partner_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key("fk_cashbook_entries_partner_id", "office_partners", ["partner_id"], ["id"])


def downgrade() -> None:
    with op.batch_alter_table("cashbook_entries") as batch_op:
        batch_op.drop_constraint("fk_cashbook_entries_partner_id", type_="foreignkey")
        batch_op.drop_column("partner_id")
        batch_op.drop_column("invoice_number")
        batch_op.drop_column("title")

    op.drop_index(op.f("ix_office_documents_owner_id"), table_name="office_documents")
    op.drop_index(op.f("ix_office_documents_id"), table_name="office_documents")
    op.drop_table("office_documents")
    op.drop_index(op.f("ix_office_partners_owner_id"), table_name="office_partners")
    op.drop_index(op.f("ix_office_partners_id"), table_name="office_partners")
    op.drop_table("office_partners")

    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        enum_type(bind, DOCUMENT_STATUS_VALUES, "officedocumentstatus", create_type=True).drop(bind, checkfirst=True)
        enum_type(bind, DOCUMENT_TYPE_VALUES, "officedocumenttype", create_type=True).drop(bind, checkfirst=True)
        enum_type(bind, PARTNER_TYPE_VALUES, "officepartnertype", create_type=True).drop(bind, checkfirst=True)
