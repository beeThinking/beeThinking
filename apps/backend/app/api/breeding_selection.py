from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user
from app.crud import breeding_selection as breeding_selection_crud
from app.crud import criterion_weight as criterion_weight_crud
from app.db.database import get_db
from app.models.user import User
from app.schemas.criterion_weight import (
    BreedingCandidateResponse,
    CriterionWeightResponse,
    CriterionWeightUpsert,
)

router = APIRouter()


@router.get("/weights", response_model=list[CriterionWeightResponse])
def list_weights(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return criterion_weight_crud.get_weights(db, user_id=current_user.id)


@router.put("/weights", response_model=CriterionWeightResponse)
def upsert_weight(
    payload: CriterionWeightUpsert,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return criterion_weight_crud.upsert_weight(db, user_id=current_user.id, payload=payload)


@router.delete("/weights/{criterion_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_weight(
    criterion_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if not criterion_weight_crud.delete_weight(db, user_id=current_user.id, criterion_id=criterion_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Weight not found")


@router.get("/candidates", response_model=list[BreedingCandidateResponse])
def ranked_candidates(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return breeding_selection_crud.rank_breeding_candidates(db, owner_id=current_user.id)
