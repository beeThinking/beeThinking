from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user
from app.crud import varroa_check as varroa_check_crud
from app.db.database import get_db
from app.models.user import User
from app.schemas.varroa_check import VarroaCheckCreate, VarroaCheckResponse, VarroaCheckUpdate

router = APIRouter()


@router.get("", response_model=list[VarroaCheckResponse])
def list_varroa_checks(
    hive_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return varroa_check_crud.get_varroa_checks(db, owner_id=current_user.id, hive_id=hive_id)


@router.post("", response_model=VarroaCheckResponse, status_code=status.HTTP_201_CREATED)
def create_varroa_check(
    check: VarroaCheckCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_check = varroa_check_crud.create_varroa_check(db, check=check, owner_id=current_user.id)
    if not db_check:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hive not found")
    return db_check


@router.get("/{check_id}", response_model=VarroaCheckResponse)
def get_varroa_check(
    check_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_check = varroa_check_crud.get_varroa_check(db, check_id=check_id, owner_id=current_user.id)
    if not db_check:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Varroa check not found")
    return db_check


@router.put("/{check_id}", response_model=VarroaCheckResponse)
def update_varroa_check(
    check_id: int,
    check_update: VarroaCheckUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_check = varroa_check_crud.update_varroa_check(
        db, check_id=check_id, owner_id=current_user.id, check_update=check_update
    )
    if not db_check:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Varroa check not found")
    return db_check


@router.delete("/{check_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_varroa_check(
    check_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if not varroa_check_crud.delete_varroa_check(db, check_id=check_id, owner_id=current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Varroa check not found")
