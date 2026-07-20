import datetime as dt

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from app.models.hive import ColonyKind, HiveStatus, HiveType


class HiveBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    stock_number: Optional[str] = Field(None, max_length=50)
    type: HiveType = HiveType.langstroth
    colony_kind: ColonyKind = ColonyKind.wirtschaftsvolk
    status: HiveStatus = HiveStatus.active
    established_at: Optional[date] = None
    tags: Optional[list[str]] = None
    sort_order: int = Field(0, ge=0)
    notes: Optional[str] = Field(None, max_length=1000)
    apiary_id: int


class HiveCreate(HiveBase):
    pass


class HiveUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    stock_number: Optional[str] = Field(None, max_length=50)
    type: Optional[HiveType] = None
    colony_kind: Optional[ColonyKind] = None
    status: Optional[HiveStatus] = None
    established_at: Optional[date] = None
    tags: Optional[list[str]] = None
    sort_order: Optional[int] = Field(None, ge=0)
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
    active_queen_year: Optional[int] = None
    active_queen_color: Optional[str] = None
    active_queen_marking: Optional[str] = None
    queen_introduced_at: Optional[date] = None

    class Config:
        from_attributes = True


class HiveLifecycleRequest(BaseModel):
    reason: str = Field(..., min_length=1, max_length=100)
    date: date
    note: Optional[str] = Field(None, max_length=1000)
    target_hive_id: Optional[int] = None


class HiveMoveRequest(BaseModel):
    target_apiary_id: int
    date: date
    note: Optional[str] = Field(None, max_length=1000)


class HiveCopyRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    stock_number: Optional[str] = Field(None, max_length=50)
    date: date
    note: Optional[str] = Field(None, max_length=1000)


class HiveRequeenRequest(BaseModel):
    date: date
    year: int = Field(..., ge=1900, le=2100)
    marking_color: Optional[str] = Field(None, max_length=50)
    marking_code: Optional[str] = Field(None, max_length=50)
    introduced_at: Optional[date] = None
    name: Optional[str] = Field(None, max_length=100)
    origin: Optional[str] = Field(None, max_length=200)
    reason: Optional[str] = Field(None, max_length=200)
    note: Optional[str] = Field(None, max_length=1000)


class HiveReorderRequest(BaseModel):
    hive_ids: list[int] = Field(..., min_length=1)


class TimelineEntryUpdate(BaseModel):
    date: Optional[dt.date] = None
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    notes: Optional[str] = Field(None, max_length=2000)


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
