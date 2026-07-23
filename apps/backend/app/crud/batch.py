import calendar
from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from app.models.batch import Batch
from app.models.harvest import Harvest
from app.schemas.batch import BatchCreate, BatchUpdate


def get_batches(db: Session, owner_id: int) -> list[Batch]:
    return db.query(Batch).filter(Batch.owner_id == owner_id).order_by(Batch.created_at.desc()).all()


def get_batch(db: Session, batch_id: int, owner_id: int) -> Optional[Batch]:
    return db.query(Batch).filter(Batch.id == batch_id, Batch.owner_id == owner_id).first()


def _add_months(d: date, months: int) -> date:
    month_index = d.month - 1 + months
    year = d.year + month_index // 12
    month = month_index % 12 + 1
    day = min(d.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def _next_lot_number(db: Session, owner_id: int, year: int) -> str:
    prefix = f"{year}-"
    existing = (
        db.query(Batch.lot_number)
        .filter(Batch.owner_id == owner_id, Batch.lot_number.like(f"{prefix}%"))
        .all()
    )
    max_sequence = 0
    for (lot_number,) in existing:
        suffix = lot_number[len(prefix):]
        if suffix.isdigit():
            max_sequence = max(max_sequence, int(suffix))
    return f"{prefix}{max_sequence + 1:03d}"


def _recalculate_total(db_batch: Batch) -> None:
    db_batch.total_amount_kg = sum(h.amount_kg for h in db_batch.harvests)


def create_batch(db: Session, batch: BatchCreate, owner_id: int) -> Optional[Batch]:
    harvests: list[Harvest] = []
    if batch.harvest_ids:
        harvests = db.query(Harvest).filter(Harvest.id.in_(batch.harvest_ids)).all()
        if len(harvests) != len(set(batch.harvest_ids)):
            return None
        for harvest in harvests:
            if harvest.owner_id != owner_id:
                return None
            if harvest.batch_id is not None:
                return None

    year = date.today().year
    lot_number = _next_lot_number(db, owner_id, year)

    best_before = batch.best_before
    if best_before is None and harvests:
        earliest = min(h.harvest_date for h in harvests)
        best_before = _add_months(earliest, 24)

    db_batch = Batch(
        owner_id=owner_id,
        lot_number=lot_number,
        best_before=best_before,
        total_amount_kg=sum(h.amount_kg for h in harvests),
        notes=batch.notes,
    )
    db.add(db_batch)
    db.flush()

    for harvest in harvests:
        harvest.batch_id = db_batch.id

    db.commit()
    db.refresh(db_batch)
    return db_batch


def update_batch(db: Session, batch_id: int, owner_id: int, batch_update: BatchUpdate) -> Optional[Batch]:
    db_batch = get_batch(db, batch_id, owner_id)
    if not db_batch:
        return None
    data = batch_update.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(db_batch, field, value)
    db.commit()
    db.refresh(db_batch)
    return db_batch


def delete_batch(db: Session, batch_id: int, owner_id: int) -> bool:
    db_batch = get_batch(db, batch_id, owner_id)
    if not db_batch:
        return False
    for harvest in db_batch.harvests:
        harvest.batch_id = None
    db.delete(db_batch)
    db.commit()
    return True


def attach_harvest(db: Session, batch_id: int, owner_id: int, harvest_id: int) -> Optional[Batch]:
    db_batch = get_batch(db, batch_id, owner_id)
    if not db_batch:
        return None
    harvest = db.query(Harvest).filter(Harvest.id == harvest_id, Harvest.owner_id == owner_id).first()
    if not harvest:
        return None
    if harvest.batch_id is not None:
        raise ValueError("Harvest is already attached to a batch")
    harvest.batch_id = db_batch.id
    db.flush()
    db.refresh(db_batch)
    _recalculate_total(db_batch)
    db.commit()
    db.refresh(db_batch)
    return db_batch


def detach_harvest(db: Session, batch_id: int, owner_id: int, harvest_id: int) -> Optional[Batch]:
    db_batch = get_batch(db, batch_id, owner_id)
    if not db_batch:
        return None
    harvest = db.query(Harvest).filter(
        Harvest.id == harvest_id, Harvest.owner_id == owner_id, Harvest.batch_id == batch_id
    ).first()
    if not harvest:
        return None
    harvest.batch_id = None
    db.flush()
    db.refresh(db_batch)
    _recalculate_total(db_batch)
    db.commit()
    db.refresh(db_batch)
    return db_batch
