from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class FeedingBase(BaseModel):
    apiary_id: Optional[int] = None
    hive_id: Optional[int] = None
    date: date
    feed_type: str = Field(..., min_length=1, max_length=120)
    amount_kg_or_l: float = Field(..., gt=0)
    notes: Optional[str] = Field(None, max_length=2000)

    @model_validator(mode="after")
    def require_target(self):
        if self.apiary_id is None and self.hive_id is None:
            raise ValueError("apiary_id or hive_id is required")
        return self


class FeedingCreate(FeedingBase):
    pass


class FeedingUpdate(BaseModel):
    apiary_id: Optional[int] = None
    hive_id: Optional[int] = None
    date: Optional[date] = None
    feed_type: Optional[str] = Field(None, min_length=1, max_length=120)
    amount_kg_or_l: Optional[float] = Field(None, gt=0)
    notes: Optional[str] = Field(None, max_length=2000)


class FeedingResponse(FeedingBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
