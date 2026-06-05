from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Treatment(Base):
    __tablename__ = "treatments"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    hive_id = Column(Integer, ForeignKey("hives.id"), nullable=False)
    started_at = Column(Date, nullable=False)
    ended_at = Column(Date, nullable=True)
    product = Column(String, nullable=False)
    method = Column(String, nullable=True)
    dosage = Column(String, nullable=True)
    reason = Column(String, nullable=True)
    weather_window_id = Column(Integer, ForeignKey("varroa_weather_windows.id"), nullable=True)
    weather_rating = Column(String, nullable=True)
    weather_source = Column(String, nullable=True)
    weather_fetched_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owner = relationship("User", back_populates="treatments")
    hive = relationship("Hive", back_populates="treatments")
    weather_window = relationship("VarroaWeatherWindow")
