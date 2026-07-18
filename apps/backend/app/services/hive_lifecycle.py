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


def move_hive(db: Session, hive_id: int, owner_id: int, target_apiary_id: int, event_date: date, note: str | None = None):
    hive = _get_writable_hive(db, hive_id, owner_id)
    if not hive or not user_can_write_apiary(db, target_apiary_id, owner_id):
        return None
    if hive.apiary_id == target_apiary_id:
        return hive
    source_apiary = hive.apiary
    hive.apiary_id = target_apiary_id
    db.flush()
    db.refresh(hive)
    create_hive_event(
        db,
        owner_id,
        hive_id,
        "moved",
        event_date,
        f"Gewandert: {source_apiary.name or source_apiary.stock_number} → {hive.apiary.name or hive.apiary.stock_number}",
        note,
        related_entity_type="apiary",
        related_entity_id=target_apiary_id,
        metadata_json={"from_apiary_id": source_apiary.id, "to_apiary_id": target_apiary_id},
    )
    db.commit()
    db.refresh(hive)
    return hive


def copy_hive(
    db: Session,
    hive_id: int,
    owner_id: int,
    event_date: date,
    name: str | None = None,
    stock_number: str | None = None,
    note: str | None = None,
):
    source = _get_writable_hive(db, hive_id, owner_id)
    if not source:
        return None
    copy = Hive(
        name=name or f"{source.name} (Kopie)",
        stock_number=stock_number,
        location=source.location,
        type=source.type,
        colony_kind=source.colony_kind,
        established_at=event_date,
        tags=list(source.tags) if source.tags else None,
        notes=source.notes,
        owner_id=source.owner_id,
        apiary_id=source.apiary_id,
    )
    db.add(copy)
    db.flush()
    create_hive_event(
        db,
        owner_id,
        copy.id,
        "copied",
        event_date,
        f"Kopiert von {source.name}",
        note,
        related_entity_type="hive",
        related_entity_id=source.id,
    )
    db.commit()
    db.refresh(copy)
    return copy


def requeen_hive(
    db: Session,
    hive_id: int,
    owner_id: int,
    event_date: date,
    year: int,
    marking_color: str | None = None,
    name: str | None = None,
    origin: str | None = None,
    reason: str | None = None,
    note: str | None = None,
):
    from app.models.queen import Queen

    hive = _get_writable_hive(db, hive_id, owner_id)
    if not hive:
        return None
    db.query(Queen).filter(Queen.hive_id == hive_id, Queen.is_active.is_(True)).update(
        {"is_active": False},
        synchronize_session=False,
    )
    queen = Queen(
        owner_id=hive.owner_id,
        hive_id=hive_id,
        name=name,
        year=year,
        origin=origin,
        marking_color=marking_color,
        is_active=True,
    )
    db.add(queen)
    db.flush()
    create_hive_event(
        db,
        owner_id,
        hive_id,
        "requeened",
        event_date,
        f"Umgeweiselt: Königin {year}" + (f" ({marking_color})" if marking_color else ""),
        note,
        related_entity_type="queen",
        related_entity_id=queen.id,
        metadata_json={"reason": reason, "year": year, "marking_color": marking_color},
    )
    db.commit()
    db.refresh(queen)
    return queen


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
