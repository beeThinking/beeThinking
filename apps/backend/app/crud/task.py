from datetime import date, datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.crud.ownership import get_apiary_member, user_can_write_apiary, validate_optional_refs
from app.models.apiary_member import ApiaryMember
from app.models.hive import Hive
from app.models.task import Task, TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate
from app.services.task_recurrence import expand_occurrences


def get_tasks(db: Session, owner_id: int, status: TaskStatus | None = None) -> list[Task]:
    visible_ids = (
        db.query(ApiaryMember.apiary_id)
        .filter(ApiaryMember.user_id == owner_id, ApiaryMember.accepted_at.is_not(None))
        .subquery()
    )
    query = (
        db.query(Task)
        .outerjoin(Hive, Hive.id == Task.hive_id)
        .filter(
            ((Task.apiary_id.is_(None)) & (Task.hive_id.is_(None)) & ((Task.owner_id == owner_id) | (Task.assignee_id == owner_id)))
            | (Task.apiary_id.in_(visible_ids))
            | ((Task.apiary_id.is_(None)) & (Hive.apiary_id.in_(visible_ids)))
        )
        .distinct()
    )
    if status is not None:
        query = query.filter(Task.status == status)
    return query.order_by(Task.due_date.asc().nulls_last(), Task.created_at.desc()).all()


def get_task(db: Session, task_id: int, owner_id: int) -> Optional[Task]:
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        return None
    apiary_id = _task_apiary_id(db, task)
    if apiary_id is None:
        if task.owner_id == owner_id or task.assignee_id == owner_id:
            return task
        return None
    if get_apiary_member(db, apiary_id, owner_id) is not None:
        return task
    return None


def create_task(db: Session, task: TaskCreate, owner_id: int) -> Optional[Task]:
    data = task.model_dump()
    if not validate_optional_refs(db, owner_id, hive_id=data.get("hive_id"), apiary_id=data.get("apiary_id")):
        return None
    if not _references_share_apiary(db, data.get("apiary_id"), data.get("hive_id")):
        return None
    assignee_id = data.get("assignee_id") or owner_id
    if not _can_assign_to(db, owner_id, assignee_id, data.get("apiary_id"), data.get("hive_id")):
        return None
    data["assignee_id"] = assignee_id
    db_task = Task(**data, owner_id=owner_id)
    if assignee_id and assignee_id != owner_id:
        db_task.delegated_at = datetime.now(timezone.utc)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def update_task(db: Session, task_id: int, owner_id: int, task_update: TaskUpdate) -> Optional[Task]:
    db_task = _get_task_for_write(db, task_id, owner_id)
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
    apiary_id = data.get("apiary_id", db_task.apiary_id)
    hive_id = data.get("hive_id", db_task.hive_id)
    if not _references_share_apiary(db, apiary_id, hive_id):
        return None
    assignee_id = data.get("assignee_id", db_task.assignee_id or db_task.owner_id)
    if not _can_assign_to(db, db_task.owner_id, assignee_id, apiary_id, hive_id):
        return None
    for field, value in data.items():
        setattr(db_task, field, value)
    if "assignee_id" in data and data["assignee_id"] and data["assignee_id"] != db_task.owner_id:
        db_task.delegated_at = datetime.now(timezone.utc)
        db_task.delegation_seen_at = None
    if data.get("status") == TaskStatus.done and db_task.completed_at is None:
        db_task.completed_at = datetime.now(timezone.utc)
    if data.get("status") in {TaskStatus.open, TaskStatus.cancelled}:
        db_task.completed_at = None
    db.commit()
    db.refresh(db_task)
    return db_task


def complete_task(db: Session, task_id: int, owner_id: int) -> Optional[Task]:
    return update_task(db, task_id, owner_id, TaskUpdate(status=TaskStatus.done))


def _user_can_write_task(db: Session, task: Task, user_id: int) -> bool:
    apiary_id = _task_apiary_id(db, task)
    return task.owner_id == user_id if apiary_id is None else user_can_write_apiary(db, apiary_id, user_id)


def _get_task_for_write(db: Session, task_id: int, user_id: int) -> Task | None:
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        return None
    if not _user_can_write_task(db, task, user_id):
        raise PermissionError
    return task


def delegate_task(db: Session, task_id: int, owner_id: int, assignee_id: int) -> Optional[Task]:
    """Assign a task to another user (#38). Any apiary member with write access may delegate."""
    db_task = get_task(db, task_id, owner_id)
    if not db_task or not _user_can_write_task(db, db_task, owner_id):
        return None
    if not _can_assign_to(db, db_task.owner_id, assignee_id, db_task.apiary_id, db_task.hive_id):
        return None
    db_task.assignee_id = assignee_id
    db_task.delegated_at = datetime.now(timezone.utc)
    db_task.delegation_seen_at = None
    db.commit()
    db.refresh(db_task)
    return db_task


def _task_apiary_id(db: Session, task: Task) -> int | None:
    if task.apiary_id is not None:
        return task.apiary_id
    if task.hive_id is not None:
        hive = db.query(Hive.apiary_id).filter(Hive.id == task.hive_id).first()
        return hive.apiary_id if hive else None
    return None


def _can_assign_to(db: Session, task_owner_id: int, assignee_id: int, apiary_id: int | None, hive_id: int | None) -> bool:
    if not _references_share_apiary(db, apiary_id, hive_id):
        return False
    if assignee_id == task_owner_id:
        return True
    if apiary_id is None and hive_id is not None:
        hive = db.query(Hive.apiary_id).filter(Hive.id == hive_id).first()
        apiary_id = hive.apiary_id if hive else None
    return apiary_id is not None and get_apiary_member(db, apiary_id, assignee_id) is not None


def _references_share_apiary(db: Session, apiary_id: int | None, hive_id: int | None) -> bool:
    if apiary_id is None or hive_id is None:
        return True
    hive = db.query(Hive.apiary_id).filter(Hive.id == hive_id).first()
    return hive is not None and hive.apiary_id == apiary_id


def mark_delegation_seen(db: Session, task_id: int, owner_id: int) -> Optional[Task]:
    db_task = get_task(db, task_id, owner_id)
    if not db_task or db_task.assignee_id != owner_id:
        return None
    db_task.delegation_seen_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_task)
    return db_task


def get_task_occurrences(
    db: Session, owner_id: int, range_start: date, range_end: date, status: TaskStatus | None = None
) -> list[tuple[Task, date]]:
    """Expand recurring tasks (#38) into concrete occurrence dates within a range."""
    tasks = get_tasks(db, owner_id, status=status)
    results: list[tuple[Task, date]] = []
    for task in tasks:
        for occurrence_date in expand_occurrences(task, range_start, range_end):
            results.append((task, occurrence_date))
    results.sort(key=lambda pair: pair[1])
    return results


def delete_task(db: Session, task_id: int, owner_id: int) -> bool:
    db_task = _get_task_for_write(db, task_id, owner_id)
    if not db_task:
        return False
    db.delete(db_task)
    db.commit()
    return True
