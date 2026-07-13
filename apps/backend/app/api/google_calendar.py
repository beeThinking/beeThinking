from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user
from app.core.config import get_settings
from app.db.database import get_db
from app.models.user import User
from app.schemas.google_calendar import (
    GoogleCalendarAuthorizationResponse,
    GoogleCalendarStatusResponse,
    GoogleCalendarSyncResponse,
)
from app.services.google_calendar import (
    GoogleCalendarError,
    complete_authorization,
    connection_status,
    create_authorization_url,
    disconnect_calendar,
    sync_calendar,
)


router = APIRouter()


@router.get("/status", response_model=GoogleCalendarStatusResponse)
def get_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return connection_status(db, current_user.id)


@router.post("/oauth/start", response_model=GoogleCalendarAuthorizationResponse)
def start_oauth(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        return {"authorization_url": create_authorization_url(db, current_user.id)}
    except GoogleCalendarError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc


@router.get("/oauth/callback", include_in_schema=False)
def oauth_callback(
    state: str = Query(...),
    code: str | None = Query(None),
    error: str | None = Query(None),
    db: Session = Depends(get_db),
):
    settings = get_settings()
    if error or not code:
        query = urlencode({"google": "error", "reason": error or "missing_code"})
        return RedirectResponse(f"{settings.GOOGLE_CALENDAR_FRONTEND_URL}?{query}")
    try:
        connection = complete_authorization(db, state, code)
        try:
            sync_calendar(db, connection.user_id)
        except GoogleCalendarError:
            pass
        query = urlencode({"google": "connected"})
    except GoogleCalendarError:
        query = urlencode({"google": "error", "reason": "connection_failed"})
    return RedirectResponse(f"{settings.GOOGLE_CALENDAR_FRONTEND_URL}?{query}")


@router.post("/sync", response_model=GoogleCalendarSyncResponse)
def sync(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        return sync_calendar(db, current_user.id)
    except GoogleCalendarError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.delete("/connection", status_code=status.HTTP_204_NO_CONTENT)
def disconnect(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    disconnect_calendar(db, current_user.id)
