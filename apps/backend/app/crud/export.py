import json
import tempfile
import zipfile
from datetime import date, datetime

from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Session

from app.models.apiary import Apiary
from app.models.batch import Batch
from app.models.cashbook import CashbookEntry, CashbookReceipt
from app.models.feeding import Feeding
from app.models.harvest import Harvest
from app.models.hive import Hive
from app.models.hive_event import HiveEvent
from app.models.inspection import Inspection
from app.models.inventory import Article, InventoryItem
from app.models.office import OfficeDocument, OfficePartner
from app.models.photo import Photo
from app.models.queen import Queen
from app.models.sale import Sale, SaleItem
from app.models.task import Task
from app.models.treatment import Treatment
from app.models.user import User
from app.models.varroa_check import VarroaCheck
from app.models.weight_reading import WeightReading
from app.models.zuchtreihe import Zuchtreihe


def _serialize(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if hasattr(value, "value"):
        return value.value
    return value


def _rows(records, excluded_columns: set[str] | None = None):
    excluded_columns = excluded_columns or set()
    return [
        {
            column.key: _serialize(getattr(record, column.key))
            for column in inspect(record).mapper.column_attrs
            if column.key not in excluded_columns
        }
        for record in records
    ]


def build_account_export(db: Session, user: User):
    apiary_ids = [row[0] for row in db.query(Apiary.id).filter(Apiary.owner_id == user.id).all()]
    hive_ids = [row[0] for row in db.query(Hive.id).filter(Hive.owner_id == user.id).all()]
    direct_models = [
        ("apiaries", Apiary), ("hives", Hive), ("batches", Batch), ("cashbook_entries", CashbookEntry),
        ("cashbook_receipts", CashbookReceipt), ("feedings", Feeding), ("harvests", Harvest),
        ("articles", Article), ("inventory_items", InventoryItem), ("office_documents", OfficeDocument),
        ("office_partners", OfficePartner), ("queens", Queen), ("sales", Sale), ("tasks", Task),
        ("treatments", Treatment), ("varroa_checks", VarroaCheck), ("zuchtreihen", Zuchtreihe),
    ]
    data = {
        "account": _rows([user], {"hashed_password"}),
        "scope": {"photos": "metadata only; object blobs are not included"},
    }
    for name, model in direct_models:
        data[name] = _rows(db.query(model).filter(model.owner_id == user.id).all())
    data["inspections"] = _rows(db.query(Inspection).filter(Inspection.hive_id.in_(hive_ids)).all()) if hive_ids else []
    data["hive_events"] = _rows(db.query(HiveEvent).filter(HiveEvent.hive_id.in_(hive_ids)).all()) if hive_ids else []
    data["weight_readings"] = _rows(db.query(WeightReading).filter(WeightReading.hive_id.in_(hive_ids)).all()) if hive_ids else []
    data["sale_items"] = _rows(db.query(SaleItem).join(Sale).filter(Sale.owner_id == user.id).all())
    data["photos"] = _rows(db.query(Photo).filter(Photo.owner_id == user.id).all())
    archive = tempfile.SpooledTemporaryFile(max_size=5 * 1024 * 1024, mode="w+b")
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
        bundle.writestr("account-export.json", json.dumps(data, default=_serialize, ensure_ascii=False))
    archive.seek(0)
    return archive
