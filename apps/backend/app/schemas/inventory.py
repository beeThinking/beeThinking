from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.inventory import ArticleCategory


class ArticleBase(BaseModel):
    category: ArticleCategory = ArticleCategory.other
    name: str = Field(..., min_length=1, max_length=200)
    sku: Optional[str] = Field(None, max_length=80)
    weight_kg: Optional[float] = Field(None, ge=0)
    unit: str = Field("piece", min_length=1, max_length=40)
    notes: Optional[str] = Field(None, max_length=2000)


class ArticleCreate(ArticleBase):
    pass


class ArticleUpdate(BaseModel):
    category: Optional[ArticleCategory] = None
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    sku: Optional[str] = Field(None, max_length=80)
    weight_kg: Optional[float] = Field(None, ge=0)
    unit: Optional[str] = Field(None, min_length=1, max_length=40)
    notes: Optional[str] = Field(None, max_length=2000)


class ArticleResponse(ArticleBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class InventoryItemBase(BaseModel):
    article_id: int
    quantity: float = Field(0, ge=0)
    unit: str = Field("piece", min_length=1, max_length=40)
    price: Optional[float] = Field(None, ge=0)
    best_before: Optional[date] = None
    batch_code: Optional[str] = Field(None, max_length=120)
    archived: bool = False
    notes: Optional[str] = Field(None, max_length=2000)


class InventoryItemCreate(InventoryItemBase):
    pass


class InventoryItemUpdate(BaseModel):
    article_id: Optional[int] = None
    quantity: Optional[float] = Field(None, ge=0)
    unit: Optional[str] = Field(None, min_length=1, max_length=40)
    price: Optional[float] = Field(None, ge=0)
    best_before: Optional[date] = None
    batch_code: Optional[str] = Field(None, max_length=120)
    archived: Optional[bool] = None
    notes: Optional[str] = Field(None, max_length=2000)


class InventoryItemResponse(InventoryItemBase):
    id: int
    owner_id: int
    article: ArticleResponse
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
