from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.models.task import TaskKind, TaskPriority, TaskSource, TaskStatus
from app.services.task_recurrence import validate_recurrence_rule


class TaskBase(BaseModel):
    hive_id: Optional[int] = None
    apiary_id: Optional[int] = None
    assignee_id: Optional[int] = None
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    due_date: Optional[date] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    kind: TaskKind = TaskKind.todo
    priority: TaskPriority = TaskPriority.medium
    status: TaskStatus = TaskStatus.open
    source: TaskSource = TaskSource.manual
    recurrence_rule: Optional[str] = Field(None, max_length=500)

    @field_validator("recurrence_rule")
    @classmethod
    def validate_rule(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and not validate_recurrence_rule(value):
            raise ValueError("recurrence_rule must be a valid RFC5545 RRULE string")
        return value


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    hive_id: Optional[int] = None
    apiary_id: Optional[int] = None
    assignee_id: Optional[int] = None
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    due_date: Optional[date] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    kind: Optional[TaskKind] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None
    source: Optional[TaskSource] = None
    recurrence_rule: Optional[str] = Field(None, max_length=500)

    @field_validator("recurrence_rule")
    @classmethod
    def validate_rule(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and not validate_recurrence_rule(value):
            raise ValueError("recurrence_rule must be a valid RFC5545 RRULE string")
        return value


class TaskResponse(TaskBase):
    id: int
    owner_id: int
    delegated_at: Optional[datetime] = None
    delegation_seen_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TaskOccurrenceResponse(BaseModel):
    task: TaskResponse
    occurrence_date: date


class TaskDelegateRequest(BaseModel):
    assignee_id: int
