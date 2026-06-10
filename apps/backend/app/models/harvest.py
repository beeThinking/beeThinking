from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Harvest(Base):
    __tablename__ = "harvests"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    performed_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    apiary_id = Column(Integer, ForeignKey("apiaries.id"), nullable=True)
    hive_id = Column(Integer, ForeignKey("hives.id"), nullable=True)
    harvest_date = Column(Date, nullable=False)
    crop_type = Column(String, nullable=True)
    amount_kg = Column(Float, nullable=False)
    batch_code = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owner = relationship("User", foreign_keys=[owner_id], back_populates="harvests")
    performed_by = relationship("User", foreign_keys=[performed_by_user_id])
    apiary = relationship("Apiary", back_populates="harvests")
    hive = relationship("Hive", back_populates="harvests")
