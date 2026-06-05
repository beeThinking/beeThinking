from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class TreatmentBase(BaseModel):
    hive_id: int
    started_at: date
    ended_at: Optional[date] = None
    product: str = Field(..., min_length=1, max_length=200)
    method: Optional[str] = Field(None, max_length=200)
    dosage: Optional[str] = Field(None, max_length=200)
    reason: Optional[str] = Field(None, max_length=300)
    weather_window_id: Optional[int] = None
    notes: Optional[str] = Field(None, max_length=1000)


class TreatmentCreate(TreatmentBase):
    pass


class TreatmentUpdate(BaseModel):
    hive_id: Optional[int] = None
    started_at: Optional[date] = None
    ended_at: Optional[date] = None
    product: Optional[str] = Field(None, min_length=1, max_length=200)
    method: Optional[str] = Field(None, max_length=200)
    dosage: Optional[str] = Field(None, max_length=200)
    reason: Optional[str] = Field(None, max_length=300)
    weather_window_id: Optional[int] = None
    notes: Optional[str] = Field(None, max_length=1000)


class TreatmentResponse(TreatmentBase):
    id: int
    owner_id: int
    weather_rating: Optional[str] = None
    weather_source: Optional[str] = None
    weather_fetched_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
