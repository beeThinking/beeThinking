import base64
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from urllib.parse import quote, urlencode

import requests
from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.models.google_calendar import GoogleCalendarConnection, GoogleCalendarEvent, GoogleOAuthState
from app.models.task import Task, TaskKind, TaskStatus


GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_REVOKE_URL = "https://oauth2.googleapis.com/revoke"
GOOGLE_CALENDAR_API = "https://www.googleapis.com/calendar/v3"
GOOGLE_CALENDAR_SCOPE = "https://www.googleapis.com/auth/calendar.app.created"


class GoogleCalendarError(RuntimeError):
    pass


def create_authorization_url(db: Session, user_id: int, settings: Settings | None = None) -> str:
    settings = settings or get_settings()
    if not settings.google_calendar_enabled:
        raise GoogleCalendarError("Google Calendar is not configured")
    now = datetime.now(timezone.utc)
    db.query(GoogleOAuthState).filter(GoogleOAuthState.expires_at < now).delete(synchronize_session=False)
    state = secrets.token_urlsafe(32)
    db.add(GoogleOAuthState(
        user_id=user_id,
        state_hash=_state_hash(state),
        expires_at=now + timedelta(minutes=10),
    ))
    db.commit()
    parameters = {
        'client_id': settings.GOOGLE_CALENDAR_CLIENT_ID,
        'redirect_uri': settings.GOOGLE_CALENDAR_REDIRECT_URI,
        'response_type': 'code',
        'scope': GOOGLE_CALENDAR_SCOPE,
        'access_type': 'offline',
        'prompt': 'consent',
        'state': state,
    }
    return f"{GOOGLE_AUTH_URL}?{urlencode(parameters)}"


def complete_authorization(
    db: Session,
    state: str,
    code: str,
    settings: Settings | None = None,
) -> GoogleCalendarConnection:
    settings = settings or get_settings()
    now = datetime.now(timezone.utc)
    oauth_state = db.query(GoogleOAuthState).filter(
        GoogleOAuthState.state_hash == _state_hash(state),
        GoogleOAuthState.expires_at >= now,
    ).first()
    if not oauth_state:
        raise GoogleCalendarError("OAuth state is invalid or expired")
    user_id = oauth_state.user_id
    db.delete(oauth_state)
    db.commit()

    token_data = _request_json(
        "POST",
        GOOGLE_TOKEN_URL,
        data={
            "client_id": settings.GOOGLE_CALENDAR_CLIENT_ID,
            "client_secret": settings.GOOGLE_CALENDAR_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": settings.GOOGLE_CALENDAR_REDIRECT_URI,
        },
    )
    access_token = token_data.get("access_token")
    refresh_token = token_data.get("refresh_token")
    if not access_token or not refresh_token:
        raise GoogleCalendarError("Google did not return offline access credentials")

    connection = db.query(GoogleCalendarConnection).filter_by(user_id=user_id).first()
    calendar_id = _usable_calendar_id(connection, access_token)
    if not calendar_id:
        calendar = _request_json(
            "POST",
            f"{GOOGLE_CALENDAR_API}/calendars",
            token=access_token,
            json={"summary": "BeeThinking", "description": "Appointments mirrored from BeeThinking"},
        )
        calendar_id = calendar.get("id")
    if not calendar_id:
        raise GoogleCalendarError("Google Calendar could not be created")

    if connection is None:
        connection = GoogleCalendarConnection(user_id=user_id)
        db.add(connection)
    connection.refresh_token_encrypted = encrypt_refresh_token(refresh_token, settings)
    connection.calendar_id = calendar_id
    connection.calendar_name = "BeeThinking"
    connection.connected_at = now
    connection.last_error = None
    db.commit()
    db.refresh(connection)
    return connection


def connection_status(db: Session, user_id: int, settings: Settings | None = None) -> dict:
    settings = settings or get_settings()
    connection = db.query(GoogleCalendarConnection).filter_by(user_id=user_id).first()
    return {
        "enabled": settings.google_calendar_enabled,
        "connected": connection is not None,
        "calendar_name": connection.calendar_name if connection else None,
        "last_sync_at": connection.last_sync_at if connection else None,
        "last_error": connection.last_error if connection else None,
    }


def sync_calendar(db: Session, user_id: int, settings: Settings | None = None) -> dict:
    settings = settings or get_settings()
    connection = db.query(GoogleCalendarConnection).filter_by(user_id=user_id).first()
    if not connection:
        raise GoogleCalendarError("Google Calendar is not connected")
    try:
        access_token = _refresh_access_token(connection, settings)
        tasks = db.query(Task).filter(
            Task.owner_id == user_id,
            Task.kind == TaskKind.appointment,
            Task.status != TaskStatus.cancelled,
        ).all()
        exportable = {task.id: task for task in tasks if task.start_at or task.due_date}
        mappings = {
            mapping.task_id: mapping
            for mapping in db.query(GoogleCalendarEvent).filter_by(user_id=user_id).all()
        }
        created = updated = deleted = 0

        for task_id, task in exportable.items():
            mapping = mappings.pop(task_id, None)
            payload = _event_payload(task)
            if mapping:
                response = requests.put(
                    _event_url(connection.calendar_id, mapping.google_event_id),
                    headers=_authorization_header(access_token),
                    json=payload,
                    timeout=15,
                )
                if response.status_code == 404:
                    db.delete(mapping)
                    mapping = None
                elif not response.ok:
                    raise GoogleCalendarError(_google_error(response))
                else:
                    mapping.synced_at = datetime.now(timezone.utc)
                    updated += 1
            if mapping is None:
                event = _request_json(
                    "POST",
                    f"{GOOGLE_CALENDAR_API}/calendars/{quote(connection.calendar_id, safe='')}/events",
                    token=access_token,
                    json=payload,
                )
                if not event.get("id"):
                    raise GoogleCalendarError("Google event ID is missing")
                db.add(GoogleCalendarEvent(
                    user_id=user_id,
                    task_id=task_id,
                    google_event_id=event["id"],
                    synced_at=datetime.now(timezone.utc),
                ))
                created += 1

        for mapping in mappings.values():
            response = requests.delete(
                _event_url(connection.calendar_id, mapping.google_event_id),
                headers=_authorization_header(access_token),
                timeout=15,
            )
            if response.status_code not in {204, 404} and not response.ok:
                raise GoogleCalendarError(_google_error(response))
            db.delete(mapping)
            deleted += 1

        synced_at = datetime.now(timezone.utc)
        connection.last_sync_at = synced_at
        connection.last_error = None
        db.commit()
        return {"created": created, "updated": updated, "deleted": deleted, "synced_at": synced_at}
    except (GoogleCalendarError, requests.RequestException, InvalidToken) as exc:
        db.rollback()
        connection = db.query(GoogleCalendarConnection).filter_by(user_id=user_id).first()
        if connection:
            connection.last_error = str(exc)
            db.commit()
        if isinstance(exc, GoogleCalendarError):
            raise
        raise GoogleCalendarError("Google Calendar request failed") from exc


def disconnect_calendar(db: Session, user_id: int, settings: Settings | None = None) -> bool:
    settings = settings or get_settings()
    connection = db.query(GoogleCalendarConnection).filter_by(user_id=user_id).first()
    if not connection:
        return False
    try:
        refresh_token = decrypt_refresh_token(connection.refresh_token_encrypted, settings)
        requests.post(GOOGLE_REVOKE_URL, data={"token": refresh_token}, timeout=10)
    except (InvalidToken, requests.RequestException):
        pass
    db.query(GoogleCalendarEvent).filter_by(user_id=user_id).delete(synchronize_session=False)
    db.query(GoogleOAuthState).filter_by(user_id=user_id).delete(synchronize_session=False)
    db.delete(connection)
    db.commit()
    return True


def encrypt_refresh_token(token: str, settings: Settings | None = None) -> str:
    return _fernet(settings or get_settings()).encrypt(token.encode()).decode()


def decrypt_refresh_token(token: str, settings: Settings | None = None) -> str:
    return _fernet(settings or get_settings()).decrypt(token.encode()).decode()


def _refresh_access_token(connection: GoogleCalendarConnection, settings: Settings) -> str:
    token_data = _request_json(
        "POST",
        GOOGLE_TOKEN_URL,
        data={
            "client_id": settings.GOOGLE_CALENDAR_CLIENT_ID,
            "client_secret": settings.GOOGLE_CALENDAR_CLIENT_SECRET,
            "refresh_token": decrypt_refresh_token(connection.refresh_token_encrypted, settings),
            "grant_type": "refresh_token",
        },
    )
    access_token = token_data.get("access_token")
    if not access_token:
        raise GoogleCalendarError("Google access token refresh failed")
    return access_token


def _event_payload(task: Task) -> dict:
    payload = {
        "summary": task.title,
        "description": task.description or "",
        "location": _task_location(task),
        "extendedProperties": {"private": {"beethinkingTaskId": str(task.id)}},
        "visibility": "private",
    }
    if task.start_at:
        start = _aware(task.start_at)
        end = _aware(task.end_at) if task.end_at else start + timedelta(hours=1)
        payload["start"] = {"dateTime": start.isoformat()}
        payload["end"] = {"dateTime": end.isoformat()}
    else:
        start_date = task.due_date
        payload["start"] = {"date": start_date.isoformat()}
        payload["end"] = {"date": (start_date + timedelta(days=1)).isoformat()}
    return payload


def _task_location(task: Task) -> str:
    if task.hive:
        return task.hive.name
    if task.apiary:
        return task.apiary.name or task.apiary.stock_number
    return ""


def _aware(value: datetime) -> datetime:
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


def _usable_calendar_id(connection: GoogleCalendarConnection | None, access_token: str) -> str | None:
    if not connection:
        return None
    response = requests.get(
        f"{GOOGLE_CALENDAR_API}/calendars/{quote(connection.calendar_id, safe='')}",
        headers=_authorization_header(access_token),
        timeout=15,
    )
    return connection.calendar_id if response.ok else None


def _event_url(calendar_id: str, event_id: str) -> str:
    return f"{GOOGLE_CALENDAR_API}/calendars/{quote(calendar_id, safe='')}/events/{quote(event_id, safe='')}"


def _request_json(method: str, url: str, token: str | None = None, **kwargs) -> dict:
    headers = kwargs.pop("headers", {})
    if token:
        headers.update(_authorization_header(token))
    try:
        response = requests.request(method, url, headers=headers, timeout=15, **kwargs)
    except requests.RequestException as exc:
        raise GoogleCalendarError("Google Calendar request failed") from exc
    if not response.ok:
        raise GoogleCalendarError(_google_error(response))
    try:
        return response.json()
    except ValueError as exc:
        raise GoogleCalendarError("Google returned an invalid response") from exc


def _google_error(response: requests.Response) -> str:
    try:
        detail = response.json().get("error", {})
        if isinstance(detail, dict):
            return detail.get("message") or f"Google request failed ({response.status_code})"
        return str(detail)
    except ValueError:
        return f"Google request failed ({response.status_code})"


def _authorization_header(access_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}"}


def _state_hash(state: str) -> str:
    return hashlib.sha256(state.encode()).hexdigest()


def _fernet(settings: Settings) -> Fernet:
    source = settings.GOOGLE_CALENDAR_TOKEN_KEY or settings.SECRET_KEY
    key = base64.urlsafe_b64encode(hashlib.sha256(source.encode()).digest())
    return Fernet(key)
