from typing import Optional

from sqlalchemy.orm import Session

from app.crud.ownership import validate_optional_refs
from app.models.feeding import Feeding
from app.schemas.feeding import FeedingCreate, FeedingUpdate


def get_feedings(db: Session, owner_id: int, apiary_id: int | None = None, hive_id: int | None = None) -> list[Feeding]:
    query = db.query(Feeding).filter(Feeding.owner_id == owner_id)
    if apiary_id is not None:
        query = query.filter(Feeding.apiary_id == apiary_id)
    if hive_id is not None:
        query = query.filter(Feeding.hive_id == hive_id)
    return query.order_by(Feeding.date.desc(), Feeding.created_at.desc()).all()


def get_feeding(db: Session, feeding_id: int, owner_id: int) -> Optional[Feeding]:
    return db.query(Feeding).filter(Feeding.id == feeding_id, Feeding.owner_id == owner_id).first()


def create_feeding(db: Session, feeding: FeedingCreate, owner_id: int) -> Optional[Feeding]:
    data = feeding.model_dump()
    if not validate_optional_refs(db, owner_id, hive_id=data.get("hive_id"), apiary_id=data.get("apiary_id")):
        return None
    db_feeding = Feeding(**data, owner_id=owner_id)
    db.add(db_feeding)
    db.commit()
    db.refresh(db_feeding)
    return db_feeding


def update_feeding(db: Session, feeding_id: int, owner_id: int, feeding_update: FeedingUpdate) -> Optional[Feeding]:
    db_feeding = get_feeding(db, feeding_id, owner_id)
    if not db_feeding:
        return None
    data = feeding_update.model_dump(exclude_unset=True)
    if not validate_optional_refs(
        db,
        owner_id,
        hive_id=data.get("hive_id", db_feeding.hive_id),
        apiary_id=data.get("apiary_id", db_feeding.apiary_id),
    ):
        return None
    for field, value in data.items():
        setattr(db_feeding, field, value)
    db.commit()
    db.refresh(db_feeding)
    return db_feeding


def delete_feeding(db: Session, feeding_id: int, owner_id: int) -> bool:
    db_feeding = get_feeding(db, feeding_id, owner_id)
    if not db_feeding:
        return False
    db.delete(db_feeding)
    db.commit()
    return True
