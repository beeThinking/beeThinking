from datetime import datetime

from pydantic import BaseModel


class GoogleCalendarAuthorizationResponse(BaseModel):
    authorization_url: str


class GoogleCalendarStatusResponse(BaseModel):
    enabled: bool
    connected: bool
    calendar_name: str | None = None
    last_sync_at: datetime | None = None
    last_error: str | None = None


class GoogleCalendarSyncResponse(BaseModel):
    created: int
    updated: int
    deleted: int
    synced_at: datetime
