from typing import Optional

from sqlalchemy.orm import Session

from app.models.inspection_criterion import CriterionSection, CriterionValueType, InspectionCriterion
from app.schemas.inspection_criterion import InspectionCriterionCreate, InspectionCriterionUpdate

DEFAULT_CRITERIA: list[dict] = [
    {"name": "Waben (Brut)", "section": "allg_befund", "value_type": "stars", "sort_order": 10},
    {"name": "Abgeschwärmt", "section": "allg_befund", "value_type": "bool", "sort_order": 20},
    {"name": "Weiselzellen gesehen", "section": "allg_befund", "value_type": "bool", "sort_order": 30},
    {"name": "Sanftmut", "section": "verhalten", "value_type": "stars", "sort_order": 40},
    {"name": "Wabenstetigkeit", "section": "verhalten", "value_type": "stars", "sort_order": 50},
    {"name": "Vitalität", "section": "verhalten", "value_type": "stars", "sort_order": 60},
    {"name": "Schwarmtrieb", "section": "verhalten", "value_type": "stars", "sort_order": 70},
    {
        "name": "Futterart",
        "section": "verschiedenes",
        "value_type": "select",
        "options": ["Honig", "Futterteig", "Futtersirup", "Kein Futter"],
        "sort_order": 80,
    },
]


def seed_default_criteria(db: Session, owner_id: int) -> list[InspectionCriterion]:
    criteria = [InspectionCriterion(owner_id=owner_id, **item) for item in DEFAULT_CRITERIA]
    db.add_all(criteria)
    db.commit()
    for criterion in criteria:
        db.refresh(criterion)
    return criteria


def get_criteria(db: Session, owner_id: int, include_inactive: bool = True) -> list[InspectionCriterion]:
    query = db.query(InspectionCriterion).filter(InspectionCriterion.owner_id == owner_id)
    if not include_inactive:
        query = query.filter(InspectionCriterion.is_active.is_(True))
    criteria = query.order_by(InspectionCriterion.sort_order.asc(), InspectionCriterion.id.asc()).all()
    if not criteria and not db.query(InspectionCriterion).filter(InspectionCriterion.owner_id == owner_id).count():
        criteria = seed_default_criteria(db, owner_id)
        if not include_inactive:
            criteria = [criterion for criterion in criteria if criterion.is_active]
    return criteria


def get_criterion(db: Session, criterion_id: int, owner_id: int) -> Optional[InspectionCriterion]:
    return (
        db.query(InspectionCriterion)
        .filter(InspectionCriterion.id == criterion_id, InspectionCriterion.owner_id == owner_id)
        .first()
    )


def create_criterion(db: Session, criterion: InspectionCriterionCreate, owner_id: int) -> InspectionCriterion:
    data = criterion.model_dump()
    data["section"] = CriterionSection(data["section"]).value
    data["value_type"] = CriterionValueType(data["value_type"]).value
    db_criterion = InspectionCriterion(**data, owner_id=owner_id)
    db.add(db_criterion)
    db.commit()
    db.refresh(db_criterion)
    return db_criterion


def update_criterion(
    db: Session, criterion_id: int, owner_id: int, criterion_update: InspectionCriterionUpdate
) -> Optional[InspectionCriterion]:
    db_criterion = get_criterion(db, criterion_id, owner_id)
    if not db_criterion:
        return None
    data = criterion_update.model_dump(exclude_unset=True)
    for enum_field, enum_cls in (("section", CriterionSection), ("value_type", CriterionValueType)):
        if enum_field in data and data[enum_field] is not None:
            data[enum_field] = enum_cls(data[enum_field]).value
    for field, value in data.items():
        setattr(db_criterion, field, value)
    db.commit()
    db.refresh(db_criterion)
    return db_criterion


def delete_criterion(db: Session, criterion_id: int, owner_id: int) -> bool:
    db_criterion = get_criterion(db, criterion_id, owner_id)
    if not db_criterion:
        return False
    db.delete(db_criterion)
    db.commit()
    return True
