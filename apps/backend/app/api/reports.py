from datetime import date
from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user
from app.crud import inventory as inventory_crud
from app.db.database import get_db
from app.models.apiary import Apiary
from app.models.feeding import Feeding
from app.models.harvest import Harvest
from app.models.hive import Hive, HiveStatus
from app.models.inspection import Inspection
from app.models.inventory import ArticleCategory
from app.models.user import User

router = APIRouter()


@router.get("/yearly")
def yearly_report(
    year: int = date.today().year,
    include_archived: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    query = db.query(Hive).filter(Hive.owner_id == current_user.id)
    if not include_archived:
        query = query.filter(Hive.is_active.is_(True))
    hives = query.all()
    return {
        "year": year,
        "include_archived": include_archived,
        "active_hives": sum(1 for hive in hives if hive.status == HiveStatus.active),
        "new_hives": sum(1 for hive in hives if hive.created_at and hive.created_at.year == year),
        "sold_hives": sum(1 for hive in hives if hive.status == HiveStatus.sold),
        "merged_hives": sum(1 for hive in hives if hive.status == HiveStatus.merged),
        "losses": sum(1 for hive in hives if hive.status in {HiveStatus.dead, HiveStatus.lost}),
        "hives": [
            {
                "id": hive.id,
                "name": hive.name,
                "status": hive.status,
                "archived_at": hive.archived_at,
                "merged_into_hive_id": hive.merged_into_hive_id,
            }
            for hive in hives
        ],
    }


@router.get("/harvest-by-crop")
def harvest_by_crop(
    from_date: date | None = None,
    to_date: date | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    query = db.query(Harvest.crop_type, func.sum(Harvest.amount_kg)).filter(Harvest.owner_id == current_user.id)
    if from_date:
        query = query.filter(Harvest.harvest_date >= from_date)
    if to_date:
        query = query.filter(Harvest.harvest_date <= to_date)
    return [
        {"crop_type": crop_type or "Unbekannt", "amount_kg": float(amount or 0)}
        for crop_type, amount in query.group_by(Harvest.crop_type).order_by(func.sum(Harvest.amount_kg).desc()).all()
    ]


@router.get("/harvest-by-apiary")
def harvest_by_apiary(
    from_date: date | None = None,
    to_date: date | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    query = (
        db.query(Apiary.id, Apiary.name, func.sum(Harvest.amount_kg))
        .join(Harvest, Harvest.apiary_id == Apiary.id)
        .filter(Harvest.owner_id == current_user.id)
    )
    if from_date:
        query = query.filter(Harvest.harvest_date >= from_date)
    if to_date:
        query = query.filter(Harvest.harvest_date <= to_date)
    return [
        {"apiary_id": apiary_id, "apiary_name": name, "amount_kg": float(amount or 0)}
        for apiary_id, name, amount in query.group_by(Apiary.id, Apiary.name).order_by(func.sum(Harvest.amount_kg).desc()).all()
    ]


@router.get("/varroa")
def varroa_report(
    from_date: date | None = None,
    to_date: date | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    query = db.query(Inspection.date, Hive.id, Hive.name, Inspection.varroa_count).join(Hive).filter(
        Hive.owner_id == current_user.id,
        Inspection.varroa_count.isnot(None),
    )
    if from_date:
        query = query.filter(Inspection.date >= from_date)
    if to_date:
        query = query.filter(Inspection.date <= to_date)
    return [
        {"date": seen_at, "hive_id": hive_id, "hive_name": hive_name, "varroa_count": float(varroa_count or 0)}
        for seen_at, hive_id, hive_name, varroa_count in query.order_by(Inspection.date.asc()).all()
    ]


def _feedings_by_apiary(
    db: Session,
    owner_id: int,
    from_date: date | None = None,
    to_date: date | None = None,
) -> list[dict]:
    query = (
        db.query(Apiary.id, Apiary.name, func.sum(Feeding.amount_kg_or_l))
        .join(Feeding, Feeding.apiary_id == Apiary.id)
        .filter(Feeding.owner_id == owner_id)
    )
    if from_date:
        query = query.filter(Feeding.date >= from_date)
    if to_date:
        query = query.filter(Feeding.date <= to_date)
    return [
        {"apiary_id": apiary_id, "apiary_name": name, "amount_kg_or_l": float(amount or 0)}
        for apiary_id, name, amount in query.group_by(Apiary.id, Apiary.name).order_by(Apiary.name).all()
    ]


@router.get("/feedings")
def feedings_report(
    from_date: date | None = None,
    to_date: date | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return _feedings_by_apiary(db, current_user.id, from_date=from_date, to_date=to_date)


def _require_reportlab():
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
    except ImportError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="PDF export dependency missing") from exc
    return canvas, A4


def _render_inventory_pdf(title: str, filename: str, items: list) -> Response:
    canvas_module, A4 = _require_reportlab()
    buffer = BytesIO()
    pdf = canvas_module.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 50
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, y, title)
    y -= 32
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawString(50, y, "Artikel")
    pdf.drawString(200, y, "SKU")
    pdf.drawString(280, y, "Menge")
    pdf.drawString(330, y, "Einheit")
    pdf.drawString(390, y, "MHD")
    pdf.drawString(450, y, "Chargen-Nr.")
    pdf.drawRightString(width - 50, y, "Preis")
    y -= 14
    pdf.setFont("Helvetica", 9)
    for item in items:
        if y < 60:
            pdf.showPage()
            y = height - 50
            pdf.setFont("Helvetica", 9)
        article = item.article
        name = (article.name if article else "") or ""
        sku = (article.sku if article else "") or ""
        best_before = item.best_before.isoformat() if item.best_before else ""
        batch_code = item.batch_code or ""
        price = f"EUR {item.price:.2f}" if item.price is not None else ""
        pdf.drawString(50, y, name[:24])
        pdf.drawString(200, y, sku[:12])
        pdf.drawString(280, y, f"{item.quantity:g}")
        pdf.drawString(330, y, item.unit or "")
        pdf.drawString(390, y, best_before)
        pdf.drawString(450, y, batch_code[:12])
        pdf.drawRightString(width - 50, y, price)
        y -= 12
    pdf.save()
    return Response(
        content=buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/inventory-material.pdf")
def inventory_material_pdf(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    items = inventory_crud.get_inventory_items(db, current_user.id)
    material_categories = {ArticleCategory.material, ArticleCategory.feed}
    items = [item for item in items if item.article and item.article.category in material_categories]
    return _render_inventory_pdf("Bestand Materiallager", "bestand-materiallager.pdf", items)


@router.get("/inventory-finished-goods.pdf")
def inventory_finished_goods_pdf(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    items = inventory_crud.get_inventory_items(db, current_user.id)
    finished_categories = {ArticleCategory.honey}
    items = [item for item in items if item.article and item.article.category in finished_categories]
    return _render_inventory_pdf("Bestand Fertigprodukte", "bestand-fertigprodukte.pdf", items)


@router.get("/feedings.pdf")
def feedings_pdf(
    from_date: date | None = None,
    to_date: date | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    rows = _feedings_by_apiary(db, current_user.id, from_date=from_date, to_date=to_date)
    canvas_module, A4 = _require_reportlab()
    buffer = BytesIO()
    pdf = canvas_module.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 50
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, y, "Fuetterungs-Report")
    y -= 32
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(50, y, "Standort")
    pdf.drawRightString(width - 50, y, "Menge (kg/l)")
    y -= 16
    pdf.setFont("Helvetica", 10)
    total = 0.0
    for row in rows:
        if y < 60:
            pdf.showPage()
            y = height - 50
            pdf.setFont("Helvetica", 10)
        pdf.drawString(50, y, row["apiary_name"])
        pdf.drawRightString(width - 50, y, f"{row['amount_kg_or_l']:.2f}")
        total += row["amount_kg_or_l"]
        y -= 14
    y -= 10
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(50, y, "Gesamt")
    pdf.drawRightString(width - 50, y, f"{total:.2f}")
    pdf.save()
    return Response(
        content=buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="fuetterungs-report.pdf"'},
    )
