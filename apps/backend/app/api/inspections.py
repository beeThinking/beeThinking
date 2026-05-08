from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.api.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.inspection import InspectionCreate, InspectionUpdate, InspectionResponse
from app.crud import inspection as inspection_crud
from app.crud import hive as hive_crud

router = APIRouter()


def _get_hive_or_404(hive_id: int, current_user: User, db: Session):
    hive = hive_crud.get_hive(db, hive_id=hive_id, owner_id=current_user.id)
    if not hive:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hive not found")
    return hive


@router.get("", response_model=list[InspectionResponse])
def list_inspections(
    hive_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    _get_hive_or_404(hive_id, current_user, db)
    return inspection_crud.get_inspections(db, hive_id=hive_id)


@router.post("", response_model=InspectionResponse, status_code=status.HTTP_201_CREATED)
def create_inspection(
    hive_id: int,
    inspection: InspectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    _get_hive_or_404(hive_id, current_user, db)
    return inspection_crud.create_inspection(db, inspection=inspection, hive_id=hive_id)


@router.get("/{inspection_id}", response_model=InspectionResponse)
def get_inspection(
    hive_id: int,
    inspection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    _get_hive_or_404(hive_id, current_user, db)
    db_inspection = inspection_crud.get_inspection(db, inspection_id=inspection_id, hive_id=hive_id)
    if not db_inspection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inspection not found")
    return db_inspection


@router.put("/{inspection_id}", response_model=InspectionResponse)
def update_inspection(
    hive_id: int,
    inspection_id: int,
    inspection_update: InspectionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    _get_hive_or_404(hive_id, current_user, db)
    db_inspection = inspection_crud.update_inspection(
        db, inspection_id=inspection_id, hive_id=hive_id, inspection_update=inspection_update
    )
    if not db_inspection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inspection not found")
    return db_inspection


@router.delete("/{inspection_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_inspection(
    hive_id: int,
    inspection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    _get_hive_or_404(hive_id, current_user, db)
    success = inspection_crud.delete_inspection(db, inspection_id=inspection_id, hive_id=hive_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inspection not found")
