from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class ApiaryMapMarker(BaseModel):
    """A Stand marker for the Leaflet map view (#41). Reuses membership-scoped
    crud.apiary.get_apiaries — no separate scoping logic needed."""

    id: int
    name: Optional[str] = None
    stock_number: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    hive_count: int = 0


class DailyForecastResponse(BaseModel):
    date: date
    weather_code: Optional[int] = None
    temperature_min: Optional[float] = None
    temperature_max: Optional[float] = None
    precipitation_sum: Optional[float] = None


class CurrentWeatherResponse(BaseModel):
    weather: str
    weather_temperature: Optional[float] = None
    weather_humidity: Optional[float] = None
    weather_wind_speed: Optional[float] = None
    weather_precipitation: Optional[float] = None
    weather_code: Optional[int] = None
    weather_source: str
    weather_fetched_at: datetime


class ApiaryWeatherForecastResponse(BaseModel):
    apiary_id: int
    current: Optional[CurrentWeatherResponse] = None
    daily: list[DailyForecastResponse] = []


class ForagePlantEntry(BaseModel):
    """A single Trachtpflanze (forage plant) entry from the static curated seed dataset."""

    id: str
    name_de: str
    name_latin: str | None = None
    bloom_start_month: int
    bloom_end_month: int
    forage_value: str
    notes: str | None = None
