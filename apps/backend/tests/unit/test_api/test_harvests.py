from datetime import date

import pytest


@pytest.fixture
def apiary(authenticated_client):
    client, _ = authenticated_client
    response = client.post("/api/apiaries", json={"stock_number": "Harvest Apiary", "name": "Harvest Apiary"})
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def hive(authenticated_client, apiary):
    client, _ = authenticated_client
    response = client.post("/api/hives", json={"name": "Harvest Hive", "apiary_id": apiary["id"]})
    assert response.status_code == 201
    return response.json()


def _harvest_payload(apiary_id: int, hive_id: int, **overrides) -> dict:
    payload = {
        "apiary_id": apiary_id,
        "hive_id": hive_id,
        "harvest_date": str(date.today()),
        "crop_type": "Sommerhonig",
        "amount_kg": 12.5,
    }
    payload.update(overrides)
    return payload


@pytest.mark.unit
@pytest.mark.api
class TestHarvestsApi:
    def test_create_harvest_with_water_content_percent(self, authenticated_client, apiary, hive):
        client, _ = authenticated_client

        response = client.post(
            "/api/harvests", json=_harvest_payload(apiary["id"], hive["id"], water_content_percent=17.5)
        )

        assert response.status_code == 201
        assert response.json()["water_content_percent"] == 17.5

    def test_create_harvest_without_water_content_percent(self, authenticated_client, apiary, hive):
        client, _ = authenticated_client

        response = client.post("/api/harvests", json=_harvest_payload(apiary["id"], hive["id"]))

        assert response.status_code == 201
        assert response.json()["water_content_percent"] is None

    @pytest.mark.parametrize("invalid_value", [-1, 100.1, 150])
    def test_create_harvest_rejects_out_of_range_water_content(self, authenticated_client, apiary, hive, invalid_value):
        client, _ = authenticated_client

        response = client.post(
            "/api/harvests", json=_harvest_payload(apiary["id"], hive["id"], water_content_percent=invalid_value)
        )

        assert response.status_code == 422

    def test_water_content_percent_roundtrips_on_get(self, authenticated_client, apiary, hive):
        client, _ = authenticated_client
        created = client.post(
            "/api/harvests", json=_harvest_payload(apiary["id"], hive["id"], water_content_percent=18.2)
        ).json()

        response = client.get(f"/api/harvests/{created['id']}")

        assert response.status_code == 200
        assert response.json()["water_content_percent"] == 18.2

    def test_update_harvest_water_content_percent(self, authenticated_client, apiary, hive):
        client, _ = authenticated_client
        created = client.post(
            "/api/harvests", json=_harvest_payload(apiary["id"], hive["id"], water_content_percent=18.2)
        ).json()

        response = client.put(f"/api/harvests/{created['id']}", json={"water_content_percent": 19.5})

        assert response.status_code == 200
        assert response.json()["water_content_percent"] == 19.5

    def test_update_harvest_clears_water_content_percent(self, authenticated_client, apiary, hive):
        client, _ = authenticated_client
        created = client.post(
            "/api/harvests", json=_harvest_payload(apiary["id"], hive["id"], water_content_percent=18.2)
        ).json()

        response = client.put(f"/api/harvests/{created['id']}", json={"water_content_percent": None})

        assert response.status_code == 200
        assert response.json()["water_content_percent"] is None
