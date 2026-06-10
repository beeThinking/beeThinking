import enum

from sqlalchemy import Column, Integer, String, Boolean, Float, Date, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class SwarmCells(str, enum.Enum):
    none = "none"
    play_cups = "play_cups"
    queen_cells = "queen_cells"


class HiveMood(str, enum.Enum):
    calm = "calm"
    normal = "normal"
    aggressive = "aggressive"


class HiveStrength(str, enum.Enum):
    weak = "weak"
    medium = "medium"
    strong = "strong"


class Inspection(Base):
    __tablename__ = "inspections"

    id = Column(Integer, primary_key=True, index=True)
    hive_id = Column(Integer, ForeignKey("hives.id"), nullable=False)
    performed_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    date = Column(Date, nullable=False)
    queen_seen = Column(Boolean, nullable=False, default=False)
    brood_strength = Column(Integer, nullable=True)
    varroa_count = Column(Float, nullable=True)
    food_stores = Column(Integer, nullable=True)
    swarm_cells = Column(Enum(SwarmCells), default=SwarmCells.none, nullable=False)
    mood = Column(Enum(HiveMood), default=HiveMood.normal, nullable=False)
    strength = Column(Enum(HiveStrength), default=HiveStrength.medium, nullable=False)
    weather = Column(String, nullable=True)
    weather_temperature = Column(Float, nullable=True)
    weather_humidity = Column(Float, nullable=True)
    weather_wind_speed = Column(Float, nullable=True)
    weather_precipitation = Column(Float, nullable=True)
    weather_code = Column(Integer, nullable=True)
    weather_source = Column(String, nullable=True)
    weather_fetched_at = Column(DateTime(timezone=True), nullable=True)
    next_steps = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    hive = relationship("Hive", back_populates="inspections")
    performed_by = relationship("User")
    photos = relationship("Photo", back_populates="inspection")
