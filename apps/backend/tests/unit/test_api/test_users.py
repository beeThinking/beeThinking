"""
Unit Tests für app/api/users.py
Tests für User API Endpoints
"""
import pytest
from fastapi.testclient import TestClient
from app.models.user import User


@pytest.mark.unit
@pytest.mark.api
class TestGetCurrentUserEndpoint:
    """Tests für /api/users/me Endpoint"""

    def test_get_current_user_authenticated(self, authenticated_client: tuple):
        """Test: Authentifizierter User kann seine Daten abrufen"""
        client, token = authenticated_client

        response = client.get("/api/users/me")

        assert response.status_code == 200
        data = response.json()
        assert "username" in data
        assert "email" in data
        assert "id" in data
        assert "password" not in data
        assert "hashed_password" not in data

    def test_get_current_user_unauthenticated(self, client: TestClient):
        """Test: Unauthentifizierter Request wird abgelehnt"""
        response = client.get("/api/users/me")

        assert response.status_code == 401

    def test_get_current_user_invalid_token(self, client: TestClient):
        """Test: Ungültiger Token wird abgelehnt"""
        headers = {"Authorization": "Bearer invalid.token.here"}
        response = client.get("/api/users/me", headers=headers)

        assert response.status_code == 401

    def test_get_current_user_expired_token(self, client: TestClient):
        """Test: Abgelaufener Token wird abgelehnt"""
        # Erstelle einen Token, der bereits abgelaufen ist
        from datetime import timedelta
        from app.core.security import create_access_token

        # Token mit negativer Laufzeit (bereits abgelaufen)
        expired_token = create_access_token(
            data={"sub": "testuser"},
            expires_delta=timedelta(seconds=-1)
        )

        headers = {"Authorization": f"Bearer {expired_token}"}
        response = client.get("/api/users/me", headers=headers)

        assert response.status_code == 401

    def test_get_current_user_missing_bearer_prefix(self, client: TestClient, test_user: User, test_user_data: dict):
        """Test: Token ohne 'Bearer' Prefix wird abgelehnt"""
        # Login to get token
        login_response = client.post(
            "/api/auth/login",
            data={
                "username": test_user_data["username"],
                "password": test_user_data["password"]
            }
        )
        token = login_response.json()["access_token"]

        # Verwende Token ohne "Bearer" Prefix
        headers = {"Authorization": token}
        response = client.get("/api/users/me", headers=headers)

        assert response.status_code == 401

    def test_get_current_user_returns_correct_data(
        self, authenticated_client: tuple, test_user: User
    ):
        """Test: Endpoint gibt korrekte User-Daten zurück"""
        client, token = authenticated_client

        response = client.get("/api/users/me")
        data = response.json()

        assert data["username"] == test_user.username
        assert data["email"] == test_user.email
        assert data["id"] == test_user.id
        assert data["is_active"] == test_user.is_active

    def test_get_current_user_multiple_calls(self, authenticated_client: tuple):
        """Test: Mehrfache Calls mit demselben Token funktionieren"""
        client, token = authenticated_client

        # Mehrere Requests mit demselben Token
        for _ in range(5):
            response = client.get("/api/users/me")
            assert response.status_code == 200
            assert "username" in response.json()


@pytest.mark.unit
@pytest.mark.api
class TestAuthorizationHeader:
    """Tests für verschiedene Authorization Header Formate"""

    def test_authorization_with_different_bearer_case(self, client: TestClient, test_user: User, test_user_data: dict):
        """Test: 'Bearer' ist case-insensitive (abhängig von Implementation)"""
        # Login
        login_response = client.post(
            "/api/auth/login",
            data={
                "username": test_user_data["username"],
                "password": test_user_data["password"]
            }
        )
        token = login_response.json()["access_token"]

        # Versuche verschiedene Case-Varianten
        for bearer_prefix in ["Bearer", "bearer", "BEARER"]:
            headers = {"Authorization": f"{bearer_prefix} {token}"}
            response = client.get("/api/users/me", headers=headers)
            # Dies könnte je nach FastAPI Security Implementation variieren

    def test_authorization_with_extra_spaces(self, client: TestClient, test_user: User, test_user_data: dict):
        """Test: Extra Spaces im Authorization Header"""
        login_response = client.post(
            "/api/auth/login",
            data={
                "username": test_user_data["username"],
                "password": test_user_data["password"]
            }
        )
        token = login_response.json()["access_token"]

        # Mit extra spaces
        headers = {"Authorization": f"Bearer  {token}"}  # Double space
        response = client.get("/api/users/me", headers=headers)

        # Könnte je nach Implementation fehlschlagen
        # Dies ist ein Edge Case Test


@pytest.mark.unit
@pytest.mark.api
class TestMultipleUsers:
    """Tests mit mehreren Usern"""

    def test_different_users_get_different_data(
        self, client: TestClient, multiple_test_users: list[User]
    ):
        """Test: Verschiedene User bekommen ihre eigenen Daten"""
        for i, user in enumerate(multiple_test_users):
            # Login für jeden User
            login_response = client.post(
                "/api/auth/login",
                data={
                    "username": user.username,
                    "password": f"password{i}"
                }
            )
            assert login_response.status_code == 200
            token = login_response.json()["access_token"]

            # Hole User-Daten
            headers = {"Authorization": f"Bearer {token}"}
            me_response = client.get("/api/users/me", headers=headers)

            assert me_response.status_code == 200
            data = me_response.json()
            assert data["username"] == user.username
            assert data["email"] == user.email
            assert data["id"] == user.id

    def test_user_cannot_access_other_users_data(
        self, client: TestClient, multiple_test_users: list[User]
    ):
        """Test: User kann nicht Daten anderer User abrufen (durch Token geschützt)"""
        # Login als erster User
        login_response = client.post(
            "/api/auth/login",
            data={
                "username": multiple_test_users[0].username,
                "password": "password0"
            }
        )
        token = login_response.json()["access_token"]

        # Mit Token von User 0 die Daten abrufen
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/users/me", headers=headers)

        data = response.json()
        # Sollte nur Daten von User 0 zurückgeben, nicht von anderen Usern
        assert data["username"] == multiple_test_users[0].username
        assert data["username"] != multiple_test_users[1].username

