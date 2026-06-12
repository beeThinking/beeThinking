import json
from datetime import date

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.cashbook import CashbookDirection, CashbookEntry
from app.models.office import OfficeDocument, OfficeDocumentType, OfficePartner
from app.schemas.office import OfficeDocumentCreate, OfficeDocumentUpdate, OfficePartnerCreate, OfficePartnerUpdate


def list_partners(db: Session, owner_id: int, partner_type: str | None = None) -> list[OfficePartner]:
    query = db.query(OfficePartner).filter(OfficePartner.owner_id == owner_id)
    if partner_type:
        query = query.filter(OfficePartner.partner_type == partner_type)
    return query.order_by(OfficePartner.name).all()


def get_partner(db: Session, owner_id: int, partner_id: int) -> OfficePartner | None:
    return db.query(OfficePartner).filter(OfficePartner.id == partner_id, OfficePartner.owner_id == owner_id).first()


def create_partner(db: Session, owner_id: int, partner: OfficePartnerCreate) -> OfficePartner:
    db_partner = OfficePartner(**partner.model_dump(), owner_id=owner_id)
    db.add(db_partner)
    db.commit()
    db.refresh(db_partner)
    return db_partner


def update_partner(db: Session, owner_id: int, partner_id: int, update: OfficePartnerUpdate) -> OfficePartner | None:
    db_partner = get_partner(db, owner_id, partner_id)
    if not db_partner:
        return None
    for field, value in update.model_dump(exclude_unset=True).items():
        setattr(db_partner, field, value)
    db.commit()
    db.refresh(db_partner)
    return db_partner


def delete_partner(db: Session, owner_id: int, partner_id: int) -> bool:
    db_partner = get_partner(db, owner_id, partner_id)
    if not db_partner:
        return False
    db.delete(db_partner)
    db.commit()
    return True


def list_documents(db: Session, owner_id: int, document_type: str | None = None) -> list[OfficeDocument]:
    query = db.query(OfficeDocument).filter(OfficeDocument.owner_id == owner_id)
    if document_type:
        query = query.filter(OfficeDocument.document_type == document_type)
    return query.order_by(OfficeDocument.document_date.desc(), OfficeDocument.id.desc()).all()


def get_document(db: Session, owner_id: int, document_id: int) -> OfficeDocument | None:
    return db.query(OfficeDocument).filter(OfficeDocument.id == document_id, OfficeDocument.owner_id == owner_id).first()


def create_document(db: Session, owner_id: int, document: OfficeDocumentCreate) -> OfficeDocument | None:
    if document.partner_id is not None and not get_partner(db, owner_id, document.partner_id):
        return None
    data = document.model_dump(exclude={"line_items"})
    db_document = OfficeDocument(**data, line_items_json=json.dumps([item.model_dump() for item in document.line_items]), owner_id=owner_id)
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document


def update_document(db: Session, owner_id: int, document_id: int, update: OfficeDocumentUpdate) -> OfficeDocument | None:
    db_document = get_document(db, owner_id, document_id)
    if not db_document:
        return None
    data = update.model_dump(exclude_unset=True, exclude={"line_items"})
    if "partner_id" in data and data["partner_id"] is not None and not get_partner(db, owner_id, data["partner_id"]):
        return None
    for field, value in data.items():
        setattr(db_document, field, value)
    if update.line_items is not None:
        db_document.line_items_json = json.dumps([item.model_dump() for item in update.line_items])
    db.commit()
    db.refresh(db_document)
    return db_document


def delete_document(db: Session, owner_id: int, document_id: int) -> bool:
    db_document = get_document(db, owner_id, document_id)
    if not db_document:
        return False
    db.delete(db_document)
    db.commit()
    return True


def dashboard(db: Session, owner_id: int, year: int, month: int | None = None) -> dict:
    from_date = date(year, month or 1, 1)
    to_date = date(year, month, _last_day(year, month)) if month else date(year, 12, 31)
    entries = (
        db.query(CashbookEntry)
        .filter(CashbookEntry.owner_id == owner_id, CashbookEntry.booking_date >= from_date, CashbookEntry.booking_date <= to_date)
        .all()
    )
    monthly_rows = (
        db.query(
            func.extract("month", CashbookEntry.booking_date),
            CashbookEntry.direction,
            func.sum(CashbookEntry.amount_gross),
        )
        .filter(CashbookEntry.owner_id == owner_id, CashbookEntry.booking_date >= date(year, 1, 1), CashbookEntry.booking_date <= date(year, 12, 31))
        .group_by(func.extract("month", CashbookEntry.booking_date), CashbookEntry.direction)
        .all()
    )
    category_rows = (
        db.query(CashbookEntry.category, CashbookEntry.direction, func.sum(CashbookEntry.amount_gross))
        .filter(CashbookEntry.owner_id == owner_id, CashbookEntry.booking_date >= from_date, CashbookEntry.booking_date <= to_date)
        .group_by(CashbookEntry.category, CashbookEntry.direction)
        .all()
    )
    return {
        "year": year,
        "month": month,
        "income": _sum(entries, CashbookDirection.income),
        "expenses": _sum(entries, CashbookDirection.expense),
        "balance": round(_sum(entries, CashbookDirection.income) - _sum(entries, CashbookDirection.expense), 2),
        "monthly": _monthly(monthly_rows),
        "categories": _categories(category_rows),
    }


def document_line_items(document: OfficeDocument) -> list[dict]:
    if not document.line_items_json:
        return []
    try:
        return json.loads(document.line_items_json)
    except json.JSONDecodeError:
        return []


def _sum(entries: list[CashbookEntry], direction: CashbookDirection) -> float:
    return round(sum(entry.amount_gross for entry in entries if entry.direction == direction), 2)


def _monthly(rows) -> list[dict]:
    data = {month: {"month": month, "income": 0.0, "expenses": 0.0, "balance": 0.0} for month in range(1, 13)}
    for month_raw, direction, amount in rows:
        month = int(month_raw)
        if direction == CashbookDirection.income:
            data[month]["income"] = float(amount or 0)
        else:
            data[month]["expenses"] = float(amount or 0)
        data[month]["balance"] = round(data[month]["income"] - data[month]["expenses"], 2)
    return list(data.values())


def _categories(rows) -> list[dict]:
    data: dict[str, dict] = {}
    for category, direction, amount in rows:
        item = data.setdefault(category, {"category": category, "income": 0.0, "expenses": 0.0})
        if direction == CashbookDirection.income:
            item["income"] = float(amount or 0)
        else:
            item["expenses"] = float(amount or 0)
    return sorted(data.values(), key=lambda item: item["category"])


def _last_day(year: int, month: int) -> int:
    if month == 12:
        return 31
    return (date(year, month + 1, 1) - date.resolution).day
