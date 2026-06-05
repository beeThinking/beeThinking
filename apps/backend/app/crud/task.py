from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.crud.ownership import validate_optional_refs
from app.models.task import Task, TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate


def get_tasks(db: Session, owner_id: int, status: TaskStatus | None = None) -> list[Task]:
    query = db.query(Task).filter(Task.owner_id == owner_id)
    if status is not None:
        query = query.filter(Task.status == status)
    return query.order_by(Task.due_date.asc().nulls_last(), Task.created_at.desc()).all()


def get_task(db: Session, task_id: int, owner_id: int) -> Optional[Task]:
    return db.query(Task).filter(Task.id == task_id, Task.owner_id == owner_id).first()


def create_task(db: Session, task: TaskCreate, owner_id: int) -> Optional[Task]:
    data = task.model_dump()
    if not validate_optional_refs(db, owner_id, hive_id=data.get("hive_id"), apiary_id=data.get("apiary_id")):
        return None
    db_task = Task(**data, owner_id=owner_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def update_task(db: Session, task_id: int, owner_id: int, task_update: TaskUpdate) -> Optional[Task]:
    db_task = get_task(db, task_id, owner_id)
    if not db_task:
        return None
    data = task_update.model_dump(exclude_unset=True)
    if not validate_optional_refs(
        db,
        owner_id,
        hive_id=data.get("hive_id"),
        apiary_id=data.get("apiary_id"),
    ):
        return None
    for field, value in data.items():
        setattr(db_task, field, value)
    if data.get("status") == TaskStatus.done and db_task.completed_at is None:
        db_task.completed_at = datetime.now(timezone.utc)
    if data.get("status") in {TaskStatus.open, TaskStatus.cancelled}:
        db_task.completed_at = None
    db.commit()
    db.refresh(db_task)
    return db_task


def complete_task(db: Session, task_id: int, owner_id: int) -> Optional[Task]:
    return update_task(db, task_id, owner_id, TaskUpdate(status=TaskStatus.done))


def delete_task(db: Session, task_id: int, owner_id: int) -> bool:
    db_task = get_task(db, task_id, owner_id)
    if not db_task:
        return False
    db.delete(db_task)
    db.commit()
    return True
