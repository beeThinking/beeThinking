from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user
from app.crud import inspection_criterion as criterion_crud
from app.db.database import get_db
from app.models.user import User
from app.schemas.inspection_criterion import (
    InspectionCriterionCreate,
    InspectionCriterionResponse,
    InspectionCriterionUpdate,
)

router = APIRouter()


@router.get("", response_model=list[InspectionCriterionResponse])
def list_criteria(
    include_inactive: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return criterion_crud.get_criteria(db, owner_id=current_user.id, include_inactive=include_inactive)


@router.post("", response_model=InspectionCriterionResponse, status_code=status.HTTP_201_CREATED)
def create_criterion(
    criterion: InspectionCriterionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return criterion_crud.create_criterion(db, criterion=criterion, owner_id=current_user.id)


@router.put("/{criterion_id}", response_model=InspectionCriterionResponse)
def update_criterion(
    criterion_id: int,
    criterion_update: InspectionCriterionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_criterion = criterion_crud.update_criterion(
        db, criterion_id=criterion_id, owner_id=current_user.id, criterion_update=criterion_update
    )
    if not db_criterion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Criterion not found")
    return db_criterion


@router.delete("/{criterion_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_criterion(
    criterion_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if not criterion_crud.delete_criterion(db, criterion_id=criterion_id, owner_id=current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Criterion not found")
