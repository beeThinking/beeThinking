from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models.apiary import Apiary
from app.models.apiary_member import ApiaryMember, ApiaryMemberRole
from app.models.beeintouch_import import BeeIntouchImportError, BeeIntouchImportRun
from app.models.cashbook import CashbookDirection, CashbookEntry
from app.models.feeding import Feeding
from app.models.hive import Hive
from app.models.office import OfficePartner, OfficePartnerType
from app.models.task import Task, TaskKind, TaskPriority, TaskSource, TaskStatus
from app.models.user import User


DEFAULT_SOURCE_DIR = Path(__file__).resolve().parents[2] / "import_sources" / "beeintouch"
SUPPORTED_FILES = {
    "Partnerliste_mit_qr.pdf": "partners",
    "Bestandsbuch.pdf": "stock",
    "Fuetterung.pdf": "feedings",
    "ToDos.pdf": "tasks",
    "kassenbuch.pdf": "cashbook",
}

GERMAN_MONTHS = {
    "januar": 1,
    "februar": 2,
    "maerz": 3,
    "märz": 3,
    "april": 4,
    "mai": 5,
    "juni": 6,
    "juli": 7,
    "august": 8,
    "september": 9,
    "oktober": 10,
    "november": 11,
    "dezember": 12,
}


@dataclass
class ExtractedPdf:
    text_pages: list[str]
    tables: list[tuple[int, list[list[str]]]]


@dataclass
class ImportContext:
    db: Session
    run: BeeIntouchImportRun
    owner: User
    source_name: str
    counters: Counter[str]


def main() -> None:
    parser = argparse.ArgumentParser(description="Import BeeIntouch PDF exports into BeeThinking.")
    parser.add_argument("--source-dir", default=str(DEFAULT_SOURCE_DIR))
    args = parser.parse_args()

    db = SessionLocal()
    try:
        result = import_beeintouch_pdfs(db, Path(args.source_dir))
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    finally:
        db.close()


def import_beeintouch_pdfs(db: Session, source_dir: Path = DEFAULT_SOURCE_DIR) -> dict[str, Any]:
    owner = _find_first_admin(db)
    if owner is None:
        return {"status": "skipped", "reason": "No active admin user found"}

    source_dir = Path(source_dir)
    results: list[dict[str, Any]] = []
    for source_name, import_kind in SUPPORTED_FILES.items():
        path = source_dir / source_name
        if not path.exists():
            results.append({"source": source_name, "status": "missing"})
            continue
        results.append(_import_one_pdf(db, owner, path, import_kind))
    return {"status": "done", "results": results}


def _import_one_pdf(db: Session, owner: User, path: Path, import_kind: str) -> dict[str, Any]:
    source_hash = _sha256(path)
    existing = (
        db.query(BeeIntouchImportRun)
        .filter(
            BeeIntouchImportRun.source_name == path.name,
            BeeIntouchImportRun.source_hash == source_hash,
        )
        .first()
    )
    if existing and existing.status in {"success", "partial"}:
        return {"source": path.name, "status": "skipped", "run_id": existing.id}

    if existing:
        run = existing
        db.query(BeeIntouchImportError).filter(BeeIntouchImportError.run_id == run.id).delete()
        run.owner_id = owner.id
        run.status = "pending"
        run.imported_count = 0
        run.error_count = 0
        run.summary = None
        run.error_text = None
        run.finished_at = None
        db.commit()
        db.refresh(run)
    else:
        run = BeeIntouchImportRun(
            owner_id=owner.id,
            source_name=path.name,
            source_hash=source_hash,
            status="pending",
            imported_count=0,
            error_count=0,
        )
        db.add(run)
        db.commit()
        db.refresh(run)

    context = ImportContext(db=db, run=run, owner=owner, source_name=path.name, counters=Counter())
    try:
        extracted = extract_pdf(path)
        if import_kind == "partners":
            _import_partners(context, extracted)
        elif import_kind == "stock":
            _import_stock(context, extracted)
        elif import_kind == "feedings":
            _import_feedings(context, extracted)
        elif import_kind == "tasks":
            _import_tasks(context, extracted)
        elif import_kind == "cashbook":
            _import_cashbook(context, extracted)
        else:
            _record_error(context, None, None, None, f"Unsupported import kind: {import_kind}", path.name)

        db.flush()
        imported_count = sum(context.counters.values())
        error_count = db.query(BeeIntouchImportError).filter(BeeIntouchImportError.run_id == run.id).count()
        run.imported_count = imported_count
        run.error_count = error_count
        run.status = "partial" if error_count else "success"
        run.summary = json.dumps(context.counters, ensure_ascii=False, sort_keys=True)
        run.finished_at = datetime.now(timezone.utc)
        db.commit()
        return {"source": path.name, "status": run.status, "run_id": run.id, "summary": dict(context.counters), "errors": error_count}
    except Exception as exc:  # keep deployment running, preserve reason in DB
        db.rollback()
        run = db.query(BeeIntouchImportRun).filter(BeeIntouchImportRun.id == run.id).first()
        if run:
            run.status = "failed"
            run.error_text = str(exc)
            run.finished_at = datetime.now(timezone.utc)
            db.commit()
        return {"source": path.name, "status": "failed", "error": str(exc)}


def extract_pdf(path: Path) -> ExtractedPdf:
    try:
        import pdfplumber
    except ImportError as exc:
        raise RuntimeError("Install pdfplumber to import BeeIntouch PDFs") from exc

    text_pages: list[str] = []
    tables: list[tuple[int, list[list[str]]]] = []
    with pdfplumber.open(path) as pdf:
        for page_index, page in enumerate(pdf.pages, start=1):
            text_pages.append(page.extract_text() or "")
            for table in page.extract_tables() or []:
                normalized = [[_clean_cell(cell) for cell in row] for row in table if any(_clean_cell(cell) for cell in row)]
                if normalized:
                    tables.append((page_index, normalized))
    return ExtractedPdf(text_pages=text_pages, tables=tables)


def _import_partners(context: ImportContext, extracted: ExtractedPdf) -> None:
    handled = False
    for page, row in _iter_table_dicts(extracted):
        name = _value(row, "name", "partner", "kunde", "lieferant", "firma")
        if not name:
            _record_error(context, page, None, "OfficePartner", "Missing partner name", _row_text(row))
            continue
        partner = OfficePartner(
            owner_id=context.owner.id,
            partner_type=_partner_type(row),
            name=name[:200],
            email=_value(row, "email", "e-mail"),
            phone=_value(row, "telefon", "phone", "tel", "mobil"),
            address=_join_values(row, "adresse", "anschrift", "straße", "strasse", "plz", "ort"),
            notes=_source_note(context.source_name),
            created_at=_now(),
        )
        context.db.add(partner)
        context.counters["partners"] += 1
        handled = True
    if not handled:
        _record_text_lines(context, extracted, "OfficePartner", "No partner table rows detected")


def _import_stock(context: ImportContext, extracted: ExtractedPdf) -> None:
    handled = False
    fallback_apiary: Apiary | None = None
    for page, row in _iter_table_dicts(extracted):
        apiary_name = _value(row, "stand", "bienenstand", "apiary", "standort")
        hive_name = _value(row, "volk", "bienenvolk", "hive", "name", "volk nr", "volknr")
        if not hive_name:
            _record_error(context, page, None, "Hive", "Missing hive name", _row_text(row))
            continue
        if apiary_name:
            apiary = _get_or_create_apiary(context.db, context.owner.id, apiary_name)
        else:
            if fallback_apiary is None:
                fallback_apiary = _get_or_create_import_apiary(context.db, context.owner.id)
            apiary = fallback_apiary
        hive = Hive(
            owner_id=context.owner.id,
            apiary_id=apiary.id,
            name=hive_name[:100],
            notes=_join_values(row, "notiz", "notizen", "bemerkung", "bemerkungen", "status") or _source_note(context.source_name),
            created_at=_now(),
        )
        context.db.add(hive)
        context.counters["hives"] += 1
        handled = True
    if not handled:
        _record_text_lines(context, extracted, "Hive", "No stock rows detected")


def _import_feedings(context: ImportContext, extracted: ExtractedPdf) -> None:
    handled = False
    fallback_apiary: Apiary | None = None
    for page, row in _iter_table_dicts(extracted):
        parsed_date = _parse_date(_value(row, "datum", "date", "tag"))
        amount = _parse_amount(_value(row, "menge", "amount", "kg", "liter", "l"))
        feed_type = _value(row, "futter", "feed", "futterart", "typ") or "BeeIntouch Futter"
        if parsed_date is None or amount is None:
            _record_error(context, page, None, "Feeding", "Missing date or amount", _row_text(row))
            continue
        if fallback_apiary is None:
            fallback_apiary = _get_or_create_import_apiary(context.db, context.owner.id)
        hive = _find_or_create_hive(context.db, context.owner.id, _value(row, "volk", "hive"), fallback_apiary)
        context.db.add(Feeding(
            owner_id=context.owner.id,
            performed_by_user_id=context.owner.id,
            apiary_id=fallback_apiary.id if hive is None else hive.apiary_id,
            hive_id=hive.id if hive else None,
            date=parsed_date,
            feed_type=feed_type[:120],
            amount_kg_or_l=amount,
            notes=_join_values(row, "notiz", "notizen", "bemerkung", "bemerkungen") or _source_note(context.source_name),
            created_at=_now(),
        ))
        context.counters["feedings"] += 1
        handled = True
    if not handled:
        _record_text_lines(context, extracted, "Feeding", "No feeding rows detected")


def _import_tasks(context: ImportContext, extracted: ExtractedPdf) -> None:
    handled = False
    for page, row in _iter_table_dicts(extracted):
        title = _value(row, "titel", "aufgabe", "todo", "beschreibung", "text")
        if not title:
            _record_error(context, page, None, "Task", "Missing task title", _row_text(row))
            continue
        context.db.add(Task(
            owner_id=context.owner.id,
            title=title[:200],
            description=_join_values(row, "notiz", "notizen", "bemerkung", "details") or _source_note(context.source_name),
            due_date=_parse_date(_value(row, "datum", "fällig", "faellig", "due", "termin")),
            kind=TaskKind.todo,
            priority=_task_priority(row),
            status=TaskStatus.done if "erledigt" in _row_text(row).lower() else TaskStatus.open,
            source=TaskSource.manual,
            created_at=_now(),
        ))
        context.counters["tasks"] += 1
        handled = True
    if not handled:
        for page_number, line in _iter_text_lines(extracted):
            parsed_date = _parse_date(line)
            title = _strip_date(line)
            if not title or len(title) < 3:
                continue
            context.db.add(Task(
                owner_id=context.owner.id,
                title=title[:200],
                description=_source_note(context.source_name),
                due_date=parsed_date,
                kind=TaskKind.todo,
                priority=TaskPriority.medium,
                status=TaskStatus.open,
                source=TaskSource.manual,
                created_at=_now(),
            ))
            context.counters["tasks"] += 1
            handled = True
    if not handled:
        _record_text_lines(context, extracted, "Task", "No task rows detected")


def _import_cashbook(context: ImportContext, extracted: ExtractedPdf) -> None:
    handled = False
    for page, row in _iter_table_dicts(extracted):
        parsed_date = _parse_date(_value(row, "datum", "date", "buchungstag")) or _cashbook_page_date(extracted, page)
        title = _value(row, "titel", "text", "beschreibung", "bezeichnung", "buchung") or "BeeIntouch Buchung"
        amount, direction = _cashbook_amount_and_direction(row)
        if parsed_date is None or amount is None:
            _record_error(context, page, None, "CashbookEntry", "Missing date or amount", _row_text(row))
            continue
        tax_rate = _parse_amount(_value(row, "ust", "mwst", "steuer", "tax")) or 0
        tax_amount = round(amount - (amount / (1 + tax_rate / 100)), 2) if tax_rate else 0
        context.db.add(CashbookEntry(
            owner_id=context.owner.id,
            performed_by_user_id=context.owner.id,
            booking_date=parsed_date,
            direction=direction,
            category=_cashbook_category(row),
            title=title[:200],
            invoice_number=_value(row, "rechnung", "rechnungsnummer", "beleg", "belegnummer"),
            amount_gross=amount,
            tax_rate=tax_rate,
            tax_amount=tax_amount,
            amount_net=round(amount - tax_amount, 2),
            counterparty=_value(row, "partner", "kunde", "lieferant", "gegenpartei"),
            description=_join_values(row, "notiz", "notizen", "bemerkung", "beschreibung") or _source_note(context.source_name),
            payment_method=_value(row, "zahlung", "zahlungsart", "konto"),
            created_at=_now(),
        ))
        context.counters["cashbook_entries"] += 1
        handled = True
    if not handled:
        _import_date_amount_lines(context, extracted, "CashbookEntry")


def _import_date_amount_lines(context: ImportContext, extracted: ExtractedPdf, target_type: str) -> None:
    handled = False
    fallback_apiary: Apiary | None = None
    for page_number, line in _iter_text_lines(extracted):
        parsed_date = _parse_date(line)
        amount = _parse_amount(line)
        if parsed_date is None or amount is None:
            continue
        title = _strip_amount(_strip_date(line)) or f"BeeIntouch {target_type}"
        if target_type == "Feeding":
            if fallback_apiary is None:
                fallback_apiary = _get_or_create_import_apiary(context.db, context.owner.id)
            context.db.add(Feeding(
                owner_id=context.owner.id,
                performed_by_user_id=context.owner.id,
                apiary_id=fallback_apiary.id,
                date=parsed_date,
                feed_type=title[:120],
                amount_kg_or_l=amount,
                notes=_source_note(context.source_name),
                created_at=_now(),
            ))
            context.counters["feedings"] += 1
        else:
            direction = CashbookDirection.expense if _looks_expense(line, amount) else CashbookDirection.income
            context.db.add(CashbookEntry(
                owner_id=context.owner.id,
                performed_by_user_id=context.owner.id,
                booking_date=parsed_date,
                direction=direction,
                category="other",
                title=title[:200],
                amount_gross=abs(amount),
                tax_rate=0,
                tax_amount=0,
                amount_net=abs(amount),
                description=_source_note(context.source_name),
                created_at=_now(),
            ))
            context.counters["cashbook_entries"] += 1
        handled = True
    if not handled:
        _record_text_lines(context, extracted, target_type, f"No parseable {target_type} rows detected")


def _find_first_admin(db: Session) -> User | None:
    return (
        db.query(User)
        .filter(User.is_admin.is_(True), User.is_active.is_(True))
        .order_by(User.id.asc())
        .first()
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _clean_cell(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _normalize_key(value: str) -> str:
    normalized = value.lower().strip()
    normalized = normalized.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    return re.sub(r"[^a-z0-9]+", "_", normalized).strip("_")


def _iter_table_dicts(extracted: ExtractedPdf) -> Iterable[tuple[int, dict[str, str]]]:
    for page, table in extracted.tables:
        if len(table) < 2:
            continue
        header_index = _find_header_index(table)
        if header_index is None:
            continue
        headers = [_normalize_key(cell) for cell in table[header_index]]
        for row in table[header_index + 1:]:
            data = {
                header: _clean_cell(row[index] if index < len(row) else "")
                for index, header in enumerate(headers)
                if header
            }
            if any(data.values()):
                yield page, data


def _find_header_index(table: list[list[str]]) -> int | None:
    known = {
        "datum", "date", "name", "partner", "kunde", "lieferant", "volk", "bienenvolk",
        "stand", "bienenstand", "menge", "betrag", "einnahme", "ausgabe", "aufgabe",
        "beschreibung", "titel",
    }
    for index, row in enumerate(table[:5]):
        keys = {_normalize_key(cell) for cell in row}
        if keys & known:
            return index
    return 0 if table and len(table) > 1 else None


def _iter_text_lines(extracted: ExtractedPdf) -> Iterable[tuple[int, str]]:
    for page_number, text in enumerate(extracted.text_pages, start=1):
        for line in text.splitlines():
            clean = _clean_cell(line)
            if clean and not _is_heading(clean):
                yield page_number, clean


def _is_heading(line: str) -> bool:
    lowered = line.lower()
    if lowered in {"partnerliste", "bestandsbuch", "fütterung", "fuetterung", "todos", "todo-liste", "kassenbuch", "allgemein"}:
        return True
    if lowered.startswith(("datum:", "seite ", "stand ")) or "gesamt:" in lowered:
        return True
    return any(header in lowered for header in [
        "stocknummer beutengewicht",
        "qr-code name",
        "art rechnungsnummer buchungstext",
    ])


def _value(row: dict[str, str], *candidates: str) -> str | None:
    normalized_candidates = [_normalize_key(candidate) for candidate in candidates]
    for candidate in normalized_candidates:
        if row.get(candidate):
            return row[candidate]
    for key, value in row.items():
        if value and any(candidate in key for candidate in normalized_candidates):
            return value
    return None


def _join_values(row: dict[str, str], *candidates: str) -> str | None:
    values = []
    for candidate in candidates:
        value = _value(row, candidate)
        if value and value not in values:
            values.append(value)
    return ", ".join(values) if values else None


def _row_text(row: dict[str, str]) -> str:
    return " | ".join(f"{key}={value}" for key, value in row.items() if value)


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    patterns = [
        r"(?P<day>\d{1,2})\.(?P<month>\d{1,2})\.(?P<year>\d{2,4})",
        r"(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})",
    ]
    for pattern in patterns:
        match = re.search(pattern, value)
        if not match:
            continue
        parts = {key: int(val) for key, val in match.groupdict().items()}
        if parts["year"] < 100:
            parts["year"] += 2000
        try:
            return date(parts["year"], parts["month"], parts["day"])
        except ValueError:
            return None
    return None


def _parse_amount(value: str | None) -> float | None:
    if not value:
        return None
    matches = re.findall(r"-?\d{1,3}(?:[.\s]\d{3})*(?:,\d+)?|-?\d+(?:[,.]\d+)?", value)
    if not matches:
        return None
    raw = matches[-1].replace(" ", "")
    if "," in raw:
        raw = raw.replace(".", "").replace(",", ".")
    try:
        return abs(float(raw))
    except ValueError:
        return None


def _cashbook_page_date(extracted: ExtractedPdf, page_number: int) -> date | None:
    text = extracted.text_pages[page_number - 1] if 0 < page_number <= len(extracted.text_pages) else ""
    lowered = text.lower()
    year_match = re.search(r"kassenbuch\s*(\d{4})", lowered)
    year = int(year_match.group(1)) if year_match else None
    if year is None:
        report_date = _parse_date(text)
        year = report_date.year if report_date else None
    if year is None:
        return None
    for month_name, month in GERMAN_MONTHS.items():
        if re.search(rf"\b{re.escape(month_name)}\b", lowered):
            return date(year, month, 1)
    return None


def _cashbook_amount_and_direction(row: dict[str, str]) -> tuple[float | None, CashbookDirection]:
    income = _parse_amount(_value(row, "einnahme", "income", "haben"))
    expense = _parse_amount(_value(row, "ausgabe", "expense", "soll"))
    if income is not None and income > 0:
        return income, CashbookDirection.income
    if expense is not None and expense > 0:
        return expense, CashbookDirection.expense
    amount_value = _value(row, "betrag", "amount", "brutto", "summe")
    amount = _parse_amount(amount_value)
    if amount is None:
        return None, CashbookDirection.expense
    return amount, CashbookDirection.expense if _looks_expense(_row_text(row), amount) else CashbookDirection.income


def _looks_expense(text: str, amount: float) -> bool:
    lowered = text.lower()
    return (
        amount < 0
        or re.search(r"-\s*\d", text) is not None
        or any(word in lowered for word in ["ausgabe", "expense", "soll", "bezahlt", "material", "futter", "zucker"])
    )


def _cashbook_category(row: dict[str, str]) -> str:
    category = _value(row, "kategorie", "category")
    if category:
        lowered = category.lower()
    else:
        lowered = _row_text(row).lower()
    if any(word in lowered for word in ["honig", "verkauf"]):
        return "honey_sales"
    if any(word in lowered for word in ["futter", "zucker", "sirup"]):
        return "feed"
    if any(word in lowered for word in ["glas", "etikett", "deckel"]):
        return "jars_labels"
    if any(word in lowered for word in ["material", "werkzeug"]):
        return "material"
    return "other"


def _partner_type(row: dict[str, str]) -> OfficePartnerType:
    text = _row_text(row).lower()
    if any(word in text for word in ["lieferant", "supplier", "ausgabe", "material"]):
        return OfficePartnerType.supplier
    return OfficePartnerType.customer


def _task_priority(row: dict[str, str]) -> TaskPriority:
    text = _row_text(row).lower()
    if any(word in text for word in ["dringend", "urgent"]):
        return TaskPriority.urgent
    if any(word in text for word in ["hoch", "high"]):
        return TaskPriority.high
    if any(word in text for word in ["niedrig", "low"]):
        return TaskPriority.low
    return TaskPriority.medium


def _source_note(source_name: str) -> str:
    return f"BeeIntouch Import: {source_name}"


def _get_or_create_import_apiary(db: Session, owner_id: int) -> Apiary:
    return _get_or_create_apiary(db, owner_id, "BeeIntouch Import")


def _get_or_create_apiary(db: Session, owner_id: int, name: str | None) -> Apiary:
    apiary_name = (name or "BeeIntouch Import").strip()[:100] or "BeeIntouch Import"
    apiary = (
        db.query(Apiary)
        .filter(Apiary.owner_id == owner_id, Apiary.stock_number == apiary_name)
        .first()
    )
    if apiary:
        return apiary
    apiary = Apiary(owner_id=owner_id, stock_number=apiary_name, name=apiary_name, notes="BeeIntouch Import")
    apiary.created_at = _now()
    db.add(apiary)
    db.flush()
    db.add(ApiaryMember(
        apiary_id=apiary.id,
        user_id=owner_id,
        role=ApiaryMemberRole.owner,
        accepted_at=_now(),
        created_at=_now(),
    ))
    db.flush()
    return apiary


def _find_or_create_hive(db: Session, owner_id: int, hive_name: str | None, apiary: Apiary) -> Hive | None:
    if not hive_name:
        return None
    cleaned = hive_name.strip()[:100]
    if not cleaned:
        return None
    hive = (
        db.query(Hive)
        .filter(Hive.owner_id == owner_id, Hive.apiary_id == apiary.id, Hive.name == cleaned)
        .first()
    )
    if hive:
        return hive
    hive = Hive(owner_id=owner_id, apiary_id=apiary.id, name=cleaned, notes="BeeIntouch Import", created_at=_now())
    db.add(hive)
    db.flush()
    return hive


def _record_error(
    context: ImportContext,
    page_number: int | None,
    row_number: int | None,
    target_type: str | None,
    message: str,
    raw_text: str | None,
) -> None:
    context.db.add(BeeIntouchImportError(
        run_id=context.run.id,
        source_name=context.source_name,
        page_number=page_number,
        row_number=row_number,
        target_type=target_type,
        message=message,
        raw_text=raw_text,
    ))


def _record_text_lines(context: ImportContext, extracted: ExtractedPdf, target_type: str, message: str) -> None:
    lines = list(_iter_text_lines(extracted))
    if not lines:
        _record_error(context, None, None, target_type, "PDF text extraction returned no content", None)
        return
    for row_number, (page_number, line) in enumerate(lines[:25], start=1):
        _record_error(context, page_number, row_number, target_type, message, line)


def _strip_date(value: str) -> str:
    value = re.sub(r"\d{1,2}\.\d{1,2}\.\d{2,4}", "", value)
    value = re.sub(r"\d{4}-\d{1,2}-\d{1,2}", "", value)
    return _clean_cell(value).strip(":- ")


def _strip_amount(value: str) -> str:
    value = re.sub(r"-?\d{1,3}(?:[.\s]\d{3})*(?:,\d+)?|-?\d+(?:[,.]\d+)?", "", value)
    value = value.replace("€", "").replace("EUR", "")
    return _clean_cell(value).strip(":- ")


if __name__ == "__main__":
    main()
