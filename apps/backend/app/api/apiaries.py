from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.api.dependencies import get_current_active_user
from app.crud import feeding as feeding_crud
from app.models.user import User
from app.models.varroa_weather import VarroaTreatmentType
from app.schemas.feeding import FeedingCreate
from app.schemas.harvest import HarvestCreate
from app.schemas.inspection import InspectionCreate
from app.schemas.apiary import ApiaryCreate, ApiaryUpdate, ApiaryResponse
from app.schemas.treatment import TreatmentCreate
from app.schemas.varroa_weather import VarroaWeatherWindowResponse
from app.crud import apiary as apiary_crud, harvest as harvest_crud, inspection as inspection_crud, treatment as treatment_crud
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


@router.post("/{apiary_id}/batch-actions/{action_type}")
def create_batch_action(
    apiary_id: int,
    action_type: str,
    payload: BatchActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_apiary = apiary_crud.get_apiary(db, apiary_id=apiary_id, owner_id=current_user.id)
    if not db_apiary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Apiary not found")
    hives_by_id = {hive.id: hive for hive in db_apiary.hives if hive.owner_id == current_user.id}
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
            ), hive_id=hive_id))
        elif action_type == "treatment":
            created_item = treatment_crud.create_treatment(db, TreatmentCreate(
                hive_id=hive_id,
                started_at=payload.date,
                product=payload.product or "Varroabehandlung",
                method=payload.method,
                dosage=payload.dosage,
                reason=payload.notes,
                notes=payload.notes,
            ), owner_id=current_user.id)
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
            ), owner_id=current_user.id)
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
            ), owner_id=current_user.id)
            if created_item:
                created.append(created_item)
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
    windows = get_varroa_weather_window(
        db,
        apiary_id=apiary_id,
        owner_id=current_user.id,
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
    windows = refresh_varroa_weather_windows(
        db,
        apiary_id=apiary_id,
        owner_id=current_user.id,
        days=days,
    )
    if not windows:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Apiary not found")
    return windows
