from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class VarroaCheckBase(BaseModel):
    hive_id: int
    date: date
    method: Optional[str] = Field(None, max_length=120)
    mite_count: Optional[int] = Field(None, ge=0)
    mites_per_day: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = Field(None, max_length=2000)


class VarroaCheckCreate(VarroaCheckBase):
    pass


class VarroaCheckUpdate(BaseModel):
    date: Optional[date] = None
    method: Optional[str] = Field(None, max_length=120)
    mite_count: Optional[int] = Field(None, ge=0)
    mites_per_day: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = Field(None, max_length=2000)


class VarroaCheckResponse(VarroaCheckBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
