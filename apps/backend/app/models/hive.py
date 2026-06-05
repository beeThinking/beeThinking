from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.database import Base


class HiveStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    lost = "lost"


class HiveType(str, enum.Enum):
    langstroth = "langstroth"
    dadant = "dadant"
    zander = "zander"
    other = "other"


class Hive(Base):
    __tablename__ = "hives"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=True)
    type = Column(Enum(HiveType), default=HiveType.langstroth, nullable=False)
    status = Column(Enum(HiveStatus), default=HiveStatus.active, nullable=False)
    notes = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    apiary_id = Column(Integer, ForeignKey("apiaries.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owner = relationship("User", back_populates="hives")
    apiary = relationship("Apiary", back_populates="hives")
    inspections = relationship("Inspection", back_populates="hive", cascade="all, delete-orphan")
    queens = relationship("Queen", back_populates="hive")
    tasks = relationship("Task", back_populates="hive")
    treatments = relationship("Treatment", back_populates="hive", cascade="all, delete-orphan")
    harvests = relationship("Harvest", back_populates="hive")
    photos = relationship("Photo", back_populates="hive")
