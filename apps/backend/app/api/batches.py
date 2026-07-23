from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user
from app.crud import batch as batch_crud
from app.db.database import get_db
from app.models.user import User
from app.schemas.batch import BatchCreate, BatchResponse, BatchUpdate, BottleRequest, BottleResponse

router = APIRouter()


@router.get("", response_model=list[BatchResponse])
def list_batches(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return batch_crud.get_batches(db, owner_id=current_user.id)


@router.post("", response_model=BatchResponse, status_code=status.HTTP_201_CREATED)
def create_batch(
    batch: BatchCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_batch = batch_crud.create_batch(db, batch=batch, owner_id=current_user.id)
    if not db_batch:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or already-batched harvest_ids")
    return db_batch


@router.get("/{batch_id}", response_model=BatchResponse)
def get_batch(
    batch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_batch = batch_crud.get_batch(db, batch_id=batch_id, owner_id=current_user.id)
    if not db_batch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Batch not found")
    return db_batch


@router.put("/{batch_id}", response_model=BatchResponse)
def update_batch(
    batch_id: int,
    batch_update: BatchUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_batch = batch_crud.update_batch(db, batch_id=batch_id, owner_id=current_user.id, batch_update=batch_update)
    if not db_batch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Batch not found")
    return db_batch


@router.delete("/{batch_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_batch(
    batch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if not batch_crud.delete_batch(db, batch_id=batch_id, owner_id=current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Batch not found")


@router.post("/{batch_id}/harvests/{harvest_id}", response_model=BatchResponse)
def attach_harvest(
    batch_id: int,
    harvest_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        db_batch = batch_crud.attach_harvest(db, batch_id=batch_id, owner_id=current_user.id, harvest_id=harvest_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    if not db_batch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Batch or harvest not found")
    return db_batch


@router.delete("/{batch_id}/harvests/{harvest_id}", response_model=BatchResponse)
def detach_harvest(
    batch_id: int,
    harvest_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_batch = batch_crud.detach_harvest(db, batch_id=batch_id, owner_id=current_user.id, harvest_id=harvest_id)
    if not db_batch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Batch or harvest not found")
    return db_batch


@router.post("/{batch_id}/bottle", response_model=BottleResponse)
def bottle_batch(
    batch_id: int,
    request: BottleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        result = batch_crud.bottle_batch(db, batch_id=batch_id, owner_id=current_user.id, request=request)
    except batch_crud.InsufficientBatchQuantityError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Batch or article not found")
    db_batch, inventory_items = result
    return BottleResponse(batch=db_batch, inventory_items=inventory_items)
