from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class VarroaCheck(Base):
    __tablename__ = "varroa_checks"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    hive_id = Column(Integer, ForeignKey("hives.id"), nullable=False, index=True)
    date = Column(Date, nullable=False)
    method = Column(String, nullable=True)
    mite_count = Column(Integer, nullable=True)
    mites_per_day = Column(Float, nullable=True)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    hive = relationship("Hive", back_populates="varroa_checks")
