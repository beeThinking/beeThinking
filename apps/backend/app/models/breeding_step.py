import enum

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class BreedingStepName(str, enum.Enum):
    pflegevolk_vorbereiten = "pflegevolk_vorbereiten"
    umlarven = "umlarven"
    annahmekontrolle = "annahmekontrolle"
    kaefigen_1 = "kaefigen_1"
    kaefigen_2 = "kaefigen_2"
    schlupf = "schlupf"
    voelkchen_bilden = "voelkchen_bilden"
    belegstelle = "belegstelle"
    abholen = "abholen"


# Default day-offsets from the Umlarven date, per issue #33's resolution comment.
BREEDING_STEP_DEFAULT_OFFSETS: dict[BreedingStepName, int] = {
    BreedingStepName.pflegevolk_vorbereiten: -1,
    BreedingStepName.umlarven: 0,
    BreedingStepName.annahmekontrolle: 1,
    BreedingStepName.kaefigen_1: 10,
    BreedingStepName.kaefigen_2: 11,
    BreedingStepName.schlupf: 12,
    BreedingStepName.voelkchen_bilden: 13,
    BreedingStepName.belegstelle: 15,
    BreedingStepName.abholen: 30,
}

BREEDING_STEP_ORDER: list[BreedingStepName] = list(BREEDING_STEP_DEFAULT_OFFSETS.keys())


class BreedingStep(Base):
    __tablename__ = "breeding_steps"

    id = Column(Integer, primary_key=True, index=True)
    zuchtreihe_id = Column(Integer, ForeignKey("zuchtreihen.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    notes = Column(String, nullable=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    zuchtreihe = relationship("Zuchtreihe", back_populates="steps")
    task = relationship("Task")
