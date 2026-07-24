from datetime import date, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.models.breeding_step import BREEDING_STEP_DEFAULT_OFFSETS, BREEDING_STEP_ORDER, BreedingStep, BreedingStepName
from app.models.task import Task, TaskPriority, TaskSource
from app.models.zuchtreihe import Zuchtreihe
from app.schemas.zuchtreihe import BreedingStepCreate, BreedingStepUpdate
from app.schemas.task import TaskCreate
from app.crud import task as task_crud


STEP_TITLES: dict[BreedingStepName, str] = {
    BreedingStepName.pflegevolk_vorbereiten: "Pflegevolk vorbereiten",
    BreedingStepName.umlarven: "Umlarven",
    BreedingStepName.annahmekontrolle: "Annahmekontrolle",
    BreedingStepName.kaefigen_1: "Käfigen (1.)",
    BreedingStepName.kaefigen_2: "Käfigen (2.)",
    BreedingStepName.schlupf: "Schlupf",
    BreedingStepName.voelkchen_bilden: "Völkchen bilden",
    BreedingStepName.belegstelle: "Belegstelle",
    BreedingStepName.abholen: "Abholen",
}


def get_steps(db: Session, zuchtreihe_id: int) -> list[BreedingStep]:
    return (
        db.query(BreedingStep)
        .filter(BreedingStep.zuchtreihe_id == zuchtreihe_id)
        .order_by(BreedingStep.date.asc())
        .all()
    )


def get_step(db: Session, step_id: int, zuchtreihe_id: int) -> Optional[BreedingStep]:
    return (
        db.query(BreedingStep)
        .filter(BreedingStep.id == step_id, BreedingStep.zuchtreihe_id == zuchtreihe_id)
        .first()
    )


def _create_task_for_step(db: Session, zuchtreihe: Zuchtreihe, owner_id: int, name: BreedingStepName, step_date) -> Task | None:
    task_create = TaskCreate(
        hive_id=zuchtreihe.herkunftsvolk_id,
        apiary_id=zuchtreihe.apiary_id,
        title=f"Zuchtreihe {zuchtreihe.name}: {STEP_TITLES[name]}",
        description=f"Zuchtkalender-Schritt '{STEP_TITLES[name]}' für Zuchtreihe '{zuchtreihe.name}'.",
        due_date=step_date,
        priority=TaskPriority.medium,
        source=TaskSource.breeding,
    )
    return task_crud.create_task(db, task_create, owner_id=owner_id)


def generate_steps_from_umlarven(
    db: Session, zuchtreihe: Zuchtreihe, owner_id: int, umlarven_date: date
) -> list[BreedingStep]:
    """Create all 9 breeding steps with dates computed from the Umlarven date.

    Per #33's resolution: offsets are only applied at creation time. Editing a
    step's date later does not retroactively recalculate other steps.
    """
    created_steps: list[BreedingStep] = []
    for name in BREEDING_STEP_ORDER:
        offset = BREEDING_STEP_DEFAULT_OFFSETS[name]
        step_date = umlarven_date + timedelta(days=offset)
        db_step = BreedingStep(zuchtreihe_id=zuchtreihe.id, name=name.value, date=step_date)
        db.add(db_step)
        db.flush()
        task = _create_task_for_step(db, zuchtreihe, owner_id, name, step_date)
        if task:
            db_step.task_id = task.id
        created_steps.append(db_step)
    db.commit()
    for step in created_steps:
        db.refresh(step)
    return created_steps


def create_step(
    db: Session, zuchtreihe: Zuchtreihe, owner_id: int, step: BreedingStepCreate
) -> BreedingStep:
    db_step = BreedingStep(zuchtreihe_id=zuchtreihe.id, name=step.name.value, date=step.date, notes=step.notes)
    db.add(db_step)
    db.flush()
    task = _create_task_for_step(db, zuchtreihe, owner_id, step.name, step.date)
    if task:
        db_step.task_id = task.id
    db.commit()
    db.refresh(db_step)
    return db_step


def update_step(
    db: Session, step: BreedingStep, zuchtreihe: Zuchtreihe, owner_id: int, step_update: BreedingStepUpdate
) -> BreedingStep:
    data = step_update.model_dump(exclude_unset=True)
    if "name" in data and data["name"] is not None:
        data["name"] = data["name"].value if hasattr(data["name"], "value") else data["name"]
    for field, value in data.items():
        setattr(step, field, value)
    if step.task_id and ("date" in data or "name" in data):
        db_task = db.query(Task).filter(Task.id == step.task_id).first()
        if db_task:
            if "date" in data:
                db_task.due_date = step.date
            if "name" in data:
                db_task.title = f"Zuchtreihe {zuchtreihe.name}: {STEP_TITLES[BreedingStepName(step.name)]}"
    db.commit()
    db.refresh(step)
    return step


def delete_step(db: Session, step: BreedingStep) -> None:
    if step.task_id:
        db_task = db.query(Task).filter(Task.id == step.task_id).first()
        if db_task:
            db.delete(db_task)
    db.delete(step)
    db.commit()
