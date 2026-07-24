from datetime import datetime, timezone

import pytest


@pytest.fixture
def apiary(authenticated_client):
    client, _ = authenticated_client
    response = client.post("/api/apiaries", json={"stock_number": "Scale Stand"})
    assert response.status_code == 201
    return response.json()


@pytest.mark.unit
class TestScaleToggle:
    def test_create_hive_with_scale_enabled(self, authenticated_client, apiary):
        client, _ = authenticated_client
        response = client.post("/api/hives", json={
            "name": "Scale Hive", "apiary_id": apiary["id"], "scale_enabled": True,
        })
        assert response.status_code == 201
        assert response.json()["scale_enabled"] is True

    def test_default_scale_disabled(self, authenticated_client, apiary):
        client, _ = authenticated_client
        response = client.post("/api/hives", json={"name": "Plain Hive", "apiary_id": apiary["id"]})
        assert response.status_code == 201
        assert response.json()["scale_enabled"] is False

    def test_update_scale_enabled(self, authenticated_client, apiary):
        client, _ = authenticated_client
        hive = client.post("/api/hives", json={"name": "Toggle Hive", "apiary_id": apiary["id"]}).json()
        response = client.put(f"/api/hives/{hive['id']}", json={"scale_enabled": True})
        assert response.status_code == 200
        assert response.json()["scale_enabled"] is True


@pytest.mark.unit
class TestWeightReadings:
    def test_list_empty_by_default(self, authenticated_client, apiary):
        client, _ = authenticated_client
        hive = client.post("/api/hives", json={"name": "Weight Hive", "apiary_id": apiary["id"], "scale_enabled": True}).json()

        response = client.get(f"/api/hives/{hive['id']}/weight-readings")

        assert response.status_code == 200
        assert response.json() == []

    def test_create_and_list_reading(self, authenticated_client, apiary):
        client, _ = authenticated_client
        hive = client.post("/api/hives", json={"name": "Weight Hive 2", "apiary_id": apiary["id"], "scale_enabled": True}).json()

        response = client.post(f"/api/hives/{hive['id']}/weight-readings", json={"weight_kg": 42.5})
        assert response.status_code == 201
        reading = response.json()
        assert reading["weight_kg"] == 42.5

        response = client.get(f"/api/hives/{hive['id']}/weight-readings")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_delete_reading(self, authenticated_client, apiary):
        client, _ = authenticated_client
        hive = client.post("/api/hives", json={"name": "Weight Hive 3", "apiary_id": apiary["id"]}).json()
        reading = client.post(f"/api/hives/{hive['id']}/weight-readings", json={"weight_kg": 30.0}).json()

        response = client.delete(f"/api/hives/{hive['id']}/weight-readings/{reading['id']}")
        assert response.status_code == 204
        assert client.get(f"/api/hives/{hive['id']}/weight-readings").json() == []

    def test_404_for_unknown_hive(self, authenticated_client):
        client, _ = authenticated_client
        assert client.get("/api/hives/999999/weight-readings").status_code == 404

    def test_requires_auth(self, client):
        assert client.get("/api/hives/1/weight-readings").status_code == 401
