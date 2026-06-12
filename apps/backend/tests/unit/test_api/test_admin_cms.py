import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.user import User


def _login(client: TestClient, username: str, password: str) -> None:
    response = client.post("/api/auth/login", data={"username": username, "password": password})
    assert response.status_code == 200
    client.headers = {**client.headers, "Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture
def admin_user(db: Session) -> User:
    user = User(
        username="admin",
        email="admin@example.com",
        hashed_password=get_password_hash("AdminPassword123!"),
        is_active=True,
        is_verified=True,
        is_admin=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.mark.unit
@pytest.mark.api
def test_regular_user_cannot_access_admin_content(authenticated_client: tuple):
    client, token = authenticated_client

    response = client.get("/api/admin/content/pages")

    assert response.status_code == 403


@pytest.mark.unit
@pytest.mark.api
def test_admin_can_manage_user_status(client: TestClient, db: Session, admin_user: User, test_user: User):
    _login(client, "admin", "AdminPassword123!")

    response = client.patch(f"/api/users/{test_user.id}", json={"is_active": False})

    assert response.status_code == 200
    assert response.json()["is_active"] is False


@pytest.mark.unit
@pytest.mark.api
def test_admin_can_publish_app_text_override(client: TestClient, admin_user: User):
    _login(client, "admin", "AdminPassword123!")

    create_response = client.post(
        "/api/admin/content/app-texts",
        json={"key": "nav.dashboard", "locale": "de", "value": "Zentrale", "status": "published"},
    )
    public_response = client.get("/api/content/app-texts?locale=de")

    assert create_response.status_code == 201
    assert public_response.status_code == 200
    assert public_response.json()["nav.dashboard"] == "Zentrale"


@pytest.mark.unit
@pytest.mark.api
def test_draft_app_text_is_not_public(client: TestClient, admin_user: User):
    _login(client, "admin", "AdminPassword123!")

    create_response = client.post(
        "/api/admin/content/app-texts",
        json={"key": "nav.tasks", "locale": "de", "value": "Planung", "status": "draft"},
    )
    public_response = client.get("/api/content/app-texts?locale=de")

    assert create_response.status_code == 201
    assert "nav.tasks" not in public_response.json()
