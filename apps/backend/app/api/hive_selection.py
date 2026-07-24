from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user
from app.crud import hive_selection as hive_selection_crud
from app.db.database import get_db
from app.models.user import User
from app.schemas.hive_selection import (
    HiveSelectionBatchTaskRequest,
    HiveSelectionBatchTaskResponse,
    HiveSelectionCandidate,
    HiveSelectionFilterRequest,
)

router = APIRouter()


@router.post("/filter", response_model=list[HiveSelectionCandidate])
def filter_hives(
    payload: HiveSelectionFilterRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return hive_selection_crud.filter_hives(
        db,
        owner_id=current_user.id,
        criteria_filters=payload.criteria,
        tags=payload.tags,
        match_all_tags=payload.match_all_tags,
    )


@router.post("/batch-tasks", response_model=HiveSelectionBatchTaskResponse, status_code=status.HTTP_201_CREATED)
def batch_create_tasks(
    payload: HiveSelectionBatchTaskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    created = hive_selection_crud.batch_create_tasks(db, owner_id=current_user.id, payload=payload)
    if not created:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="One or more hives not found or not writable")
    return {"created_task_ids": [task.id for task in created]}
