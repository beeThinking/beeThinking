from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PhotoBase(BaseModel):
    hive_id: Optional[int] = None
    inspection_id: Optional[int] = None
    object_key: str = Field(..., min_length=1, max_length=500)
    filename: str = Field(..., min_length=1, max_length=255)
    content_type: str = Field(..., min_length=1, max_length=100)
    size_bytes: int = Field(..., ge=0)
    caption: Optional[str] = Field(None, max_length=500)


class PhotoCreate(PhotoBase):
    pass


class PhotoResponse(PhotoBase):
    id: int
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True
