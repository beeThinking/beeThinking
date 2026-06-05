from datetime import date, datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.apiary import Apiary
from app.models.varroa_weather import VarroaTreatmentType, VarroaWeatherRating, VarroaWeatherWindow
from app.services.varroa_weather.base import rate_treatment_weather_window
from app.services.varroa_weather.internal_rules_provider import InternalRulesProvider
from app.services.varroa_weather.official_varroawetter_provider import OfficialVarroaWeatherProvider
from app.services.varroa_weather.open_meteo_provider import OpenMeteoProvider


def get_varroa_weather_window(
    db: Session,
    apiary_id: int,
    owner_id: int,
    treatment_type: VarroaTreatmentType,
    start_date: date,
    days: int = 5,
) -> list[VarroaWeatherWindow]:
    end_date = start_date + timedelta(days=days)
    cached = (
        db.query(VarroaWeatherWindow)
        .filter(
            VarroaWeatherWindow.owner_id == owner_id,
            VarroaWeatherWindow.apiary_id == apiary_id,
            VarroaWeatherWindow.treatment_type == treatment_type,
            VarroaWeatherWindow.date >= start_date,
            VarroaWeatherWindow.date < end_date,
        )
        .order_by(VarroaWeatherWindow.date)
        .all()
    )
    if len(cached) >= days and _fresh(cached[0].fetched_at):
        return cached
    refreshed = refresh_varroa_weather_windows(
        db,
        apiary_id=apiary_id,
        owner_id=owner_id,
        days=days,
        treatment_types=[treatment_type],
        start_date=start_date,
    )
    return [window for window in refreshed if window.treatment_type == treatment_type]


def refresh_varroa_weather_windows(
    db: Session,
    apiary_id: int,
    owner_id: int,
    days: int = 5,
    treatment_types: list[VarroaTreatmentType] | None = None,
    start_date: date | None = None,
) -> list[VarroaWeatherWindow]:
    apiary = db.query(Apiary).filter(Apiary.id == apiary_id, Apiary.owner_id == owner_id).first()
    if not apiary:
        return []

    treatment_types = treatment_types or list(VarroaTreatmentType)
    provider = _provider()
    try:
        weather_days = provider.fetch_days(apiary.latitude or 0, apiary.longitude or 0, days)
    except Exception:
        provider = InternalRulesProvider()
        weather_days = provider.fetch_days(apiary.latitude or 0, apiary.longitude or 0, days)

    start = start_date or date.today()
    end = start + timedelta(days=days)
    db.query(VarroaWeatherWindow).filter(
        VarroaWeatherWindow.owner_id == owner_id,
        VarroaWeatherWindow.apiary_id == apiary_id,
        VarroaWeatherWindow.date >= start,
        VarroaWeatherWindow.date < end,
        VarroaWeatherWindow.treatment_type.in_(treatment_types),
    ).delete(synchronize_session=False)

    windows = []
    fetched_at = datetime.now(timezone.utc)
    for weather_day in weather_days:
        for treatment_type in treatment_types:
            rating, reason = rate_treatment_weather_window(weather_day, treatment_type)
            window = VarroaWeatherWindow(
                owner_id=owner_id,
                apiary_id=apiary_id,
                source=provider.source,
                provider_version=provider.provider_version,
                treatment_type=treatment_type,
                date=weather_day.date,
                rating=rating,
                reason=reason,
                min_temperature=weather_day.min_temperature,
                max_temperature=weather_day.max_temperature,
                avg_humidity=weather_day.avg_humidity,
                precipitation_probability=weather_day.precipitation_probability,
                wind_speed=weather_day.wind_speed,
                raw_payload_json=weather_day.raw_payload,
                fetched_at=fetched_at,
            )
            db.add(window)
            windows.append(window)
    db.commit()
    for window in windows:
        db.refresh(window)
    return sorted(windows, key=lambda item: (item.date, item.treatment_type.value))


def suggest_best_treatment_days(
    db: Session,
    apiary_id: int,
    owner_id: int,
    treatment_type: VarroaTreatmentType,
    days: int = 5,
) -> list[VarroaWeatherWindow]:
    windows = get_varroa_weather_window(db, apiary_id, owner_id, treatment_type, date.today(), days)
    rank = {
        VarroaWeatherRating.suitable: 0,
        VarroaWeatherRating.caution: 1,
        VarroaWeatherRating.unknown: 2,
        VarroaWeatherRating.unsuitable: 3,
    }
    return sorted(windows, key=lambda window: (rank[window.rating], window.date))


def _provider():
    provider_name = get_settings().VARROA_WEATHER_PROVIDER
    if provider_name == "official_varroawetter":
        return OfficialVarroaWeatherProvider()
    if provider_name == "open_meteo":
        return OpenMeteoProvider()
    return InternalRulesProvider()


def _fresh(fetched_at: datetime) -> bool:
    if fetched_at.tzinfo is None:
        fetched_at = fetched_at.replace(tzinfo=timezone.utc)
    age = datetime.now(timezone.utc) - fetched_at
    return age <= timedelta(hours=get_settings().VARROA_WEATHER_CACHE_TTL_HOURS)
