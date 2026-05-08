from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.api.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.apiary import ApiaryCreate, ApiaryUpdate, ApiaryResponse
from app.crud import apiary as apiary_crud

router = APIRouter()


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
