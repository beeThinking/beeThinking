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
def admin_client(client: TestClient, db: Session) -> TestClient:
    user = User(
        username="cmsadmin",
        email="cmsadmin@example.com",
        hashed_password=get_password_hash("AdminPassword123!"),
        is_active=True,
        is_verified=True,
        is_admin=True,
    )
    db.add(user)
    db.commit()
    _login(client, "cmsadmin", "AdminPassword123!")
    return client


def _page_payload(slug: str, status: str) -> dict:
    return {
        "slug": slug,
        "locale": "de",
        "title": "Über uns",
        "lead": "BeeThinking Info",
        "status": status,
        "sections": [{"sort_order": 0, "heading": "Team", "body": "Wir imkern."}],
    }


@pytest.mark.unit
@pytest.mark.api
def test_published_page_is_public(admin_client: TestClient):
    create_response = admin_client.post("/api/admin/content/pages", json=_page_payload("about", "published"))
    assert create_response.status_code == 201

    admin_client.headers.pop("Authorization")
    response = admin_client.get("/api/content/pages/about")

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Über uns"
    assert body["sections"][0]["heading"] == "Team"


@pytest.mark.unit
@pytest.mark.api
def test_draft_page_is_not_public(admin_client: TestClient):
    create_response = admin_client.post("/api/admin/content/pages", json=_page_payload("secret", "draft"))
    assert create_response.status_code == 201

    admin_client.headers.pop("Authorization")
    response = admin_client.get("/api/content/pages/secret")

    assert response.status_code == 404


@pytest.mark.unit
@pytest.mark.api
def test_unknown_page_returns_404(client: TestClient):
    response = client.get("/api/content/pages/does-not-exist")

    assert response.status_code == 404


@pytest.mark.unit
@pytest.mark.api
def test_public_app_texts_empty_without_content(client: TestClient):
    response = client.get("/api/content/app-texts?locale=de")

    assert response.status_code == 200
    assert response.json() == {}
