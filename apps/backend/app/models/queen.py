from sqlalchemy import Boolean, Column, Date, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Queen(Base):
    __tablename__ = "queens"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    hive_id = Column(Integer, ForeignKey("hives.id"), nullable=True)
    name = Column(String, nullable=True)
    year = Column(Integer, nullable=False)
    origin = Column(String, nullable=True)
    marking_color = Column(String, nullable=True)
    marking_code = Column(String, nullable=True)
    introduced_at = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    notes = Column(String, nullable=True)

    # Breeding data (M7.1)
    rasse = Column(String, nullable=True)
    linie = Column(String, nullable=True)
    lebensnummer = Column(String, nullable=True)
    paartyp = Column(String, nullable=True)

    # Beebreed-Zuchtbuchnummer (Land|LV|Züchter|Nr|Jahr) — Königin
    zuchtbuchnummer_land = Column(String, nullable=True)
    zuchtbuchnummer_lv = Column(String, nullable=True)
    zuchtbuchnummer_zuechter = Column(String, nullable=True)
    zuchtbuchnummer_nr = Column(String, nullable=True)
    zuchtbuchnummer_jahr = Column(Integer, nullable=True)

    # Beebreed-Zuchtbuchnummer — Mutter
    zuchtbuchnummer_mutter_land = Column(String, nullable=True)
    zuchtbuchnummer_mutter_lv = Column(String, nullable=True)
    zuchtbuchnummer_mutter_zuechter = Column(String, nullable=True)
    zuchtbuchnummer_mutter_nr = Column(String, nullable=True)
    zuchtbuchnummer_mutter_jahr = Column(Integer, nullable=True)

    # Beebreed-Zuchtbuchnummer — Drohnen
    zuchtbuchnummer_drohnen_land = Column(String, nullable=True)
    zuchtbuchnummer_drohnen_lv = Column(String, nullable=True)
    zuchtbuchnummer_drohnen_zuechter = Column(String, nullable=True)
    zuchtbuchnummer_drohnen_nr = Column(String, nullable=True)
    zuchtbuchnummer_drohnen_jahr = Column(Integer, nullable=True)

    # Buckfast-Pedigree (Pedigree|Kasten-Nr|Züchter|Jahr)
    pedigree_pedigree = Column(String, nullable=True)
    pedigree_kasten_nr = Column(String, nullable=True)
    pedigree_zuechter = Column(String, nullable=True)
    pedigree_jahr = Column(Integer, nullable=True)

    # Belegstelle (Land|Verband|Nummer|Durchgang)
    belegstelle_land = Column(String, nullable=True)
    belegstelle_verband = Column(String, nullable=True)
    belegstelle_nummer = Column(String, nullable=True)
    belegstelle_durchgang = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owner = relationship("User", back_populates="queens")
    hive = relationship("Hive", back_populates="queens")
