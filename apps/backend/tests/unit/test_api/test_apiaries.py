import pytest


@pytest.fixture
def apiary(authenticated_client):
    client, _ = authenticated_client
    response = client.post("/api/apiaries", json={"name": "Test Apiary"})
    assert response.status_code == 201
    return response.json()


@pytest.mark.unit
class TestListApiaries:
    def test_list_empty(self, authenticated_client):
        client, _ = authenticated_client
        response = client.get("/api/apiaries")
        assert response.status_code == 200
        assert response.json() == []

    def test_requires_auth(self, client):
        assert client.get("/api/apiaries").status_code == 401


@pytest.mark.unit
class TestCreateApiary:
    def test_create_minimal(self, authenticated_client):
        client, _ = authenticated_client
        response = client.post("/api/apiaries", json={"name": "Garden"})
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Garden"
        assert data["hive_count"] == 0

    def test_create_full(self, authenticated_client):
        client, _ = authenticated_client
        payload = {
            "name": "Forest Stand",
            "address": "Waldweg 1, 12345 Musterstadt",
            "latitude": 48.1374,
            "longitude": 11.5755,
            "notes": "Near the oak trees"
        }
        response = client.post("/api/apiaries", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["address"] == "Waldweg 1, 12345 Musterstadt"
        assert data["latitude"] == 48.1374

    def test_create_empty_name_fails(self, authenticated_client):
        client, _ = authenticated_client
        assert client.post("/api/apiaries", json={"name": ""}).status_code == 422

    def test_create_invalid_gps_fails(self, authenticated_client):
        client, _ = authenticated_client
        assert client.post("/api/apiaries", json={"name": "X", "latitude": 999}).status_code == 422


@pytest.mark.unit
class TestGetApiary:
    def test_get(self, authenticated_client, apiary):
        client, _ = authenticated_client
        response = client.get(f"/api/apiaries/{apiary['id']}")
        assert response.status_code == 200
        assert response.json()["name"] == apiary["name"]

    def test_get_not_found(self, authenticated_client):
        client, _ = authenticated_client
        assert client.get("/api/apiaries/99999").status_code == 404


@pytest.mark.unit
class TestUpdateApiary:
    def test_update(self, authenticated_client, apiary):
        client, _ = authenticated_client
        response = client.put(f"/api/apiaries/{apiary['id']}", json={"name": "Updated", "notes": "Changed"})
        assert response.status_code == 200
        assert response.json()["name"] == "Updated"

    def test_update_not_found(self, authenticated_client):
        client, _ = authenticated_client
        assert client.put("/api/apiaries/99999", json={"name": "X"}).status_code == 404


@pytest.mark.unit
class TestDeleteApiary:
    def test_delete(self, authenticated_client, apiary):
        client, _ = authenticated_client
        assert client.delete(f"/api/apiaries/{apiary['id']}").status_code == 204
        assert client.get(f"/api/apiaries/{apiary['id']}").status_code == 404

    def test_delete_not_found(self, authenticated_client):
        client, _ = authenticated_client
        assert client.delete("/api/apiaries/99999").status_code == 404


@pytest.mark.unit
class TestApiaryHiveCount:
    def test_hive_count_reflects_hives(self, authenticated_client, apiary):
        client, _ = authenticated_client
        client.post("/api/hives", json={"name": "H1", "apiary_id": apiary["id"]})
        client.post("/api/hives", json={"name": "H2", "apiary_id": apiary["id"]})
        response = client.get(f"/api/apiaries/{apiary['id']}")
        assert response.json()["hive_count"] == 2
