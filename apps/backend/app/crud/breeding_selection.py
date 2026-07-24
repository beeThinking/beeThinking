from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.hive import Hive
from app.models.inspection import Inspection
from app.models.inspection_criterion import CriterionValueType, InspectionCriterion
from app.models.criterion_weight import CriterionWeight


def _criterion_value_score(criterion: InspectionCriterion, raw_value) -> float | None:
    if raw_value is None:
        return None
    value_type = criterion.value_type
    if value_type == CriterionValueType.text.value:
        return None
    if value_type == CriterionValueType.bool.value:
        return 1.0 if raw_value else 0.0
    if value_type == CriterionValueType.select.value:
        option_scores = criterion.option_scores or {}
        try:
            return float(option_scores.get(str(raw_value)))
        except (TypeError, ValueError):
            return None
    try:
        return float(raw_value)
    except (TypeError, ValueError):
        return None


def _latest_inspection_by_hive(db: Session, hive_ids: list[int]) -> dict[int, Inspection]:
    if not hive_ids:
        return {}
    latest_dates = (
        db.query(Inspection.hive_id, func.max(Inspection.date).label("max_date"))
        .filter(Inspection.hive_id.in_(hive_ids))
        .group_by(Inspection.hive_id)
        .subquery()
    )
    inspections = (
        db.query(Inspection)
        .join(
            latest_dates,
            (Inspection.hive_id == latest_dates.c.hive_id) & (Inspection.date == latest_dates.c.max_date),
        )
        .all()
    )
    result: dict[int, Inspection] = {}
    for inspection in inspections:
        # If multiple inspections share the latest date, keep the one with the highest id.
        existing = result.get(inspection.hive_id)
        if existing is None or inspection.id > existing.id:
            result[inspection.hive_id] = inspection
    return result


def rank_breeding_candidates(db: Session, owner_id: int) -> list[dict]:
    candidate_hives = (
        db.query(Hive)
        .filter(Hive.owner_id == owner_id, Hive.is_breeding_candidate.is_(True))
        .all()
    )
    if not candidate_hives:
        return []

    weights = {
        weight.criterion_id: weight.weight
        for weight in db.query(CriterionWeight).filter(CriterionWeight.user_id == owner_id).all()
    }
    if not weights:
        return [
            {
                "hive_id": hive.id,
                "hive_name": hive.name,
                "score": 0.0,
                "latest_inspection_id": None,
                "latest_inspection_date": None,
            }
            for hive in candidate_hives
        ]

    criteria = {
        criterion.id: criterion
        for criterion in db.query(InspectionCriterion)
        .filter(InspectionCriterion.owner_id == owner_id, InspectionCriterion.id.in_(weights.keys()))
        .all()
    }

    latest_by_hive = _latest_inspection_by_hive(db, [hive.id for hive in candidate_hives])

    results = []
    for hive in candidate_hives:
        inspection = latest_by_hive.get(hive.id)
        score = 0.0
        if inspection and inspection.criteria_values:
            for criterion_id, weight in weights.items():
                criterion = criteria.get(criterion_id)
                if not criterion:
                    continue
                raw_value = inspection.criteria_values.get(str(criterion_id))
                value_score = _criterion_value_score(criterion, raw_value)
                if value_score is not None:
                    score += value_score * weight
        results.append(
            {
                "hive_id": hive.id,
                "hive_name": hive.name,
                "score": round(score, 4),
                "latest_inspection_id": inspection.id if inspection else None,
                "latest_inspection_date": inspection.date if inspection else None,
            }
        )

    results.sort(key=lambda item: item["score"], reverse=True)
    return results
