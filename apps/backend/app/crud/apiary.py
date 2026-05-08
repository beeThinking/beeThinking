from sqlalchemy.orm import Session
from typing import Optional
from app.models.apiary import Apiary
from app.schemas.apiary import ApiaryCreate, ApiaryUpdate


def get_apiaries(db: Session, owner_id: int) -> list[Apiary]:
    return db.query(Apiary).filter(Apiary.owner_id == owner_id).all()


def get_apiary(db: Session, apiary_id: int, owner_id: int) -> Optional[Apiary]:
    return db.query(Apiary).filter(
        Apiary.id == apiary_id,
        Apiary.owner_id == owner_id
    ).first()


def create_apiary(db: Session, apiary: ApiaryCreate, owner_id: int) -> Apiary:
    db_apiary = Apiary(**apiary.model_dump(), owner_id=owner_id)
    db.add(db_apiary)
    db.commit()
    db.refresh(db_apiary)
    return db_apiary


def update_apiary(db: Session, apiary_id: int, owner_id: int, apiary_update: ApiaryUpdate) -> Optional[Apiary]:
    db_apiary = get_apiary(db, apiary_id, owner_id)
    if not db_apiary:
        return None
    for field, value in apiary_update.model_dump(exclude_unset=True).items():
        setattr(db_apiary, field, value)
    db.commit()
    db.refresh(db_apiary)
    return db_apiary


def delete_apiary(db: Session, apiary_id: int, owner_id: int) -> bool:
    db_apiary = get_apiary(db, apiary_id, owner_id)
    if not db_apiary:
        return False
    db.delete(db_apiary)
    db.commit()
    return True
