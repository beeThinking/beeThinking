from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class HarvestBase(BaseModel):
    apiary_id: Optional[int] = None
    hive_id: Optional[int] = None
    harvest_date: date
    crop_type: Optional[str] = Field(None, max_length=100)
    amount_kg: float = Field(..., ge=0)
    batch_code: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=1000)


class HarvestCreate(HarvestBase):
    pass


class HarvestUpdate(BaseModel):
    apiary_id: Optional[int] = None
    hive_id: Optional[int] = None
    harvest_date: Optional[date] = None
    crop_type: Optional[str] = Field(None, max_length=100)
    amount_kg: Optional[float] = Field(None, ge=0)
    batch_code: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=1000)


class HarvestResponse(HarvestBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
