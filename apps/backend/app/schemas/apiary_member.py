from datetime import datetime

from pydantic import BaseModel, Field

from app.models.apiary_member import ApiaryMemberRole


class ApiaryMemberCreate(BaseModel):
    username_or_email: str = Field(..., min_length=1, max_length=255)
    role: ApiaryMemberRole = ApiaryMemberRole.member


class ApiaryMemberUpdate(BaseModel):
    role: ApiaryMemberRole


class ApiaryMemberResponse(BaseModel):
    id: int
    apiary_id: int
    user_id: int
    role: ApiaryMemberRole
    invited_by_user_id: int | None = None
    accepted_at: datetime | None = None
    created_at: datetime

    class Config:
        from_attributes = True
