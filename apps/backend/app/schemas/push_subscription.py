from datetime import datetime

from pydantic import BaseModel, Field


class PushSubscriptionCreate(BaseModel):
    endpoint: str = Field(..., min_length=1)
    p256dh_key: str = Field(..., min_length=1)
    auth_key: str = Field(..., min_length=1)
    user_agent: str | None = None


class PushSubscriptionResponse(BaseModel):
    id: int
    user_id: int
    endpoint: str
    created_at: datetime

    class Config:
        from_attributes = True


class VapidPublicKeyResponse(BaseModel):
    public_key: str | None = None
    enabled: bool
