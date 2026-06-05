from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user
from app.crud import queen as queen_crud
from app.db.database import get_db
from app.models.user import User
from app.schemas.queen import QueenCreate, QueenResponse, QueenUpdate

router = APIRouter()


@router.get("", response_model=list[QueenResponse])
def list_queens(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return queen_crud.get_queens(db, owner_id=current_user.id)


@router.post("", response_model=QueenResponse, status_code=status.HTTP_201_CREATED)
def create_queen(
    queen: QueenCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_queen = queen_crud.create_queen(db, queen=queen, owner_id=current_user.id)
    if not db_queen:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hive not found")
    return db_queen


@router.get("/{queen_id}", response_model=QueenResponse)
def get_queen(
    queen_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_queen = queen_crud.get_queen(db, queen_id=queen_id, owner_id=current_user.id)
    if not db_queen:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Queen not found")
    return db_queen


@router.put("/{queen_id}", response_model=QueenResponse)
def update_queen(
    queen_id: int,
    queen_update: QueenUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_queen = queen_crud.update_queen(
        db, queen_id=queen_id, owner_id=current_user.id, queen_update=queen_update
    )
    if not db_queen:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Queen not found")
    return db_queen


@router.delete("/{queen_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_queen(
    queen_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if not queen_crud.delete_queen(db, queen_id=queen_id, owner_id=current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Queen not found")
