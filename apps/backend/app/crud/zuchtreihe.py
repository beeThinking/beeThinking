from typing import Optional

from sqlalchemy.orm import Session, joinedload

from app.crud.ownership import validate_optional_refs
from app.models.zuchtreihe import Zuchtreihe
from app.schemas.zuchtreihe import ZuchtreiheCreate, ZuchtreiheUpdate


def _success_rate(numerator: int | None, denominator: int | None) -> float | None:
    if numerator is None or denominator is None or denominator == 0:
        return None
    return round(numerator / denominator * 100, 2)


def attach_success_rates(zuchtreihe: Zuchtreihe) -> dict:
    data = {
        "success_rate_angenommen": _success_rate(zuchtreihe.anzahl_angenommen, zuchtreihe.anzahl_larven),
        "success_rate_geschluepft": _success_rate(zuchtreihe.anzahl_geschluepft, zuchtreihe.anzahl_angenommen),
        "success_rate_begattet": _success_rate(zuchtreihe.anzahl_begattet, zuchtreihe.anzahl_geschluepft),
    }
    return data


def get_zuchtreihen(db: Session, owner_id: int, apiary_id: int | None = None) -> list[Zuchtreihe]:
    query = (
        db.query(Zuchtreihe)
        .options(joinedload(Zuchtreihe.steps))
        .filter(Zuchtreihe.owner_id == owner_id)
    )
    if apiary_id is not None:
        query = query.filter(Zuchtreihe.apiary_id == apiary_id)
    return query.order_by(Zuchtreihe.created_at.desc()).all()


def get_zuchtreihe(db: Session, zuchtreihe_id: int, owner_id: int) -> Optional[Zuchtreihe]:
    return (
        db.query(Zuchtreihe)
        .options(joinedload(Zuchtreihe.steps))
        .filter(Zuchtreihe.id == zuchtreihe_id, Zuchtreihe.owner_id == owner_id)
        .first()
    )


def create_zuchtreihe(db: Session, zuchtreihe: ZuchtreiheCreate, owner_id: int) -> Optional[Zuchtreihe]:
    data = zuchtreihe.model_dump()
    if not validate_optional_refs(
        db, owner_id, apiary_id=data.get("apiary_id"), hive_id=data.get("herkunftsvolk_id")
    ):
        return None
    db_zuchtreihe = Zuchtreihe(**data, owner_id=owner_id)
    db.add(db_zuchtreihe)
    db.commit()
    db.refresh(db_zuchtreihe)
    return db_zuchtreihe


def update_zuchtreihe(
    db: Session, zuchtreihe_id: int, owner_id: int, zuchtreihe_update: ZuchtreiheUpdate
) -> Optional[Zuchtreihe]:
    db_zuchtreihe = get_zuchtreihe(db, zuchtreihe_id, owner_id)
    if not db_zuchtreihe:
        return None
    data = zuchtreihe_update.model_dump(exclude_unset=True)
    if not validate_optional_refs(
        db, owner_id, apiary_id=data.get("apiary_id"), hive_id=data.get("herkunftsvolk_id")
    ):
        return None
    for field, value in data.items():
        setattr(db_zuchtreihe, field, value)
    db.commit()
    db.refresh(db_zuchtreihe)
    return db_zuchtreihe


def delete_zuchtreihe(db: Session, zuchtreihe_id: int, owner_id: int) -> bool:
    db_zuchtreihe = get_zuchtreihe(db, zuchtreihe_id, owner_id)
    if not db_zuchtreihe:
        return False
    db.delete(db_zuchtreihe)
    db.commit()
    return True
