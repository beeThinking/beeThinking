from datetime import date, timedelta

from app.models.hive import Hive
from app.models.inspection import HiveStrength, Inspection, SwarmCells
from app.models.task import TaskPriority, TaskSource
from app.schemas.task import TaskCreate


def calculate_hive_status(hive: Hive, latest_inspection: Inspection | None) -> str:
    if latest_inspection is None:
        return "needs_inspection"
    if latest_inspection.food_stores is not None and latest_inspection.food_stores <= 3:
        return "needs_attention"
    if latest_inspection.varroa_count is not None and latest_inspection.varroa_count >= 10:
        return "critical"
    if latest_inspection.swarm_cells == SwarmCells.queen_cells:
        return "swarm_risk"
    return hive.status.value


def calculate_swarm_risk(hive: Hive, latest_inspection: Inspection | None, today: date) -> str:
    if latest_inspection is None:
        return "unknown"
    if latest_inspection.swarm_cells == SwarmCells.queen_cells:
        return "high"
    if latest_inspection.swarm_cells == SwarmCells.play_cups and latest_inspection.strength == HiveStrength.strong:
        return "medium"
    if latest_inspection.date < today - timedelta(days=14):
        return "unknown"
    return "low"


def get_inspection_warnings(inspection: Inspection) -> list[str]:
    warnings = []
    if inspection.food_stores is not None and inspection.food_stores <= 3:
        warnings.append("Food stores are low")
    if inspection.varroa_count is not None and inspection.varroa_count >= 10:
        warnings.append("Varroa count is high")
    if not inspection.queen_seen and inspection.strength == HiveStrength.weak:
        warnings.append("Queen status should be checked")
    if inspection.swarm_cells == SwarmCells.queen_cells:
        warnings.append("Swarm risk is high")
    return warnings


def suggest_tasks_after_inspection(hive: Hive, inspection: Inspection) -> list[TaskCreate]:
    tasks = []
    due_today = date.today()
    if inspection.food_stores is not None and inspection.food_stores <= 3:
        tasks.append(TaskCreate(
            hive_id=hive.id,
            apiary_id=hive.apiary_id,
            title="Check food stores",
            description="Inspection reported low food stores.",
            due_date=due_today,
            priority=TaskPriority.high,
            source=TaskSource.inspection,
        ))
    if inspection.varroa_count is not None and inspection.varroa_count >= 10:
        tasks.append(TaskCreate(
            hive_id=hive.id,
            apiary_id=hive.apiary_id,
            title="Review varroa treatment",
            description="Inspection reported a high varroa count.",
            due_date=due_today,
            priority=TaskPriority.urgent,
            source=TaskSource.inspection,
        ))
    if not inspection.queen_seen and inspection.strength == HiveStrength.weak:
        tasks.append(TaskCreate(
            hive_id=hive.id,
            apiary_id=hive.apiary_id,
            title="Check queen status",
            description="Queen was not seen and colony strength is weak.",
            due_date=due_today,
            priority=TaskPriority.high,
            source=TaskSource.inspection,
        ))
    if inspection.swarm_cells == SwarmCells.queen_cells:
        tasks.append(TaskCreate(
            hive_id=hive.id,
            apiary_id=hive.apiary_id,
            title="Perform swarm control",
            description="Inspection found queen cells.",
            due_date=due_today,
            priority=TaskPriority.urgent,
            source=TaskSource.inspection,
        ))
    return tasks
