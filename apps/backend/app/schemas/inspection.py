from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime


class InspectionBase(BaseModel):
    date: date
    queen_seen: bool = False
    brood_strength: Optional[int] = Field(None, ge=1, le=10)
    varroa_count: Optional[float] = Field(None, ge=0)
    food_stores: Optional[int] = Field(None, ge=1, le=10)
    notes: Optional[str] = Field(None, max_length=2000)


class InspectionCreate(InspectionBase):
    pass


class InspectionUpdate(BaseModel):
    date: Optional[date] = None
    queen_seen: Optional[bool] = None
    brood_strength: Optional[int] = Field(None, ge=1, le=10)
    varroa_count: Optional[float] = Field(None, ge=0)
    food_stores: Optional[int] = Field(None, ge=1, le=10)
    notes: Optional[str] = Field(None, max_length=2000)


class InspectionResponse(InspectionBase):
    id: int
    hive_id: int
    created_at: datetime

    class Config:
        from_attributes = True
