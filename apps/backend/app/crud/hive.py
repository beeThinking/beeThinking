from sqlalchemy.orm import Session
from typing import Optional
from app.models.hive import Hive
from app.schemas.hive import HiveCreate, HiveUpdate


def get_hives(db: Session, owner_id: int) -> list[Hive]:
    return db.query(Hive).filter(Hive.owner_id == owner_id).all()


def get_hive(db: Session, hive_id: int, owner_id: int) -> Optional[Hive]:
    return db.query(Hive).filter(Hive.id == hive_id, Hive.owner_id == owner_id).first()


def create_hive(db: Session, hive: HiveCreate, owner_id: int) -> Hive:
    db_hive = Hive(**hive.model_dump(), owner_id=owner_id)
    db.add(db_hive)
    db.commit()
    db.refresh(db_hive)
    return db_hive


def update_hive(db: Session, hive_id: int, owner_id: int, hive_update: HiveUpdate) -> Optional[Hive]:
    db_hive = get_hive(db, hive_id, owner_id)
    if not db_hive:
        return None
    for field, value in hive_update.model_dump(exclude_unset=True).items():
        setattr(db_hive, field, value)
    db.commit()
    db.refresh(db_hive)
    return db_hive


def delete_hive(db: Session, hive_id: int, owner_id: int) -> bool:
    db_hive = get_hive(db, hive_id, owner_id)
    if not db_hive:
        return False
    db.delete(db_hive)
    db.commit()
    return True
