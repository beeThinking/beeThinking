from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel

from app.models.varroa_weather import VarroaTreatmentType, VarroaWeatherRating


class VarroaWeatherWindowResponse(BaseModel):
    id: int
    apiary_id: int
    source: str
    provider_version: str
    treatment_type: VarroaTreatmentType
    date: date
    rating: VarroaWeatherRating
    reason: str
    min_temperature: Optional[float] = None
    max_temperature: Optional[float] = None
    avg_humidity: Optional[float] = None
    precipitation_probability: Optional[float] = None
    wind_speed: Optional[float] = None
    fetched_at: datetime
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class VarroaWeatherRefreshResponse(BaseModel):
    windows: list[VarroaWeatherWindowResponse]


class VarroaAssistantResponse(BaseModel):
    hive_id: int
    apiary_id: int
    disclaimer: str
    source_note: str
    windows: list[VarroaWeatherWindowResponse]


class WeatherDay(BaseModel):
    date: date
    min_temperature: Optional[float] = None
    max_temperature: Optional[float] = None
    avg_humidity: Optional[float] = None
    precipitation_probability: Optional[float] = None
    wind_speed: Optional[float] = None
    raw_payload: dict[str, Any] = {}
