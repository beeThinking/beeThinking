from sqlalchemy.orm import Session

from app.models.apiary import Apiary
from app.models.hive import Hive
from app.models.inspection import Inspection


def user_owns_apiary(db: Session, apiary_id: int, owner_id: int) -> bool:
    return db.query(Apiary).filter(Apiary.id == apiary_id, Apiary.owner_id == owner_id).first() is not None


def user_owns_hive(db: Session, hive_id: int, owner_id: int) -> bool:
    return db.query(Hive).filter(Hive.id == hive_id, Hive.owner_id == owner_id).first() is not None


def user_owns_inspection(db: Session, inspection_id: int, owner_id: int) -> bool:
    return (
        db.query(Inspection)
        .join(Hive)
        .filter(Inspection.id == inspection_id, Hive.owner_id == owner_id)
        .first()
        is not None
    )


def validate_optional_refs(
    db: Session,
    owner_id: int,
    hive_id: int | None = None,
    apiary_id: int | None = None,
    inspection_id: int | None = None,
) -> bool:
    if hive_id is not None and not user_owns_hive(db, hive_id, owner_id):
        return False
    if apiary_id is not None and not user_owns_apiary(db, apiary_id, owner_id):
        return False
    if inspection_id is not None and not user_owns_inspection(db, inspection_id, owner_id):
        return False
    return True
