from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from app.crud.office import get_partner
from app.models.cashbook import CashbookDirection, CashbookEntry, CashbookReceipt
from app.models.inventory import Article, ArticleCategory, InventoryItem
from app.models.office import OfficePartnerType
from app.models.sale import Sale, SaleItem
from app.schemas.sale import SaleCreate

HONEY_VAT_RATE = 0.07
STANDARD_VAT_RATE = 0.19


class InsufficientStockError(Exception):
    pass


class InvalidSaleError(Exception):
    pass


# NOTE: this applies a single VAT rate to the whole sale even for mixed carts
# (honey + non-honey items), taking the honey rate if any line is honey. This is
# a known simplification — see ticket M6.2 (#26). If per-line VAT splitting is
# needed later, this function and the Sale/CashbookEntry VAT handling will need
# to change together.
def _default_vat_rate(inventory_items: list[InventoryItem]) -> float:
    for item in inventory_items:
        article = item.article
        if article and article.category == ArticleCategory.honey:
            return HONEY_VAT_RATE
    return STANDARD_VAT_RATE


def get_sales(db: Session, owner_id: int) -> list[Sale]:
    return db.query(Sale).filter(Sale.owner_id == owner_id).order_by(Sale.sale_date.desc(), Sale.id.desc()).all()


def get_sale(db: Session, sale_id: int, owner_id: int) -> Optional[Sale]:
    return db.query(Sale).filter(Sale.id == sale_id, Sale.owner_id == owner_id).first()


def create_sale(db: Session, sale: SaleCreate, owner_id: int) -> Sale:
    if sale.partner_id is not None:
        partner = get_partner(db, owner_id, sale.partner_id)
        if not partner:
            raise InvalidSaleError("Partner not found")
        if partner.partner_type != OfficePartnerType.customer:
            raise InvalidSaleError("Partner must be a customer")

    merged: dict[int, float] = {}
    prices: dict[int, float] = {}
    for line in sale.items:
        merged[line.inventory_item_id] = merged.get(line.inventory_item_id, 0) + line.quantity
        prices[line.inventory_item_id] = line.unit_price_gross

    inventory_items: dict[int, InventoryItem] = {}
    for inventory_item_id in merged:
        db_item = (
            db.query(InventoryItem)
            .filter(InventoryItem.id == inventory_item_id, InventoryItem.owner_id == owner_id)
            .first()
        )
        if not db_item:
            raise InvalidSaleError(f"Inventory item {inventory_item_id} not found")
        inventory_items[inventory_item_id] = db_item

    for inventory_item_id, requested_quantity in merged.items():
        db_item = inventory_items[inventory_item_id]
        if db_item.quantity < requested_quantity:
            raise InsufficientStockError(
                f"Insufficient stock for inventory item {inventory_item_id}"
            )

    vat_rate = sale.vat_rate
    if vat_rate is None:
        vat_rate = _default_vat_rate(list(inventory_items.values()))

    db_sale = Sale(
        owner_id=owner_id,
        partner_id=sale.partner_id,
        sale_date=sale.sale_date,
        vat_rate=vat_rate,
        amount_gross=0,
        amount_net=0,
        notes=sale.notes,
    )
    db.add(db_sale)
    db.flush()

    amount_gross = 0.0
    for line in sale.items:
        db_item = inventory_items[line.inventory_item_id]
        line_total_gross = round(line.quantity * line.unit_price_gross, 2)
        amount_gross += line_total_gross
        db.add(
            SaleItem(
                sale_id=db_sale.id,
                inventory_item_id=line.inventory_item_id,
                quantity=line.quantity,
                unit_price_gross=line.unit_price_gross,
                line_total_gross=line_total_gross,
            )
        )

    for inventory_item_id, requested_quantity in merged.items():
        inventory_items[inventory_item_id].quantity -= requested_quantity

    amount_gross = round(amount_gross, 2)
    amount_net = round(amount_gross / (1 + vat_rate), 2) if vat_rate else amount_gross
    tax_amount = round(amount_gross - amount_net, 2)

    db_sale.amount_gross = amount_gross
    db_sale.amount_net = amount_net

    receipt = CashbookReceipt(
        owner_id=owner_id,
        file_object_key=None,
        filename=f"sale-{db_sale.id}",
        content_type="application/x-sale-receipt",
        size_bytes=0,
        ocr_status="confirmed",
    )
    db.add(receipt)
    db.flush()

    entry = CashbookEntry(
        apiary_id=None,
        owner_id=owner_id,
        performed_by_user_id=owner_id,
        booking_date=sale.sale_date,
        direction=CashbookDirection.income,
        # "honey_sales" is used as a single generic sales bucket for all sale
        # entries, regardless of the actual article category being sold.
        category="honey_sales",
        title=f"Sale #{db_sale.id}",
        partner_id=sale.partner_id,
        amount_gross=amount_gross,
        tax_rate=vat_rate * 100,
        tax_amount=tax_amount,
        amount_net=amount_net,
        receipt_id=receipt.id,
        sale_id=db_sale.id,
    )
    db.add(entry)
    db.flush()

    db_sale.cashbook_entry_id = entry.id

    db.commit()
    db.refresh(db_sale)
    return db_sale


def delete_sale(db: Session, sale_id: int, owner_id: int) -> bool:
    db_sale = get_sale(db, sale_id, owner_id)
    if not db_sale:
        return False

    for item in db_sale.items:
        inventory_item = (
            db.query(InventoryItem)
            .filter(InventoryItem.id == item.inventory_item_id, InventoryItem.owner_id == owner_id)
            .first()
        )
        if inventory_item:
            inventory_item.quantity += item.quantity

    entry = None
    if db_sale.cashbook_entry_id:
        entry = db.query(CashbookEntry).filter(CashbookEntry.id == db_sale.cashbook_entry_id).first()

    receipt = None
    if entry and entry.receipt_id:
        receipt = db.query(CashbookReceipt).filter(CashbookReceipt.id == entry.receipt_id).first()

    if entry:
        db.delete(entry)
    if receipt:
        db.delete(receipt)

    db.delete(db_sale)
    db.commit()
    return True


def sales_report(
    db: Session, owner_id: int, from_date: date | None = None, to_date: date | None = None
) -> list[dict]:
    query = (
        db.query(
            Article.id,
            Article.name,
            SaleItem.quantity,
            SaleItem.line_total_gross,
            Sale.vat_rate,
        )
        .join(SaleItem, SaleItem.sale_id == Sale.id)
        .join(InventoryItem, InventoryItem.id == SaleItem.inventory_item_id)
        .join(Article, Article.id == InventoryItem.article_id)
        .filter(Sale.owner_id == owner_id)
    )
    if from_date:
        query = query.filter(Sale.sale_date >= from_date)
    if to_date:
        query = query.filter(Sale.sale_date <= to_date)

    aggregated: dict[int, dict] = {}
    for article_id, article_name, quantity, line_total_gross, vat_rate in query.all():
        row = aggregated.setdefault(
            article_id,
            {"article_id": article_id, "article_name": article_name, "quantity": 0.0, "amount_gross": 0.0, "amount_net": 0.0},
        )
        row["quantity"] += quantity
        row["amount_gross"] += line_total_gross
        row["amount_net"] += line_total_gross / (1 + vat_rate) if vat_rate else line_total_gross

    result = []
    for row in aggregated.values():
        row["amount_gross"] = round(row["amount_gross"], 2)
        row["amount_net"] = round(row["amount_net"], 2)
        result.append(row)
    result.sort(key=lambda r: r["article_name"])
    return result
