from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from app.db.database import get_db
from app.api.dependencies import get_current_active_user
from app.models.user import User
from app.models.harvest import Harvest
from app.models.feeding import Feeding
from app.models.inspection import Inspection
from app.models.photo import Photo
from app.models.task import Task
from app.models.treatment import Treatment
from app.models.queen import Queen
from app.models.varroa_weather import VarroaTreatmentType
from app.schemas.varroa_weather import VarroaAssistantResponse
from app.services.beekeeping_rules import get_inspection_warnings
from app.services.varroa_weather import get_varroa_weather_window
from app.schemas.hive import (
    HiveCopyRequest,
    HiveCreate,
    HiveEventResponse,
    HiveLifecycleRequest,
    HiveMoveRequest,
    HiveRequeenRequest,
    TimelineEntryUpdate,
    HiveUpdate,
    HiveResponse,
)
from app.schemas.queen import QueenResponse
from app.models.hive import HiveStatus
from app.models.varroa_check import VarroaCheck
from app.services.hive_lifecycle import (
    archive_hive,
    copy_hive,
    dissolve_hive,
    get_hive_timeline as get_lifecycle_timeline,
    merge_hives,
    move_hive,
    requeen_hive,
)
from app.crud import hive as hive_crud
from app.crud.ownership import user_can_admin_apiary, user_can_write_apiary
from datetime import date

router = APIRouter()


def _hive_response(hive, db: Session) -> dict:
    data = HiveResponse.model_validate(hive).model_dump()
    queen = db.query(Queen).filter(Queen.hive_id == hive.id, Queen.is_active.is_(True)).first()
    if queen:
        data.update({
            "active_queen_year": queen.year,
            "active_queen_color": queen.marking_color,
            "active_queen_marking": queen.marking_code,
            "queen_introduced_at": queen.introduced_at,
        })
    return data


@router.get("", response_model=list[HiveResponse])
def list_hives(
    apiary_id: Optional[int] = None,
    hive_status: Optional[HiveStatus] = Query(HiveStatus.active, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return [_hive_response(hive, db) for hive in hive_crud.get_hives(
        db, owner_id=current_user.id, apiary_id=apiary_id, status=hive_status
    )]


@router.post("", response_model=HiveResponse, status_code=status.HTTP_201_CREATED)
def create_hive(
    hive: HiveCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_hive = hive_crud.create_hive(db, hive=hive, owner_id=current_user.id)
    if not db_hive:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Apiary not found")
    return _hive_response(db_hive, db)


@router.get("/{hive_id}", response_model=HiveResponse)
def get_hive(
    hive_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_hive = hive_crud.get_hive(db, hive_id=hive_id, owner_id=current_user.id)
    if not db_hive:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hive not found")
    return _hive_response(db_hive, db)


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
            "editable": False,
            "deletable": False,
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
            "editable": True,
            "deletable": True,
        })
    for task in db.query(Task).filter(Task.hive_id == hive_id).all():
        events.append({
            "type": "task",
            "id": task.id,
            "date": task.due_date or task.created_at.date(),
            "title": task.title,
            "status": task.status,
            "notes": task.description,
            "editable": True,
            "deletable": True,
        })
    for treatment in db.query(Treatment).filter(Treatment.hive_id == hive_id).all():
        events.append({
            "type": "treatment",
            "id": treatment.id,
            "date": treatment.started_at,
            "title": treatment.product,
            "notes": treatment.reason,
            "editable": True,
            "deletable": True,
        })
    for harvest in db.query(Harvest).filter(Harvest.hive_id == hive_id).all():
        events.append({
            "type": "harvest",
            "id": harvest.id,
            "date": harvest.harvest_date,
            "title": harvest.crop_type or "Harvest",
            "amount_kg": harvest.amount_kg,
            "notes": harvest.notes,
            "editable": True,
            "deletable": True,
        })
    for feeding in db.query(Feeding).filter(Feeding.hive_id == hive_id).all():
        events.append({
            "type": "feeding",
            "id": feeding.id,
            "date": feeding.date,
            "title": feeding.feed_type,
            "amount_kg_or_l": feeding.amount_kg_or_l,
            "notes": feeding.notes,
            "editable": True,
            "deletable": True,
        })
    for photo in db.query(Photo).filter(Photo.hive_id == hive_id).all():
        events.append({
            "type": "photo",
            "id": photo.id,
            "date": photo.created_at.date(),
            "title": photo.filename,
            "caption": photo.caption,
            "editable": False,
            "deletable": False,
        })
    for check in db.query(VarroaCheck).filter(VarroaCheck.hive_id == hive_id).all():
        events.append({
            "type": "varroa_check",
            "id": check.id,
            "date": check.date,
            "title": check.method or "Varroakontrolle",
            "mite_count": check.mite_count,
            "mites_per_day": check.mites_per_day,
            "notes": check.notes,
            "editable": True,
            "deletable": True,
        })

    return sorted(events, key=lambda event: event["date"], reverse=True)


TIMELINE_MODELS = {
    "inspection": (Inspection, "date", None, "notes"),
    "task": (Task, "due_date", "title", "description"),
    "treatment": (Treatment, "started_at", "product", "reason"),
    "harvest": (Harvest, "harvest_date", "crop_type", "notes"),
    "feeding": (Feeding, "date", "feed_type", "notes"),
    "varroa_check": (VarroaCheck, "date", "method", "notes"),
}


def _timeline_entry(db: Session, hive_id: int, event_type: str, event_id: int):
    config = TIMELINE_MODELS.get(event_type)
    if not config:
        return None, None
    model = config[0]
    return db.query(model).filter(model.id == event_id, model.hive_id == hive_id).first(), config


@router.patch("/{hive_id}/timeline/{event_type}/{event_id}")
def update_timeline_entry(
    hive_id: int,
    event_type: str,
    event_id: int,
    payload: TimelineEntryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    hive = hive_crud.get_hive(db, hive_id=hive_id, owner_id=current_user.id)
    if not hive or not user_can_write_apiary(db, hive.apiary_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Timeline entry not found")
    entry, config = _timeline_entry(db, hive_id, event_type, event_id)
    if not entry or not config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Timeline entry not found")
    _, date_field, title_field, notes_field = config
    if payload.date is not None:
        setattr(entry, date_field, payload.date)
    if payload.title is not None and title_field:
        setattr(entry, title_field, payload.title)
    if payload.notes is not None:
        setattr(entry, notes_field, payload.notes)
    db.commit()
    return {"updated": True}


@router.delete("/{hive_id}/timeline/{event_type}/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_timeline_entry(
    hive_id: int,
    event_type: str,
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    hive = hive_crud.get_hive(db, hive_id=hive_id, owner_id=current_user.id)
    if not hive or not user_can_write_apiary(db, hive.apiary_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Timeline entry not found")
    entry, _ = _timeline_entry(db, hive_id, event_type, event_id)
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Timeline entry not found")
    db.delete(entry)
    db.commit()


@router.get("/{hive_id}/stock-card")
def get_stock_card(
    hive_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_hive = hive_crud.get_hive(db, hive_id=hive_id, owner_id=current_user.id)
    if not db_hive:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hive not found")
    return {
        "hive": _hive_response(db_hive, db),
        "qr_url": f"/stock-card/{db_hive.id}",
        "events": get_hive_timeline(hive_id=hive_id, db=db, current_user=current_user),
    }


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


@router.post("/{hive_id}/move", response_model=HiveResponse)
def move_hive_endpoint(
    hive_id: int,
    payload: HiveMoveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    hive = move_hive(db, hive_id, current_user.id, payload.target_apiary_id, payload.date, payload.note)
    if not hive:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hive or target apiary not found")
    return hive


@router.post("/{hive_id}/copy", response_model=HiveResponse, status_code=status.HTTP_201_CREATED)
def copy_hive_endpoint(
    hive_id: int,
    payload: HiveCopyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    hive = copy_hive(
        db,
        hive_id,
        current_user.id,
        payload.date,
        name=payload.name,
        stock_number=payload.stock_number,
        note=payload.note,
    )
    if not hive:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hive not found")
    return hive


@router.post("/{hive_id}/requeen", response_model=QueenResponse, status_code=status.HTTP_201_CREATED)
def requeen_hive_endpoint(
    hive_id: int,
    payload: HiveRequeenRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    queen = requeen_hive(
        db,
        hive_id,
        current_user.id,
        payload.date,
        payload.year,
        marking_color=payload.marking_color,
        marking_code=payload.marking_code,
        introduced_at=payload.introduced_at,
        name=payload.name,
        origin=payload.origin,
        reason=payload.reason,
        note=payload.note,
    )
    if not queen:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hive not found")
    return queen


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
        owner_id=db_hive.owner_id,
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
    if not user_can_admin_apiary(db, exists.apiary_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hive not found")
    success = hive_crud.delete_hive(db, hive_id=hive_id, owner_id=current_user.id)
    if not success:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Hive has historical records; archive it instead")
