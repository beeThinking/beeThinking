from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.api.dependencies import get_current_active_user
from app.crud import user as user_crud
from app.crud.ownership import user_can_admin_apiary, user_can_write_apiary
from app.models.apiary_member import ApiaryMember, ApiaryMemberRole
from app.crud import feeding as feeding_crud
from app.models.user import User
from app.schemas.apiary_member import ApiaryMemberCreate, ApiaryMemberResponse, ApiaryMemberUpdate
from app.models.varroa_weather import VarroaTreatmentType
from app.schemas.feeding import FeedingCreate
from app.schemas.harvest import HarvestCreate
from app.schemas.inspection import InspectionCreate
from app.schemas.apiary import ApiaryCreate, ApiaryUpdate, ApiaryResponse
from app.schemas.treatment import TreatmentCreate
from app.schemas.varroa_weather import VarroaWeatherWindowResponse
from app.crud import apiary as apiary_crud, harvest as harvest_crud, inspection as inspection_crud, treatment as treatment_crud
from app.services.hive_lifecycle import move_hive
from app.services.varroa_weather import get_varroa_weather_window, refresh_varroa_weather_windows

router = APIRouter()


class BatchActionRequest(BaseModel):
    hive_ids: list[int] = Field(..., min_length=1)
    date: date
    notes: str | None = Field(None, max_length=2000)
    queen_seen: bool = False
    brood_strength: int | None = Field(None, ge=1, le=10)
    varroa_count: float | None = Field(None, ge=0)
    food_stores: int | None = Field(None, ge=1, le=10)
    product: str | None = Field(None, max_length=200)
    method: str | None = Field(None, max_length=200)
    dosage: str | None = Field(None, max_length=200)
    feed_type: str | None = Field(None, max_length=120)
    amount_kg_or_l: float | None = Field(None, gt=0)
    crop_type: str | None = Field(None, max_length=100)
    amount_kg: float | None = Field(None, ge=0)
    batch_code: str | None = Field(None, max_length=100)
    target_apiary_id: int | None = None


@router.get("", response_model=list[ApiaryResponse])
def list_apiaries(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    apiaries = apiary_crud.get_apiaries(db, owner_id=current_user.id)
    result = []
    for a in apiaries:
        data = ApiaryResponse.model_validate(a)
        data.hive_count = len(a.hives)
        result.append(data)
    return result


@router.post("", response_model=ApiaryResponse, status_code=status.HTTP_201_CREATED)
def create_apiary(
    apiary: ApiaryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return apiary_crud.create_apiary(db, apiary=apiary, owner_id=current_user.id)


@router.get("/invitations", response_model=list[ApiaryMemberResponse])
def list_apiary_invitations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return db.query(ApiaryMember).filter(
        ApiaryMember.user_id == current_user.id,
        ApiaryMember.accepted_at.is_(None),
    ).order_by(ApiaryMember.created_at.desc()).all()


@router.post("/invitations/{member_id}/accept", response_model=ApiaryMemberResponse)
def accept_apiary_invitation(
    member_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    member = db.query(ApiaryMember).filter(
        ApiaryMember.id == member_id,
        ApiaryMember.user_id == current_user.id,
        ApiaryMember.accepted_at.is_(None),
    ).first()
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found")
    member.accepted_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(member)
    return member


@router.delete("/invitations/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def decline_apiary_invitation(
    member_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    member = db.query(ApiaryMember).filter(
        ApiaryMember.id == member_id,
        ApiaryMember.user_id == current_user.id,
        ApiaryMember.accepted_at.is_(None),
    ).first()
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found")
    db.delete(member)
    db.commit()


@router.get("/{apiary_id}", response_model=ApiaryResponse)
def get_apiary(
    apiary_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_apiary = apiary_crud.get_apiary(db, apiary_id=apiary_id, owner_id=current_user.id)
    if not db_apiary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Apiary not found")
    data = ApiaryResponse.model_validate(db_apiary)
    data.hive_count = len(db_apiary.hives)
    return data


@router.put("/{apiary_id}", response_model=ApiaryResponse)
def update_apiary(
    apiary_id: int,
    apiary_update: ApiaryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_apiary = apiary_crud.update_apiary(
        db, apiary_id=apiary_id, owner_id=current_user.id, apiary_update=apiary_update
    )
    if not db_apiary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Apiary not found")
    data = ApiaryResponse.model_validate(db_apiary)
    data.hive_count = len(db_apiary.hives)
    return data


@router.delete("/{apiary_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_apiary(
    apiary_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    success = apiary_crud.delete_apiary(db, apiary_id=apiary_id, owner_id=current_user.id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Apiary not found")


@router.get("/{apiary_id}/members", response_model=list[ApiaryMemberResponse])
def list_apiary_members(
    apiary_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if not apiary_crud.get_apiary(db, apiary_id=apiary_id, owner_id=current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Apiary not found")
    return db.query(ApiaryMember).filter(ApiaryMember.apiary_id == apiary_id).all()


@router.post("/{apiary_id}/members", response_model=ApiaryMemberResponse, status_code=status.HTTP_201_CREATED)
def add_apiary_member(
    apiary_id: int,
    payload: ApiaryMemberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if not user_can_admin_apiary(db, apiary_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Apiary not found")
    user = user_crud.get_user_by_username(db, payload.username_or_email) or user_crud.get_user_by_email(db, payload.username_or_email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Users cannot invite themselves")
    if payload.role == ApiaryMemberRole.owner:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Owner role cannot be assigned")
    existing = db.query(ApiaryMember).filter(ApiaryMember.apiary_id == apiary_id, ApiaryMember.user_id == user.id).first()
    if existing:
        existing.role = payload.role
        if existing.accepted_at is None:
            existing.invited_by_user_id = current_user.id
        db.commit()
        db.refresh(existing)
        return existing
    member = ApiaryMember(
        apiary_id=apiary_id,
        user_id=user.id,
        role=payload.role,
        invited_by_user_id=current_user.id,
    )
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


@router.put("/{apiary_id}/members/{member_id}", response_model=ApiaryMemberResponse)
def update_apiary_member(
    apiary_id: int,
    member_id: int,
    payload: ApiaryMemberUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if not user_can_admin_apiary(db, apiary_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Apiary not found")
    member = db.query(ApiaryMember).filter(ApiaryMember.id == member_id, ApiaryMember.apiary_id == apiary_id).first()
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    if member.role == ApiaryMemberRole.owner or payload.role == ApiaryMemberRole.owner:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Owner role cannot be changed")
    member.role = payload.role
    db.commit()
    db.refresh(member)
    return member


@router.delete("/{apiary_id}/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_apiary_member(
    apiary_id: int,
    member_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if not user_can_admin_apiary(db, apiary_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Apiary not found")
    member = db.query(ApiaryMember).filter(ApiaryMember.id == member_id, ApiaryMember.apiary_id == apiary_id).first()
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    if member.role == ApiaryMemberRole.owner:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Apiary owner cannot be removed")
    db.delete(member)
    db.commit()


@router.post("/{apiary_id}/batch-actions/{action_type}")
def create_batch_action(
    apiary_id: int,
    action_type: str,
    payload: BatchActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if not user_can_write_apiary(db, apiary_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Apiary not found")
    db_apiary = apiary_crud.get_apiary(db, apiary_id=apiary_id, owner_id=current_user.id)
    if not db_apiary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Apiary not found")
    hives_by_id = {hive.id: hive for hive in db_apiary.hives}
    missing = [hive_id for hive_id in payload.hive_ids if hive_id not in hives_by_id]
    if missing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Hives not found in apiary: {missing}")

    created = []
    for hive_id in payload.hive_ids:
        if action_type == "inspection":
            created.append(inspection_crud.create_inspection(db, InspectionCreate(
                date=payload.date,
                queen_seen=payload.queen_seen,
                brood_strength=payload.brood_strength,
                varroa_count=payload.varroa_count,
                food_stores=payload.food_stores,
                notes=payload.notes,
            ), hive_id=hive_id, performed_by_user_id=current_user.id))
        elif action_type == "treatment":
            created_item = treatment_crud.create_treatment(db, TreatmentCreate(
                hive_id=hive_id,
                started_at=payload.date,
                product=payload.product or "Varroabehandlung",
                method=payload.method,
                dosage=payload.dosage,
                reason=payload.notes,
                notes=payload.notes,
            ), owner_id=db_apiary.owner_id, performed_by_user_id=current_user.id)
            if created_item:
                created.append(created_item)
        elif action_type == "feeding":
            created_item = feeding_crud.create_feeding(db, FeedingCreate(
                apiary_id=apiary_id,
                hive_id=hive_id,
                date=payload.date,
                feed_type=payload.feed_type or "Futter",
                amount_kg_or_l=payload.amount_kg_or_l or 0.1,
                notes=payload.notes,
            ), owner_id=db_apiary.owner_id, performed_by_user_id=current_user.id)
            if created_item:
                created.append(created_item)
        elif action_type == "harvest":
            created_item = harvest_crud.create_harvest(db, HarvestCreate(
                apiary_id=apiary_id,
                hive_id=hive_id,
                harvest_date=payload.date,
                crop_type=payload.crop_type,
                amount_kg=payload.amount_kg or 0,
                batch_code=payload.batch_code,
                notes=payload.notes,
            ), owner_id=db_apiary.owner_id, performed_by_user_id=current_user.id)
            if created_item:
                created.append(created_item)
        elif action_type == "move":
            if not payload.target_apiary_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="target_apiary_id required")
            moved = move_hive(db, hive_id, current_user.id, payload.target_apiary_id, payload.date, payload.notes)
            if moved:
                created.append(moved)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported batch action")
    return {"action_type": action_type, "created": len(created), "hive_ids": payload.hive_ids}


@router.get("/{apiary_id}/varroa-weather", response_model=list[VarroaWeatherWindowResponse])
def list_varroa_weather(
    apiary_id: int,
    treatment_type: VarroaTreatmentType = VarroaTreatmentType.formic_acid_short,
    start_date: date | None = None,
    days: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_apiary = apiary_crud.get_apiary(db, apiary_id=apiary_id, owner_id=current_user.id)
    if not db_apiary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Apiary not found")
    windows = get_varroa_weather_window(
        db,
        apiary_id=apiary_id,
        owner_id=db_apiary.owner_id,
        treatment_type=treatment_type,
        start_date=start_date or date.today(),
        days=days,
    )
    if not windows:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Apiary not found")
    return windows


@router.post("/{apiary_id}/varroa-weather/refresh", response_model=list[VarroaWeatherWindowResponse])
def refresh_varroa_weather(
    apiary_id: int,
    days: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if not user_can_write_apiary(db, apiary_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Apiary not found")
    db_apiary = apiary_crud.get_apiary(db, apiary_id=apiary_id, owner_id=current_user.id)
    if not db_apiary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Apiary not found")
    windows = refresh_varroa_weather_windows(
        db,
        apiary_id=apiary_id,
        owner_id=db_apiary.owner_id,
        days=days,
    )
    if not windows:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Apiary not found")
    return windows
