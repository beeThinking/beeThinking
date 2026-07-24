from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user
from app.crud import task as task_crud
from app.db.database import get_db
from app.models.task import TaskStatus
from app.models.user import User
from app.schemas.task import TaskCreate, TaskDelegateRequest, TaskOccurrenceResponse, TaskResponse, TaskUpdate

router = APIRouter()


@router.get("", response_model=list[TaskResponse])
def list_tasks(
    task_status: Optional[TaskStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return task_crud.get_tasks(db, owner_id=current_user.id, status=task_status)


@router.get("/occurrences", response_model=list[TaskOccurrenceResponse])
def list_task_occurrences(
    range_start: date | None = None,
    range_end: date | None = None,
    task_status: Optional[TaskStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Expand recurring tasks (#38) into concrete occurrence dates within a window."""
    start = range_start or date.today()
    end = range_end or (start + timedelta(days=90))
    pairs = task_crud.get_task_occurrences(db, owner_id=current_user.id, range_start=start, range_end=end, status=task_status)
    return [{"task": task, "occurrence_date": occurrence_date} for task, occurrence_date in pairs]


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_task = task_crud.create_task(db, task=task, owner_id=current_user.id)
    if not db_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Related resource not found")
    return db_task


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_task = task_crud.get_task(db, task_id=task_id, owner_id=current_user.id)
    if not db_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return db_task


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        db_task = task_crud.update_task(db, task_id=task_id, owner_id=current_user.id, task_update=task_update)
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to modify this task")
    if not db_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return db_task


@router.post("/{task_id}/complete", response_model=TaskResponse)
def complete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        db_task = task_crud.complete_task(db, task_id=task_id, owner_id=current_user.id)
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to modify this task")
    if not db_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return db_task


@router.post("/{task_id}/delegate", response_model=TaskResponse)
def delegate_task(
    task_id: int,
    payload: TaskDelegateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_task = task_crud.delegate_task(db, task_id=task_id, owner_id=current_user.id, assignee_id=payload.assignee_id)
    if not db_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return db_task


@router.post("/{task_id}/delegation-seen", response_model=TaskResponse)
def acknowledge_delegation(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_task = task_crud.mark_delegation_seen(db, task_id=task_id, owner_id=current_user.id)
    if not db_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return db_task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        deleted = task_crud.delete_task(db, task_id=task_id, owner_id=current_user.id)
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to modify this task")
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
