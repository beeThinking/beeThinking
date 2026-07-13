from datetime import date

from sqlalchemy.orm import Session

from app.models.harvest import Harvest
from app.models.hive import Hive, HiveStatus
from app.models.hive_event import HiveEvent
from app.models.inspection import Inspection
from app.models.photo import Photo
from app.models.task import Task, TaskStatus
from app.models.treatment import Treatment
from app.crud.ownership import user_can_write_apiary


def create_hive_event(
    db: Session,
    owner_id: int,
    hive_id: int,
    event_type: str,
    event_date: date,
    title: str,
    description: str | None = None,
    related_entity_type: str | None = None,
    related_entity_id: int | None = None,
    metadata_json: dict | None = None,
) -> HiveEvent:
    event = HiveEvent(
        user_id=owner_id,
        hive_id=hive_id,
        event_type=event_type,
        event_date=event_date,
        title=title,
        description=description,
        related_entity_type=related_entity_type,
        related_entity_id=related_entity_id,
        metadata_json=metadata_json,
        created_by=owner_id,
    )
    db.add(event)
    return event


def archive_hive(db: Session, hive_id: int, owner_id: int, reason: str, event_date: date, note: str | None = None):
    hive = _get_writable_hive(db, hive_id, owner_id)
    if not hive:
        return None
    hive.status = HiveStatus.archived
    hive.is_active = False
    hive.archived_at = event_date
    create_hive_event(db, owner_id, hive_id, "archived", event_date, "Volk archiviert", note, metadata_json={"reason": reason})
    _close_open_tasks(db, hive_id)
    db.commit()
    db.refresh(hive)
    return hive


def dissolve_hive(db: Session, hive_id: int, owner_id: int, reason: str, event_date: date, note: str | None = None):
    hive = _get_writable_hive(db, hive_id, owner_id)
    if not hive:
        return None
    status_map = {
        "merged": HiveStatus.merged,
        "sold": HiveStatus.sold,
        "dead": HiveStatus.dead,
        "lost": HiveStatus.lost,
    }
    hive.status = status_map.get(reason, HiveStatus.dissolved)
    hive.is_active = False
    hive.archived_at = event_date
    create_hive_event(db, owner_id, hive_id, "dissolved", event_date, "Volk aufgelöst", note, metadata_json={"reason": reason})
    _close_open_tasks(db, hive_id)
    db.commit()
    db.refresh(hive)
    return hive


def merge_hives(db: Session, source_hive_id: int, target_hive_id: int, owner_id: int, event_date: date, note: str | None = None):
    source = _get_writable_hive(db, source_hive_id, owner_id)
    target = _get_writable_hive(db, target_hive_id, owner_id)
    if not source or not target or source.id == target.id:
        return None
    source.status = HiveStatus.merged
    source.is_active = False
    source.archived_at = event_date
    source.merged_into_hive_id = target.id
    create_hive_event(
        db,
        owner_id,
        source.id,
        "merged",
        event_date,
        "Volk vereinigt",
        note,
        related_entity_type="hive",
        related_entity_id=target.id,
    )
    create_hive_event(
        db,
        owner_id,
        target.id,
        "merge_received",
        event_date,
        f"Volk {source.name} wurde vereinigt",
        note,
        related_entity_type="hive",
        related_entity_id=source.id,
    )
    _close_open_tasks(db, source.id)
    db.commit()
    db.refresh(source)
    return source


def can_hard_delete_hive(db: Session, hive_id: int, owner_id: int) -> bool:
    hive = _get_hive(db, hive_id)
    if not hive:
        return False
    if hive.status == HiveStatus.created_by_mistake:
        return True
    dependency_count = (
        db.query(Inspection).filter(Inspection.hive_id == hive_id).count()
        + db.query(Treatment).filter(Treatment.hive_id == hive_id).count()
        + db.query(Harvest).filter(Harvest.hive_id == hive_id).count()
        + db.query(Photo).filter(Photo.hive_id == hive_id).count()
    )
    return dependency_count == 0


def get_hive_timeline(db: Session, hive_id: int, owner_id: int) -> list[HiveEvent]:
    return (
        db.query(HiveEvent)
        .filter(HiveEvent.hive_id == hive_id)
        .order_by(HiveEvent.event_date.desc(), HiveEvent.created_at.desc())
        .all()
    )


def _get_hive(db: Session, hive_id: int):
    return db.query(Hive).filter(Hive.id == hive_id).first()


def _get_writable_hive(db: Session, hive_id: int, user_id: int):
    hive = _get_hive(db, hive_id)
    if not hive or not user_can_write_apiary(db, hive.apiary_id, user_id):
        return None
    return hive


def _close_open_tasks(db: Session, hive_id: int) -> None:
    db.query(Task).filter(Task.hive_id == hive_id, Task.status == TaskStatus.open).update(
        {"status": TaskStatus.cancelled},
        synchronize_session=False,
    )
