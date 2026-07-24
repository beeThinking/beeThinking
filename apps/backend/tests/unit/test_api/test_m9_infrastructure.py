from datetime import datetime, timedelta, timezone
import zipfile
from io import BytesIO
from pathlib import Path
from threading import Barrier, Thread

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core import rate_limit
from app.crud.refresh_token import issue_refresh_token, rotate_refresh_token
from app.db.database import Base
from app.models.refresh_token import RefreshToken
from app.models.user import User


@pytest.mark.unit
def test_refresh_rotation_rejects_reuse_and_revokes_family(client, test_user, test_user_data, db):
    login = client.post("/api/auth/login", data={"username": test_user_data["username"], "password": test_user_data["password"]})
    initial = login.json()["refresh_token"]
    refreshed = client.post("/api/auth/refresh", json={"refresh_token": initial})
    assert refreshed.status_code == 200
    replacement = refreshed.json()["refresh_token"]
    assert client.post("/api/auth/refresh", json={"refresh_token": initial}).status_code == 401
    assert client.post("/api/auth/refresh", json={"refresh_token": replacement}).status_code == 401
    assert db.query(RefreshToken).filter(RefreshToken.reuse_detected.is_(True)).count() == 1


@pytest.mark.unit
def test_refresh_rotation_allows_only_one_concurrent_replacement(tmp_path: Path, test_user_data):
    engine = create_engine(
        f"sqlite:///{tmp_path / 'refresh-race.db'}",
        connect_args={"check_same_thread": False, "timeout": 10},
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    setup_session = session_factory()
    user = User(username=test_user_data["username"], email=test_user_data["email"], hashed_password="hash", is_active=True)
    setup_session.add(user)
    setup_session.commit()
    refresh_token, _ = issue_refresh_token(setup_session, user)
    setup_session.commit()
    setup_session.close()

    barrier = Barrier(2)
    results = []

    def rotate() -> None:
        session = session_factory()
        barrier.wait()
        results.append(rotate_refresh_token(session, refresh_token))
        session.close()

    threads = [Thread(target=rotate), Thread(target=rotate)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert sum(result is not None for result in results) == 1
    verification_session = session_factory()
    assert verification_session.query(RefreshToken).filter(RefreshToken.revoked_at.is_(None)).count() == 0
    assert verification_session.query(RefreshToken).filter(RefreshToken.reuse_detected.is_(True)).count() == 1
    verification_session.close()
    engine.dispose()


@pytest.mark.unit
def test_refresh_logout_and_expiry(client, test_user, test_user_data, db):
    refresh_token = client.post("/api/auth/login", data={"username": test_user_data["username"], "password": test_user_data["password"]}).json()["refresh_token"]
    assert client.post("/api/auth/logout", json={"refresh_token": refresh_token}).status_code == 204
    assert client.post("/api/auth/refresh", json={"refresh_token": refresh_token}).status_code == 401
    fresh_token = client.post("/api/auth/login", data={"username": test_user_data["username"], "password": test_user_data["password"]}).json()["refresh_token"]
    record = db.query(RefreshToken).filter(RefreshToken.token_hash.is_not(None), RefreshToken.revoked_at.is_(None)).one()
    record.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    db.commit()
    assert client.post("/api/auth/refresh", json={"refresh_token": fresh_token}).status_code == 401


@pytest.mark.unit
def test_auth_rate_limit_returns_retry_after(client):
    payload = {"username": "rateuser", "email": "rate@example.com", "password": "SecurePassword123!"}
    for _ in range(5):
        client.post("/api/auth/register", json=payload)
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 429
    assert "Retry-After" in response.headers


@pytest.mark.unit
def test_rate_limit_uses_forwarded_address_only_for_trusted_proxy(monkeypatch):
    class Settings:
        TRUST_PROXY_HEADERS = True
        trusted_proxy_ips_set = {"10.0.0.1"}

    class Request:
        def __init__(self, remote_address: str):
            self.client = type("Client", (), {"host": remote_address})()
            self.headers = {"X-Forwarded-For": "198.51.100.9, 10.0.0.1"}

    monkeypatch.setattr(rate_limit, "get_settings", lambda: Settings())
    assert rate_limit.get_rate_limit_key(Request("10.0.0.1")) == "198.51.100.9"
    assert rate_limit.get_rate_limit_key(Request("198.51.100.8")) == "198.51.100.8"


@pytest.mark.unit
def test_metrics_is_admin_protected_and_export_excludes_password_and_blobs(authenticated_client, test_user, db):
    client, _ = authenticated_client
    assert client.get("/metrics").status_code == 403
    export = client.get("/api/users/me/export")
    assert export.status_code == 200
    with zipfile.ZipFile(BytesIO(export.content)) as archive:
        payload = archive.read("account-export.json").decode()
    assert "hashed_password" not in payload
    assert "object blobs are not included" in payload
