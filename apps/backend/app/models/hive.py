from sqlalchemy import Boolean, Column, Integer, JSON, String, Date, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.database import Base


class HiveStatus(str, enum.Enum):
    active = "active"
    archived = "archived"
    dissolved = "dissolved"
    merged = "merged"
    sold = "sold"
    dead = "dead"
    inactive = "inactive"
    lost = "lost"
    created_by_mistake = "created_by_mistake"


class HiveType(str, enum.Enum):
    langstroth = "langstroth"
    dadant = "dadant"
    zander = "zander"
    other = "other"


class ColonyKind(str, enum.Enum):
    wirtschaftsvolk = "wirtschaftsvolk"
    ableger = "ableger"
    schwarm = "schwarm"
    kunstschwarm = "kunstschwarm"
    other = "other"


class Hive(Base):
    __tablename__ = "hives"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    stock_number = Column(String, nullable=True)
    location = Column(String, nullable=True)
    type = Column(Enum(HiveType), default=HiveType.langstroth, nullable=False)
    colony_kind = Column(String, default=ColonyKind.wirtschaftsvolk.value, nullable=False)
    established_at = Column(Date, nullable=True)
    tags = Column(JSON, nullable=True)
    sort_order = Column(Integer, default=0, nullable=False)
    status = Column(Enum(HiveStatus), default=HiveStatus.active, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_breeding_candidate = Column(Boolean, default=False, nullable=False)
    archived_at = Column(Date, nullable=True)
    merged_into_hive_id = Column(Integer, ForeignKey("hives.id"), nullable=True)
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
    feedings = relationship("Feeding", back_populates="hive")
    photos = relationship("Photo", back_populates="hive")
    merged_into_hive = relationship("Hive", remote_side=[id])
    events = relationship("HiveEvent", back_populates="hive", cascade="all, delete-orphan")
    varroa_checks = relationship("VarroaCheck", back_populates="hive", cascade="all, delete-orphan")
    breeding_series = relationship("Zuchtreihe", back_populates="herkunftsvolk")
