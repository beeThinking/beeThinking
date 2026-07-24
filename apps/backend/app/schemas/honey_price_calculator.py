from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class HoneyPriceCalculatorRequest(BaseModel):
    apiary_id: int
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    target_margin_percent: float = Field(0, ge=0, le=500)


class HoneyPriceCalculatorResponse(BaseModel):
    apiary_id: int
    total_relevant_costs: float
    total_harvested_kg: float
    colony_count: int
    cost_per_kg: Optional[float] = None
    cost_per_colony: Optional[float] = None
    suggested_price_per_kg: Optional[float] = None
    simplification_note: str
