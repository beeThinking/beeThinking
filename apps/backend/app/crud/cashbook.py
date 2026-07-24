from datetime import date

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.crud.ownership import user_can_access_apiary, visible_apiary_ids_subquery
from app.crud.office import get_partner
from app.models.cashbook import CashbookDirection, CashbookEntry, CashbookReceipt, CashbookReceiptSuggestion
from app.schemas.cashbook import CashbookEntryCreate, CashbookEntryUpdate


def list_entries(db: Session, user_id: int, from_date: date | None = None, to_date: date | None = None) -> list[CashbookEntry]:
    visible_ids = visible_apiary_ids_subquery(db, user_id)
    query = db.query(CashbookEntry).filter(
        (CashbookEntry.owner_id == user_id) | (CashbookEntry.apiary_id.in_(visible_ids))
    )
    if from_date:
        query = query.filter(CashbookEntry.booking_date >= from_date)
    if to_date:
        query = query.filter(CashbookEntry.booking_date <= to_date)
    return query.order_by(CashbookEntry.booking_date.desc(), CashbookEntry.id.desc()).all()


def create_entry(db: Session, entry: CashbookEntryCreate, user_id: int) -> CashbookEntry | None:
    if entry.apiary_id is not None and not user_can_access_apiary(db, entry.apiary_id, user_id):
        return None
    if entry.partner_id is not None and not get_partner(db, user_id, entry.partner_id):
        return None
    data = entry.model_dump()
    db_entry = CashbookEntry(**data, owner_id=user_id, performed_by_user_id=user_id)
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry


def get_entry(db: Session, entry_id: int, user_id: int) -> CashbookEntry | None:
    visible_ids = visible_apiary_ids_subquery(db, user_id)
    return db.query(CashbookEntry).filter(
        CashbookEntry.id == entry_id,
        (CashbookEntry.owner_id == user_id) | (CashbookEntry.apiary_id.in_(visible_ids)),
    ).first()


def update_entry(db: Session, entry_id: int, update: CashbookEntryUpdate, user_id: int) -> CashbookEntry | None:
    db_entry = get_entry(db, entry_id, user_id)
    if not db_entry:
        return None
    data = update.model_dump(exclude_unset=True)
    if "apiary_id" in data and data["apiary_id"] is not None and not user_can_access_apiary(db, data["apiary_id"], user_id):
        return None
    if "partner_id" in data and data["partner_id"] is not None and not get_partner(db, user_id, data["partner_id"]):
        return None
    for field, value in data.items():
        setattr(db_entry, field, value)
    db.commit()
    db.refresh(db_entry)
    return db_entry


def delete_entry(db: Session, entry_id: int, user_id: int) -> bool:
    db_entry = get_entry(db, entry_id, user_id)
    if not db_entry:
        return False
    db.delete(db_entry)
    db.commit()
    return True


def summary(db: Session, user_id: int, from_date: date | None = None, to_date: date | None = None) -> tuple[float, float]:
    visible_ids = visible_apiary_ids_subquery(db, user_id)
    query = db.query(CashbookEntry.direction, func.sum(CashbookEntry.amount_net)).filter(
        (CashbookEntry.owner_id == user_id) | (CashbookEntry.apiary_id.in_(visible_ids))
    )
    if from_date:
        query = query.filter(CashbookEntry.booking_date >= from_date)
    if to_date:
        query = query.filter(CashbookEntry.booking_date <= to_date)
    totals = {direction: amount or 0 for direction, amount in query.group_by(CashbookEntry.direction).all()}
    return float(totals.get(CashbookDirection.income, 0)), float(totals.get(CashbookDirection.expense, 0))


def create_receipt(
    db: Session,
    user_id: int,
    filename: str,
    content_type: str,
    size_bytes: int,
    file_object_key: str,
    ocr_text: str | None = None,
) -> CashbookReceipt:
    receipt = CashbookReceipt(
        owner_id=user_id,
        filename=filename,
        content_type=content_type,
        size_bytes=size_bytes,
        file_object_key=file_object_key,
        ocr_text=ocr_text,
        ocr_status="parsed" if ocr_text else "pending",
        ocr_provider="manual" if ocr_text else None,
    )
    db.add(receipt)
    db.flush()
    for field_name, suggested_value in _suggest_from_text(ocr_text or filename).items():
        db.add(CashbookReceiptSuggestion(
            receipt_id=receipt.id,
            field_name=field_name,
            suggested_value=suggested_value,
            confidence=0.45,
        ))
    db.commit()
    db.refresh(receipt)
    return receipt


def list_receipts(db: Session, user_id: int) -> list[CashbookReceipt]:
    return (
        db.query(CashbookReceipt)
        .filter(CashbookReceipt.owner_id == user_id)
        .order_by(CashbookReceipt.created_at.desc())
        .all()
    )


def get_receipt(db: Session, user_id: int, receipt_id: int) -> CashbookReceipt | None:
    return db.query(CashbookReceipt).filter(
        CashbookReceipt.id == receipt_id,
        CashbookReceipt.owner_id == user_id,
    ).first()


def _suggest_from_text(text: str) -> dict[str, str]:
    lowered = text.lower()
    suggestions: dict[str, str] = {}
    if any(word in lowered for word in ["glas", "etikett", "deckel"]):
        suggestions["category"] = "jars_labels"
        suggestions["direction"] = "expense"
    elif any(word in lowered for word in ["futter", "sirup", "zucker"]):
        suggestions["category"] = "feed"
        suggestions["direction"] = "expense"
    elif any(word in lowered for word in ["honig", "verkauf"]):
        suggestions["category"] = "honey_sales"
        suggestions["direction"] = "income"
    return suggestions
