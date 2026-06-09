from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class Feeding(Base):
    __tablename__ = "feedings"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    apiary_id = Column(Integer, ForeignKey("apiaries.id"), nullable=True)
    hive_id = Column(Integer, ForeignKey("hives.id"), nullable=True)
    date = Column(Date, nullable=False)
    feed_type = Column(String, nullable=False)
    amount_kg_or_l = Column(Float, nullable=False)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owner = relationship("User", back_populates="feedings")
    apiary = relationship("Apiary", back_populates="feedings")
    hive = relationship("Hive", back_populates="feedings")
