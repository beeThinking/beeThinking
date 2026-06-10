from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ContentSectionBase(BaseModel):
    sort_order: int = 0
    heading: str = Field(..., min_length=1, max_length=200)
    body: str = Field(..., min_length=1)


class ContentSectionCreate(ContentSectionBase):
    pass


class ContentSectionResponse(ContentSectionBase):
    id: int

    class Config:
        from_attributes = True


class ContentPageBase(BaseModel):
    slug: str = Field(..., min_length=1, max_length=120)
    locale: str = Field("de", min_length=2, max_length=8)
    title: str = Field(..., min_length=1, max_length=200)
    eyebrow: Optional[str] = Field(None, max_length=100)
    lead: Optional[str] = None
    cta_label: Optional[str] = Field(None, max_length=100)
    cta_link: Optional[str] = Field(None, max_length=300)
    status: str = Field("draft", pattern="^(draft|published)$")


class ContentPageCreate(ContentPageBase):
    sections: list[ContentSectionCreate] = []


class ContentPageUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    eyebrow: Optional[str] = Field(None, max_length=100)
    lead: Optional[str] = None
    cta_label: Optional[str] = Field(None, max_length=100)
    cta_link: Optional[str] = Field(None, max_length=300)
    status: Optional[str] = Field(None, pattern="^(draft|published)$")
    sections: Optional[list[ContentSectionCreate]] = None


class ContentPageResponse(ContentPageBase):
    id: int
    updated_by_user_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    sections: list[ContentSectionResponse] = []

    class Config:
        from_attributes = True
