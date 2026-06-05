from abc import ABC, abstractmethod

from app.models.varroa_weather import VarroaTreatmentType, VarroaWeatherRating
from app.schemas.varroa_weather import WeatherDay


class VarroaWeatherProvider(ABC):
    source = "base"
    provider_version = "1"

    @abstractmethod
    def fetch_days(self, latitude: float, longitude: float, days: int) -> list[WeatherDay]:
        raise NotImplementedError


def rate_treatment_weather_window(
    weather_day: WeatherDay, treatment_type: VarroaTreatmentType
) -> tuple[VarroaWeatherRating, str]:
    min_temp = weather_day.min_temperature
    max_temp = weather_day.max_temperature
    rain = weather_day.precipitation_probability
    wind = weather_day.wind_speed

    if min_temp is None or max_temp is None:
        return VarroaWeatherRating.unknown, "Wetterdaten unvollständig."

    rain_high = rain is not None and rain >= 60
    wind_high = wind is not None and wind >= 35

    if treatment_type in {VarroaTreatmentType.formic_acid_short, VarroaTreatmentType.formic_acid_long}:
        if max_temp > 30:
            return VarroaWeatherRating.unsuitable, "Höchsttemperatur für Ameisensäure zu hoch."
        if max_temp < 15:
            return VarroaWeatherRating.unsuitable, "Temperatur für Ameisensäure zu niedrig."
        if rain_high or wind_high or max_temp > 27:
            return VarroaWeatherRating.caution, "Wetterfenster kritisch; Packungsbeilage und Volkzustand prüfen."
        return VarroaWeatherRating.suitable, "Wetterfenster wirkt für Ameisensäure geeignet."

    if treatment_type == VarroaTreatmentType.thymol:
        if max_temp > 30 or max_temp < 15:
            return VarroaWeatherRating.unsuitable, "Temperaturbereich für Thymol ungünstig."
        if rain_high or max_temp > 27:
            return VarroaWeatherRating.caution, "Thymol-Wetterfenster kritisch; Details prüfen."
        return VarroaWeatherRating.suitable, "Wetterfenster wirkt für Thymol geeignet."

    if treatment_type in {VarroaTreatmentType.oxalic_acid_dribble, VarroaTreatmentType.oxalic_acid_sublimation}:
        if min_temp < -5:
            return VarroaWeatherRating.caution, "Sehr kalt; Anwendung und Methode genau prüfen."
        return VarroaWeatherRating.caution, "Wetter meist zweitrangig; Brutfreiheit, Zulassung und Methode prüfen."

    if treatment_type == VarroaTreatmentType.lactic_acid:
        if max_temp < 5:
            return VarroaWeatherRating.caution, "Kühl; Methode und Volkzustand prüfen."
        return VarroaWeatherRating.caution, "Planungshilfe; Brutfreiheit und Zulassung separat prüfen."

    if treatment_type == VarroaTreatmentType.biotechnical:
        return VarroaWeatherRating.suitable, "Biotechnische Maßnahme wetterarm; Volkzustand und Timing prüfen."

    return VarroaWeatherRating.unknown, "Keine gepflegte Wetterregel für diese Behandlung."
