from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user
from app.crud import photo as photo_crud
from app.db.database import get_db
from app.models.user import User
from app.schemas.photo import PhotoCreate, PhotoResponse

router = APIRouter()


@router.get("", response_model=list[PhotoResponse])
def list_photos(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return photo_crud.get_photos(db, owner_id=current_user.id)


@router.post("", response_model=PhotoResponse, status_code=status.HTTP_201_CREATED)
def create_photo(
    photo: PhotoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_photo = photo_crud.create_photo(db, photo=photo, owner_id=current_user.id)
    if not db_photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Related resource not found")
    return db_photo


@router.get("/{photo_id}", response_model=PhotoResponse)
def get_photo(
    photo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_photo = photo_crud.get_photo(db, photo_id=photo_id, owner_id=current_user.id)
    if not db_photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
    return db_photo


@router.delete("/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_photo(
    photo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if not photo_crud.delete_photo(db, photo_id=photo_id, owner_id=current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
