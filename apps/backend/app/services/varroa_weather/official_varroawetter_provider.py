from app.schemas.varroa_weather import WeatherDay
from app.services.varroa_weather.base import VarroaWeatherProvider


class OfficialVarroaWeatherProvider(VarroaWeatherProvider):
    source = "official-varroawetter"
    provider_version = "stub-v1"

    def fetch_days(self, latitude: float, longitude: float, days: int) -> list[WeatherDay]:
        raise RuntimeError("No official Varroa weather API endpoint configured")
