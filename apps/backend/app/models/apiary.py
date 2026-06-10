from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Apiary(Base):
    __tablename__ = "apiaries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    notes = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owner = relationship("User", back_populates="apiaries")
    hives = relationship("Hive", back_populates="apiary")
    tasks = relationship("Task", back_populates="apiary")
    harvests = relationship("Harvest", back_populates="apiary")
    varroa_weather_windows = relationship("VarroaWeatherWindow", back_populates="apiary", cascade="all, delete-orphan")
    feedings = relationship("Feeding", back_populates="apiary")
    members = relationship("ApiaryMember", back_populates="apiary", cascade="all, delete-orphan")
    cashbook_entries = relationship("CashbookEntry", back_populates="apiary")
