import pytest
from app.models.apiary import Apiary


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

    def test_list_returns_only_own_apiaries(self, authenticated_client, multiple_test_users, db):
        client, _ = authenticated_client
        db.add(Apiary(name="Other Apiary", owner_id=multiple_test_users[0].id))
        db.commit()

        response = client.get("/api/apiaries")

        assert response.status_code == 200
        assert response.json() == []


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

    def test_get_other_user_apiary_returns_404(self, authenticated_client, multiple_test_users, db):
        client, _ = authenticated_client
        other_apiary = Apiary(name="Other Apiary", owner_id=multiple_test_users[0].id)
        db.add(other_apiary)
        db.commit()
        db.refresh(other_apiary)

        response = client.get(f"/api/apiaries/{other_apiary.id}")

        assert response.status_code == 404


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

    def test_update_other_user_apiary_returns_404(self, authenticated_client, multiple_test_users, db):
        client, _ = authenticated_client
        other_apiary = Apiary(name="Other Apiary", owner_id=multiple_test_users[0].id)
        db.add(other_apiary)
        db.commit()
        db.refresh(other_apiary)

        response = client.put(f"/api/apiaries/{other_apiary.id}", json={"name": "Changed"})
        db.refresh(other_apiary)

        assert response.status_code == 404
        assert other_apiary.name == "Other Apiary"


@pytest.mark.unit
class TestDeleteApiary:
    def test_delete(self, authenticated_client, apiary):
        client, _ = authenticated_client
        assert client.delete(f"/api/apiaries/{apiary['id']}").status_code == 204
        assert client.get(f"/api/apiaries/{apiary['id']}").status_code == 404

    def test_delete_not_found(self, authenticated_client):
        client, _ = authenticated_client
        assert client.delete("/api/apiaries/99999").status_code == 404

    def test_delete_other_user_apiary_returns_404(self, authenticated_client, multiple_test_users, db):
        client, _ = authenticated_client
        other_apiary = Apiary(name="Other Apiary", owner_id=multiple_test_users[0].id)
        db.add(other_apiary)
        db.commit()
        db.refresh(other_apiary)

        response = client.delete(f"/api/apiaries/{other_apiary.id}")

        assert response.status_code == 404
        assert db.get(Apiary, other_apiary.id) is not None


@pytest.mark.unit
class TestApiaryHiveCount:
    def test_hive_count_reflects_hives(self, authenticated_client, apiary):
        client, _ = authenticated_client
        client.post("/api/hives", json={"name": "H1", "apiary_id": apiary["id"]})
        client.post("/api/hives", json={"name": "H2", "apiary_id": apiary["id"]})
        response = client.get(f"/api/apiaries/{apiary['id']}")
        assert response.json()["hive_count"] == 2
