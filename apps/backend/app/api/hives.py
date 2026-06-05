from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from app.db.database import get_db
from app.api.dependencies import get_current_active_user
from app.models.user import User
from app.models.harvest import Harvest
from app.models.inspection import Inspection
from app.models.photo import Photo
from app.models.task import Task
from app.models.treatment import Treatment
from app.services.beekeeping_rules import get_inspection_warnings
from app.schemas.hive import HiveCreate, HiveUpdate, HiveResponse
from app.crud import hive as hive_crud

router = APIRouter()


@router.get("", response_model=list[HiveResponse])
def list_hives(
    apiary_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return hive_crud.get_hives(db, owner_id=current_user.id, apiary_id=apiary_id)


@router.post("", response_model=HiveResponse, status_code=status.HTTP_201_CREATED)
def create_hive(
    hive: HiveCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_hive = hive_crud.create_hive(db, hive=hive, owner_id=current_user.id)
    if not db_hive:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Apiary not found")
    return db_hive


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


@router.get("/{hive_id}/timeline")
def get_hive_timeline(
    hive_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_hive = hive_crud.get_hive(db, hive_id=hive_id, owner_id=current_user.id)
    if not db_hive:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hive not found")

    events = []
    for inspection in db.query(Inspection).filter(Inspection.hive_id == hive_id).all():
        events.append({
            "type": "inspection",
            "id": inspection.id,
            "date": inspection.date,
            "title": "Inspection",
            "notes": inspection.notes,
            "warnings": get_inspection_warnings(inspection),
        })
    for task in db.query(Task).filter(Task.owner_id == current_user.id, Task.hive_id == hive_id).all():
        events.append({
            "type": "task",
            "id": task.id,
            "date": task.due_date or task.created_at.date(),
            "title": task.title,
            "status": task.status,
        })
    for treatment in db.query(Treatment).filter(Treatment.owner_id == current_user.id, Treatment.hive_id == hive_id).all():
        events.append({
            "type": "treatment",
            "id": treatment.id,
            "date": treatment.started_at,
            "title": treatment.product,
            "notes": treatment.reason,
        })
    for harvest in db.query(Harvest).filter(Harvest.owner_id == current_user.id, Harvest.hive_id == hive_id).all():
        events.append({
            "type": "harvest",
            "id": harvest.id,
            "date": harvest.harvest_date,
            "title": harvest.crop_type or "Harvest",
            "amount_kg": harvest.amount_kg,
        })
    for photo in db.query(Photo).filter(Photo.owner_id == current_user.id, Photo.hive_id == hive_id).all():
        events.append({
            "type": "photo",
            "id": photo.id,
            "date": photo.created_at.date(),
            "title": photo.filename,
            "caption": photo.caption,
        })

    return sorted(events, key=lambda event: event["date"], reverse=True)


@router.put("/{hive_id}", response_model=HiveResponse)
def update_hive(
    hive_id: int,
    hive_update: HiveUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_hive = hive_crud.update_hive(
        db, hive_id=hive_id, owner_id=current_user.id, hive_update=hive_update
    )
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
