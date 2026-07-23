from typing import Optional

from sqlalchemy.orm import Session, joinedload

from app.models.batch import Batch
from app.models.harvest import Harvest


def get_traceability(db: Session, owner_id: int, lot_number: str) -> Optional[Batch]:
    return (
        db.query(Batch)
        .options(joinedload(Batch.harvests).joinedload(Harvest.hive))
        .options(joinedload(Batch.harvests).joinedload(Harvest.apiary))
        .options(joinedload(Batch.inventory_items))
        .filter(Batch.owner_id == owner_id, Batch.lot_number == lot_number)
        .first()
    )
