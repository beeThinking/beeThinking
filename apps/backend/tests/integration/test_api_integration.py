"""
Integration Tests für BeeThinking Backend API
Vollständige End-to-End Tests des kompletten API Flows
Basierend auf dem originalen test_api.py Script
"""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
class TestHealthEndpoint:
    """Integration Tests für Health Check"""

    def test_health_check(self, client: TestClient):
        """Test: Health endpoint ist erreichbar"""
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


@pytest.mark.integration
@pytest.mark.auth
class TestCompleteAuthenticationFlow:
    """Integration Tests für kompletten Authentication Flow"""

    def test_full_registration_and_login_flow(self, client: TestClient):
        """
        Test: Kompletter Flow von Registration bis authentifiziertem Request
        Entspricht dem originalen test_api.py Smoke Test
        """
        # Step 1: Registrierung
        registration_data = {
            "username": "integrationuser",
            "email": "integration@example.com",
            "password": "SecurePassword123!"
        }

        register_response = client.post("/api/auth/register", json=registration_data)

        # Sollte entweder erfolgreich sein oder User existiert bereits
        assert register_response.status_code in [201, 400]

        if register_response.status_code == 201:
            user_data = register_response.json()
            assert user_data["username"] == registration_data["username"]
            assert user_data["email"] == registration_data["email"]
            assert "password" not in user_data

        # Step 2: Login
        login_data = {
            "username": registration_data["username"],
            "password": registration_data["password"]
        }

        login_response = client.post("/api/auth/login", data=login_data)

        assert login_response.status_code == 200
        token_data = login_response.json()
        assert "access_token" in token_data
        assert token_data["token_type"] == "bearer"
        assert len(token_data["access_token"]) > 0

        access_token = token_data["access_token"]

        # Step 3: Authentifizierter Request
        headers = {"Authorization": f"Bearer {access_token}"}
        me_response = client.get("/api/users/me", headers=headers)

        assert me_response.status_code == 200
        current_user = me_response.json()
        assert current_user["username"] == registration_data["username"]
        assert current_user["email"] == registration_data["email"]
        assert "id" in current_user
        assert "password" not in current_user
        assert "hashed_password" not in current_user


@pytest.mark.integration
class TestMultipleUsersIntegration:
    """Integration Tests mit mehreren Usern"""

    def test_multiple_users_can_register_and_login(self, client: TestClient):
        """Test: Mehrere User können sich registrieren und einloggen"""
        users = []

        for i in range(3):
            user_data = {
                "username": f"multiuser{i}",
                "email": f"multi{i}@example.com",
                "password": f"SecurePass{i}!"
            }

            # Registrierung
            register_response = client.post("/api/auth/register", json=user_data)
            assert register_response.status_code in [201, 400]  # OK wenn bereits existiert

            # Login
            login_response = client.post(
                "/api/auth/login",
                data={
                    "username": user_data["username"],
                    "password": user_data["password"]
                }
            )
            assert login_response.status_code == 200

            token = login_response.json()["access_token"]
            users.append((user_data, token))

        # Verify each user can access their own data
        for user_data, token in users:
            headers = {"Authorization": f"Bearer {token}"}
            response = client.get("/api/users/me", headers=headers)

            assert response.status_code == 200
            data = response.json()
            assert data["username"] == user_data["username"]
            assert data["email"] == user_data["email"]


@pytest.mark.integration
@pytest.mark.slow
class TestAPIPerformance:
    """Integration Tests für API Performance"""

    def test_multiple_sequential_requests(self, authenticated_client: tuple):
        """Test: Mehrere sequenzielle Requests funktionieren zuverlässig"""
        client, token = authenticated_client

        # Führe 10 Requests nacheinander aus
        for i in range(10):
            response = client.get("/api/users/me")
            assert response.status_code == 200
            assert "username" in response.json()

    def test_health_check_response_time(self, client: TestClient):
        """Test: Health Check antwortet schnell"""
        import time

        start = time.time()
        response = client.get("/health")
        duration = time.time() - start

        assert response.status_code == 200
        # Health check sollte unter 100ms antworten
        assert duration < 0.1, f"Health check took {duration}s"


@pytest.mark.integration
class TestErrorHandling:
    """Integration Tests für Error Handling"""

    def test_404_on_nonexistent_endpoint(self, client: TestClient):
        """Test: 404 für nicht existierende Endpoints"""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404

    def test_405_on_wrong_method(self, client: TestClient):
        """Test: 405 für falsche HTTP Methode"""
        # POST auf /health ist nicht erlaubt (nur GET)
        response = client.post("/health")
        assert response.status_code == 405

    def test_422_on_invalid_json(self, client: TestClient):
        """Test: 422 bei ungültigem Request Body"""
        response = client.post(
            "/api/auth/register",
            json={"invalid": "data"}
        )
        assert response.status_code == 422

    def test_401_unauthorized_access(self, client: TestClient):
        """Test: 401 bei unauthentifiziertem Zugriff auf geschützte Endpoints"""
        protected_endpoints = [
            "/api/users/me",
        ]

        for endpoint in protected_endpoints:
            response = client.get(endpoint)
            assert response.status_code == 401, f"Endpoint {endpoint} should be protected"


@pytest.mark.integration
class TestAPIConsistency:
    """Integration Tests für API Consistency"""

    def test_response_format_consistency(self, client: TestClient):
        """Test: API Responses haben konsistentes Format"""
        # Registrierung
        user_data = {
            "username": "consistencytest",
            "email": "consistency@example.com",
            "password": "SecurePassword123!"
        }

        register_response = client.post("/api/auth/register", json=user_data)

        if register_response.status_code == 201:
            data = register_response.json()
            # Response sollte Standard-Felder haben
            assert "username" in data
            assert "email" in data
            assert "id" in data
            assert isinstance(data["id"], int)

    def test_token_format_consistency(self, client: TestClient, test_user, test_user_data):
        """Test: Token haben konsistentes Format"""
        login_response = client.post(
            "/api/auth/login",
            data={
                "username": test_user_data["username"],
                "password": test_user_data["password"]
            }
        )

        assert login_response.status_code == 200
        data = login_response.json()

        # Token Response sollte Standard-Format haben
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"

        # JWT Token sollte 3 Teile haben (header.payload.signature)
        token_parts = data["access_token"].split(".")
        assert len(token_parts) == 3


@pytest.mark.integration
class TestDataPersistence:
    """Integration Tests für Datenpersistenz"""

    def test_user_data_persists_across_requests(self, client: TestClient):
        """Test: User-Daten bleiben über mehrere Requests hinweg konsistent"""
        # Erstelle User
        user_data = {
            "username": "persistencetest",
            "email": "persist@example.com",
            "password": "SecurePassword123!"
        }

        # Registrierung
        register_response = client.post("/api/auth/register", json=user_data)
        assert register_response.status_code in [201, 400]

        # Login mehrmals
        for _ in range(3):
            login_response = client.post(
                "/api/auth/login",
                data={
                    "username": user_data["username"],
                    "password": user_data["password"]
                }
            )
            assert login_response.status_code == 200

            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}

            # User-Daten sollten gleich bleiben
            me_response = client.get("/api/users/me", headers=headers)
            assert me_response.status_code == 200
            data = me_response.json()
            assert data["username"] == user_data["username"]
            assert data["email"] == user_data["email"]

