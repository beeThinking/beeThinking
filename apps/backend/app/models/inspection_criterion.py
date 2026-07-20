import enum

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.sql import func

from app.db.database import Base


class CriterionSection(str, enum.Enum):
    allg_befund = "allg_befund"
    verhalten = "verhalten"
    klima = "klima"
    verschiedenes = "verschiedenes"


class CriterionValueType(str, enum.Enum):
    stars = "stars"
    bool = "bool"
    number = "number"
    text = "text"
    select = "select"


class InspectionCriterion(Base):
    __tablename__ = "inspection_criteria"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    section = Column(String(50), nullable=False, default=CriterionSection.verschiedenes.value)
    value_type = Column(String(20), nullable=False, default=CriterionValueType.stars.value)
    options = Column(JSON, nullable=True)
    sort_order = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
