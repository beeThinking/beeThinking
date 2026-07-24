from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class SaleItemCreate(BaseModel):
    inventory_item_id: int
    quantity: float = Field(..., gt=0)
    unit_price_gross: float = Field(..., ge=0)


class SaleCreate(BaseModel):
    partner_id: Optional[int] = None
    sale_date: date = Field(default_factory=date.today)
    vat_rate: Optional[float] = Field(None, ge=0, le=1)
    notes: Optional[str] = Field(None, max_length=1000)
    items: list[SaleItemCreate] = Field(..., min_length=1)


class SaleItemResponse(BaseModel):
    id: int
    inventory_item_id: int
    quantity: float
    unit_price_gross: float
    line_total_gross: float

    class Config:
        from_attributes = True


class SaleResponse(BaseModel):
    id: int
    owner_id: int
    partner_id: Optional[int] = None
    sale_date: date
    vat_rate: float
    amount_gross: float
    amount_net: float
    notes: Optional[str] = None
    cashbook_entry_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: list[SaleItemResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


class SaleReportRow(BaseModel):
    article_id: int
    article_name: str
    quantity: float
    amount_gross: float
    amount_net: float
