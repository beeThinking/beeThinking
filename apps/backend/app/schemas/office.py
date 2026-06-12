from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, model_validator

from app.models.office import OfficeDocumentStatus, OfficeDocumentType, OfficePartnerType


class OfficePartnerBase(BaseModel):
    partner_type: OfficePartnerType
    name: str = Field(..., min_length=1, max_length=200)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=80)
    address: Optional[str] = None
    tax_id: Optional[str] = Field(None, max_length=80)
    notes: Optional[str] = None


class OfficePartnerCreate(OfficePartnerBase):
    pass


class OfficePartnerUpdate(BaseModel):
    partner_type: Optional[OfficePartnerType] = None
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=80)
    address: Optional[str] = None
    tax_id: Optional[str] = Field(None, max_length=80)
    notes: Optional[str] = None


class OfficePartnerResponse(OfficePartnerBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OfficeLineItem(BaseModel):
    description: str = Field(..., min_length=1, max_length=240)
    quantity: float = Field(1, ge=0)
    unit_price: float = Field(0, ge=0)
    tax_rate: float = Field(0, ge=0, le=100)

    @property
    def amount_gross(self) -> float:
        return round(self.quantity * self.unit_price, 2)


class OfficeDocumentBase(BaseModel):
    partner_id: Optional[int] = None
    document_type: OfficeDocumentType
    status: OfficeDocumentStatus = OfficeDocumentStatus.draft
    document_number: str = Field(..., min_length=1, max_length=80)
    title: str = Field(..., min_length=1, max_length=200)
    document_date: date
    due_date: Optional[date] = None
    amount_gross: float = Field(0, ge=0)
    tax_rate: float = Field(0, ge=0, le=100)
    tax_amount: float = Field(0, ge=0)
    amount_net: float = Field(0, ge=0)
    line_items: list[OfficeLineItem] = []
    notes: Optional[str] = None
    receipt_id: Optional[int] = None
    cashbook_entry_id: Optional[int] = None

    @model_validator(mode="after")
    def derive_amounts(self):
        if self.line_items:
            self.amount_gross = round(sum(item.amount_gross for item in self.line_items), 2)
            if self.tax_rate == 0:
                rates = {item.tax_rate for item in self.line_items}
                self.tax_rate = rates.pop() if len(rates) == 1 else 0
        if self.tax_amount == 0 and self.tax_rate > 0 and self.amount_gross > 0:
            self.tax_amount = round(self.amount_gross - (self.amount_gross / (1 + self.tax_rate / 100)), 2)
        if self.amount_net == 0 and self.amount_gross > 0:
            self.amount_net = round(self.amount_gross - self.tax_amount, 2)
        return self


class OfficeDocumentCreate(OfficeDocumentBase):
    pass


class OfficeDocumentUpdate(BaseModel):
    partner_id: Optional[int] = None
    document_type: Optional[OfficeDocumentType] = None
    status: Optional[OfficeDocumentStatus] = None
    document_number: Optional[str] = Field(None, min_length=1, max_length=80)
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    document_date: Optional[date] = None
    due_date: Optional[date] = None
    amount_gross: Optional[float] = Field(None, ge=0)
    tax_rate: Optional[float] = Field(None, ge=0, le=100)
    tax_amount: Optional[float] = Field(None, ge=0)
    amount_net: Optional[float] = Field(None, ge=0)
    line_items: Optional[list[OfficeLineItem]] = None
    notes: Optional[str] = None
    receipt_id: Optional[int] = None
    cashbook_entry_id: Optional[int] = None


class OfficeDocumentResponse(OfficeDocumentBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OfficeMonthlySummary(BaseModel):
    month: int
    income: float
    expenses: float
    balance: float


class OfficeCategorySummary(BaseModel):
    category: str
    income: float
    expenses: float


class OfficeDashboard(BaseModel):
    year: int
    month: Optional[int] = None
    income: float
    expenses: float
    balance: float
    monthly: list[OfficeMonthlySummary]
    categories: list[OfficeCategorySummary]
