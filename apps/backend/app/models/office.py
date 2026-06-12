import enum
import json

from sqlalchemy import Column, Date, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from app.db.database import Base


class OfficePartnerType(str, enum.Enum):
    customer = "customer"
    supplier = "supplier"


class OfficeDocumentType(str, enum.Enum):
    receipt = "receipt"
    invoice = "invoice"
    offer = "offer"
    report = "report"


class OfficeDocumentStatus(str, enum.Enum):
    draft = "draft"
    sent = "sent"
    accepted = "accepted"
    paid = "paid"
    cancelled = "cancelled"


class OfficePartner(Base):
    __tablename__ = "office_partners"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    partner_type = Column(Enum(OfficePartnerType), nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    tax_id = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class OfficeDocument(Base):
    __tablename__ = "office_documents"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    partner_id = Column(Integer, ForeignKey("office_partners.id"), nullable=True)
    document_type = Column(Enum(OfficeDocumentType), nullable=False)
    status = Column(Enum(OfficeDocumentStatus), nullable=False, default=OfficeDocumentStatus.draft)
    document_number = Column(String, nullable=False)
    title = Column(String, nullable=False)
    document_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=True)
    amount_gross = Column(Float, nullable=False, default=0)
    tax_rate = Column(Float, nullable=False, default=0)
    tax_amount = Column(Float, nullable=False, default=0)
    amount_net = Column(Float, nullable=False, default=0)
    line_items_json = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    receipt_id = Column(Integer, ForeignKey("cashbook_receipts.id"), nullable=True)
    cashbook_entry_id = Column(Integer, ForeignKey("cashbook_entries.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @property
    def line_items(self) -> list[dict]:
        if not self.line_items_json:
            return []
        try:
            return json.loads(self.line_items_json)
        except json.JSONDecodeError:
            return []
