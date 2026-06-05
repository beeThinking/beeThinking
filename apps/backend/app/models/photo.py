from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Photo(Base):
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    hive_id = Column(Integer, ForeignKey("hives.id"), nullable=True)
    inspection_id = Column(Integer, ForeignKey("inspections.id"), nullable=True)
    object_key = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    size_bytes = Column(Integer, nullable=False)
    caption = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="photos")
    hive = relationship("Hive", back_populates="photos")
    inspection = relationship("Inspection", back_populates="photos")
