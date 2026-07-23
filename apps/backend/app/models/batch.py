from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Batch(Base):
    __tablename__ = "batches"
    __table_args__ = (
        UniqueConstraint("owner_id", "lot_number", name="uq_batches_owner_id_lot_number"),
    )

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lot_number = Column(String, nullable=False)
    best_before = Column(Date, nullable=True)
    total_amount_kg = Column(Float, nullable=False, default=0)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owner = relationship("User", foreign_keys=[owner_id])
    harvests = relationship("Harvest", back_populates="batch")
