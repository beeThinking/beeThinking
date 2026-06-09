from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.task import TaskKind, TaskPriority, TaskSource, TaskStatus


class TaskBase(BaseModel):
    hive_id: Optional[int] = None
    apiary_id: Optional[int] = None
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    due_date: Optional[date] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    kind: TaskKind = TaskKind.todo
    priority: TaskPriority = TaskPriority.medium
    status: TaskStatus = TaskStatus.open
    source: TaskSource = TaskSource.manual


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    hive_id: Optional[int] = None
    apiary_id: Optional[int] = None
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    due_date: Optional[date] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    kind: Optional[TaskKind] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None
    source: Optional[TaskSource] = None


class TaskResponse(TaskBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
