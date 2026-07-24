from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user
from app.crud import apiary as apiary_crud
from app.db.database import get_db
from app.models.user import User
from app.schemas.map import ApiaryMapMarker, ApiaryWeatherForecastResponse, ForagePlantEntry
from app.services.forage_plants import list_forage_plants
from app.services.inspection_weather import WeatherUnavailableError, fetch_apiary_weather_forecast

router = APIRouter()


@router.get("/apiaries", response_model=list[ApiaryMapMarker])
def list_map_apiaries(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Apiary markers for the Leaflet map view (#41). Reuses the already
    membership-scoped crud.apiary.get_apiaries rather than a separate query."""
    apiaries = apiary_crud.get_apiaries(db, owner_id=current_user.id)
    return [
        {
            "id": apiary.id,
            "name": apiary.name,
            "stock_number": apiary.stock_number,
            "latitude": apiary.latitude,
            "longitude": apiary.longitude,
            "hive_count": len(apiary.hives),
        }
        for apiary in apiaries
    ]


@router.get("/apiaries/{apiary_id}/weather", response_model=ApiaryWeatherForecastResponse)
def get_apiary_weather_forecast(
    apiary_id: int,
    forecast_days: int = 3,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_apiary = apiary_crud.get_apiary(db, apiary_id=apiary_id, owner_id=current_user.id)
    if not db_apiary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Apiary not found")
    try:
        forecast = fetch_apiary_weather_forecast(db_apiary, forecast_days=forecast_days)
    except WeatherUnavailableError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    if not forecast:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Apiary has no coordinates set")
    return {
        "apiary_id": apiary_id,
        "current": forecast.current,
        "daily": forecast.daily,
    }


@router.get("/forage-plants", response_model=list[ForagePlantEntry])
def get_forage_plants(current_user: User = Depends(get_current_active_user)):
    """Static curated Trachtpflanzen dataset (#41), served directly from an in-repo JSON file."""
    return list_forage_plants()
