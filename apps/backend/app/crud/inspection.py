from sqlalchemy.orm import Session
from typing import Optional
from app.models.inspection import Inspection
from app.models.task import Task
from app.schemas.inspection import InspectionCreate, InspectionUpdate
from app.services.beekeeping_rules import suggest_tasks_after_inspection


def get_inspections(db: Session, hive_id: int) -> list[Inspection]:
    return db.query(Inspection).filter(Inspection.hive_id == hive_id).order_by(Inspection.date.desc()).all()


def get_inspection(db: Session, inspection_id: int, hive_id: int) -> Optional[Inspection]:
    return db.query(Inspection).filter(
        Inspection.id == inspection_id,
        Inspection.hive_id == hive_id
    ).first()


def create_inspection(db: Session, inspection: InspectionCreate, hive_id: int) -> Inspection:
    db_inspection = Inspection(**inspection.model_dump(), hive_id=hive_id)
    db.add(db_inspection)
    db.flush()
    for task in suggest_tasks_after_inspection(db_inspection.hive, db_inspection):
        db.add(Task(**task.model_dump(), owner_id=db_inspection.hive.owner_id))
    db.commit()
    db.refresh(db_inspection)
    return db_inspection


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
