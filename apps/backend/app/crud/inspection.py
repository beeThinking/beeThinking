from sqlalchemy.orm import Session
from typing import Optional
from app.models.inspection import Inspection
from app.models.task import Task
from app.schemas.inspection import InspectionCreate, InspectionUpdate
from app.services.beekeeping_rules import suggest_tasks_after_inspection
from app.services.inspection_weather import fetch_inspection_weather


def get_inspections(db: Session, hive_id: int) -> list[Inspection]:
    return db.query(Inspection).filter(Inspection.hive_id == hive_id).order_by(Inspection.date.desc()).all()


def get_inspection(db: Session, inspection_id: int, hive_id: int) -> Optional[Inspection]:
    return db.query(Inspection).filter(
        Inspection.id == inspection_id,
        Inspection.hive_id == hive_id
    ).first()


def create_inspection(db: Session, inspection: InspectionCreate, hive_id: int, performed_by_user_id: int | None = None) -> Inspection:
    data = inspection.model_dump()
    db_inspection = Inspection(**data, hive_id=hive_id, performed_by_user_id=performed_by_user_id)
    db.add(db_inspection)
    db.flush()
    if not db_inspection.weather_source:
        _attach_weather_snapshot(db_inspection)
    for task in suggest_tasks_after_inspection(db_inspection.hive, db_inspection):
        db.add(Task(**task.model_dump(), owner_id=db_inspection.hive.owner_id))
    db.commit()
    db.refresh(db_inspection)
    return db_inspection


def _attach_weather_snapshot(inspection: Inspection) -> None:
    try:
        snapshot = fetch_inspection_weather(inspection.hive)
    except Exception:
        return
    if not snapshot:
        return
    if not inspection.weather:
        inspection.weather = snapshot.weather
    inspection.weather_temperature = snapshot.weather_temperature
    inspection.weather_humidity = snapshot.weather_humidity
    inspection.weather_wind_speed = snapshot.weather_wind_speed
    inspection.weather_precipitation = snapshot.weather_precipitation
    inspection.weather_code = snapshot.weather_code
    inspection.weather_source = snapshot.weather_source
    inspection.weather_fetched_at = snapshot.weather_fetched_at


def update_inspection(
    db: Session, inspection_id: int, hive_id: int, inspection_update: InspectionUpdate
) -> Optional[Inspection]:
    db_inspection = get_inspection(db, inspection_id, hive_id)
    if not db_inspection:
        return None
    for field, value in inspection_update.model_dump(exclude_unset=True).items():
        setattr(db_inspection, field, value)
    db.commit()
    db.refresh(db_inspection)
    return db_inspection


def delete_inspection(db: Session, inspection_id: int, hive_id: int) -> bool:
    db_inspection = get_inspection(db, inspection_id, hive_id)
    if not db_inspection:
        return False
    db.delete(db_inspection)
    db.commit()
    return True
