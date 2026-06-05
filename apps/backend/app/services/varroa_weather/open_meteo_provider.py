from datetime import date

import requests

from app.schemas.varroa_weather import WeatherDay
from app.services.varroa_weather.base import VarroaWeatherProvider


class OpenMeteoProvider(VarroaWeatherProvider):
    source = "open-meteo"
    provider_version = "open-meteo-v1"

    def fetch_days(self, latitude: float, longitude: float, days: int) -> list[WeatherDay]:
        response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "daily": ",".join(
                    [
                        "temperature_2m_min",
                        "temperature_2m_max",
                        "relative_humidity_2m_mean",
                        "precipitation_probability_max",
                        "wind_speed_10m_max",
                    ]
                ),
                "forecast_days": days,
                "timezone": "auto",
            },
            timeout=8,
        )
        response.raise_for_status()
        payload = response.json()
        daily = payload.get("daily", {})
        times = daily.get("time", [])
        result = []
        for index, day in enumerate(times):
            result.append(
                WeatherDay(
                    date=date.fromisoformat(day),
                    min_temperature=_value(daily, "temperature_2m_min", index),
                    max_temperature=_value(daily, "temperature_2m_max", index),
                    avg_humidity=_value(daily, "relative_humidity_2m_mean", index),
                    precipitation_probability=_value(daily, "precipitation_probability_max", index),
                    wind_speed=_value(daily, "wind_speed_10m_max", index),
                    raw_payload={key: _value(daily, key, index) for key in daily if key != "time"},
                )
            )
        return result


def _value(payload: dict, key: str, index: int):
    values = payload.get(key) or []
    return values[index] if index < len(values) else None
