from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user
from app.crud import traceability as traceability_crud
from app.db.database import get_db
from app.models.user import User
from app.schemas.traceability import TraceabilityHarvestEntry, TraceabilityResponse

router = APIRouter()


@router.get("/{lot_number}", response_model=TraceabilityResponse)
def get_traceability(
    lot_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    batch = traceability_crud.get_traceability(db, owner_id=current_user.id, lot_number=lot_number)
    if not batch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lot number not found")

    harvests = [
        TraceabilityHarvestEntry(harvest=harvest, hive=harvest.hive, apiary=harvest.apiary)
        for harvest in batch.harvests
    ]

    return TraceabilityResponse(
        lot_number=batch.lot_number,
        batch=batch,
        harvests=harvests,
        inventory_items=batch.inventory_items,
    )
