from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator

from app.models.cashbook import CashbookDirection, OcrStatus


class CashbookEntryBase(BaseModel):
    apiary_id: Optional[int] = None
    booking_date: date
    direction: CashbookDirection
    category: str = Field(..., min_length=1, max_length=120)
    amount_gross: float = Field(..., ge=0)
    tax_rate: float = Field(0, ge=0, le=100)
    tax_amount: float = Field(0, ge=0)
    amount_net: float = Field(..., ge=0)
    counterparty: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    payment_method: Optional[str] = Field(None, max_length=80)
    receipt_id: Optional[int] = None

    @model_validator(mode="after")
    def derive_tax_amount(self):
        if self.tax_amount == 0 and self.tax_rate > 0 and self.amount_gross > 0:
            self.tax_amount = round(self.amount_gross - (self.amount_gross / (1 + self.tax_rate / 100)), 2)
        if self.amount_net == 0 and self.amount_gross > 0:
            self.amount_net = round(self.amount_gross - self.tax_amount, 2)
        return self


class CashbookEntryCreate(CashbookEntryBase):
    pass


class CashbookEntryUpdate(BaseModel):
    apiary_id: Optional[int] = None
    booking_date: Optional[date] = None
    direction: Optional[CashbookDirection] = None
    category: Optional[str] = Field(None, min_length=1, max_length=120)
    amount_gross: Optional[float] = Field(None, ge=0)
    tax_rate: Optional[float] = Field(None, ge=0, le=100)
    tax_amount: Optional[float] = Field(None, ge=0)
    amount_net: Optional[float] = Field(None, ge=0)
    counterparty: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    payment_method: Optional[str] = Field(None, max_length=80)
    receipt_id: Optional[int] = None


class CashbookEntryResponse(CashbookEntryBase):
    id: int
    owner_id: int
    performed_by_user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CashbookSummary(BaseModel):
    income: float
    expenses: float
    surplus: float


class CashbookReceiptSuggestionResponse(BaseModel):
    id: int
    field_name: str
    suggested_value: str
    confidence: float

    class Config:
        from_attributes = True


class CashbookReceiptResponse(BaseModel):
    id: int
    owner_id: int
    filename: str
    content_type: str
    size_bytes: int
    ocr_status: OcrStatus
    ocr_text: Optional[str] = None
    ocr_provider: Optional[str] = None
    created_at: datetime
    suggestions: list[CashbookReceiptSuggestionResponse] = []

    class Config:
        from_attributes = True
