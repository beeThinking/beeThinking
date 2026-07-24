from datetime import datetime

from pydantic import BaseModel, Field


class WeightReadingCreate(BaseModel):
    timestamp: datetime | None = None
    weight_kg: float = Field(..., ge=0)


class WeightReadingResponse(BaseModel):
    id: int
    hive_id: int
    timestamp: datetime
    weight_kg: float
    created_at: datetime

    class Config:
        from_attributes = True
