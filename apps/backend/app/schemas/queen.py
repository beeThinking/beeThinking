from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class QueenBase(BaseModel):
    hive_id: Optional[int] = None
    name: Optional[str] = Field(None, max_length=100)
    year: int = Field(..., ge=1900, le=2100)
    origin: Optional[str] = Field(None, max_length=200)
    marking_color: Optional[str] = Field(None, max_length=50)
    marking_code: Optional[str] = Field(None, max_length=50)
    introduced_at: Optional[date] = None
    is_active: bool = True
    notes: Optional[str] = Field(None, max_length=1000)

    # Breeding data (M7.1)
    rasse: Optional[str] = Field(None, max_length=100)
    linie: Optional[str] = Field(None, max_length=100)
    lebensnummer: Optional[str] = Field(None, max_length=100)
    paartyp: Optional[str] = Field(None, max_length=100)

    zuchtbuchnummer_land: Optional[str] = Field(None, max_length=50)
    zuchtbuchnummer_lv: Optional[str] = Field(None, max_length=50)
    zuchtbuchnummer_zuechter: Optional[str] = Field(None, max_length=100)
    zuchtbuchnummer_nr: Optional[str] = Field(None, max_length=50)
    zuchtbuchnummer_jahr: Optional[int] = Field(None, ge=1900, le=2100)

    zuchtbuchnummer_mutter_land: Optional[str] = Field(None, max_length=50)
    zuchtbuchnummer_mutter_lv: Optional[str] = Field(None, max_length=50)
    zuchtbuchnummer_mutter_zuechter: Optional[str] = Field(None, max_length=100)
    zuchtbuchnummer_mutter_nr: Optional[str] = Field(None, max_length=50)
    zuchtbuchnummer_mutter_jahr: Optional[int] = Field(None, ge=1900, le=2100)

    zuchtbuchnummer_drohnen_land: Optional[str] = Field(None, max_length=50)
    zuchtbuchnummer_drohnen_lv: Optional[str] = Field(None, max_length=50)
    zuchtbuchnummer_drohnen_zuechter: Optional[str] = Field(None, max_length=100)
    zuchtbuchnummer_drohnen_nr: Optional[str] = Field(None, max_length=50)
    zuchtbuchnummer_drohnen_jahr: Optional[int] = Field(None, ge=1900, le=2100)

    pedigree_pedigree: Optional[str] = Field(None, max_length=100)
    pedigree_kasten_nr: Optional[str] = Field(None, max_length=50)
    pedigree_zuechter: Optional[str] = Field(None, max_length=100)
    pedigree_jahr: Optional[int] = Field(None, ge=1900, le=2100)

    belegstelle_land: Optional[str] = Field(None, max_length=50)
    belegstelle_verband: Optional[str] = Field(None, max_length=100)
    belegstelle_nummer: Optional[str] = Field(None, max_length=50)
    belegstelle_durchgang: Optional[str] = Field(None, max_length=50)


class QueenCreate(QueenBase):
    pass


class QueenUpdate(BaseModel):
    hive_id: Optional[int] = None
    name: Optional[str] = Field(None, max_length=100)
    year: Optional[int] = Field(None, ge=1900, le=2100)
    origin: Optional[str] = Field(None, max_length=200)
    marking_color: Optional[str] = Field(None, max_length=50)
    marking_code: Optional[str] = Field(None, max_length=50)
    introduced_at: Optional[date] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = Field(None, max_length=1000)

    rasse: Optional[str] = Field(None, max_length=100)
    linie: Optional[str] = Field(None, max_length=100)
    lebensnummer: Optional[str] = Field(None, max_length=100)
    paartyp: Optional[str] = Field(None, max_length=100)

    zuchtbuchnummer_land: Optional[str] = Field(None, max_length=50)
    zuchtbuchnummer_lv: Optional[str] = Field(None, max_length=50)
    zuchtbuchnummer_zuechter: Optional[str] = Field(None, max_length=100)
    zuchtbuchnummer_nr: Optional[str] = Field(None, max_length=50)
    zuchtbuchnummer_jahr: Optional[int] = Field(None, ge=1900, le=2100)

    zuchtbuchnummer_mutter_land: Optional[str] = Field(None, max_length=50)
    zuchtbuchnummer_mutter_lv: Optional[str] = Field(None, max_length=50)
    zuchtbuchnummer_mutter_zuechter: Optional[str] = Field(None, max_length=100)
    zuchtbuchnummer_mutter_nr: Optional[str] = Field(None, max_length=50)
    zuchtbuchnummer_mutter_jahr: Optional[int] = Field(None, ge=1900, le=2100)

    zuchtbuchnummer_drohnen_land: Optional[str] = Field(None, max_length=50)
    zuchtbuchnummer_drohnen_lv: Optional[str] = Field(None, max_length=50)
    zuchtbuchnummer_drohnen_zuechter: Optional[str] = Field(None, max_length=100)
    zuchtbuchnummer_drohnen_nr: Optional[str] = Field(None, max_length=50)
    zuchtbuchnummer_drohnen_jahr: Optional[int] = Field(None, ge=1900, le=2100)

    pedigree_pedigree: Optional[str] = Field(None, max_length=100)
    pedigree_kasten_nr: Optional[str] = Field(None, max_length=50)
    pedigree_zuechter: Optional[str] = Field(None, max_length=100)
    pedigree_jahr: Optional[int] = Field(None, ge=1900, le=2100)

    belegstelle_land: Optional[str] = Field(None, max_length=50)
    belegstelle_verband: Optional[str] = Field(None, max_length=100)
    belegstelle_nummer: Optional[str] = Field(None, max_length=50)
    belegstelle_durchgang: Optional[str] = Field(None, max_length=50)


class QueenResponse(QueenBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
