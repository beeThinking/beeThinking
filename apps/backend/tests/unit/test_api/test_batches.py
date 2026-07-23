from datetime import date

import pytest

from app.models.harvest import Harvest


@pytest.fixture
def apiary(authenticated_client):
    client, _ = authenticated_client
    response = client.post("/api/apiaries", json={"stock_number": "Batch Apiary", "name": "Batch Apiary"})
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def hive(authenticated_client, apiary):
    client, _ = authenticated_client
    response = client.post("/api/hives", json={"name": "Batch Hive", "apiary_id": apiary["id"]})
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


@pytest.mark.unit
@pytest.mark.api
class TestCreateBatch:
    def test_create_batch_from_harvest_ids_computes_defaults(self, authenticated_client, apiary, hive):
        client, _ = authenticated_client
        h1 = _create_harvest(client, apiary["id"], hive["id"], date(2026, 5, 1), 10.0)
        h2 = _create_harvest(client, apiary["id"], hive["id"], date(2026, 6, 1), 5.5)

        response = client.post("/api/batches", json={"harvest_ids": [h1["id"], h2["id"]]})

        assert response.status_code == 201
        data = response.json()
        assert data["lot_number"] == f"{date.today().year}-001"
        assert data["total_amount_kg"] == pytest.approx(15.5)
        assert data["best_before"] == "2028-05-01"
        assert {h["id"] for h in data["harvests"]} == {h1["id"], h2["id"]}

    def test_lot_number_sequence_increments_for_second_batch(self, authenticated_client, apiary, hive):
        client, _ = authenticated_client
        h1 = _create_harvest(client, apiary["id"], hive["id"], date.today(), 1.0)
        h2 = _create_harvest(client, apiary["id"], hive["id"], date.today(), 2.0)

        first = client.post("/api/batches", json={"harvest_ids": [h1["id"]]})
        second = client.post("/api/batches", json={"harvest_ids": [h2["id"]]})

        assert first.status_code == 201
        assert second.status_code == 201
        assert first.json()["lot_number"] == f"{date.today().year}-001"
        assert second.json()["lot_number"] == f"{date.today().year}-002"

    def test_create_batch_rejects_harvest_not_owned_by_user(self, authenticated_client, multiple_test_users, db):
        client, _ = authenticated_client
        other_harvest = Harvest(
            owner_id=multiple_test_users[0].id,
            harvest_date=date.today(),
            amount_kg=3.0,
        )
        db.add(other_harvest)
        db.commit()
        db.refresh(other_harvest)

        response = client.post("/api/batches", json={"harvest_ids": [other_harvest.id]})

        assert response.status_code == 400

    def test_create_batch_rejects_already_batched_harvest(self, authenticated_client, apiary, hive):
        client, _ = authenticated_client
        h1 = _create_harvest(client, apiary["id"], hive["id"], date.today(), 1.0)
        first = client.post("/api/batches", json={"harvest_ids": [h1["id"]]})
        assert first.status_code == 201

        response = client.post("/api/batches", json={"harvest_ids": [h1["id"]]})

        assert response.status_code == 400

    def test_create_batch_with_explicit_best_before_and_notes(self, authenticated_client, apiary, hive):
        client, _ = authenticated_client
        h1 = _create_harvest(client, apiary["id"], hive["id"], date.today(), 1.0)

        response = client.post(
            "/api/batches",
            json={"harvest_ids": [h1["id"]], "best_before": "2030-01-01", "notes": "custom"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["best_before"] == "2030-01-01"
        assert data["notes"] == "custom"

    def test_create_batch_with_no_harvests(self, authenticated_client):
        client, _ = authenticated_client
        response = client.post("/api/batches", json={"harvest_ids": []})
        assert response.status_code == 201
        data = response.json()
        assert data["total_amount_kg"] == 0
        assert data["best_before"] is None
        assert data["harvests"] == []


@pytest.mark.unit
@pytest.mark.api
class TestAttachDetachHarvest:
    def test_attach_recalculates_total(self, authenticated_client, apiary, hive):
        client, _ = authenticated_client
        h1 = _create_harvest(client, apiary["id"], hive["id"], date.today(), 1.0)
        h2 = _create_harvest(client, apiary["id"], hive["id"], date.today(), 2.5)
        batch = client.post("/api/batches", json={"harvest_ids": [h1["id"]]}).json()
        assert batch["total_amount_kg"] == pytest.approx(1.0)

        response = client.post(f"/api/batches/{batch['id']}/harvests/{h2['id']}")

        assert response.status_code == 200
        assert response.json()["total_amount_kg"] == pytest.approx(3.5)

    def test_attach_already_batched_harvest_returns_conflict(self, authenticated_client, apiary, hive):
        client, _ = authenticated_client
        h1 = _create_harvest(client, apiary["id"], hive["id"], date.today(), 1.0)
        h2 = _create_harvest(client, apiary["id"], hive["id"], date.today(), 2.0)
        batch_a = client.post("/api/batches", json={"harvest_ids": [h1["id"]]}).json()
        batch_b = client.post("/api/batches", json={"harvest_ids": [h2["id"]]}).json()

        response = client.post(f"/api/batches/{batch_a['id']}/harvests/{h2['id']}")

        assert response.status_code == 409

    def test_detach_recalculates_total(self, authenticated_client, apiary, hive):
        client, _ = authenticated_client
        h1 = _create_harvest(client, apiary["id"], hive["id"], date.today(), 1.0)
        h2 = _create_harvest(client, apiary["id"], hive["id"], date.today(), 2.5)
        batch = client.post("/api/batches", json={"harvest_ids": [h1["id"], h2["id"]]}).json()

        response = client.delete(f"/api/batches/{batch['id']}/harvests/{h2['id']}")

        assert response.status_code == 200
        data = response.json()
        assert data["total_amount_kg"] == pytest.approx(1.0)
        assert {h["id"] for h in data["harvests"]} == {h1["id"]}

        harvest_response = client.get(f"/api/harvests/{h2['id']}")
        assert harvest_response.json()["batch_id"] is None


@pytest.mark.unit
@pytest.mark.api
class TestDeleteBatch:
    def test_delete_batch_nulls_out_harvest_batch_id(self, authenticated_client, apiary, hive):
        client, _ = authenticated_client
        h1 = _create_harvest(client, apiary["id"], hive["id"], date.today(), 1.0)
        batch = client.post("/api/batches", json={"harvest_ids": [h1["id"]]}).json()

        response = client.delete(f"/api/batches/{batch['id']}")

        assert response.status_code == 204
        harvest_response = client.get(f"/api/harvests/{h1['id']}")
        assert harvest_response.status_code == 200
        assert harvest_response.json()["batch_id"] is None

    def test_delete_batch_not_found(self, authenticated_client):
        client, _ = authenticated_client
        response = client.delete("/api/batches/99999")
        assert response.status_code == 404


@pytest.mark.unit
@pytest.mark.api
class TestUpdateBatch:
    def test_update_best_before_and_notes(self, authenticated_client, apiary, hive):
        client, _ = authenticated_client
        h1 = _create_harvest(client, apiary["id"], hive["id"], date.today(), 1.0)
        batch = client.post("/api/batches", json={"harvest_ids": [h1["id"]]}).json()

        response = client.put(
            f"/api/batches/{batch['id']}",
            json={"best_before": "2031-06-15", "notes": "Updated notes"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["best_before"] == "2031-06-15"
        assert data["notes"] == "Updated notes"

    def test_update_not_found(self, authenticated_client):
        client, _ = authenticated_client
        response = client.put("/api/batches/99999", json={"notes": "x"})
        assert response.status_code == 404
