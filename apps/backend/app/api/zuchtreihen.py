from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user
from app.crud import breeding_step as breeding_step_crud
from app.crud import zuchtreihe as zuchtreihe_crud
from app.db.database import get_db
from app.models.user import User
from app.schemas.zuchtreihe import (
    BreedingStepCreate,
    BreedingStepResponse,
    BreedingStepsGenerateRequest,
    BreedingStepUpdate,
    ZuchtreiheCreate,
    ZuchtreiheResponse,
    ZuchtreiheUpdate,
)

router = APIRouter()


def _zuchtreihe_response(zuchtreihe) -> dict:
    data = ZuchtreiheResponse.model_validate(zuchtreihe).model_dump()
    data.update(zuchtreihe_crud.attach_success_rates(zuchtreihe))
    return data


@router.get("", response_model=list[ZuchtreiheResponse])
def list_zuchtreihen(
    apiary_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return [
        _zuchtreihe_response(zuchtreihe)
        for zuchtreihe in zuchtreihe_crud.get_zuchtreihen(db, owner_id=current_user.id, apiary_id=apiary_id)
    ]


@router.post("", response_model=ZuchtreiheResponse, status_code=status.HTTP_201_CREATED)
def create_zuchtreihe(
    zuchtreihe: ZuchtreiheCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_zuchtreihe = zuchtreihe_crud.create_zuchtreihe(db, zuchtreihe=zuchtreihe, owner_id=current_user.id)
    if not db_zuchtreihe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Apiary or Herkunftsvolk not found")
    return _zuchtreihe_response(db_zuchtreihe)


@router.get("/{zuchtreihe_id}", response_model=ZuchtreiheResponse)
def get_zuchtreihe(
    zuchtreihe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_zuchtreihe = zuchtreihe_crud.get_zuchtreihe(db, zuchtreihe_id=zuchtreihe_id, owner_id=current_user.id)
    if not db_zuchtreihe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zuchtreihe not found")
    return _zuchtreihe_response(db_zuchtreihe)


@router.put("/{zuchtreihe_id}", response_model=ZuchtreiheResponse)
def update_zuchtreihe(
    zuchtreihe_id: int,
    zuchtreihe_update: ZuchtreiheUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_zuchtreihe = zuchtreihe_crud.update_zuchtreihe(
        db, zuchtreihe_id=zuchtreihe_id, owner_id=current_user.id, zuchtreihe_update=zuchtreihe_update
    )
    if not db_zuchtreihe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zuchtreihe not found")
    return _zuchtreihe_response(db_zuchtreihe)


@router.delete("/{zuchtreihe_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_zuchtreihe(
    zuchtreihe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if not zuchtreihe_crud.delete_zuchtreihe(db, zuchtreihe_id=zuchtreihe_id, owner_id=current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zuchtreihe not found")


@router.get("/{zuchtreihe_id}/steps", response_model=list[BreedingStepResponse])
def list_steps(
    zuchtreihe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_zuchtreihe = zuchtreihe_crud.get_zuchtreihe(db, zuchtreihe_id=zuchtreihe_id, owner_id=current_user.id)
    if not db_zuchtreihe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zuchtreihe not found")
    return breeding_step_crud.get_steps(db, zuchtreihe_id=zuchtreihe_id)


@router.post("/{zuchtreihe_id}/steps/generate", response_model=list[BreedingStepResponse], status_code=status.HTTP_201_CREATED)
def generate_steps(
    zuchtreihe_id: int,
    payload: BreedingStepsGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_zuchtreihe = zuchtreihe_crud.get_zuchtreihe(db, zuchtreihe_id=zuchtreihe_id, owner_id=current_user.id)
    if not db_zuchtreihe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zuchtreihe not found")
    if breeding_step_crud.get_steps(db, zuchtreihe_id=zuchtreihe_id):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Breeding steps already exist for this Zuchtreihe")
    return breeding_step_crud.generate_steps_from_umlarven(
        db, zuchtreihe=db_zuchtreihe, owner_id=current_user.id, umlarven_date=payload.umlarven_date
    )


@router.post("/{zuchtreihe_id}/steps", response_model=BreedingStepResponse, status_code=status.HTTP_201_CREATED)
def create_step(
    zuchtreihe_id: int,
    step: BreedingStepCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_zuchtreihe = zuchtreihe_crud.get_zuchtreihe(db, zuchtreihe_id=zuchtreihe_id, owner_id=current_user.id)
    if not db_zuchtreihe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zuchtreihe not found")
    return breeding_step_crud.create_step(db, zuchtreihe=db_zuchtreihe, owner_id=current_user.id, step=step)


@router.put("/{zuchtreihe_id}/steps/{step_id}", response_model=BreedingStepResponse)
def update_step(
    zuchtreihe_id: int,
    step_id: int,
    step_update: BreedingStepUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_zuchtreihe = zuchtreihe_crud.get_zuchtreihe(db, zuchtreihe_id=zuchtreihe_id, owner_id=current_user.id)
    if not db_zuchtreihe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zuchtreihe not found")
    db_step = breeding_step_crud.get_step(db, step_id=step_id, zuchtreihe_id=zuchtreihe_id)
    if not db_step:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Breeding step not found")
    return breeding_step_crud.update_step(
        db, step=db_step, zuchtreihe=db_zuchtreihe, owner_id=current_user.id, step_update=step_update
    )


@router.delete("/{zuchtreihe_id}/steps/{step_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_step(
    zuchtreihe_id: int,
    step_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_zuchtreihe = zuchtreihe_crud.get_zuchtreihe(db, zuchtreihe_id=zuchtreihe_id, owner_id=current_user.id)
    if not db_zuchtreihe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zuchtreihe not found")
    db_step = breeding_step_crud.get_step(db, step_id=step_id, zuchtreihe_id=zuchtreihe_id)
    if not db_step:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Breeding step not found")
    breeding_step_crud.delete_step(db, step=db_step)
