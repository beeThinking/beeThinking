from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.hive import HiveStatus, HiveType


class HiveBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    location: Optional[str] = Field(None, max_length=200)
    type: HiveType = HiveType.langstroth
    status: HiveStatus = HiveStatus.active
    notes: Optional[str] = Field(None, max_length=1000)


class HiveCreate(HiveBase):
    pass


class HiveUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    location: Optional[str] = Field(None, max_length=200)
    type: Optional[HiveType] = None
    status: Optional[HiveStatus] = None
    notes: Optional[str] = Field(None, max_length=1000)


class HiveResponse(HiveBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
