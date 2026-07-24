import csv
from datetime import date
from io import BytesIO, StringIO

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user
from app.crud import cashbook as cashbook_crud
from app.crud import office as office_crud
from app.db.database import get_db
from app.models.user import User
from app.schemas.cashbook import CashbookEntryResponse
from app.schemas.office import (
    OfficeDashboard,
    OfficeDocumentCreate,
    OfficeDocumentResponse,
    OfficeDocumentUpdate,
    OfficePartnerCreate,
    OfficePartnerResponse,
    OfficePartnerUpdate,
)

router = APIRouter()


@router.get("/dashboard", response_model=OfficeDashboard)
def get_dashboard(
    year: int = date.today().year,
    month: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if month is not None and (month < 1 or month > 12):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Month must be between 1 and 12")
    return office_crud.dashboard(db, current_user.id, year=year, month=month)


@router.get("/partners", response_model=list[OfficePartnerResponse])
def list_partners(
    partner_type: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return office_crud.list_partners(db, current_user.id, partner_type=partner_type)


@router.get("/partners/customers.pdf")
def get_customer_label_sheet(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    from app.services.qr_labels import customer_label_sheet_pdf

    customers = office_crud.list_partners(db, current_user.id, partner_type="customer")
    if not customers:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No customers found")
    pdf = customer_label_sheet_pdf(customers)
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="kundenliste-qr.pdf"'},
    )


@router.post("/partners", response_model=OfficePartnerResponse, status_code=status.HTTP_201_CREATED)
def create_partner(
    partner: OfficePartnerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return office_crud.create_partner(db, current_user.id, partner)


@router.put("/partners/{partner_id}", response_model=OfficePartnerResponse)
def update_partner(
    partner_id: int,
    partner: OfficePartnerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    updated = office_crud.update_partner(db, current_user.id, partner_id, partner)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Partner not found")
    return updated


@router.delete("/partners/{partner_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_partner(
    partner_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if not office_crud.delete_partner(db, current_user.id, partner_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Partner not found")


@router.get("/documents", response_model=list[OfficeDocumentResponse])
def list_documents(
    document_type: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return office_crud.list_documents(db, current_user.id, document_type=document_type)


@router.post("/documents", response_model=OfficeDocumentResponse, status_code=status.HTTP_201_CREATED)
def create_document(
    document: OfficeDocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    created = office_crud.create_document(db, current_user.id, document)
    if not created:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Related partner not found")
    return created


@router.put("/documents/{document_id}", response_model=OfficeDocumentResponse)
def update_document(
    document_id: int,
    document: OfficeDocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    updated = office_crud.update_document(db, current_user.id, document_id, document)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return updated


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if not office_crud.delete_document(db, current_user.id, document_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")


@router.get("/cashbook/export.csv")
def export_cashbook_csv(
    year: int = date.today().year,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    entries = cashbook_crud.list_entries(db, current_user.id, from_date=date(year, 1, 1), to_date=date(year, 12, 31))
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Datum", "Typ", "Kategorie", "Titel", "Rechnungsnummer", "Gegenpartei", "Brutto", "MwSt %", "Steuer", "Netto"])
    for entry in entries:
        writer.writerow([
            entry.booking_date.isoformat(),
            entry.direction.value,
            entry.category,
            entry.title or "",
            entry.invoice_number or "",
            entry.counterparty or "",
            f"{entry.amount_gross:.2f}",
            f"{entry.tax_rate:.2f}",
            f"{entry.tax_amount:.2f}",
            f"{entry.amount_net:.2f}",
        ])
    return Response(
        content=output.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="kassenbuch-{year}.csv"'},
    )


@router.get("/cashbook/report.pdf")
def export_cashbook_pdf(
    year: int = date.today().year,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
    except ImportError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="PDF export dependency missing") from exc

    summary = office_crud.dashboard(db, current_user.id, year=year)
    entries = cashbook_crud.list_entries(db, current_user.id, from_date=date(year, 1, 1), to_date=date(year, 12, 31))
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 50
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, y, f"Kassenbuch Jahresreport {year}")
    y -= 32
    pdf.setFont("Helvetica", 11)
    pdf.drawString(50, y, f"Einnahmen: EUR {summary['income']:.2f}")
    pdf.drawString(220, y, f"Ausgaben: EUR {summary['expenses']:.2f}")
    pdf.drawString(390, y, f"Saldo: EUR {summary['balance']:.2f}")
    y -= 30
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y, "Monatsuebersicht")
    y -= 18
    pdf.setFont("Helvetica", 9)
    for item in summary["monthly"]:
        pdf.drawString(55, y, f"{item['month']:02d}.")
        pdf.drawString(100, y, f"Ein: {item['income']:.2f}")
        pdf.drawString(210, y, f"Aus: {item['expenses']:.2f}")
        pdf.drawString(320, y, f"Saldo: {item['balance']:.2f}")
        y -= 13
    y -= 10
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y, "Buchungen")
    y -= 18
    pdf.setFont("Helvetica", 8)
    for entry in entries:
        if y < 60:
            pdf.showPage()
            y = height - 50
            pdf.setFont("Helvetica", 8)
        sign = "+" if entry.direction.value == "income" else "-"
        title = entry.title or entry.description or entry.category
        pdf.drawString(50, y, entry.booking_date.isoformat())
        pdf.drawString(125, y, sign)
        pdf.drawString(145, y, title[:42])
        pdf.drawRightString(width - 50, y, f"EUR {entry.amount_gross:.2f}")
        y -= 12
    pdf.save()
    return Response(
        content=buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="kassenbuch-{year}.pdf"'},
    )
