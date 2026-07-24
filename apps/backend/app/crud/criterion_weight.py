from typing import Optional

from sqlalchemy.orm import Session

from app.models.criterion_weight import CriterionWeight
from app.schemas.criterion_weight import CriterionWeightUpsert


def get_weights(db: Session, user_id: int) -> list[CriterionWeight]:
    return db.query(CriterionWeight).filter(CriterionWeight.user_id == user_id).all()


def get_weight(db: Session, user_id: int, criterion_id: int) -> Optional[CriterionWeight]:
    return (
        db.query(CriterionWeight)
        .filter(CriterionWeight.user_id == user_id, CriterionWeight.criterion_id == criterion_id)
        .first()
    )


def upsert_weight(db: Session, user_id: int, payload: CriterionWeightUpsert) -> CriterionWeight:
    db_weight = get_weight(db, user_id, payload.criterion_id)
    if db_weight:
        db_weight.weight = payload.weight
    else:
        db_weight = CriterionWeight(user_id=user_id, criterion_id=payload.criterion_id, weight=payload.weight)
        db.add(db_weight)
    db.commit()
    db.refresh(db_weight)
    return db_weight


def delete_weight(db: Session, user_id: int, criterion_id: int) -> bool:
    db_weight = get_weight(db, user_id, criterion_id)
    if not db_weight:
        return False
    db.delete(db_weight)
    db.commit()
    return True
