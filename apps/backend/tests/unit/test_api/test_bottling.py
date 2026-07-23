from datetime import date

import pytest

from app.models.batch import Batch


@pytest.fixture
def apiary(authenticated_client):
    client, _ = authenticated_client
    response = client.post("/api/apiaries", json={"stock_number": "Bottling Apiary", "name": "Bottling Apiary"})
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def hive(authenticated_client, apiary):
    client, _ = authenticated_client
    response = client.post("/api/hives", json={"name": "Bottling Hive", "apiary_id": apiary["id"]})
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def batch_10kg(authenticated_client, apiary, hive):
    client, _ = authenticated_client
    harvest = client.post(
        "/api/harvests",
        json={
            "apiary_id": apiary["id"],
            "hive_id": hive["id"],
            "harvest_date": str(date.today()),
            "crop_type": "Sommerhonig",
            "amount_kg": 10.0,
        },
    ).json()
    batch = client.post("/api/batches", json={"harvest_ids": [harvest["id"]]}).json()
    assert batch["remaining_kg"] == pytest.approx(10.0)
    return batch


def _create_article(client, weight_kg, **overrides):
    payload = {"name": "Honigglas 500g", "category": "finished_product", "unit": "piece", "weight_kg": weight_kg}
    payload.update(overrides)
    response = client.post("/api/articles", json=payload)
    assert response.status_code == 201
    return response.json()


@pytest.mark.unit
@pytest.mark.api
class TestBottleBatch:
    def test_bottle_creates_inventory_items_and_decrements_remaining(self, authenticated_client, batch_10kg):
        client, _ = authenticated_client
        article = _create_article(client, weight_kg=0.5)

        response = client.post(
            f"/api/batches/{batch_10kg['id']}/bottle",
            json={"items": [{"article_id": article["id"], "quantity": 4, "price": 9.9, "best_before": "2028-01-01"}]},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["batch"]["remaining_kg"] == pytest.approx(8.0)
        assert len(data["inventory_items"]) == 1
        item = data["inventory_items"][0]
        assert item["quantity"] == pytest.approx(4)
        assert item["batch_id"] == batch_10kg["id"]
        assert item["price"] == pytest.approx(9.9)
        assert item["best_before"] == "2028-01-01"

    def test_bottle_increments_existing_inventory_item(self, authenticated_client, batch_10kg):
        client, _ = authenticated_client
        article = _create_article(client, weight_kg=0.5)

        first = client.post(
            f"/api/batches/{batch_10kg['id']}/bottle",
            json={"items": [{"article_id": article["id"], "quantity": 4}]},
        )
        assert first.status_code == 200

        second = client.post(
            f"/api/batches/{batch_10kg['id']}/bottle",
            json={"items": [{"article_id": article["id"], "quantity": 2}]},
        )

        assert second.status_code == 200
        data = second.json()
        assert len(data["inventory_items"]) == 1
        assert data["inventory_items"][0]["quantity"] == pytest.approx(6)
        assert data["batch"]["remaining_kg"] == pytest.approx(7.0)

    def test_bottle_merges_duplicate_article_ids_in_single_request(self, authenticated_client, batch_10kg):
        client, _ = authenticated_client
        article = _create_article(client, weight_kg=0.5)

        response = client.post(
            f"/api/batches/{batch_10kg['id']}/bottle",
            json={
                "items": [
                    {"article_id": article["id"], "quantity": 3},
                    {"article_id": article["id"], "quantity": 2},
                ]
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["inventory_items"]) == 1
        assert data["inventory_items"][0]["quantity"] == pytest.approx(5)
        assert data["batch"]["remaining_kg"] == pytest.approx(7.5)

    def test_bottle_rejects_when_exceeding_remaining_kg(self, authenticated_client, batch_10kg):
        client, _ = authenticated_client
        article = _create_article(client, weight_kg=0.5)

        response = client.post(
            f"/api/batches/{batch_10kg['id']}/bottle",
            json={"items": [{"article_id": article["id"], "quantity": 100}]},
        )

        assert response.status_code == 409

    def test_bottle_other_users_batch_returns_404(self, authenticated_client, multiple_test_users, db):
        client, _ = authenticated_client
        other_batch = Batch(
            owner_id=multiple_test_users[0].id,
            lot_number="2026-999",
            total_amount_kg=5.0,
            remaining_kg=5.0,
        )
        db.add(other_batch)
        db.commit()
        db.refresh(other_batch)

        response = client.post(
            f"/api/batches/{other_batch.id}/bottle",
            json={"items": [{"article_id": 1, "quantity": 1}]},
        )

        assert response.status_code == 404

    def test_bottle_unknown_article_returns_404(self, authenticated_client, batch_10kg):
        client, _ = authenticated_client

        response = client.post(
            f"/api/batches/{batch_10kg['id']}/bottle",
            json={"items": [{"article_id": 999999, "quantity": 1}]},
        )

        assert response.status_code == 404

    def test_bottle_unknown_batch_returns_404(self, authenticated_client):
        client, _ = authenticated_client

        response = client.post(
            "/api/batches/999999/bottle",
            json={"items": [{"article_id": 1, "quantity": 1}]},
        )

        assert response.status_code == 404
