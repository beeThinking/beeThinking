from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.weight_reading import WeightReading
from app.schemas.weight_reading import WeightReadingCreate


def get_readings(db: Session, hive_id: int) -> list[WeightReading]:
    return (
        db.query(WeightReading)
        .filter(WeightReading.hive_id == hive_id)
        .order_by(WeightReading.timestamp.asc())
        .all()
    )


def create_reading(db: Session, hive_id: int, payload: WeightReadingCreate) -> WeightReading:
    """Stockwaage (#46) — basic CRUD even though nothing writes to it yet until a
    future vendor-integration ticket provides an ingestion mechanism."""
    reading = WeightReading(
        hive_id=hive_id,
        timestamp=payload.timestamp or datetime.now(timezone.utc),
        weight_kg=payload.weight_kg,
    )
    db.add(reading)
    db.commit()
    db.refresh(reading)
    return reading


def delete_reading(db: Session, hive_id: int, reading_id: int) -> bool:
    reading = db.query(WeightReading).filter(
        WeightReading.id == reading_id, WeightReading.hive_id == hive_id
    ).first()
    if not reading:
        return False
    db.delete(reading)
    db.commit()
    return True
