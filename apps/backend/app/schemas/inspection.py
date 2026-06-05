from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from app.models.inspection import HiveMood, HiveStrength, SwarmCells


class InspectionBase(BaseModel):
    date: date
    queen_seen: bool = False
    brood_strength: Optional[int] = Field(None, ge=1, le=10)
    varroa_count: Optional[float] = Field(None, ge=0)
    food_stores: Optional[int] = Field(None, ge=1, le=10)
    swarm_cells: SwarmCells = SwarmCells.none
    mood: HiveMood = HiveMood.normal
    strength: HiveStrength = HiveStrength.medium
    weather: Optional[str] = Field(None, max_length=200)
    next_steps: Optional[str] = Field(None, max_length=2000)
    notes: Optional[str] = Field(None, max_length=2000)


class InspectionCreate(InspectionBase):
    pass


class InspectionUpdate(BaseModel):
    date: Optional[date] = None
    queen_seen: Optional[bool] = None
    brood_strength: Optional[int] = Field(None, ge=1, le=10)
    varroa_count: Optional[float] = Field(None, ge=0)
    food_stores: Optional[int] = Field(None, ge=1, le=10)
    swarm_cells: Optional[SwarmCells] = None
    mood: Optional[HiveMood] = None
    strength: Optional[HiveStrength] = None
    weather: Optional[str] = Field(None, max_length=200)
    next_steps: Optional[str] = Field(None, max_length=2000)
    notes: Optional[str] = Field(None, max_length=2000)


class InspectionResponse(InspectionBase):
    id: int
    hive_id: int
    created_at: datetime

    class Config:
        from_attributes = True
