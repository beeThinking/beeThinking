from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.task import TaskKind, TaskPriority


class CriterionAverageFilter(BaseModel):
    criterion_id: int
    min_average: Optional[float] = None
    max_average: Optional[float] = None


class HiveSelectionFilterRequest(BaseModel):
    criteria: list[CriterionAverageFilter] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    match_all_tags: bool = False


class HiveSelectionCandidate(BaseModel):
    hive_id: int
    hive_name: str
    apiary_id: int
    tags: list[str] = Field(default_factory=list)
    criterion_averages: dict[int, float] = Field(default_factory=dict)
    inspection_count: int


class HiveSelectionBatchTaskRequest(BaseModel):
    hive_ids: list[int] = Field(..., min_length=1)
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    due_date: Optional[date] = None
    kind: TaskKind = TaskKind.todo
    priority: TaskPriority = TaskPriority.medium


class HiveSelectionBatchTaskResponse(BaseModel):
    created_task_ids: list[int]
