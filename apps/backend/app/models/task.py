import enum

from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class TaskPriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"


class TaskStatus(str, enum.Enum):
    open = "open"
    done = "done"
    cancelled = "cancelled"


class TaskSource(str, enum.Enum):
    manual = "manual"
    inspection = "inspection"
    system = "system"
    breeding = "breeding"


class TaskKind(str, enum.Enum):
    todo = "todo"
    appointment = "appointment"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    hive_id = Column(Integer, ForeignKey("hives.id"), nullable=True)
    apiary_id = Column(Integer, ForeignKey("apiaries.id"), nullable=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    due_date = Column(Date, nullable=True)
    start_at = Column(DateTime(timezone=True), nullable=True)
    end_at = Column(DateTime(timezone=True), nullable=True)
    kind = Column(Enum(TaskKind), default=TaskKind.todo, nullable=False)
    priority = Column(Enum(TaskPriority), default=TaskPriority.medium, nullable=False)
    status = Column(Enum(TaskStatus), default=TaskStatus.open, nullable=False)
    source = Column(Enum(TaskSource), default=TaskSource.manual, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    owner = relationship("User", back_populates="tasks")
    hive = relationship("Hive", back_populates="tasks")
    apiary = relationship("Apiary", back_populates="tasks")
