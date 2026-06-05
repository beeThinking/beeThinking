from datetime import date, timedelta

from app.schemas.varroa_weather import WeatherDay
from app.services.varroa_weather.base import VarroaWeatherProvider


class InternalRulesProvider(VarroaWeatherProvider):
    source = "internal-rules"
    provider_version = "internal-rules-v1"

    def fetch_days(self, latitude: float, longitude: float, days: int) -> list[WeatherDay]:
        today = date.today()
        return [
            WeatherDay(
                date=today + timedelta(days=offset),
                min_temperature=None,
                max_temperature=None,
                avg_humidity=None,
                precipitation_probability=None,
                wind_speed=None,
                raw_payload={"reason": "weather provider disabled or unavailable"},
            )
            for offset in range(days)
        ]
