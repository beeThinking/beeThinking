from sqlalchemy import Column, Integer, String, Boolean, Float, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Inspection(Base):
    __tablename__ = "inspections"

    id = Column(Integer, primary_key=True, index=True)
    hive_id = Column(Integer, ForeignKey("hives.id"), nullable=False)
    date = Column(Date, nullable=False)
    queen_seen = Column(Boolean, nullable=False, default=False)
    brood_strength = Column(Integer, nullable=True)
    varroa_count = Column(Float, nullable=True)
    food_stores = Column(Integer, nullable=True)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    hive = relationship("Hive", back_populates="inspections")
