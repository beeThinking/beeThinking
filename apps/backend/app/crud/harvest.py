from typing import Optional

from sqlalchemy.orm import Session

from app.crud.ownership import validate_optional_refs
from app.models.harvest import Harvest
from app.schemas.harvest import HarvestCreate, HarvestUpdate


def get_harvests(db: Session, owner_id: int) -> list[Harvest]:
    return db.query(Harvest).filter(Harvest.owner_id == owner_id).order_by(Harvest.harvest_date.desc()).all()


def get_harvest(db: Session, harvest_id: int, owner_id: int) -> Optional[Harvest]:
    return db.query(Harvest).filter(Harvest.id == harvest_id, Harvest.owner_id == owner_id).first()


def create_harvest(db: Session, harvest: HarvestCreate, owner_id: int, performed_by_user_id: int | None = None) -> Optional[Harvest]:
    data = harvest.model_dump()
    if not validate_optional_refs(db, owner_id, hive_id=data.get("hive_id"), apiary_id=data.get("apiary_id")):
        return None
    db_harvest = Harvest(**data, owner_id=owner_id, performed_by_user_id=performed_by_user_id or owner_id)
    db.add(db_harvest)
    db.commit()
    db.refresh(db_harvest)
    return db_harvest


def update_harvest(db: Session, harvest_id: int, owner_id: int, harvest_update: HarvestUpdate) -> Optional[Harvest]:
    db_harvest = get_harvest(db, harvest_id, owner_id)
    if not db_harvest:
        return None
    data = harvest_update.model_dump(exclude_unset=True)
    if not validate_optional_refs(
        db,
        owner_id,
        hive_id=data.get("hive_id"),
        apiary_id=data.get("apiary_id"),
    ):
        return None
    for field, value in data.items():
        setattr(db_harvest, field, value)
    db.commit()
    db.refresh(db_harvest)
    return db_harvest


def delete_harvest(db: Session, harvest_id: int, owner_id: int) -> bool:
    db_harvest = get_harvest(db, harvest_id, owner_id)
    if not db_harvest:
        return False
    db.delete(db_harvest)
    db.commit()
    return True
