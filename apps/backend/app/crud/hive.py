from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
from app.models.hive import Hive, HiveStatus
from app.models.apiary import Apiary
from app.schemas.hive import HiveCreate, HiveUpdate
from app.services.hive_lifecycle import can_hard_delete_hive, create_hive_event


def _verify_apiary(db: Session, apiary_id: int, owner_id: int) -> bool:
    return db.query(Apiary).filter(
        Apiary.id == apiary_id,
        Apiary.owner_id == owner_id
    ).first() is not None


def get_hives(db: Session, owner_id: int, apiary_id: Optional[int] = None, status: Optional[HiveStatus] = HiveStatus.active) -> list[Hive]:
    q = db.query(Hive).filter(Hive.owner_id == owner_id)
    if status is not None:
        if status == HiveStatus.archived:
            q = q.filter(Hive.is_active.is_(False))
        else:
            q = q.filter(Hive.status == status)
    if apiary_id is not None:
        q = q.filter(Hive.apiary_id == apiary_id)
    return q.all()


def get_hive(db: Session, hive_id: int, owner_id: int) -> Optional[Hive]:
    return db.query(Hive).filter(Hive.id == hive_id, Hive.owner_id == owner_id).first()


def create_hive(db: Session, hive: HiveCreate, owner_id: int) -> Optional[Hive]:
    if not _verify_apiary(db, hive.apiary_id, owner_id):
        return None
    db_hive = Hive(**hive.model_dump(), owner_id=owner_id)
    db.add(db_hive)
    db.flush()
    create_hive_event(db, owner_id, db_hive.id, "created", date.today(), "Volk erstellt")
    db.commit()
    db.refresh(db_hive)
    return db_hive


def update_hive(db: Session, hive_id: int, owner_id: int, hive_update: HiveUpdate) -> Optional[Hive]:
    db_hive = get_hive(db, hive_id, owner_id)
    if not db_hive:
        return None
    data = hive_update.model_dump(exclude_unset=True)
    if "apiary_id" in data and not _verify_apiary(db, data["apiary_id"], owner_id):
        return None
    for field, value in data.items():
        setattr(db_hive, field, value)
    db.commit()
    db.refresh(db_hive)
    return db_hive


def delete_hive(db: Session, hive_id: int, owner_id: int) -> bool:
    db_hive = get_hive(db, hive_id, owner_id)
    if not db_hive:
        return False
    if not can_hard_delete_hive(db, hive_id, owner_id):
        return False
    create_hive_event(db, owner_id, hive_id, "hard_deleted", date.today(), "Volk endgültig gelöscht")
    db.delete(db_hive)
    db.commit()
    return True
