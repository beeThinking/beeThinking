from typing import Optional

from sqlalchemy.orm import Session

from app.crud.ownership import validate_optional_refs
from app.models.varroa_check import VarroaCheck
from app.schemas.varroa_check import VarroaCheckCreate, VarroaCheckUpdate


def get_varroa_checks(db: Session, owner_id: int, hive_id: int | None = None) -> list[VarroaCheck]:
    query = db.query(VarroaCheck).filter(VarroaCheck.owner_id == owner_id)
    if hive_id is not None:
        query = query.filter(VarroaCheck.hive_id == hive_id)
    return query.order_by(VarroaCheck.date.desc(), VarroaCheck.created_at.desc()).all()


def get_varroa_check(db: Session, check_id: int, owner_id: int) -> Optional[VarroaCheck]:
    return db.query(VarroaCheck).filter(VarroaCheck.id == check_id, VarroaCheck.owner_id == owner_id).first()


def create_varroa_check(db: Session, check: VarroaCheckCreate, owner_id: int) -> Optional[VarroaCheck]:
    data = check.model_dump()
    if not validate_optional_refs(db, owner_id, hive_id=data.get("hive_id")):
        return None
    db_check = VarroaCheck(**data, owner_id=owner_id)
    db.add(db_check)
    db.commit()
    db.refresh(db_check)
    return db_check


def update_varroa_check(db: Session, check_id: int, owner_id: int, check_update: VarroaCheckUpdate) -> Optional[VarroaCheck]:
    db_check = get_varroa_check(db, check_id, owner_id)
    if not db_check:
        return None
    for field, value in check_update.model_dump(exclude_unset=True).items():
        setattr(db_check, field, value)
    db.commit()
    db.refresh(db_check)
    return db_check


def delete_varroa_check(db: Session, check_id: int, owner_id: int) -> bool:
    db_check = get_varroa_check(db, check_id, owner_id)
    if not db_check:
        return False
    db.delete(db_check)
    db.commit()
    return True
