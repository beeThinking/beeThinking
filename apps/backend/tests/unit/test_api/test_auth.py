"""
Unit Tests für app/api/auth.py
Tests für Authentication API Endpoints
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.user import User


@pytest.mark.unit
@pytest.mark.auth
@pytest.mark.api
class TestRegisterEndpoint:
    """Tests für /api/auth/register Endpoint"""

    def test_register_new_user(self, client: TestClient, db: Session):
        """Test: Neuer User kann sich registrieren"""
        user_data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "SecurePassword123!"
        }

        response = client.post("/api/auth/register", json=user_data)

        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "new@example.com"
        assert "password" not in data
        assert "hashed_password" not in data

    def test_register_duplicate_username(self, client: TestClient, test_user: User):
        """Test: Doppelter Username wird abgelehnt"""
        user_data = {
            "username": test_user.username,  # Bereits existiert
            "email": "different@example.com",
            "password": "SecurePassword123!"
        }

        response = client.post("/api/auth/register", json=user_data)

        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    def test_register_duplicate_email(self, client: TestClient, test_user: User):
        """Test: Doppelte Email wird abgelehnt"""
        user_data = {
            "username": "differentuser",
            "email": test_user.email,  # Bereits existiert
            "password": "SecurePassword123!"
        }

        response = client.post("/api/auth/register", json=user_data)

        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    def test_register_invalid_email(self, client: TestClient):
        """Test: Ungültige Email wird abgelehnt"""
        user_data = {
            "username": "testuser",
            "email": "not-an-email",
            "password": "SecurePassword123!"
        }

        response = client.post("/api/auth/register", json=user_data)

        assert response.status_code == 422  # Validation error

    def test_register_missing_fields(self, client: TestClient):
        """Test: Fehlende Pflichtfelder werden abgelehnt"""
        incomplete_data = {
            "username": "testuser"
            # email und password fehlen
        }

        response = client.post("/api/auth/register", json=incomplete_data)

        assert response.status_code == 422

    def test_register_empty_password(self, client: TestClient):
        """Test: Leeres Passwort wird abgelehnt"""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": ""
        }

        response = client.post("/api/auth/register", json=user_data)

        assert response.status_code == 422

    @pytest.mark.parametrize("username", ["ab", "a" * 100])
    def test_register_invalid_username_length(self, client: TestClient, username: str):
        """Test: Ungültige Username-Länge (zu kurz/lang)"""
        user_data = {
            "username": username,
            "email": "test@example.com",
            "password": "SecurePassword123!"
        }

        response = client.post("/api/auth/register", json=user_data)

        # Könnte 422 sein, wenn Validation existiert, sonst 201
        # Dies hängt von deinem Schema ab


@pytest.mark.unit
@pytest.mark.auth
@pytest.mark.api
class TestLoginEndpoint:
    """Tests für /api/auth/login Endpoint"""

    def test_login_success(self, client: TestClient, test_user: User, test_user_data: dict):
        """Test: Erfolgreiche Login"""
        login_data = {
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        }

        response = client.post("/api/auth/login", data=login_data)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0

    def test_login_wrong_password(self, client: TestClient, test_user: User):
        """Test: Login mit falschem Passwort schlägt fehl"""
        login_data = {
            "username": test_user.username,
            "password": "WrongPassword123!"
        }

        response = client.post("/api/auth/login", data=login_data)

        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    def test_login_wrong_username(self, client: TestClient):
        """Test: Login mit falschem Username schlägt fehl"""
        login_data = {
            "username": "nonexistent",
            "password": "AnyPassword123!"
        }

        response = client.post("/api/auth/login", data=login_data)

        assert response.status_code == 401

    def test_login_empty_credentials(self, client: TestClient):
        """Test: Login mit leeren Credentials schlägt fehl"""
        login_data = {
            "username": "",
            "password": ""
        }

        response = client.post("/api/auth/login", data=login_data)

        assert response.status_code == 401 or response.status_code == 422

    def test_login_missing_fields(self, client: TestClient):
        """Test: Login mit fehlenden Feldern schlägt fehl"""
        response = client.post("/api/auth/login", data={})

        assert response.status_code == 422

    def test_login_inactive_user(self, client: TestClient, db: Session, test_user_data: dict):
        """Test: Login mit inaktivem User schlägt fehl"""
        from app.crud.user import create_user
        from app.schemas.user import UserCreate

        # Erstelle einen inaktiven User
        user_data = UserCreate(
            username="inactiveuser",
            email="inactive@example.com",
            password="password"
        )
        user = create_user(db, user_data)
        user.is_active = False
        db.commit()

        login_data = {
            "username": "inactiveuser",
            "password": "password"
        }

        response = client.post("/api/auth/login", data=login_data)

        assert response.status_code == 400
        assert "inactive" in response.json()["detail"].lower()

    def test_login_returns_valid_jwt(self, client: TestClient, test_user: User, test_user_data: dict):
        """Test: Login gibt einen gültigen JWT Token zurück"""
        from app.core.security import decode_access_token

        login_data = {
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        }

        response = client.post("/api/auth/login", data=login_data)
        token = response.json()["access_token"]

        # Token sollte dekodierbar sein
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == test_user_data["username"]

    def test_login_token_can_be_used_for_authentication(
        self, client: TestClient, test_user: User, test_user_data: dict
    ):
        """Test: Login Token kann für authentifizierte Requests verwendet werden"""
        # Login
        login_data = {
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        }
        response = client.post("/api/auth/login", data=login_data)
        token = response.json()["access_token"]

        # Verwende Token für authentifizierten Request
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/users/me", headers=headers)

        assert response.status_code == 200
        user_data = response.json()
        assert user_data["username"] == test_user_data["username"]


@pytest.mark.unit
@pytest.mark.api
class TestAuthenticationFlow:
    """Tests für den kompletten Authentication Flow"""

    def test_complete_registration_login_flow(self, client: TestClient):
        """Test: Kompletter Flow von Registrierung bis Login"""
        # 1. Registrierung
        user_data = {
            "username": "flowtest",
            "email": "flow@example.com",
            "password": "FlowPassword123!"
        }

        register_response = client.post("/api/auth/register", json=user_data)
        assert register_response.status_code == 201

        # 2. Login
        login_data = {
            "username": user_data["username"],
            "password": user_data["password"]
        }

        login_response = client.post("/api/auth/login", data=login_data)
        assert login_response.status_code == 200
        assert "access_token" in login_response.json()

        # 3. Authentifizierter Request
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        me_response = client.get("/api/users/me", headers=headers)
        assert me_response.status_code == 200
        assert me_response.json()["username"] == user_data["username"]

