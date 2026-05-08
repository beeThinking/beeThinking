import pytest
from fastapi.testclient import TestClient


@pytest.mark.unit
class TestListHives:
    def test_list_hives_empty(self, authenticated_client):
        client, _ = authenticated_client
        response = client.get("/api/hives")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_hives_returns_only_own_hives(self, authenticated_client, db):
        client, _ = authenticated_client
        client.post("/api/hives", json={"name": "My Hive", "type": "langstroth", "status": "active"})
        response = client.get("/api/hives")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_list_hives_requires_auth(self, client: TestClient):
        response = client.get("/api/hives")
        assert response.status_code == 401


@pytest.mark.unit
class TestCreateHive:
    def test_create_hive_minimal(self, authenticated_client):
        client, _ = authenticated_client
        response = client.post("/api/hives", json={"name": "Alpha"})
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Alpha"
        assert data["status"] == "active"
        assert data["type"] == "langstroth"
        assert "id" in data
        assert "owner_id" in data

    def test_create_hive_full(self, authenticated_client):
        client, _ = authenticated_client
        payload = {
            "name": "Beta Hive",
            "location": "Garden",
            "type": "dadant",
            "status": "active",
            "notes": "Strong colony"
        }
        response = client.post("/api/hives", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Beta Hive"
        assert data["location"] == "Garden"
        assert data["type"] == "dadant"
        assert data["notes"] == "Strong colony"

    def test_create_hive_empty_name_fails(self, authenticated_client):
        client, _ = authenticated_client
        response = client.post("/api/hives", json={"name": ""})
        assert response.status_code == 422

    def test_create_hive_requires_auth(self, client: TestClient):
        response = client.post("/api/hives", json={"name": "No Auth"})
        assert response.status_code == 401


@pytest.mark.unit
class TestGetHive:
    def test_get_hive(self, authenticated_client):
        client, _ = authenticated_client
        created = client.post("/api/hives", json={"name": "Gamma"}).json()
        response = client.get(f"/api/hives/{created['id']}")
        assert response.status_code == 200
        assert response.json()["name"] == "Gamma"

    def test_get_hive_not_found(self, authenticated_client):
        client, _ = authenticated_client
        response = client.get("/api/hives/99999")
        assert response.status_code == 404

    def test_get_hive_of_other_user_returns_404(self, authenticated_client, multiple_test_users, db):
        client, _ = authenticated_client
        from app.models.hive import Hive
        other_hive = Hive(name="Other Hive", owner_id=multiple_test_users[0].id)
        db.add(other_hive)
        db.commit()
        db.refresh(other_hive)
        response = client.get(f"/api/hives/{other_hive.id}")
        assert response.status_code == 404


@pytest.mark.unit
class TestUpdateHive:
    def test_update_hive(self, authenticated_client):
        client, _ = authenticated_client
        created = client.post("/api/hives", json={"name": "Delta"}).json()
        response = client.put(f"/api/hives/{created['id']}", json={"name": "Delta Updated", "status": "inactive"})
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Delta Updated"
        assert data["status"] == "inactive"

    def test_update_hive_not_found(self, authenticated_client):
        client, _ = authenticated_client
        response = client.put("/api/hives/99999", json={"name": "X"})
        assert response.status_code == 404

    def test_partial_update_preserves_fields(self, authenticated_client):
        client, _ = authenticated_client
        created = client.post("/api/hives", json={"name": "Epsilon", "location": "Forest"}).json()
        response = client.put(f"/api/hives/{created['id']}", json={"status": "inactive"})
        assert response.status_code == 200
        data = response.json()
        assert data["location"] == "Forest"
        assert data["status"] == "inactive"


@pytest.mark.unit
class TestDeleteHive:
    def test_delete_hive(self, authenticated_client):
        client, _ = authenticated_client
        created = client.post("/api/hives", json={"name": "Zeta"}).json()
        response = client.delete(f"/api/hives/{created['id']}")
        assert response.status_code == 204
        assert client.get(f"/api/hives/{created['id']}").status_code == 404

    def test_delete_hive_not_found(self, authenticated_client):
        client, _ = authenticated_client
        response = client.delete("/api/hives/99999")
        assert response.status_code == 404
