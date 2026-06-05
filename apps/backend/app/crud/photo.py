from typing import Optional

from sqlalchemy.orm import Session

from app.crud.ownership import validate_optional_refs
from app.models.photo import Photo
from app.schemas.photo import PhotoCreate


def get_photos(db: Session, owner_id: int) -> list[Photo]:
    return db.query(Photo).filter(Photo.owner_id == owner_id).order_by(Photo.created_at.desc()).all()


def get_photo(db: Session, photo_id: int, owner_id: int) -> Optional[Photo]:
    return db.query(Photo).filter(Photo.id == photo_id, Photo.owner_id == owner_id).first()


def create_photo(db: Session, photo: PhotoCreate, owner_id: int) -> Optional[Photo]:
    data = photo.model_dump()
    if not validate_optional_refs(
        db,
        owner_id,
        hive_id=data.get("hive_id"),
        inspection_id=data.get("inspection_id"),
    ):
        return None
    db_photo = Photo(**data, owner_id=owner_id)
    db.add(db_photo)
    db.commit()
    db.refresh(db_photo)
    return db_photo


def delete_photo(db: Session, photo_id: int, owner_id: int) -> bool:
    db_photo = get_photo(db, photo_id, owner_id)
    if not db_photo:
        return False
    db.delete(db_photo)
    db.commit()
    return True
