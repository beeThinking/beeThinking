import enum

from sqlalchemy import Column, Date, DateTime, Enum, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class VarroaTreatmentType(str, enum.Enum):
    formic_acid_short = "formic_acid_short"
    formic_acid_long = "formic_acid_long"
    thymol = "thymol"
    oxalic_acid_dribble = "oxalic_acid_dribble"
    oxalic_acid_sublimation = "oxalic_acid_sublimation"
    lactic_acid = "lactic_acid"
    biotechnical = "biotechnical"
    other = "other"


class VarroaWeatherRating(str, enum.Enum):
    suitable = "suitable"
    caution = "caution"
    unsuitable = "unsuitable"
    unknown = "unknown"


class VarroaWeatherWindow(Base):
    __tablename__ = "varroa_weather_windows"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    apiary_id = Column(Integer, ForeignKey("apiaries.id"), nullable=False)
    source = Column(String, nullable=False)
    provider_version = Column(String, nullable=False)
    treatment_type = Column(Enum(VarroaTreatmentType), nullable=False)
    date = Column(Date, nullable=False)
    rating = Column(Enum(VarroaWeatherRating), nullable=False)
    reason = Column(String, nullable=False)
    min_temperature = Column(Float, nullable=True)
    max_temperature = Column(Float, nullable=True)
    avg_humidity = Column(Float, nullable=True)
    precipitation_probability = Column(Float, nullable=True)
    wind_speed = Column(Float, nullable=True)
    raw_payload_json = Column(JSON, nullable=True)
    fetched_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="varroa_weather_windows")
    apiary = relationship("Apiary", back_populates="varroa_weather_windows")
