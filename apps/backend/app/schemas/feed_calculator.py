from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class FeedCalculatorSeason(str, Enum):
    winter = "winter"
    spring_buildup = "spring_buildup"
    summer_gap = "summer_gap"


class FeedCalculatorRequest(BaseModel):
    colony_count: int = Field(..., ge=1, le=1000)
    colony_strength: str = Field("medium", pattern="^(weak|medium|strong)$")
    season: FeedCalculatorSeason = FeedCalculatorSeason.winter


class FeedCalculatorResponse(BaseModel):
    kg_sugar_per_colony: float
    total_kg_sugar: float
    formula_note: str
