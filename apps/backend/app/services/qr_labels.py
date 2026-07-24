from io import BytesIO

import segno
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from app.core.config import get_settings
from app.models.hive import Hive
from app.models.office import OfficePartner


def stock_card_url(hive_id: int) -> str:
    base = get_settings().FRONTEND_BASE_URL.rstrip("/")
    return f"{base}/stock-card/{hive_id}"


def inspect_url(hive_id: int) -> str:
    base = get_settings().FRONTEND_BASE_URL.rstrip("/")
    return f"{base}/hives/{hive_id}/inspect"


def hive_qr_svg(hive_id: int, target: str = "stock_card") -> str:
    url = inspect_url(hive_id) if target == "inspect" else stock_card_url(hive_id)
    qr = segno.make(url, error="m")
    return qr.svg_inline(scale=4, dark="#000000")


def _draw_qr(pdf: canvas.Canvas, content: str, x: float, y: float, size: float) -> None:
    qr = segno.make(content, error="m")
    matrix = list(qr.matrix_iter(scale=1, border=0))
    modules = len(matrix)
    module_size = size / modules
    pdf.setFillColorRGB(0, 0, 0)
    for row_index, row in enumerate(matrix):
        for col_index, value in enumerate(row):
            if value:
                pdf.rect(
                    x + col_index * module_size,
                    y + size - (row_index + 1) * module_size,
                    module_size,
                    module_size,
                    stroke=0,
                    fill=1,
                )


def hive_label_sheet_pdf(hives: list[Hive]) -> bytes:
    buffer = BytesIO()
    page_width, page_height = A4
    pdf = canvas.Canvas(buffer, pagesize=A4)

    columns, rows = 2, 4
    margin = 36.0
    cell_width = (page_width - 2 * margin) / columns
    cell_height = (page_height - 2 * margin) / rows
    qr_size = min(cell_width, cell_height) - 60.0

    for index, hive in enumerate(hives):
        slot = index % (columns * rows)
        if index > 0 and slot == 0:
            pdf.showPage()
        column = slot % columns
        row = slot // columns
        cell_x = margin + column * cell_width
        cell_y = page_height - margin - (row + 1) * cell_height

        qr_x = cell_x + (cell_width - qr_size) / 2
        qr_y = cell_y + 44.0
        _draw_qr(pdf, stock_card_url(hive.id), qr_x, qr_y, qr_size)

        pdf.setFillColorRGB(0, 0, 0)
        pdf.setFont("Helvetica-Bold", 12)
        title = hive.name if not hive.stock_number else f"{hive.name} · #{hive.stock_number}"
        pdf.drawCentredString(cell_x + cell_width / 2, cell_y + 26, title[:48])
        pdf.setFont("Helvetica", 9)
        apiary_name = hive.apiary.name or hive.apiary.stock_number if hive.apiary else ""
        pdf.drawCentredString(cell_x + cell_width / 2, cell_y + 12, apiary_name[:60])

    pdf.save()
    return buffer.getvalue()


def partner_vcard(partner: OfficePartner) -> str:
    lines = ["BEGIN:VCARD", "VERSION:3.0", f"N:{partner.name}", f"FN:{partner.name}"]
    if partner.phone:
        lines.append(f"TEL:{partner.phone}")
    if partner.email:
        lines.append(f"EMAIL:{partner.email}")
    if partner.address:
        address = partner.address.replace("\n", ";")
        lines.append(f"ADR:;;{address};;;;")
    lines.append("END:VCARD")
    return "\n".join(lines)


def customer_label_sheet_pdf(partners: list[OfficePartner]) -> bytes:
    buffer = BytesIO()
    page_width, page_height = A4
    pdf = canvas.Canvas(buffer, pagesize=A4)

    columns, rows = 2, 4
    margin = 36.0
    cell_width = (page_width - 2 * margin) / columns
    cell_height = (page_height - 2 * margin) / rows
    qr_size = min(cell_width, cell_height) - 60.0

    for index, partner in enumerate(partners):
        slot = index % (columns * rows)
        if index > 0 and slot == 0:
            pdf.showPage()
        column = slot % columns
        row = slot // columns
        cell_x = margin + column * cell_width
        cell_y = page_height - margin - (row + 1) * cell_height

        qr_x = cell_x + (cell_width - qr_size) / 2
        qr_y = cell_y + 44.0
        _draw_qr(pdf, partner_vcard(partner), qr_x, qr_y, qr_size)

        pdf.setFillColorRGB(0, 0, 0)
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawCentredString(cell_x + cell_width / 2, cell_y + 26, partner.name[:48])
        pdf.setFont("Helvetica", 9)
        subtitle = partner.phone or partner.email or ""
        pdf.drawCentredString(cell_x + cell_width / 2, cell_y + 12, subtitle[:60])

    pdf.save()
    return buffer.getvalue()
