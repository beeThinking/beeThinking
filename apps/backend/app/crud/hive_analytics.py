"""Per-colony analytics (#42): KPI counters + chart data grouped by
Jahr/Monat/Woche/Tag over Harvest/Feeding/Inspection/Treatment/HiveEvent
records for a single hive, with a date-range filter.

'Stunde' (hourly) grouping is explicitly dropped per the resolved ticket —
not meaningful for once-daily harvest/feeding records.
"""

from collections import defaultdict
from datetime import date

from sqlalchemy.orm import Session

from app.crud.ownership import user_can_access_apiary
from app.models.feeding import Feeding
from app.models.harvest import Harvest
from app.models.hive import Hive
from app.models.hive_event import HiveEvent
from app.models.inspection import Inspection
from app.models.treatment import Treatment
from app.schemas.hive_analytics import (
    AnalyticsGrouping,
    HiveAnalyticsChartPoint,
    HiveAnalyticsKpi,
    HiveAnalyticsResponse,
)


def _period_key(value: date, grouping: AnalyticsGrouping) -> tuple[str, date]:
    if grouping == AnalyticsGrouping.year:
        return str(value.year), date(value.year, 1, 1)
    if grouping == AnalyticsGrouping.month:
        return f"{value.year}-{value.month:02d}", date(value.year, value.month, 1)
    if grouping == AnalyticsGrouping.week:
        iso_year, iso_week, _ = value.isocalendar()
        period_start = date.fromisocalendar(iso_year, iso_week, 1)
        return f"{iso_year}-W{iso_week:02d}", period_start
    return value.isoformat(), value


def get_hive_analytics(
    db: Session,
    hive_id: int,
    owner_id: int,
    grouping: AnalyticsGrouping,
    from_date: date | None,
    to_date: date | None,
) -> HiveAnalyticsResponse | None:
    hive = db.query(Hive).filter(Hive.id == hive_id).first()
    if not hive or not user_can_access_apiary(db, hive.apiary_id, owner_id):
        return None

    harvests = db.query(Harvest).filter(Harvest.hive_id == hive_id).all()
    feedings = db.query(Feeding).filter(Feeding.hive_id == hive_id).all()
    inspections = db.query(Inspection).filter(Inspection.hive_id == hive_id).all()
    treatments = db.query(Treatment).filter(Treatment.hive_id == hive_id).all()
    events = db.query(HiveEvent).filter(HiveEvent.hive_id == hive_id).all()

    def in_range(value: date) -> bool:
        if from_date and value < from_date:
            return False
        if to_date and value > to_date:
            return False
        return True

    harvests = [h for h in harvests if in_range(h.harvest_date)]
    feedings = [f for f in feedings if in_range(f.date)]
    inspections = [i for i in inspections if in_range(i.date)]
    treatments = [t for t in treatments if in_range(t.started_at)]
    events = [e for e in events if in_range(e.event_date)]

    kpi = HiveAnalyticsKpi(
        total_harvest_kg=round(sum(h.amount_kg for h in harvests), 2),
        total_feeding_kg_or_l=round(sum(f.amount_kg_or_l for f in feedings), 2),
        inspection_count=len(inspections),
        treatment_count=len(treatments),
        event_count=len(events),
    )

    buckets: dict[str, dict] = defaultdict(lambda: {
        "period_start": None,
        "harvest_kg": 0.0,
        "feeding_kg_or_l": 0.0,
        "inspection_count": 0,
        "treatment_count": 0,
        "event_count": 0,
    })

    def add(value_date: date, field: str, amount=1):
        key, period_start = _period_key(value_date, grouping)
        bucket = buckets[key]
        bucket["period_start"] = period_start
        bucket[field] += amount

    for harvest in harvests:
        add(harvest.harvest_date, "harvest_kg", harvest.amount_kg)
    for feeding in feedings:
        add(feeding.date, "feeding_kg_or_l", feeding.amount_kg_or_l)
    for inspection in inspections:
        add(inspection.date, "inspection_count")
    for treatment in treatments:
        add(treatment.started_at, "treatment_count")
    for event in events:
        add(event.event_date, "event_count")

    chart = [
        HiveAnalyticsChartPoint(
            period_key=key,
            period_start=bucket["period_start"],
            harvest_kg=round(bucket["harvest_kg"], 2),
            feeding_kg_or_l=round(bucket["feeding_kg_or_l"], 2),
            inspection_count=bucket["inspection_count"],
            treatment_count=bucket["treatment_count"],
            event_count=bucket["event_count"],
        )
        for key, bucket in buckets.items()
    ]
    chart.sort(key=lambda point: point.period_start)

    return HiveAnalyticsResponse(
        hive_id=hive_id,
        from_date=from_date,
        to_date=to_date,
        grouping=grouping,
        kpi=kpi,
        chart=chart,
    )
