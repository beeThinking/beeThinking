from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    partner_id = Column(Integer, ForeignKey("office_partners.id"), nullable=True)
    sale_date = Column(Date, nullable=False)
    vat_rate = Column(Float, nullable=False)
    amount_gross = Column(Float, nullable=False, default=0)
    amount_net = Column(Float, nullable=False, default=0)
    notes = Column(String, nullable=True)
    cashbook_entry_id = Column(Integer, ForeignKey("cashbook_entries.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owner = relationship("User", foreign_keys=[owner_id])
    partner = relationship("OfficePartner", foreign_keys=[partner_id])
    cashbook_entry = relationship("CashbookEntry", foreign_keys=[cashbook_entry_id])
    items = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")


class SaleItem(Base):
    __tablename__ = "sale_items"

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id", ondelete="CASCADE"), nullable=False)
    inventory_item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    quantity = Column(Float, nullable=False)
    unit_price_gross = Column(Float, nullable=False)
    line_total_gross = Column(Float, nullable=False)

    sale = relationship("Sale", back_populates="items")
    inventory_item = relationship("InventoryItem")
