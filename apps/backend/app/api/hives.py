from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.api.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.hive import HiveCreate, HiveUpdate, HiveResponse
from app.crud import hive as hive_crud

router = APIRouter()


@router.get("", response_model=list[HiveResponse])
def list_hives(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return hive_crud.get_hives(db, owner_id=current_user.id)


@router.post("", response_model=HiveResponse, status_code=status.HTTP_201_CREATED)
def create_hive(
    hive: HiveCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return hive_crud.create_hive(db, hive=hive, owner_id=current_user.id)


@router.get("/{hive_id}", response_model=HiveResponse)
def get_hive(
    hive_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_hive = hive_crud.get_hive(db, hive_id=hive_id, owner_id=current_user.id)
    if not db_hive:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hive not found")
    return db_hive


@router.put("/{hive_id}", response_model=HiveResponse)
def update_hive(
    hive_id: int,
    hive_update: HiveUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_hive = hive_crud.update_hive(db, hive_id=hive_id, owner_id=current_user.id, hive_update=hive_update)
    if not db_hive:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hive not found")
    return db_hive


@router.delete("/{hive_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_hive(
    hive_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    success = hive_crud.delete_hive(db, hive_id=hive_id, owner_id=current_user.id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hive not found")
