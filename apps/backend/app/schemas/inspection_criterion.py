from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.inspection_criterion import CriterionSection, CriterionValueType


class InspectionCriterionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    section: CriterionSection = CriterionSection.verschiedenes
    value_type: CriterionValueType = CriterionValueType.stars
    options: Optional[list[str]] = None
    sort_order: int = 0
    is_active: bool = True


class InspectionCriterionCreate(InspectionCriterionBase):
    pass


class InspectionCriterionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    section: Optional[CriterionSection] = None
    value_type: Optional[CriterionValueType] = None
    options: Optional[list[str]] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class InspectionCriterionResponse(InspectionCriterionBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
