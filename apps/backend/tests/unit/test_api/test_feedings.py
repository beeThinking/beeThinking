from datetime import date

import pytest


@pytest.fixture
def apiary(authenticated_client):
    client, _ = authenticated_client
    response = client.post("/api/apiaries", json={"stock_number": "Feeding Apiary", "name": "Feeding Apiary"})
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def hive(authenticated_client, apiary):
    client, _ = authenticated_client
    response = client.post("/api/hives", json={"name": "Feeding Hive", "apiary_id": apiary["id"]})
    assert response.status_code == 201
    return response.json()


def _feeding_payload(apiary_id: int, hive_id: int, **overrides) -> dict:
    payload = {
        "apiary_id": apiary_id,
        "hive_id": hive_id,
        "date": str(date.today()),
        "feed_type": "Futtersirup",
        "amount_kg_or_l": 2.5,
    }
    payload.update(overrides)
    return payload


@pytest.mark.unit
@pytest.mark.api
class TestFeedingsApi:
    def test_get_single_feeding(self, authenticated_client, apiary, hive):
        client, _ = authenticated_client
        feeding = client.post("/api/feedings", json=_feeding_payload(apiary["id"], hive["id"])).json()

        response = client.get(f"/api/feedings/{feeding['id']}")

        assert response.status_code == 200
        assert response.json()["feed_type"] == "Futtersirup"

    def test_update_feeding(self, authenticated_client, apiary, hive):
        client, _ = authenticated_client
        feeding = client.post("/api/feedings", json=_feeding_payload(apiary["id"], hive["id"])).json()

        response = client.put(f"/api/feedings/{feeding['id']}", json={"amount_kg_or_l": 4.0})

        assert response.status_code == 200
        assert response.json()["amount_kg_or_l"] == 4.0

    def test_delete_feeding(self, authenticated_client, apiary, hive):
        client, _ = authenticated_client
        feeding = client.post("/api/feedings", json=_feeding_payload(apiary["id"], hive["id"])).json()

        assert client.delete(f"/api/feedings/{feeding['id']}").status_code == 204
        assert client.get(f"/api/feedings/{feeding['id']}").status_code == 404

    def test_missing_feeding_returns_404(self, authenticated_client):
        client, _ = authenticated_client

        assert client.get("/api/feedings/9999").status_code == 404

    def test_feedings_require_authentication(self, client):
        assert client.get("/api/feedings").status_code == 401
