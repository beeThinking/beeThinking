from datetime import date
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.batch import BatchResponse
from app.schemas.harvest import HarvestResponse


class TraceabilityHiveInfo(BaseModel):
    id: int
    name: str
    stock_number: Optional[str] = None

    class Config:
        from_attributes = True


class TraceabilityApiaryInfo(BaseModel):
    id: int
    name: Optional[str] = None
    stock_number: str

    class Config:
        from_attributes = True


class TraceabilityHarvestEntry(BaseModel):
    harvest: HarvestResponse
    hive: Optional[TraceabilityHiveInfo] = None
    apiary: Optional[TraceabilityApiaryInfo] = None


class TraceabilityInventoryItemInfo(BaseModel):
    id: int
    article_id: int
    quantity: float
    unit: str
    best_before: Optional[date] = None
    archived: bool

    class Config:
        from_attributes = True


class TraceabilityResponse(BaseModel):
    lot_number: str
    batch: BatchResponse
    harvests: list[TraceabilityHarvestEntry] = Field(default_factory=list)
    inventory_items: list[TraceabilityInventoryItemInfo] = Field(default_factory=list)
