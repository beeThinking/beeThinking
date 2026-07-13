from sqlalchemy.orm import Session
from typing import Optional
from app.models.apiary import Apiary
from app.models.apiary_member import ApiaryMember, ApiaryMemberRole
from app.crud.ownership import user_can_admin_apiary, user_can_write_apiary
from app.schemas.apiary import ApiaryCreate, ApiaryUpdate


def get_apiaries(db: Session, owner_id: int) -> list[Apiary]:
    return (
        db.query(Apiary)
        .outerjoin(ApiaryMember, ApiaryMember.apiary_id == Apiary.id)
        .filter((Apiary.owner_id == owner_id) | (ApiaryMember.user_id == owner_id))
        .distinct()
        .all()
    )


def get_apiary(db: Session, apiary_id: int, owner_id: int) -> Optional[Apiary]:
    return (
        db.query(Apiary)
        .outerjoin(ApiaryMember, ApiaryMember.apiary_id == Apiary.id)
        .filter(Apiary.id == apiary_id)
        .filter((Apiary.owner_id == owner_id) | (ApiaryMember.user_id == owner_id))
        .first()
    )


def create_apiary(db: Session, apiary: ApiaryCreate, owner_id: int) -> Apiary:
    db_apiary = Apiary(**apiary.model_dump(), owner_id=owner_id)
    db.add(db_apiary)
    db.flush()
    db.add(ApiaryMember(apiary_id=db_apiary.id, user_id=owner_id, role=ApiaryMemberRole.owner))
    db.commit()
    db.refresh(db_apiary)
    return db_apiary


def update_apiary(db: Session, apiary_id: int, owner_id: int, apiary_update: ApiaryUpdate) -> Optional[Apiary]:
    if not user_can_write_apiary(db, apiary_id, owner_id):
        return None
    db_apiary = get_apiary(db, apiary_id, owner_id)
    if not db_apiary:
        return None
    for field, value in apiary_update.model_dump(exclude_unset=True).items():
        setattr(db_apiary, field, value)
    db.commit()
    db.refresh(db_apiary)
    return db_apiary


def delete_apiary(db: Session, apiary_id: int, owner_id: int) -> bool:
    if not user_can_admin_apiary(db, apiary_id, owner_id):
        return False
    db_apiary = get_apiary(db, apiary_id, owner_id)
    if not db_apiary:
        return False
    db.delete(db_apiary)
    db.commit()
    return True
