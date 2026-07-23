from datetime import date
from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user
from app.crud import honeybook as honeybook_crud
from app.db.database import get_db
from app.models.user import User
from app.schemas.honeybook import HoneybookEntry

router = APIRouter()


@router.get("/register", response_model=list[HoneybookEntry])
def get_register(
    year: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return honeybook_crud.get_register(db, current_user.id, year=year)


def _require_reportlab():
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
    except ImportError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="PDF export dependency missing") from exc
    return canvas, A4


def _render_register_pdf(entries: list[HoneybookEntry], year: int) -> bytes:
    canvas_module, A4 = _require_reportlab()
    buffer = BytesIO()
    pdf = canvas_module.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 50
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, y, f"Honigbuch {year}")
    y -= 30
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawString(40, y, "Los-Nr.")
    pdf.drawString(90, y, "Datum")
    pdf.drawString(140, y, "Stand")
    pdf.drawString(210, y, "Volk")
    pdf.drawString(270, y, "Sorte")
    pdf.drawString(330, y, "Menge kg")
    pdf.drawString(380, y, "Wasser %")
    pdf.drawString(430, y, "MHD")
    pdf.drawString(480, y, "Abgefuellt")
    y -= 16
    pdf.setFont("Helvetica", 8)
    for entry in entries:
        if y < 60:
            pdf.showPage()
            y = height - 50
            pdf.setFont("Helvetica", 8)
        pdf.drawString(40, y, entry.lot_number or "-")
        pdf.drawString(90, y, entry.harvest_date.isoformat())
        pdf.drawString(140, y, (entry.apiary_name or "-")[:14])
        pdf.drawString(210, y, (entry.hive_name or "-")[:12])
        pdf.drawString(270, y, (entry.crop_type or "-")[:12])
        pdf.drawString(330, y, f"{entry.amount_kg:.2f}")
        pdf.drawString(
            380, y, f"{entry.water_content_percent:.1f}" if entry.water_content_percent is not None else "-"
        )
        pdf.drawString(430, y, entry.best_before.isoformat() if entry.best_before else "-")
        articles = ", ".join(entry.bottled_articles)
        pdf.drawString(480, y, f"{entry.bottled_quantity} {articles}"[:40] if entry.bottled_quantity else "-")
        y -= 12
    pdf.save()
    return buffer.getvalue()


@router.get("/register.pdf")
def get_register_pdf(
    year: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    resolved_year = year if year is not None else date.today().year
    entries = honeybook_crud.get_register(db, current_user.id, year=resolved_year)
    content = _render_register_pdf(entries, resolved_year)
    return Response(
        content=content,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="honigbuch-{resolved_year}.pdf"'},
    )
