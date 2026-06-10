from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user
from app.crud import harvest as harvest_crud
from app.db.database import get_db
from app.models.user import User
from app.schemas.harvest import HarvestCreate, HarvestResponse, HarvestUpdate

router = APIRouter()


@router.get("", response_model=list[HarvestResponse])
def list_harvests(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return harvest_crud.get_harvests(db, owner_id=current_user.id)


@router.post("", response_model=HarvestResponse, status_code=status.HTTP_201_CREATED)
def create_harvest(
    harvest: HarvestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_harvest = harvest_crud.create_harvest(
        db, harvest=harvest, owner_id=current_user.id, performed_by_user_id=current_user.id
    )
    if not db_harvest:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Related resource not found")
    return db_harvest


@router.get("/{harvest_id}", response_model=HarvestResponse)
def get_harvest(
    harvest_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_harvest = harvest_crud.get_harvest(db, harvest_id=harvest_id, owner_id=current_user.id)
    if not db_harvest:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Harvest not found")
    return db_harvest


@router.put("/{harvest_id}", response_model=HarvestResponse)
def update_harvest(
    harvest_id: int,
    harvest_update: HarvestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_harvest = harvest_crud.update_harvest(
        db, harvest_id=harvest_id, owner_id=current_user.id, harvest_update=harvest_update
    )
    if not db_harvest:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Harvest not found")
    return db_harvest


@router.delete("/{harvest_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_harvest(
    harvest_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if not harvest_crud.delete_harvest(db, harvest_id=harvest_id, owner_id=current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Harvest not found")
