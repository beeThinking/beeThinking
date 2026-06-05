from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user
from app.crud import photo as photo_crud
from app.crud.ownership import validate_optional_refs
from app.db.database import get_db
from app.models.user import User
from app.schemas.photo import PhotoCreate, PhotoResponse
from app.services.storage import (
    StorageUnavailableError,
    build_object_key,
    get_photo_url,
    upload_photo_object,
)

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


@router.post("/upload", response_model=PhotoResponse, status_code=status.HTTP_201_CREATED)
def upload_photo(
    file: UploadFile = File(...),
    hive_id: int | None = Form(None),
    inspection_id: int | None = Form(None),
    caption: str | None = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if not validate_optional_refs(db, current_user.id, hive_id=hive_id, inspection_id=inspection_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Related resource not found")

    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)
    object_key = build_object_key(current_user.id, file.filename or "photo")
    content_type = file.content_type or "application/octet-stream"
    try:
        upload_photo_object(object_key, file.file, size, content_type)
    except StorageUnavailableError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc

    db_photo = photo_crud.create_photo(
        db,
        PhotoCreate(
            hive_id=hive_id,
            inspection_id=inspection_id,
            object_key=object_key,
            filename=file.filename or object_key.rsplit("/", 1)[-1],
            content_type=content_type,
            size_bytes=size,
            caption=caption,
        ),
        owner_id=current_user.id,
    )
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


@router.get("/{photo_id}/preview")
def get_photo_preview(
    photo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_photo = photo_crud.get_photo(db, photo_id=photo_id, owner_id=current_user.id)
    if not db_photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
    try:
        return {"url": get_photo_url(db_photo.object_key)}
    except StorageUnavailableError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc


@router.delete("/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_photo(
    photo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if not photo_crud.delete_photo(db, photo_id=photo_id, owner_id=current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
