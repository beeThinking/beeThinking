import calendar
from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from app.models.batch import Batch
from app.models.harvest import Harvest
from app.models.inventory import Article, InventoryItem
from app.schemas.batch import BatchCreate, BatchUpdate, BottleItem, BottleRequest


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

    total_amount_kg = sum(h.amount_kg for h in harvests)
    db_batch = Batch(
        owner_id=owner_id,
        lot_number=lot_number,
        best_before=best_before,
        total_amount_kg=total_amount_kg,
        remaining_kg=total_amount_kg,
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


class InsufficientBatchQuantityError(Exception):
    pass


def bottle_batch(
    db: Session, batch_id: int, owner_id: int, request: BottleRequest
) -> Optional[tuple[Batch, list[InventoryItem]]]:
    db_batch = get_batch(db, batch_id, owner_id)
    if not db_batch:
        return None

    merged_items: dict[int, BottleItem] = {}
    for bottle_item in request.items:
        existing = merged_items.get(bottle_item.article_id)
        if existing:
            existing.quantity += bottle_item.quantity
            if bottle_item.price is not None:
                existing.price = bottle_item.price
            if bottle_item.best_before is not None:
                existing.best_before = bottle_item.best_before
        else:
            merged_items[bottle_item.article_id] = bottle_item.model_copy()

    articles: dict[int, Article] = {}
    for article_id in merged_items:
        article = db.query(Article).filter(
            Article.id == article_id, Article.owner_id == owner_id
        ).first()
        if not article:
            return None
        articles[article_id] = article

    total_weight_kg = sum(
        (articles[item.article_id].weight_kg or 0) * item.quantity for item in merged_items.values()
    )

    remaining = db_batch.remaining_kg if db_batch.remaining_kg is not None else db_batch.total_amount_kg
    if remaining - total_weight_kg < 0:
        raise InsufficientBatchQuantityError("Bottling would exceed remaining batch quantity")

    affected_items: list[InventoryItem] = []
    for bottle_item in merged_items.values():
        db_item = db.query(InventoryItem).filter(
            InventoryItem.owner_id == owner_id,
            InventoryItem.article_id == bottle_item.article_id,
            InventoryItem.batch_id == batch_id,
        ).first()
        if db_item:
            db_item.quantity += bottle_item.quantity
            if bottle_item.price is not None:
                db_item.price = bottle_item.price
            if bottle_item.best_before is not None:
                db_item.best_before = bottle_item.best_before
        else:
            article = articles[bottle_item.article_id]
            db_item = InventoryItem(
                owner_id=owner_id,
                article_id=bottle_item.article_id,
                batch_id=batch_id,
                quantity=bottle_item.quantity,
                unit=article.unit,
                price=bottle_item.price,
                best_before=bottle_item.best_before,
            )
            db.add(db_item)
        affected_items.append(db_item)

    db_batch.remaining_kg = remaining - total_weight_kg

    db.commit()
    db.refresh(db_batch)
    for item in affected_items:
        db.refresh(item)
    return db_batch, affected_items
