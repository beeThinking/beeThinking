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
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    hives = relationship("Hive", back_populates="owner", cascade="all, delete-orphan")
    apiaries = relationship("Apiary", back_populates="owner", cascade="all, delete-orphan")
    queens = relationship("Queen", back_populates="owner", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="owner", cascade="all, delete-orphan")
    treatments = relationship("Treatment", foreign_keys="Treatment.owner_id", back_populates="owner", cascade="all, delete-orphan")
    harvests = relationship("Harvest", foreign_keys="Harvest.owner_id", back_populates="owner", cascade="all, delete-orphan")
    photos = relationship("Photo", back_populates="owner", cascade="all, delete-orphan")
    varroa_weather_windows = relationship("VarroaWeatherWindow", back_populates="owner", cascade="all, delete-orphan")
    feedings = relationship("Feeding", foreign_keys="Feeding.owner_id", back_populates="owner", cascade="all, delete-orphan")
    articles = relationship("Article", back_populates="owner", cascade="all, delete-orphan")
    inventory_items = relationship("InventoryItem", back_populates="owner", cascade="all, delete-orphan")
    apiary_memberships = relationship("ApiaryMember", foreign_keys="ApiaryMember.user_id", back_populates="user", cascade="all, delete-orphan")
    content_updates = relationship("ContentPage", back_populates="updated_by")
    cashbook_entries = relationship("CashbookEntry", foreign_keys="CashbookEntry.owner_id", back_populates="owner", cascade="all, delete-orphan")
    cashbook_receipts = relationship("CashbookReceipt", back_populates="owner", cascade="all, delete-orphan")
