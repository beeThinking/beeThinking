from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.apiary_member import ApiaryMemberRole


class ApiaryMemberCreate(BaseModel):
    username_or_email: str = Field(..., min_length=1, max_length=255)
    role: ApiaryMemberRole = ApiaryMemberRole.member


class ApiaryMemberUpdate(BaseModel):
    role: ApiaryMemberRole


class ApiaryMemberUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str


class ApiaryMemberApiaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    stock_number: str
    name: str | None = None


class ApiaryMemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    apiary_id: int
    user_id: int
    role: ApiaryMemberRole
    invited_by_user_id: int | None = None
    accepted_at: datetime | None = None
    created_at: datetime
    user: ApiaryMemberUserResponse
    apiary: ApiaryMemberApiaryResponse
