from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Queen(Base):
    __tablename__ = "queens"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    hive_id = Column(Integer, ForeignKey("hives.id"), nullable=True)
    name = Column(String, nullable=True)
    year = Column(Integer, nullable=False)
    origin = Column(String, nullable=True)
    marking_color = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owner = relationship("User", back_populates="queens")
    hive = relationship("Hive", back_populates="queens")
