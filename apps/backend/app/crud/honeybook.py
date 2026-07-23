from typing import Optional

from sqlalchemy import extract
from sqlalchemy.orm import Session, joinedload

from app.models.batch import Batch
from app.models.harvest import Harvest
from app.models.inventory import InventoryItem
from app.schemas.honeybook import HoneybookEntry


def _bottled_summary(db: Session, owner_id: int, batch_id: int) -> tuple[int, list[str]]:
    items = (
        db.query(InventoryItem)
        .options(joinedload(InventoryItem.article))
        .filter(InventoryItem.owner_id == owner_id, InventoryItem.batch_id == batch_id)
        .all()
    )
    bottled_quantity = int(sum(item.quantity for item in items))
    bottled_articles = sorted({item.article.name for item in items if item.article})
    return bottled_quantity, bottled_articles


def get_register(db: Session, owner_id: int, year: Optional[int] = None) -> list[HoneybookEntry]:
    query = (
        db.query(Harvest)
        .options(joinedload(Harvest.batch), joinedload(Harvest.apiary), joinedload(Harvest.hive))
        .filter(Harvest.owner_id == owner_id)
    )
    if year is not None:
        query = query.filter(extract("year", Harvest.harvest_date) == year)
    harvests = query.order_by(Harvest.harvest_date.desc()).all()

    entries: list[HoneybookEntry] = []
    for harvest in harvests:
        batch: Optional[Batch] = harvest.batch
        if batch is not None:
            bottled_quantity, bottled_articles = _bottled_summary(db, owner_id, batch.id)
            entries.append(
                HoneybookEntry(
                    lot_number=batch.lot_number,
                    status="batched",
                    harvest_date=harvest.harvest_date,
                    apiary_name=harvest.apiary.name if harvest.apiary else None,
                    hive_name=harvest.hive.name if harvest.hive else None,
                    crop_type=harvest.crop_type,
                    amount_kg=harvest.amount_kg,
                    water_content_percent=harvest.water_content_percent,
                    best_before=batch.best_before,
                    bottled_quantity=bottled_quantity,
                    bottled_articles=bottled_articles,
                )
            )
        else:
            entries.append(
                HoneybookEntry(
                    lot_number=None,
                    status="unbatched",
                    harvest_date=harvest.harvest_date,
                    apiary_name=harvest.apiary.name if harvest.apiary else None,
                    hive_name=harvest.hive.name if harvest.hive else None,
                    crop_type=harvest.crop_type,
                    amount_kg=harvest.amount_kg,
                    water_content_percent=harvest.water_content_percent,
                    best_before=None,
                    bottled_quantity=0,
                    bottled_articles=[],
                )
            )
    return entries
