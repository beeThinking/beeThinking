from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ApiaryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    address: Optional[str] = Field(None, max_length=300)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    notes: Optional[str] = Field(None, max_length=1000)


class ApiaryCreate(ApiaryBase):
    pass


class ApiaryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    address: Optional[str] = Field(None, max_length=300)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    notes: Optional[str] = Field(None, max_length=1000)


class ApiaryResponse(ApiaryBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    hive_count: int = 0

    class Config:
        from_attributes = True
