from datetime import date
from typing import Optional

from sqlalchemy.orm import Session, joinedload

from app.crud.ownership import validate_optional_refs
from app.models.treatment import Treatment
from app.models.apiary import Apiary
from app.models.varroa_weather import VarroaWeatherWindow
from app.schemas.treatment import TreatmentCreate, TreatmentJournalEntry, TreatmentUpdate


def get_treatments(db: Session, owner_id: int, year: Optional[int] = None) -> list[Treatment]:
    query = db.query(Treatment).filter(Treatment.owner_id == owner_id)
    if year is not None:
        query = query.filter(
            Treatment.started_at >= date(year, 1, 1), Treatment.started_at <= date(year, 12, 31)
        )
    return query.order_by(Treatment.started_at.desc()).all()


def get_journal_entries(db: Session, owner_id: int, year: Optional[int] = None) -> list[TreatmentJournalEntry]:
    query = (
        db.query(Treatment)
        .options(joinedload(Treatment.hive), joinedload(Treatment.performed_by))
        .filter(Treatment.owner_id == owner_id)
    )
    if year is not None:
        query = query.filter(
            Treatment.started_at >= date(year, 1, 1), Treatment.started_at <= date(year, 12, 31)
        )
    treatments = query.order_by(Treatment.started_at.desc()).all()
    return [
        TreatmentJournalEntry(
            id=treatment.id,
            hive_id=treatment.hive_id,
            started_at=treatment.started_at,
            ended_at=treatment.ended_at,
            product=treatment.product,
            method=treatment.method,
            dosage=treatment.dosage,
            reason=treatment.reason,
            weather_window_id=treatment.weather_window_id,
            weather_rating=treatment.weather_rating,
            weather_source=treatment.weather_source,
            weather_fetched_at=treatment.weather_fetched_at,
            notes=treatment.notes,
            waiting_period_days=treatment.waiting_period_days,
            date=treatment.started_at,
            hive_label=(
                f"{treatment.hive.name} ({treatment.hive.stock_number})"
                if treatment.hive and treatment.hive.stock_number
                else (treatment.hive.name if treatment.hive else str(treatment.hive_id))
            ),
            amount=treatment.dosage,
            treater=treatment.performed_by.username if treatment.performed_by else None,
        )
        for treatment in treatments
    ]


def get_treatment(db: Session, treatment_id: int, owner_id: int) -> Optional[Treatment]:
    return db.query(Treatment).filter(Treatment.id == treatment_id, Treatment.owner_id == owner_id).first()


def create_treatment(db: Session, treatment: TreatmentCreate, owner_id: int, performed_by_user_id: int | None = None) -> Optional[Treatment]:
    data = treatment.model_dump()
    if not validate_optional_refs(db, owner_id, hive_id=data["hive_id"]):
        return None
    if not _attach_weather_context(db, data, owner_id):
        return None
    db_treatment = Treatment(**data, owner_id=owner_id, performed_by_user_id=performed_by_user_id or owner_id)
    db.add(db_treatment)
    db.commit()
    db.refresh(db_treatment)
    return db_treatment


def update_treatment(
    db: Session, treatment_id: int, owner_id: int, treatment_update: TreatmentUpdate
) -> Optional[Treatment]:
    db_treatment = get_treatment(db, treatment_id, owner_id)
    if not db_treatment:
        return None
    data = treatment_update.model_dump(exclude_unset=True)
    if "hive_id" in data and not validate_optional_refs(db, owner_id, hive_id=data["hive_id"]):
        return None
    if not _attach_weather_context(db, data, owner_id):
        return None
    for field, value in data.items():
        setattr(db_treatment, field, value)
    db.commit()
    db.refresh(db_treatment)
    return db_treatment


def delete_treatment(db: Session, treatment_id: int, owner_id: int) -> bool:
    db_treatment = get_treatment(db, treatment_id, owner_id)
    if not db_treatment:
        return False
    db.delete(db_treatment)
    db.commit()
    return True


def _attach_weather_context(db: Session, data: dict, owner_id: int) -> bool:
    window_id = data.get("weather_window_id")
    if not window_id:
        return True
    window = (
        db.query(VarroaWeatherWindow)
        .join(Apiary)
        .filter(VarroaWeatherWindow.id == window_id, Apiary.owner_id == owner_id)
        .first()
    )
    if not window:
        return False
    data["weather_rating"] = window.rating.value
    data["weather_source"] = window.source
    data["weather_fetched_at"] = window.fetched_at
    return True
