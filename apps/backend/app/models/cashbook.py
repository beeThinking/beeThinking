import enum

from sqlalchemy import Column, Date, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class CashbookDirection(str, enum.Enum):
    income = "income"
    expense = "expense"


class OcrStatus(str, enum.Enum):
    pending = "pending"
    parsed = "parsed"
    confirmed = "confirmed"
    failed = "failed"


class CashbookReceipt(Base):
    __tablename__ = "cashbook_receipts"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    file_object_key = Column(String, nullable=True)
    filename = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    size_bytes = Column(Integer, nullable=False, default=0)
    ocr_status = Column(Enum(OcrStatus), nullable=False, default=OcrStatus.pending)
    ocr_text = Column(Text, nullable=True)
    ocr_provider = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="cashbook_receipts")
    suggestions = relationship("CashbookReceiptSuggestion", back_populates="receipt", cascade="all, delete-orphan")
    entries = relationship("CashbookEntry", back_populates="receipt")


class CashbookReceiptSuggestion(Base):
    __tablename__ = "cashbook_receipt_suggestions"

    id = Column(Integer, primary_key=True, index=True)
    receipt_id = Column(Integer, ForeignKey("cashbook_receipts.id"), nullable=False)
    field_name = Column(String, nullable=False)
    suggested_value = Column(String, nullable=False)
    confidence = Column(Float, nullable=False, default=0)

    receipt = relationship("CashbookReceipt", back_populates="suggestions")


class CashbookEntry(Base):
    __tablename__ = "cashbook_entries"

    id = Column(Integer, primary_key=True, index=True)
    apiary_id = Column(Integer, ForeignKey("apiaries.id"), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    performed_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    booking_date = Column(Date, nullable=False)
    direction = Column(Enum(CashbookDirection), nullable=False)
    category = Column(String, nullable=False)
    title = Column(String, nullable=True)
    invoice_number = Column(String, nullable=True)
    partner_id = Column(Integer, ForeignKey("office_partners.id"), nullable=True)
    amount_gross = Column(Float, nullable=False)
    tax_rate = Column(Float, nullable=False, default=0)
    tax_amount = Column(Float, nullable=False, default=0)
    amount_net = Column(Float, nullable=False)
    counterparty = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    payment_method = Column(String, nullable=True)
    receipt_id = Column(Integer, ForeignKey("cashbook_receipts.id"), nullable=True)
    sale_id = Column(Integer, ForeignKey("sales.id", use_alter=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    apiary = relationship("Apiary", back_populates="cashbook_entries")
    owner = relationship("User", foreign_keys=[owner_id], back_populates="cashbook_entries")
    performed_by = relationship("User", foreign_keys=[performed_by_user_id])
    receipt = relationship("CashbookReceipt", back_populates="entries")
