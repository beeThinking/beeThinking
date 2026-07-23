from datetime import date
from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user
from app.crud import treatment as treatment_crud
from app.db.database import get_db
from app.models.user import User
from app.schemas.treatment import TreatmentCreate, TreatmentJournalEntry, TreatmentResponse, TreatmentUpdate

router = APIRouter()


@router.get("", response_model=list[TreatmentResponse])
def list_treatments(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return treatment_crud.get_treatments(db, owner_id=current_user.id)


@router.post("", response_model=TreatmentResponse, status_code=status.HTTP_201_CREATED)
def create_treatment(
    treatment: TreatmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_treatment = treatment_crud.create_treatment(
        db, treatment=treatment, owner_id=current_user.id, performed_by_user_id=current_user.id
    )
    if not db_treatment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hive not found")
    return db_treatment


@router.get("/journal/export")
def export_treatment_journal(
    year: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    entries = treatment_crud.get_journal_entries(db, owner_id=current_user.id, year=year)
    return {
        "format": "journal-export-fields",
        "items": entries,
    }


def _require_reportlab():
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
    except ImportError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="PDF export dependency missing") from exc
    return canvas, A4


def _render_journal_pdf(entries: list[TreatmentJournalEntry], year: int) -> bytes:
    canvas_module, A4 = _require_reportlab()
    buffer = BytesIO()
    pdf = canvas_module.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 50
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, y, f"Bestandsbuch (TAMG) {year}")
    y -= 30
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawString(50, y, "Datum")
    pdf.drawString(100, y, "Volk")
    pdf.drawString(200, y, "Mittel")
    pdf.drawString(300, y, "Methode")
    pdf.drawString(370, y, "Menge")
    pdf.drawString(430, y, "Wartezeit")
    pdf.drawString(500, y, "Anwender")
    y -= 16
    pdf.setFont("Helvetica", 8)
    for entry in entries:
        if y < 60:
            pdf.showPage()
            y = height - 50
            pdf.setFont("Helvetica", 8)
        pdf.drawString(50, y, entry.date.isoformat())
        pdf.drawString(100, y, entry.hive_label[:20])
        pdf.drawString(200, y, entry.product[:20])
        pdf.drawString(300, y, (entry.method or "")[:15])
        pdf.drawString(370, y, (entry.amount or "")[:12])
        pdf.drawString(430, y, str(entry.waiting_period_days) if entry.waiting_period_days is not None else "-")
        pdf.drawString(500, y, entry.treater or "-")
        y -= 12
    pdf.save()
    return buffer.getvalue()


@router.get("/journal/export.pdf")
def export_treatment_journal_pdf(
    year: int = date.today().year,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    entries = treatment_crud.get_journal_entries(db, owner_id=current_user.id, year=year)
    content = _render_journal_pdf(entries, year)
    return Response(
        content=content,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="bestandsbuch-{year}.pdf"'},
    )


@router.get("/{treatment_id}", response_model=TreatmentResponse)
def get_treatment(
    treatment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_treatment = treatment_crud.get_treatment(db, treatment_id=treatment_id, owner_id=current_user.id)
    if not db_treatment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Treatment not found")
    return db_treatment


@router.put("/{treatment_id}", response_model=TreatmentResponse)
def update_treatment(
    treatment_id: int,
    treatment_update: TreatmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_treatment = treatment_crud.update_treatment(
        db, treatment_id=treatment_id, owner_id=current_user.id, treatment_update=treatment_update
    )
    if not db_treatment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Treatment not found")
    return db_treatment


@router.delete("/{treatment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_treatment(
    treatment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if not treatment_crud.delete_treatment(db, treatment_id=treatment_id, owner_id=current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Treatment not found")
