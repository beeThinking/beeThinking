from datetime import date, datetime, timedelta, timezone
from urllib.parse import parse_qs, urlparse

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.models.google_calendar import GoogleCalendarConnection, GoogleCalendarEvent, GoogleOAuthState
from app.models.task import Task, TaskKind
from app.models.user import User
from app.services.google_calendar import (
    complete_authorization,
    create_authorization_url,
    decrypt_refresh_token,
    encrypt_refresh_token,
    sync_calendar,
    _pull_remote_changes,
)


class FakeResponse:
    def __init__(self, data: dict | None = None, status_code: int = 200):
        self.data = data or {}
        self.status_code = status_code
        self.ok = 200 <= status_code < 300

    def json(self):
        return self.data


def google_settings() -> Settings:
    return Settings(
        DATABASE_URL="sqlite://",
        SECRET_KEY="test-secret",
        GOOGLE_CALENDAR_CLIENT_ID="client-id",
        GOOGLE_CALENDAR_CLIENT_SECRET="client-secret",
        GOOGLE_CALENDAR_TOKEN_KEY="separate-token-key",
    )


def test_status_requires_authentication(client: TestClient):
    response = client.get("/api/google-calendar/status")

    assert response.status_code == 401


def test_oauth_start_uses_single_use_hashed_state(
    authenticated_client: tuple[TestClient, str],
    db: Session,
    monkeypatch,
):
    client, _ = authenticated_client
    settings = get_settings()
    monkeypatch.setattr(settings, "GOOGLE_CALENDAR_CLIENT_ID", "client-id")
    monkeypatch.setattr(settings, "GOOGLE_CALENDAR_CLIENT_SECRET", "client-secret")

    response = client.post("/api/google-calendar/oauth/start")

    assert response.status_code == 200
    authorization_url = response.json()["authorization_url"]
    query = parse_qs(urlparse(authorization_url).query)
    state = query["state"][0]
    saved_state = db.query(GoogleOAuthState).one()
    assert saved_state.state_hash != state
    assert query["access_type"] == ["offline"]
    assert query["scope"] == ["https://www.googleapis.com/auth/calendar.app.created"]


def test_refresh_tokens_are_encrypted():
    settings = google_settings()

    encrypted = encrypt_refresh_token("refresh-secret", settings)

    assert "refresh-secret" not in encrypted
    assert decrypt_refresh_token(encrypted, settings) == "refresh-secret"


def test_authorization_creates_dedicated_calendar_and_consumes_state(db: Session, test_user: User, monkeypatch):
    settings = google_settings()
    authorization_url = create_authorization_url(db, test_user.id, settings)
    state = parse_qs(urlparse(authorization_url).query)["state"][0]

    def request(method, url, **kwargs):
        if url.endswith("/token"):
            return FakeResponse({"access_token": "access-token", "refresh_token": "refresh-token"})
        if url.endswith("/calendars"):
            assert kwargs["json"]["summary"] == "BeeThinking"
            return FakeResponse({"id": "bee-calendar@example.com"})
        raise AssertionError(f"Unexpected Google request: {method} {url}")

    monkeypatch.setattr("app.services.google_calendar.requests.request", request)

    connection = complete_authorization(db, state, "auth-code", settings)

    assert connection.calendar_id == "bee-calendar@example.com"
    assert decrypt_refresh_token(connection.refresh_token_encrypted, settings) == "refresh-token"
    assert db.query(GoogleOAuthState).count() == 0


def test_sync_creates_updates_and_removes_google_events(db: Session, test_user: User, monkeypatch):
    settings = google_settings()
    authorization_url = create_authorization_url(db, test_user.id, settings)
    state = parse_qs(urlparse(authorization_url).query)["state"][0]
    inserted_payloads = []

    def request(method, url, **kwargs):
        if url.endswith("/token") and kwargs.get("data", {}).get("grant_type") == "authorization_code":
            return FakeResponse({"access_token": "first-access", "refresh_token": "refresh-token"})
        if url.endswith("/token"):
            return FakeResponse({"access_token": "refreshed-access"})
        if url.endswith("/calendars"):
            return FakeResponse({"id": "bee-calendar@example.com"})
        if url.endswith("/events"):
            inserted_payloads.append(kwargs["json"])
            return FakeResponse({"id": "google-event-1"})
        raise AssertionError(f"Unexpected Google request: {method} {url}")

    monkeypatch.setattr("app.services.google_calendar.requests.request", request)
    complete_authorization(db, state, "auth-code", settings)
    task = Task(
        owner_id=test_user.id,
        title="Hive inspection",
        description="Bring smoker",
        start_at=datetime(2026, 7, 20, 8, 0, tzinfo=timezone.utc),
        end_at=datetime(2026, 7, 20, 9, 0, tzinfo=timezone.utc),
        kind=TaskKind.appointment,
    )
    db.add(task)
    db.commit()

    created = sync_calendar(db, test_user.id, settings)

    assert created["created"] == 1
    assert inserted_payloads[0]["summary"] == "Hive inspection"
    assert inserted_payloads[0]["visibility"] == "private"
    mapping = db.query(GoogleCalendarEvent).one()

    monkeypatch.setattr(
        "app.services.google_calendar.requests.get",
        lambda *args, **kwargs: FakeResponse(status_code=404),
    )
    monkeypatch.setattr(
        "app.services.google_calendar.requests.put",
        lambda *args, **kwargs: FakeResponse({"id": mapping.google_event_id}),
    )
    updated = sync_calendar(db, test_user.id, settings)
    assert updated["updated"] == 1

    db.delete(task)
    db.commit()
    monkeypatch.setattr(
        "app.services.google_calendar.requests.delete",
        lambda *args, **kwargs: FakeResponse(status_code=204),
    )
    deleted = sync_calendar(db, test_user.id, settings)
    assert deleted["deleted"] == 1
    assert db.query(GoogleCalendarEvent).count() == 0


def test_sync_recreates_event_deleted_on_google(db: Session, test_user: User, monkeypatch):
    settings = google_settings()
    authorization_url = create_authorization_url(db, test_user.id, settings)
    state = parse_qs(urlparse(authorization_url).query)["state"][0]
    created_event_ids = iter(["google-event-1", "google-event-2"])

    def request(method, url, **kwargs):
        if url.endswith("/token") and kwargs.get("data", {}).get("grant_type") == "authorization_code":
            return FakeResponse({"access_token": "first-access", "refresh_token": "refresh-token"})
        if url.endswith("/token"):
            return FakeResponse({"access_token": "refreshed-access"})
        if url.endswith("/calendars"):
            return FakeResponse({"id": "bee-calendar@example.com"})
        if url.endswith("/events"):
            return FakeResponse({"id": next(created_event_ids)})
        raise AssertionError(f"Unexpected Google request: {method} {url}")

    monkeypatch.setattr("app.services.google_calendar.requests.request", request)
    complete_authorization(db, state, "auth-code", settings)
    task = Task(
        owner_id=test_user.id,
        title="Hive inspection",
        start_at=datetime(2026, 7, 20, 8, 0, tzinfo=timezone.utc),
        kind=TaskKind.appointment,
    )
    db.add(task)
    db.commit()
    sync_calendar(db, test_user.id, settings)

    monkeypatch.setattr(
        "app.services.google_calendar.requests.get",
        lambda *args, **kwargs: FakeResponse(status_code=404),
    )
    monkeypatch.setattr(
        "app.services.google_calendar.requests.put",
        lambda *args, **kwargs: FakeResponse(status_code=404),
    )
    result = sync_calendar(db, test_user.id, settings)

    assert result["created"] == 1
    assert result["updated"] == 0
    mapping = db.query(GoogleCalendarEvent).one()
    assert mapping.google_event_id == "google-event-2"


def test_sync_pulls_remote_edit_when_newer_than_local(db: Session, test_user: User, monkeypatch):
    settings = google_settings()
    authorization_url = create_authorization_url(db, test_user.id, settings)
    state = parse_qs(urlparse(authorization_url).query)["state"][0]

    def request(method, url, **kwargs):
        if url.endswith("/token") and kwargs.get("data", {}).get("grant_type") == "authorization_code":
            return FakeResponse({"access_token": "first-access", "refresh_token": "refresh-token"})
        if url.endswith("/token"):
            return FakeResponse({"access_token": "refreshed-access"})
        if url.endswith("/calendars"):
            return FakeResponse({"id": "bee-calendar@example.com"})
        if url.endswith("/events"):
            return FakeResponse({"id": "google-event-1"})
        raise AssertionError(f"Unexpected Google request: {method} {url}")

    monkeypatch.setattr("app.services.google_calendar.requests.request", request)
    complete_authorization(db, state, "auth-code", settings)

    local_updated = datetime(2026, 7, 1, 8, 0, tzinfo=timezone.utc)
    task = Task(
        owner_id=test_user.id,
        title="Original title",
        start_at=datetime(2026, 7, 20, 8, 0, tzinfo=timezone.utc),
        kind=TaskKind.appointment,
    )
    db.add(task)
    db.commit()
    task.updated_at = local_updated
    db.commit()

    monkeypatch.setattr(
        "app.services.google_calendar.requests.get",
        lambda *args, **kwargs: FakeResponse(status_code=404),
    )
    monkeypatch.setattr(
        "app.services.google_calendar.requests.put",
        lambda *args, **kwargs: FakeResponse({"id": "google-event-1"}),
    )
    sync_calendar(db, test_user.id, settings)

    remote_updated_at = (local_updated + timedelta(days=1)).isoformat().replace("+00:00", "Z")
    monkeypatch.setattr(
        "app.services.google_calendar.requests.get",
        lambda *args, **kwargs: FakeResponse({
            "summary": "Edited on Google",
            "description": "Changed remotely",
            "updated": remote_updated_at,
            "start": {"dateTime": "2026-07-21T09:00:00+00:00"},
            "end": {"dateTime": "2026-07-21T10:00:00+00:00"},
        }),
    )

    result = sync_calendar(db, test_user.id, settings)

    assert result["pulled"] == 1
    db.refresh(task)
    assert task.title == "Edited on Google"
    assert task.description == "Changed remotely"


def test_sync_does_not_pull_older_remote_edit(db: Session, test_user: User, monkeypatch):
    settings = google_settings()
    authorization_url = create_authorization_url(db, test_user.id, settings)
    state = parse_qs(urlparse(authorization_url).query)["state"][0]

    def request(method, url, **kwargs):
        if url.endswith("/token") and kwargs.get("data", {}).get("grant_type") == "authorization_code":
            return FakeResponse({"access_token": "first-access", "refresh_token": "refresh-token"})
        if url.endswith("/token"):
            return FakeResponse({"access_token": "refreshed-access"})
        if url.endswith("/calendars"):
            return FakeResponse({"id": "bee-calendar@example.com"})
        if url.endswith("/events"):
            return FakeResponse({"id": "google-event-1"})
        raise AssertionError(f"Unexpected Google request: {method} {url}")

    monkeypatch.setattr("app.services.google_calendar.requests.request", request)
    complete_authorization(db, state, "auth-code", settings)

    local_updated = datetime(2026, 7, 5, 8, 0, tzinfo=timezone.utc)
    task = Task(
        owner_id=test_user.id,
        title="Kept local title",
        start_at=datetime(2026, 7, 20, 8, 0, tzinfo=timezone.utc),
        kind=TaskKind.appointment,
    )
    db.add(task)
    db.commit()
    task.updated_at = local_updated
    db.commit()

    monkeypatch.setattr(
        "app.services.google_calendar.requests.get",
        lambda *args, **kwargs: FakeResponse(status_code=404),
    )
    monkeypatch.setattr(
        "app.services.google_calendar.requests.put",
        lambda *args, **kwargs: FakeResponse({"id": "google-event-1"}),
    )
    sync_calendar(db, test_user.id, settings)

    older_remote_updated_at = (local_updated - timedelta(days=1)).isoformat().replace("+00:00", "Z")
    monkeypatch.setattr(
        "app.services.google_calendar.requests.get",
        lambda *args, **kwargs: FakeResponse({
            "summary": "Stale remote title",
            "updated": older_remote_updated_at,
            "start": {"dateTime": "2026-07-20T08:00:00+00:00"},
        }),
    )

    result = sync_calendar(db, test_user.id, settings)

    assert result["pulled"] == 0
    db.refresh(task)
    assert task.title == "Kept local title"


def test_pull_remote_all_day_event_updates_due_date(db: Session, test_user: User, monkeypatch):
    task = Task(
        owner_id=test_user.id,
        title="Timed appointment",
        due_date=date(2026, 7, 20),
        start_at=datetime(2026, 7, 20, 8, 0, tzinfo=timezone.utc),
        end_at=datetime(2026, 7, 20, 9, 0, tzinfo=timezone.utc),
        kind=TaskKind.appointment,
    )
    connection = GoogleCalendarConnection(
        user_id=test_user.id,
        calendar_id="calendar",
        refresh_token_encrypted="encrypted-token",
    )
    db.add_all([task, connection])
    db.commit()
    task.updated_at = datetime(2026, 7, 1, tzinfo=timezone.utc)
    db.add(GoogleCalendarEvent(user_id=test_user.id, task_id=task.id, google_event_id="event"))
    db.commit()
    monkeypatch.setattr(
        "app.services.google_calendar.requests.get",
        lambda *args, **kwargs: FakeResponse({
            "updated": "2026-07-02T00:00:00Z",
            "start": {"date": "2026-07-23"},
            "end": {"date": "2026-07-24"},
        }),
    )

    pulled = _pull_remote_changes(db, connection, test_user.id, "access-token")

    assert pulled == {task.id}
    assert task.due_date == date(2026, 7, 23)
    assert task.start_at is None
    assert task.end_at is None
