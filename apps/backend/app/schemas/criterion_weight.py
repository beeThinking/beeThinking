from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class CriterionWeightBase(BaseModel):
    criterion_id: int
    weight: float = Field(1.0, ge=0)


class CriterionWeightUpsert(CriterionWeightBase):
    pass


class CriterionWeightResponse(CriterionWeightBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BreedingCandidateResponse(BaseModel):
    hive_id: int
    hive_name: str
    score: float
    latest_inspection_id: Optional[int] = None
    latest_inspection_date: Optional[date] = None
