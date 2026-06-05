from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from app.models.hive import HiveStatus, HiveType


class HiveBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: HiveType = HiveType.langstroth
    status: HiveStatus = HiveStatus.active
    notes: Optional[str] = Field(None, max_length=1000)
    apiary_id: int


class HiveCreate(HiveBase):
    pass


class HiveUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    type: Optional[HiveType] = None
    status: Optional[HiveStatus] = None
    notes: Optional[str] = Field(None, max_length=1000)
    apiary_id: Optional[int] = None


class HiveResponse(HiveBase):
    id: int
    owner_id: int
    apiary_id: int
    is_active: bool
    archived_at: Optional[date] = None
    merged_into_hive_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class HiveLifecycleRequest(BaseModel):
    reason: str = Field(..., min_length=1, max_length=100)
    date: date
    note: Optional[str] = Field(None, max_length=1000)
    target_hive_id: Optional[int] = None


class HiveEventResponse(BaseModel):
    id: int
    user_id: int
    hive_id: int
    event_type: str
    event_date: date
    title: str
    description: Optional[str] = None
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[int] = None
    metadata_json: Optional[dict] = None
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
