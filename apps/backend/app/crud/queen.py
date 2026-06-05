from typing import Optional

from sqlalchemy.orm import Session

from app.crud.ownership import validate_optional_refs
from app.models.queen import Queen
from app.schemas.queen import QueenCreate, QueenUpdate


def get_queens(db: Session, owner_id: int) -> list[Queen]:
    return db.query(Queen).filter(Queen.owner_id == owner_id).all()


def get_queen(db: Session, queen_id: int, owner_id: int) -> Optional[Queen]:
    return db.query(Queen).filter(Queen.id == queen_id, Queen.owner_id == owner_id).first()


def create_queen(db: Session, queen: QueenCreate, owner_id: int) -> Optional[Queen]:
    data = queen.model_dump()
    if not validate_optional_refs(db, owner_id, hive_id=data.get("hive_id")):
        return None
    db_queen = Queen(**data, owner_id=owner_id)
    db.add(db_queen)
    db.commit()
    db.refresh(db_queen)
    return db_queen


def update_queen(db: Session, queen_id: int, owner_id: int, queen_update: QueenUpdate) -> Optional[Queen]:
    db_queen = get_queen(db, queen_id, owner_id)
    if not db_queen:
        return None
    data = queen_update.model_dump(exclude_unset=True)
    if "hive_id" in data and not validate_optional_refs(db, owner_id, hive_id=data["hive_id"]):
        return None
    for field, value in data.items():
        setattr(db_queen, field, value)
    db.commit()
    db.refresh(db_queen)
    return db_queen


def delete_queen(db: Session, queen_id: int, owner_id: int) -> bool:
    db_queen = get_queen(db, queen_id, owner_id)
    if not db_queen:
        return False
    db.delete(db_queen)
    db.commit()
    return True
