from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user
from app.db.database import get_db
from app.models.apiary import Apiary
from app.models.harvest import Harvest
from app.models.hive import Hive
from app.models.inspection import Inspection
from app.models.task import Task, TaskStatus
from app.models.treatment import Treatment
from app.models.user import User
from app.services.beekeeping_rules import calculate_hive_status, calculate_swarm_risk

router = APIRouter()


@router.get("/summary")
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    today = date.today()
    week_end = today + timedelta(days=7)
    latest_inspection = (
        db.query(Inspection)
        .join(Hive)
        .filter(Hive.owner_id == current_user.id)
        .order_by(Inspection.date.desc())
        .first()
    )
    hives = db.query(Hive).filter(Hive.owner_id == current_user.id).all()
    hive_statuses = []
    for hive in hives:
        hive_latest_inspection = (
            db.query(Inspection)
            .filter(Inspection.hive_id == hive.id)
            .order_by(Inspection.date.desc())
            .first()
        )
        hive_statuses.append({
            "hive_id": hive.id,
            "name": hive.name,
            "status": calculate_hive_status(hive, hive_latest_inspection),
            "swarm_risk": calculate_swarm_risk(hive, hive_latest_inspection, today),
            "latest_inspection_date": hive_latest_inspection.date if hive_latest_inspection else None,
        })

    return {
        "apiary_count": db.query(Apiary).filter(Apiary.owner_id == current_user.id).count(),
        "hive_count": db.query(Hive).filter(Hive.owner_id == current_user.id).count(),
        "open_task_count": db.query(Task)
        .filter(Task.owner_id == current_user.id, Task.status == TaskStatus.open)
        .count(),
        "overdue_task_count": db.query(Task)
        .filter(Task.owner_id == current_user.id, Task.status == TaskStatus.open, Task.due_date < today)
        .count(),
        "tasks_due_this_week": db.query(Task)
        .filter(
            Task.owner_id == current_user.id,
            Task.status == TaskStatus.open,
            Task.due_date >= today,
            Task.due_date <= week_end,
        )
        .count(),
        "treatment_count": db.query(Treatment).filter(Treatment.owner_id == current_user.id).count(),
        "harvest_kg_total": sum(
            value or 0 for (value,) in db.query(Harvest.amount_kg).filter(Harvest.owner_id == current_user.id).all()
        ),
        "latest_inspection_date": latest_inspection.date if latest_inspection else None,
        "hives": hive_statuses,
    }
