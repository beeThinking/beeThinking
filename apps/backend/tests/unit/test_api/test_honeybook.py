from datetime import date

import pytest


@pytest.fixture
def apiary(authenticated_client):
    client, _ = authenticated_client
    response = client.post("/api/apiaries", json={"stock_number": "Honey Apiary", "name": "Honey Apiary"})
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def hive(authenticated_client, apiary):
    client, _ = authenticated_client
    response = client.post(
        "/api/hives", json={"name": "Honey Hive", "apiary_id": apiary["id"], "stock_number": "HH-1"}
    )
    assert response.status_code == 201
    return response.json()


def _create_harvest(client, apiary, hive, harvest_date, crop_type="Bluetenhonig"):
    response = client.post(
        "/api/harvests",
        json={
            "apiary_id": apiary["id"],
            "hive_id": hive["id"],
            "harvest_date": harvest_date,
            "crop_type": crop_type,
            "amount_kg": 10.0,
            "water_content_percent": 17.5,
        },
    )
    assert response.status_code == 201
    return response.json()


@pytest.mark.unit
@pytest.mark.api
class TestHoneybookRegister:
    def test_register_json_includes_batched_and_unbatched_entries(self, authenticated_client, apiary, hive):
        client, _ = authenticated_client
        year = date.today().year
        batched_harvest = _create_harvest(client, apiary, hive, f"{year}-06-01")
        unbatched_harvest = _create_harvest(client, apiary, hive, f"{year}-07-01")

        batch_response = client.post("/api/batches", json={"harvest_ids": [batched_harvest["id"]]})
        assert batch_response.status_code == 201
        batch = batch_response.json()

        article_response = client.post(
            "/api/articles", json={"category": "finished_product", "name": "Glas 500g", "unit": "piece"}
        )
        assert article_response.status_code == 201
        article = article_response.json()

        bottle_response = client.post(
            f"/api/batches/{batch['id']}/bottle",
            json={"items": [{"article_id": article["id"], "quantity": 5}]},
        )
        assert bottle_response.status_code == 200

        response = client.get(f"/api/honeybook/register?year={year}")
        assert response.status_code == 200
        entries = response.json()
        assert len(entries) == 2

        batched_entry = next(e for e in entries if e["harvest_date"] == f"{year}-06-01")
        assert batched_entry["status"] == "batched"
        assert batched_entry["lot_number"] == batch["lot_number"]
        assert batched_entry["apiary_name"] == "Honey Apiary"
        assert batched_entry["hive_name"] == "Honey Hive"
        assert batched_entry["crop_type"] == "Bluetenhonig"
        assert batched_entry["amount_kg"] == 10.0
        assert batched_entry["water_content_percent"] == 17.5
        assert batched_entry["best_before"] == batch["best_before"]
        assert batched_entry["bottled_quantity"] == 5
        assert batched_entry["bottled_articles"] == ["Glas 500g"]

        unbatched_entry = next(e for e in entries if e["harvest_date"] == f"{year}-07-01")
        assert unbatched_entry["status"] == "unbatched"
        assert unbatched_entry["lot_number"] is None
        assert unbatched_entry["bottled_quantity"] == 0
        assert unbatched_entry["bottled_articles"] == []
        assert unbatched_entry["id"] != batched_harvest["id"] if "id" in unbatched_entry else True

        assert unbatched_harvest["id"] != batched_harvest["id"]

    def test_register_year_filter(self, authenticated_client, apiary, hive):
        client, _ = authenticated_client
        _create_harvest(client, apiary, hive, "2024-05-01")
        _create_harvest(client, apiary, hive, "2025-05-01")

        response_2024 = client.get("/api/honeybook/register?year=2024")
        assert response_2024.status_code == 200
        assert len(response_2024.json()) == 1
        assert response_2024.json()[0]["harvest_date"] == "2024-05-01"

        response_2025 = client.get("/api/honeybook/register?year=2025")
        assert response_2025.status_code == 200
        assert len(response_2025.json()) == 1
        assert response_2025.json()[0]["harvest_date"] == "2025-05-01"

    def test_register_pdf_returns_pdf_with_content_disposition(self, authenticated_client, apiary, hive):
        client, _ = authenticated_client
        year = date.today().year
        _create_harvest(client, apiary, hive, f"{year}-03-01")

        response = client.get(f"/api/honeybook/register.pdf?year={year}")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert response.headers["content-disposition"] == f'attachment; filename="honigbuch-{year}.pdf"'
        assert response.content.startswith(b"%PDF")

    def test_register_requires_authentication(self, client):
        assert client.get("/api/honeybook/register").status_code == 401
        assert client.get("/api/honeybook/register.pdf").status_code == 401

    def test_register_is_owner_scoped(self, authenticated_client, apiary, hive, client, db):
        first_client, _ = authenticated_client
        year = date.today().year
        _create_harvest(first_client, apiary, hive, f"{year}-04-01")

        second_user_data = {
            "username": "otheruser",
            "email": "other@example.com",
            "password": "SecurePassword123!",
        }
        register_response = client.post("/api/auth/register", json=second_user_data)
        assert register_response.status_code == 201

        login_response = client.post(
            "/api/auth/login",
            data={"username": second_user_data["username"], "password": second_user_data["password"]},
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        client.headers.update({"Authorization": f"Bearer {token}"})

        response = client.get(f"/api/honeybook/register?year={year}")
        assert response.status_code == 200
        assert response.json() == []
