from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel, Field


class HoneybookEntry(BaseModel):
    lot_number: Optional[str] = None
    status: Literal["batched", "unbatched"]
    harvest_date: date
    apiary_name: Optional[str] = None
    hive_name: Optional[str] = None
    crop_type: Optional[str] = None
    amount_kg: float
    water_content_percent: Optional[float] = None
    best_before: Optional[date] = None
    bottled_quantity: int = 0
    bottled_articles: list[str] = Field(default_factory=list)

    class Config:
        from_attributes = True
