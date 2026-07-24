from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class WeightReading(Base):
    """Stockwaage (#46) weight time series. Empty until a vendor integration lands
    (explicitly out of scope for this ticket — no device/vendor is chosen yet).
    """

    __tablename__ = "weight_readings"

    id = Column(Integer, primary_key=True, index=True)
    hive_id = Column(Integer, ForeignKey("hives.id"), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    weight_kg = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    hive = relationship("Hive", back_populates="weight_readings")
