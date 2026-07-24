"""Bienenvolk-Selektion (#39): filter hives by inspection-criteria averages + tags,
then batch-create Tasks for the filtered set.

Only `stars` and `number` value-type criteria are averaged (bool/select/text are
excluded — those serve the separate #36 breeding-candidate scoring, not this
filter). The average is computed over the FULL inspection history for a hive,
with no date-range window.
"""

from collections import defaultdict

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.crud.ownership import user_can_write_apiary, visible_apiary_ids_subquery
from app.models.hive import Hive
from app.models.inspection import Inspection
from app.models.inspection_criterion import CriterionValueType, InspectionCriterion
from app.models.task import Task
from app.schemas.hive_selection import CriterionAverageFilter, HiveSelectionBatchTaskRequest, HiveSelectionCandidate

AVERAGEABLE_VALUE_TYPES = {CriterionValueType.stars.value, CriterionValueType.number.value}


def _hive_tags(hive: Hive) -> list[str]:
    return list(hive.tags or [])


def _criterion_numeric_value(criterion: InspectionCriterion, raw_value) -> float | None:
    if raw_value is None or criterion.value_type not in AVERAGEABLE_VALUE_TYPES:
        return None
    try:
        return float(raw_value)
    except (TypeError, ValueError):
        return None


def compute_criterion_averages(db: Session, hive_ids: list[int]) -> dict[int, dict[int, float]]:
    """Return {hive_id: {criterion_id: average}} over each hive's full inspection history."""
    if not hive_ids:
        return {}
    inspections = db.query(Inspection).filter(Inspection.hive_id.in_(hive_ids)).all()
    criteria = {criterion.id: criterion for criterion in db.query(InspectionCriterion).all()}

    sums: dict[int, dict[int, float]] = defaultdict(lambda: defaultdict(float))
    counts: dict[int, dict[int, int]] = defaultdict(lambda: defaultdict(int))

    for inspection in inspections:
        if not inspection.criteria_values:
            continue
        for criterion_key, raw_value in inspection.criteria_values.items():
            try:
                criterion_id = int(criterion_key)
            except (TypeError, ValueError):
                continue
            criterion = criteria.get(criterion_id)
            if not criterion:
                continue
            value = _criterion_numeric_value(criterion, raw_value)
            if value is None:
                continue
            sums[inspection.hive_id][criterion_id] += value
            counts[inspection.hive_id][criterion_id] += 1

    averages: dict[int, dict[int, float]] = {}
    for hive_id in hive_ids:
        averages[hive_id] = {
            criterion_id: round(total / counts[hive_id][criterion_id], 4)
            for criterion_id, total in sums.get(hive_id, {}).items()
            if counts[hive_id][criterion_id] > 0
        }
    return averages


def filter_hives(
    db: Session,
    owner_id: int,
    criteria_filters: list[CriterionAverageFilter],
    tags: list[str],
    match_all_tags: bool,
) -> list[HiveSelectionCandidate]:
    visible_ids = visible_apiary_ids_subquery(db, owner_id)
    hives = (
        db.query(Hive)
        .filter(Hive.apiary_id.in_(visible_ids), Hive.is_active.is_(True))
        .all()
    )
    if not hives:
        return []

    hive_ids = [hive.id for hive in hives]
    averages_by_hive = compute_criterion_averages(db, hive_ids)
    counts_query = (
        db.query(Inspection.hive_id, func.count(Inspection.id))
        .filter(Inspection.hive_id.in_(hive_ids))
        .group_by(Inspection.hive_id)
        .all()
    )
    inspection_counts = dict(counts_query)

    results: list[HiveSelectionCandidate] = []
    for hive in hives:
        hive_tags = _hive_tags(hive)
        if tags:
            if match_all_tags and not all(tag in hive_tags for tag in tags):
                continue
            if not match_all_tags and not any(tag in hive_tags for tag in tags):
                continue

        hive_averages = averages_by_hive.get(hive.id, {})
        matches_all_criteria = True
        for criterion_filter in criteria_filters:
            average = hive_averages.get(criterion_filter.criterion_id)
            if average is None:
                matches_all_criteria = False
                break
            if criterion_filter.min_average is not None and average < criterion_filter.min_average:
                matches_all_criteria = False
                break
            if criterion_filter.max_average is not None and average > criterion_filter.max_average:
                matches_all_criteria = False
                break
        if not matches_all_criteria:
            continue

        results.append(
            HiveSelectionCandidate(
                hive_id=hive.id,
                hive_name=hive.name,
                apiary_id=hive.apiary_id,
                tags=hive_tags,
                criterion_averages=hive_averages,
                inspection_count=inspection_counts.get(hive.id, 0),
            )
        )
    return results


def batch_create_tasks(db: Session, owner_id: int, payload: HiveSelectionBatchTaskRequest) -> list[Task]:
    """Batch-create Tasks for a filtered set of hives (#39). Any apiary member with
    write access on a hive's apiary may create tasks for it."""
    hives = db.query(Hive).filter(Hive.id.in_(payload.hive_ids)).all()
    hives_by_id = {hive.id: hive for hive in hives}
    missing = [hive_id for hive_id in payload.hive_ids if hive_id not in hives_by_id]
    if missing:
        return []
    for hive in hives:
        if not user_can_write_apiary(db, hive.apiary_id, owner_id):
            return []

    created: list[Task] = []
    for hive_id in payload.hive_ids:
        task = Task(
            owner_id=owner_id,
            hive_id=hive_id,
            title=payload.title,
            description=payload.description,
            due_date=payload.due_date,
            kind=payload.kind,
            priority=payload.priority,
        )
        db.add(task)
        created.append(task)
    db.commit()
    for task in created:
        db.refresh(task)
    return created
