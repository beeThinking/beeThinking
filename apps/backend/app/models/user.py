from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    hives = relationship("Hive", back_populates="owner", cascade="all, delete-orphan")
    apiaries = relationship("Apiary", back_populates="owner", cascade="all, delete-orphan")
    queens = relationship("Queen", back_populates="owner", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="owner", cascade="all, delete-orphan")
    treatments = relationship("Treatment", back_populates="owner", cascade="all, delete-orphan")
    harvests = relationship("Harvest", back_populates="owner", cascade="all, delete-orphan")
    photos = relationship("Photo", back_populates="owner", cascade="all, delete-orphan")
    varroa_weather_windows = relationship("VarroaWeatherWindow", back_populates="owner", cascade="all, delete-orphan")
    feedings = relationship("Feeding", back_populates="owner", cascade="all, delete-orphan")
    articles = relationship("Article", back_populates="owner", cascade="all, delete-orphan")
    inventory_items = relationship("InventoryItem", back_populates="owner", cascade="all, delete-orphan")
