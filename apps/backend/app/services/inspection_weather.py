from dataclasses import dataclass
from datetime import datetime, timezone

import requests

from app.models.hive import Hive


@dataclass(frozen=True)
class InspectionWeatherSnapshot:
    weather: str
    weather_temperature: float | None
    weather_humidity: float | None
    weather_wind_speed: float | None
    weather_precipitation: float | None
    weather_code: int | None
    weather_source: str
    weather_fetched_at: datetime


def fetch_inspection_weather(hive: Hive) -> InspectionWeatherSnapshot | None:
    apiary = hive.apiary
    if not apiary or apiary.latitude is None or apiary.longitude is None:
        return None

    response = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": apiary.latitude,
            "longitude": apiary.longitude,
            "current": ",".join(
                [
                    "temperature_2m",
                    "relative_humidity_2m",
                    "precipitation",
                    "weather_code",
                    "wind_speed_10m",
                ]
            ),
            "timezone": "auto",
        },
        timeout=8,
    )
    response.raise_for_status()
    current = response.json().get("current", {})

    temperature = _number(current.get("temperature_2m"))
    humidity = _number(current.get("relative_humidity_2m"))
    precipitation = _number(current.get("precipitation"))
    wind_speed = _number(current.get("wind_speed_10m"))
    weather_code = _int(current.get("weather_code"))
    description = weather_code_label(weather_code)

    return InspectionWeatherSnapshot(
        weather=_summary(description, temperature, humidity, wind_speed, precipitation),
        weather_temperature=temperature,
        weather_humidity=humidity,
        weather_wind_speed=wind_speed,
        weather_precipitation=precipitation,
        weather_code=weather_code,
        weather_source="open-meteo",
        weather_fetched_at=datetime.now(timezone.utc),
    )


def weather_code_label(code: int | None) -> str:
    labels = {
        0: "Klar",
        1: "Überwiegend klar",
        2: "Teilweise bewölkt",
        3: "Bewölkt",
        45: "Nebel",
        48: "Reifnebel",
        51: "Leichter Nieselregen",
        53: "Nieselregen",
        55: "Starker Nieselregen",
        61: "Leichter Regen",
        63: "Regen",
        65: "Starker Regen",
        71: "Leichter Schnee",
        73: "Schnee",
        75: "Starker Schnee",
        80: "Leichte Schauer",
        81: "Schauer",
        82: "Starke Schauer",
        95: "Gewitter",
        96: "Gewitter mit Hagel",
        99: "Starkes Gewitter mit Hagel",
    }
    return labels.get(code, "Wetter")


def _summary(
    description: str,
    temperature: float | None,
    humidity: float | None,
    wind_speed: float | None,
    precipitation: float | None,
) -> str:
    parts = [description]
    if temperature is not None:
        parts.append(f"{temperature:g} °C")
    if humidity is not None:
        parts.append(f"{humidity:g} % rF")
    if wind_speed is not None:
        parts.append(f"Wind {wind_speed:g} km/h")
    if precipitation is not None and precipitation > 0:
        parts.append(f"Regen {precipitation:g} mm")
    return " · ".join(parts)


def _number(value) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _int(value) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
