from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user
from app.crud import treatment as treatment_crud
from app.db.database import get_db
from app.models.user import User
from app.schemas.treatment import TreatmentCreate, TreatmentResponse, TreatmentUpdate

router = APIRouter()


@router.get("", response_model=list[TreatmentResponse])
def list_treatments(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return treatment_crud.get_treatments(db, owner_id=current_user.id)


@router.post("", response_model=TreatmentResponse, status_code=status.HTTP_201_CREATED)
def create_treatment(
    treatment: TreatmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_treatment = treatment_crud.create_treatment(
        db, treatment=treatment, owner_id=current_user.id, performed_by_user_id=current_user.id
    )
    if not db_treatment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hive not found")
    return db_treatment


@router.get("/journal/export")
def export_treatment_journal(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    treatments = treatment_crud.get_treatments(db, owner_id=current_user.id)
    return {
        "format": "journal-export-fields",
        "items": [
            {
                "id": treatment.id,
                "hive_id": treatment.hive_id,
                "started_at": treatment.started_at,
                "ended_at": treatment.ended_at,
                "product": treatment.product,
                "method": treatment.method,
                "dosage": treatment.dosage,
                "reason": treatment.reason,
                "weather_window_id": treatment.weather_window_id,
                "weather_rating": treatment.weather_rating,
                "weather_source": treatment.weather_source,
                "weather_fetched_at": treatment.weather_fetched_at,
                "notes": treatment.notes,
            }
            for treatment in treatments
        ],
    }


@router.get("/{treatment_id}", response_model=TreatmentResponse)
def get_treatment(
    treatment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_treatment = treatment_crud.get_treatment(db, treatment_id=treatment_id, owner_id=current_user.id)
    if not db_treatment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Treatment not found")
    return db_treatment


@router.put("/{treatment_id}", response_model=TreatmentResponse)
def update_treatment(
    treatment_id: int,
    treatment_update: TreatmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_treatment = treatment_crud.update_treatment(
        db, treatment_id=treatment_id, owner_id=current_user.id, treatment_update=treatment_update
    )
    if not db_treatment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Treatment not found")
    return db_treatment


@router.delete("/{treatment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_treatment(
    treatment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if not treatment_crud.delete_treatment(db, treatment_id=treatment_id, owner_id=current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Treatment not found")
