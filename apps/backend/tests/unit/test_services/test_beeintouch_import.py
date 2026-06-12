from pathlib import Path

import pytest

from app.core.security import get_password_hash
from app.importers import beeintouch_pdf_import
from app.importers.beeintouch_pdf_import import ExtractedPdf, import_beeintouch_pdfs
from app.models.beeintouch_import import BeeIntouchImportRun
from app.models.cashbook import CashbookDirection, CashbookEntry
from app.models.user import User


@pytest.mark.unit
def test_beeintouch_import_skips_without_admin(db, tmp_path):
    (tmp_path / "kassenbuch.pdf").write_bytes(b"%PDF-1.4 empty")

    result = import_beeintouch_pdfs(db, tmp_path)

    assert result == {"status": "skipped", "reason": "No active admin user found"}
    assert db.query(BeeIntouchImportRun).count() == 0


@pytest.mark.unit
def test_beeintouch_cashbook_import_is_idempotent(db, tmp_path, monkeypatch):
    admin = User(
        username="admin",
        email="admin@example.com",
        hashed_password=get_password_hash("SecurePassword123!"),
        is_active=True,
        is_verified=True,
        is_admin=True,
    )
    db.add(admin)
    db.commit()

    (tmp_path / "kassenbuch.pdf").write_bytes(b"%PDF-1.4 cashbook")

    def fake_extract_pdf(path: Path):
        return ExtractedPdf(
            text_pages=[],
            tables=[
                (
                    1,
                    [
                        ["Datum", "Beschreibung", "Einnahme", "Ausgabe", "Kategorie"],
                        ["01.06.2026", "Honig Verkauf", "25,00", "", "Honig"],
                        ["02.06.2026", "Zucker", "", "10,50", "Futter"],
                    ],
                )
            ],
        )

    monkeypatch.setattr(beeintouch_pdf_import, "extract_pdf", fake_extract_pdf)

    first = import_beeintouch_pdfs(db, tmp_path)
    second = import_beeintouch_pdfs(db, tmp_path)

    assert first["status"] == "done"
    assert second["status"] == "done"
    assert db.query(CashbookEntry).count() == 2
    assert db.query(CashbookEntry).filter(CashbookEntry.direction == CashbookDirection.income).count() == 1
    assert db.query(CashbookEntry).filter(CashbookEntry.direction == CashbookDirection.expense).count() == 1
    assert db.query(BeeIntouchImportRun).filter(BeeIntouchImportRun.status == "success").count() == 1
