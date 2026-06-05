from typing import Optional

from sqlalchemy.orm import Session

from app.crud.ownership import validate_optional_refs
from app.models.treatment import Treatment
from app.schemas.treatment import TreatmentCreate, TreatmentUpdate


def get_treatments(db: Session, owner_id: int) -> list[Treatment]:
    return db.query(Treatment).filter(Treatment.owner_id == owner_id).order_by(Treatment.started_at.desc()).all()


def get_treatment(db: Session, treatment_id: int, owner_id: int) -> Optional[Treatment]:
    return db.query(Treatment).filter(Treatment.id == treatment_id, Treatment.owner_id == owner_id).first()


def create_treatment(db: Session, treatment: TreatmentCreate, owner_id: int) -> Optional[Treatment]:
    data = treatment.model_dump()
    if not validate_optional_refs(db, owner_id, hive_id=data["hive_id"]):
        return None
    db_treatment = Treatment(**data, owner_id=owner_id)
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
