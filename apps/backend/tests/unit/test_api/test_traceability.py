from datetime import date

import pytest

from app.models.batch import Batch
from app.models.harvest import Harvest


def _create_apiary(client, stock_number):
    response = client.post("/api/apiaries", json={"stock_number": stock_number, "name": stock_number})
    assert response.status_code == 201
    return response.json()


def _create_hive(client, apiary_id, name):
    response = client.post("/api/hives", json={"name": name, "apiary_id": apiary_id})
    assert response.status_code == 201
    return response.json()


def _create_harvest(client, apiary_id, hive_id, harvest_date, amount_kg, **overrides):
    payload = {
        "apiary_id": apiary_id,
        "hive_id": hive_id,
        "harvest_date": str(harvest_date),
        "crop_type": "Sommerhonig",
        "amount_kg": amount_kg,
    }
    payload.update(overrides)
    response = client.post("/api/harvests", json=payload)
    assert response.status_code == 201
    return response.json()


def _create_article(client, name="Glas 500g"):
    response = client.post("/api/articles", json={"name": name, "unit": "piece"})
    assert response.status_code == 201
    return response.json()


@pytest.mark.unit
@pytest.mark.api
class TestGetTraceability:
    def test_full_chain_lookup(self, authenticated_client):
        client, _ = authenticated_client
        apiary = _create_apiary(client, "AP-1")
        hive = _create_hive(client, apiary["id"], "Hive 1")
        harvest = _create_harvest(client, apiary["id"], hive["id"], date.today(), 10.0)
        batch = client.post("/api/batches", json={"harvest_ids": [harvest["id"]]}).json()
        article = _create_article(client)
        client.post(
            "/api/batches/{}/bottle".format(batch["id"]),
            json={"items": [{"article_id": article["id"], "quantity": 5}]},
        )

        response = client.get(f"/api/traceability/{batch['lot_number']}")

        assert response.status_code == 200
        data = response.json()
        assert data["lot_number"] == batch["lot_number"]
        assert data["batch"]["id"] == batch["id"]
        assert len(data["harvests"]) == 1
        entry = data["harvests"][0]
        assert entry["harvest"]["id"] == harvest["id"]
        assert entry["hive"]["id"] == hive["id"]
        assert entry["hive"]["name"] == "Hive 1"
        assert entry["apiary"]["id"] == apiary["id"]
        assert entry["apiary"]["stock_number"] == "AP-1"
        assert len(data["inventory_items"]) == 1
        assert data["inventory_items"][0]["article_id"] == article["id"]

    def test_partial_chain_null_hive_and_apiary(self, authenticated_client, test_user, db):
        client, _ = authenticated_client
        harvest = Harvest(
            owner_id=test_user.id,
            harvest_date=date.today(),
            amount_kg=3.0,
        )
        db.add(harvest)
        db.commit()
        db.refresh(harvest)

        batch = Batch(owner_id=test_user.id, lot_number="NOHIVE-001", total_amount_kg=3.0)
        db.add(batch)
        db.flush()
        harvest.batch_id = batch.id
        db.commit()

        response = client.get(f"/api/traceability/{batch.lot_number}")

        assert response.status_code == 200
        data = response.json()
        entry = data["harvests"][0]
        assert entry["hive"] is None
        assert entry["apiary"] is None

    def test_unknown_lot_number_returns_404(self, authenticated_client):
        client, _ = authenticated_client
        response = client.get("/api/traceability/does-not-exist")
        assert response.status_code == 404

    def test_other_users_lot_number_not_leaked(self, authenticated_client, multiple_test_users, db):
        client, _ = authenticated_client
        other_batch = Batch(
            owner_id=multiple_test_users[0].id,
            lot_number="OTHER-001",
            total_amount_kg=1.0,
        )
        db.add(other_batch)
        db.commit()

        response = client.get(f"/api/traceability/{other_batch.lot_number}")

        assert response.status_code == 404

    def test_multiple_harvests_hives_apiaries_returned_as_arrays(self, authenticated_client):
        client, _ = authenticated_client
        apiary_a = _create_apiary(client, "AP-A")
        apiary_b = _create_apiary(client, "AP-B")
        hive_a = _create_hive(client, apiary_a["id"], "Hive A")
        hive_b = _create_hive(client, apiary_b["id"], "Hive B")
        h1 = _create_harvest(client, apiary_a["id"], hive_a["id"], date.today(), 5.0)
        h2 = _create_harvest(client, apiary_b["id"], hive_b["id"], date.today(), 7.0)

        batch = client.post("/api/batches", json={"harvest_ids": [h1["id"], h2["id"]]}).json()

        response = client.get(f"/api/traceability/{batch['lot_number']}")

        assert response.status_code == 200
        data = response.json()
        assert len(data["harvests"]) == 2
        hive_ids = {entry["hive"]["id"] for entry in data["harvests"]}
        apiary_ids = {entry["apiary"]["id"] for entry in data["harvests"]}
        assert hive_ids == {hive_a["id"], hive_b["id"]}
        assert apiary_ids == {apiary_a["id"], apiary_b["id"]}
