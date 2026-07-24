import datetime as dt
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.breeding_step import BreedingStepName


class BreedingStepBase(BaseModel):
    name: BreedingStepName
    date: date
    notes: Optional[str] = Field(None, max_length=1000)


class BreedingStepCreate(BreedingStepBase):
    pass


class BreedingStepUpdate(BaseModel):
    name: Optional[BreedingStepName] = None
    date: Optional[dt.date] = None
    notes: Optional[str] = Field(None, max_length=1000)


class BreedingStepResponse(BreedingStepBase):
    id: int
    zuchtreihe_id: int
    task_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BreedingStepsGenerateRequest(BaseModel):
    umlarven_date: date


class ZuchtreiheBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    apiary_id: int
    herkunftsvolk_id: Optional[int] = None
    anzahl_larven: Optional[int] = Field(None, ge=0)
    anzahl_angenommen: Optional[int] = Field(None, ge=0)
    anzahl_geschluepft: Optional[int] = Field(None, ge=0)
    anzahl_begattet: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = Field(None, max_length=1000)


class ZuchtreiheCreate(ZuchtreiheBase):
    pass


class ZuchtreiheUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    apiary_id: Optional[int] = None
    herkunftsvolk_id: Optional[int] = None
    anzahl_larven: Optional[int] = Field(None, ge=0)
    anzahl_angenommen: Optional[int] = Field(None, ge=0)
    anzahl_geschluepft: Optional[int] = Field(None, ge=0)
    anzahl_begattet: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = Field(None, max_length=1000)


class ZuchtreiheResponse(ZuchtreiheBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    success_rate_angenommen: Optional[float] = None
    success_rate_geschluepft: Optional[float] = None
    success_rate_begattet: Optional[float] = None
    steps: list[BreedingStepResponse] = []

    class Config:
        from_attributes = True
