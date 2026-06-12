from datetime import date

import pytest

from app.models.apiary import Apiary
from app.models.varroa_weather import VarroaTreatmentType, VarroaWeatherRating
from app.services.varroa_weather.base import rate_treatment_weather_window
from app.services.varroa_weather.schemas import WeatherDay
from app.services.varroa_weather.service import get_varroa_weather_window


@pytest.mark.unit
class TestVarroaWeather:
    def test_rates_formic_acid_suitable_window(self):
        day = WeatherDay(date.today(), 16, 24, 65, 10, 12, {})

        rating, _ = rate_treatment_weather_window(day, VarroaTreatmentType.formic_acid_short)
        assert rating == VarroaWeatherRating.suitable

    def test_rates_formic_acid_hot_day_unsuitable(self):
        day = WeatherDay(date.today(), 20, 31, 65, 10, 12, {})

        rating, _ = rate_treatment_weather_window(day, VarroaTreatmentType.formic_acid_short)
        assert rating == VarroaWeatherRating.unsuitable

    def test_windows_are_cached(self, db, test_user):
        apiary = Apiary(stock_number="Weather Stand", name="Weather Stand", owner_id=test_user.id, latitude=50.0, longitude=8.0)
        db.add(apiary)
        db.commit()
        db.refresh(apiary)

        first = get_varroa_weather_window(
            db, apiary.id, test_user.id, VarroaTreatmentType.formic_acid_short, date.today(), days=3
        )
        second = get_varroa_weather_window(
            db, apiary.id, test_user.id, VarroaTreatmentType.formic_acid_short, date.today(), days=3
        )

        assert len(first) == 3
        assert [window.id for window in first] == [window.id for window in second]
