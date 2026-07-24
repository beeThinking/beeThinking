"""Honigpreis-Rechner (#44): honey pricing calculator.

Formula:
- cost_per_kg = total relevant apiary costs / total harvested kg (over the
  same date range).
- cost_per_colony = apiary-level costs divided evenly across the apiary's
  colony count. This is a documented SIMPLIFICATION: CashbookEntry has no
  hive_id, so per-colony cost allocation cannot be precise — costs are
  assumed to be spread evenly across all active colonies in the apiary,
  which is not exact for apiaries with heterogeneous colony strength/size.

Requires real cashbook data, hence this is an authenticated aggregation
endpoint (unlike #43's public, stateless calculator).
"""

from datetime import date

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.crud.ownership import user_can_access_apiary
from app.models.cashbook import CashbookDirection, CashbookEntry
from app.models.harvest import Harvest
from app.models.hive import Hive, HiveStatus
from app.schemas.honey_price_calculator import HoneyPriceCalculatorRequest, HoneyPriceCalculatorResponse

SIMPLIFICATION_NOTE = (
    "cost_per_colony assumes apiary-level costs are spread evenly across all "
    "active colonies in the apiary, since CashbookEntry has no hive_id. This "
    "is an approximation, not an exact per-colony cost allocation."
)


def calculate_honey_price(
    db: Session, owner_id: int, payload: HoneyPriceCalculatorRequest
) -> HoneyPriceCalculatorResponse | None:
    if not user_can_access_apiary(db, payload.apiary_id, owner_id):
        return None

    cost_query = db.query(CashbookEntry).filter(
        CashbookEntry.apiary_id == payload.apiary_id,
        CashbookEntry.direction == CashbookDirection.expense,
    )
    if payload.from_date:
        cost_query = cost_query.filter(CashbookEntry.booking_date >= payload.from_date)
    if payload.to_date:
        cost_query = cost_query.filter(CashbookEntry.booking_date <= payload.to_date)
    total_costs = sum(entry.amount_net for entry in cost_query.all())

    harvest_query = (
        db.query(Harvest)
        .outerjoin(Hive, Hive.id == Harvest.hive_id)
        .filter(or_(Harvest.apiary_id == payload.apiary_id, Hive.apiary_id == payload.apiary_id))
    )
    if payload.from_date:
        harvest_query = harvest_query.filter(Harvest.harvest_date >= payload.from_date)
    if payload.to_date:
        harvest_query = harvest_query.filter(Harvest.harvest_date <= payload.to_date)
    total_kg = sum(harvest.amount_kg for harvest in harvest_query.all())

    colony_count = (
        db.query(Hive)
        .filter(Hive.apiary_id == payload.apiary_id, Hive.status == HiveStatus.active)
        .count()
    )

    cost_per_kg = round(total_costs / total_kg, 2) if total_kg > 0 else None
    cost_per_colony = round(total_costs / colony_count, 2) if colony_count > 0 else None
    suggested_price_per_kg = (
        round(cost_per_kg * (1 + payload.target_margin_percent / 100), 2) if cost_per_kg is not None else None
    )

    return HoneyPriceCalculatorResponse(
        apiary_id=payload.apiary_id,
        total_relevant_costs=round(total_costs, 2),
        total_harvested_kg=round(total_kg, 2),
        colony_count=colony_count,
        cost_per_kg=cost_per_kg,
        cost_per_colony=cost_per_colony,
        suggested_price_per_kg=suggested_price_per_kg,
        simplification_note=SIMPLIFICATION_NOTE,
    )
