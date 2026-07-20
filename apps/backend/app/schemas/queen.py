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


class QueenResponse(QueenBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
