from sqlalchemy.orm import Session

from app.models.apiary import Apiary
from app.models.apiary_member import ApiaryMember, ApiaryMemberRole
from app.models.hive import Hive
from app.models.inspection import Inspection


WRITE_ROLES = {ApiaryMemberRole.owner, ApiaryMemberRole.admin, ApiaryMemberRole.member}
ADMIN_ROLES = {ApiaryMemberRole.owner, ApiaryMemberRole.admin}


def user_owns_apiary(db: Session, apiary_id: int, owner_id: int) -> bool:
    return db.query(Apiary).filter(Apiary.id == apiary_id, Apiary.owner_id == owner_id).first() is not None


def get_apiary_member(db: Session, apiary_id: int, user_id: int) -> ApiaryMember | None:
    return db.query(ApiaryMember).filter(
        ApiaryMember.apiary_id == apiary_id,
        ApiaryMember.user_id == user_id,
        ApiaryMember.accepted_at.is_not(None),
    ).first()


def user_can_access_apiary(db: Session, apiary_id: int, user_id: int) -> bool:
    return user_owns_apiary(db, apiary_id, user_id) or get_apiary_member(db, apiary_id, user_id) is not None


def user_can_write_apiary(db: Session, apiary_id: int, user_id: int) -> bool:
    if user_owns_apiary(db, apiary_id, user_id):
        return True
    member = get_apiary_member(db, apiary_id, user_id)
    return member is not None and member.role in WRITE_ROLES


def user_can_admin_apiary(db: Session, apiary_id: int, user_id: int) -> bool:
    if user_owns_apiary(db, apiary_id, user_id):
        return True
    member = get_apiary_member(db, apiary_id, user_id)
    return member is not None and member.role in ADMIN_ROLES


def user_owns_hive(db: Session, hive_id: int, owner_id: int) -> bool:
    hive = db.query(Hive).filter(Hive.id == hive_id).first()
    return hive is not None and user_can_write_apiary(db, hive.apiary_id, owner_id)


def user_owns_inspection(db: Session, inspection_id: int, owner_id: int) -> bool:
    inspection = (
        db.query(Inspection)
        .join(Hive)
        .filter(Inspection.id == inspection_id)
        .first()
    )
    return inspection is not None and user_can_write_apiary(db, inspection.hive.apiary_id, owner_id)


def validate_optional_refs(
    db: Session,
    owner_id: int,
    hive_id: int | None = None,
    apiary_id: int | None = None,
    inspection_id: int | None = None,
) -> bool:
    if hive_id is not None and not user_owns_hive(db, hive_id, owner_id):
        return False
    if apiary_id is not None and not user_can_write_apiary(db, apiary_id, owner_id):
        return False
    if inspection_id is not None and not user_owns_inspection(db, inspection_id, owner_id):
        return False
    return True
