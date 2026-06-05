from fastapi import APIRouter, Depends, HTTPException, Query, status
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
from app.models.varroa_weather import VarroaTreatmentType
from app.schemas.varroa_weather import VarroaAssistantResponse
from app.services.beekeeping_rules import get_inspection_warnings
from app.services.varroa_weather import get_varroa_weather_window
from app.schemas.hive import HiveCreate, HiveEventResponse, HiveLifecycleRequest, HiveUpdate, HiveResponse
from app.models.hive import HiveStatus
from app.services.hive_lifecycle import archive_hive, dissolve_hive, get_hive_timeline as get_lifecycle_timeline, merge_hives
from app.crud import hive as hive_crud
from datetime import date

router = APIRouter()


@router.get("", response_model=list[HiveResponse])
def list_hives(
    apiary_id: Optional[int] = None,
    hive_status: Optional[HiveStatus] = Query(HiveStatus.active, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return hive_crud.get_hives(db, owner_id=current_user.id, apiary_id=apiary_id, status=hive_status)


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

    events = [
        {
            "type": event.event_type,
            "id": event.id,
            "date": event.event_date,
            "title": event.title,
            "notes": event.description,
        }
        for event in get_lifecycle_timeline(db, hive_id, current_user.id)
    ]
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


@router.get("/{hive_id}/history", response_model=list[HiveEventResponse])
def get_hive_history(
    hive_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if not hive_crud.get_hive(db, hive_id=hive_id, owner_id=current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hive not found")
    return get_lifecycle_timeline(db, hive_id, current_user.id)


@router.post("/{hive_id}/archive", response_model=HiveResponse)
def archive_hive_endpoint(
    hive_id: int,
    payload: HiveLifecycleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    hive = archive_hive(db, hive_id, current_user.id, payload.reason, payload.date, payload.note)
    if not hive:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hive not found")
    return hive


@router.post("/{hive_id}/dissolve", response_model=HiveResponse)
def dissolve_hive_endpoint(
    hive_id: int,
    payload: HiveLifecycleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    hive = dissolve_hive(db, hive_id, current_user.id, payload.reason, payload.date, payload.note)
    if not hive:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hive not found")
    return hive


@router.post("/{hive_id}/merge", response_model=HiveResponse)
def merge_hive_endpoint(
    hive_id: int,
    payload: HiveLifecycleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if not payload.target_hive_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="target_hive_id required")
    hive = merge_hives(db, hive_id, payload.target_hive_id, current_user.id, payload.date, payload.note)
    if not hive:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hive not found")
    return hive


@router.get("/{hive_id}/varroa-assistant", response_model=VarroaAssistantResponse)
def get_varroa_assistant(
    hive_id: int,
    treatment_type: VarroaTreatmentType = VarroaTreatmentType.formic_acid_short,
    days: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_hive = hive_crud.get_hive(db, hive_id=hive_id, owner_id=current_user.id)
    if not db_hive:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hive not found")
    windows = get_varroa_weather_window(
        db,
        apiary_id=db_hive.apiary_id,
        owner_id=current_user.id,
        treatment_type=treatment_type,
        start_date=date.today(),
        days=days,
    )
    return {
        "hive_id": db_hive.id,
        "apiary_id": db_hive.apiary_id,
        "disclaimer": "Diese Anzeige ist eine Planungshilfe. Bitte Zulassung, Packungsbeilage, regionale Empfehlungen und Volkzustand prüfen.",
        "source_note": "Planungshilfe. Zulassung, Packungsbeilage, regionale Empfehlungen und Volkzustand prüfen.",
        "windows": windows,
    }


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
    exists = hive_crud.get_hive(db, hive_id=hive_id, owner_id=current_user.id)
    if not exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hive not found")
    success = hive_crud.delete_hive(db, hive_id=hive_id, owner_id=current_user.id)
    if not success:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Hive has historical records; archive it instead")
