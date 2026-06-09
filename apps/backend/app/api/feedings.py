from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user
from app.crud import feeding as feeding_crud
from app.db.database import get_db
from app.models.user import User
from app.schemas.feeding import FeedingCreate, FeedingResponse, FeedingUpdate

router = APIRouter()


@router.get("", response_model=list[FeedingResponse])
def list_feedings(
    apiary_id: Optional[int] = None,
    hive_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return feeding_crud.get_feedings(db, owner_id=current_user.id, apiary_id=apiary_id, hive_id=hive_id)


@router.post("", response_model=FeedingResponse, status_code=status.HTTP_201_CREATED)
def create_feeding(
    feeding: FeedingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_feeding = feeding_crud.create_feeding(db, feeding=feeding, owner_id=current_user.id)
    if not db_feeding:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Related resource not found")
    return db_feeding


@router.get("/{feeding_id}", response_model=FeedingResponse)
def get_feeding(
    feeding_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_feeding = feeding_crud.get_feeding(db, feeding_id=feeding_id, owner_id=current_user.id)
    if not db_feeding:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feeding not found")
    return db_feeding


@router.put("/{feeding_id}", response_model=FeedingResponse)
def update_feeding(
    feeding_id: int,
    feeding_update: FeedingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_feeding = feeding_crud.update_feeding(db, feeding_id=feeding_id, owner_id=current_user.id, feeding_update=feeding_update)
    if not db_feeding:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feeding not found")
    return db_feeding


@router.delete("/{feeding_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_feeding(
    feeding_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if not feeding_crud.delete_feeding(db, feeding_id=feeding_id, owner_id=current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feeding not found")
