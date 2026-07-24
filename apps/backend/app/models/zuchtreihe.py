from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Zuchtreihe(Base):
    __tablename__ = "zuchtreihen"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    apiary_id = Column(Integer, ForeignKey("apiaries.id"), nullable=False)
    herkunftsvolk_id = Column(Integer, ForeignKey("hives.id"), nullable=True)

    # Manual counters (M7.4) — entered directly by the beekeeper
    anzahl_larven = Column(Integer, nullable=True)
    anzahl_angenommen = Column(Integer, nullable=True)
    anzahl_geschluepft = Column(Integer, nullable=True)
    anzahl_begattet = Column(Integer, nullable=True)

    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owner = relationship("User", back_populates="zuchtreihen")
    apiary = relationship("Apiary", back_populates="zuchtreihen")
    herkunftsvolk = relationship("Hive", back_populates="breeding_series")
    steps = relationship("BreedingStep", back_populates="zuchtreihe", cascade="all, delete-orphan", order_by="BreedingStep.date")
