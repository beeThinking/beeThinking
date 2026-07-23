from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.inventory import InventoryItemResponse


class BatchHarvestSummary(BaseModel):
    id: int
    harvest_date: date
    apiary_id: Optional[int] = None
    hive_id: Optional[int] = None
    crop_type: Optional[str] = None
    amount_kg: float

    class Config:
        from_attributes = True


class BatchCreate(BaseModel):
    harvest_ids: list[int] = Field(default_factory=list)
    best_before: Optional[date] = None
    notes: Optional[str] = Field(None, max_length=1000)


class BatchUpdate(BaseModel):
    best_before: Optional[date] = None
    notes: Optional[str] = Field(None, max_length=1000)


class BatchResponse(BaseModel):
    id: int
    owner_id: int
    lot_number: str
    best_before: Optional[date] = None
    total_amount_kg: float
    remaining_kg: Optional[float] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    harvests: list[BatchHarvestSummary] = Field(default_factory=list)

    class Config:
        from_attributes = True


class BottleItem(BaseModel):
    article_id: int
    quantity: float = Field(..., gt=0)
    price: Optional[float] = Field(None, ge=0)
    best_before: Optional[date] = None


class BottleRequest(BaseModel):
    items: list[BottleItem] = Field(..., min_length=1)


class BottleResponse(BaseModel):
    batch: BatchResponse
    inventory_items: list[InventoryItemResponse] = Field(default_factory=list)
