from dataclasses import dataclass
from datetime import date
from typing import Any

from app.models.varroa_weather import VarroaTreatmentType, VarroaWeatherRating


@dataclass(frozen=True)
class WeatherDay:
    date: date
    min_temperature: float | None
    max_temperature: float | None
    avg_humidity: float | None
    precipitation_probability: float | None
    wind_speed: float | None
    raw_payload: dict[str, Any]


@dataclass(frozen=True)
class RatedWeatherWindow:
    weather_day: WeatherDay
    treatment_type: VarroaTreatmentType
    rating: VarroaWeatherRating
    reason: str
    source: str
    provider_version: str
