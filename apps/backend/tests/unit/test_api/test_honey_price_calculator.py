from datetime import date

import pytest


@pytest.fixture
def apiary(authenticated_client):
    client, _ = authenticated_client
    response = client.post("/api/apiaries", json={"stock_number": "Pricing Stand"})
    assert response.status_code == 201
    return response.json()


@pytest.mark.unit
class TestHoneyPriceCalculator:
    def test_requires_auth(self, client):
        response = client.post("/api/honey-price-calculator/calculate", json={"apiary_id": 1})
        assert response.status_code == 401

    def test_404_for_unknown_apiary(self, authenticated_client):
        client, _ = authenticated_client
        response = client.post("/api/honey-price-calculator/calculate", json={"apiary_id": 999999})
        assert response.status_code == 404

    def test_cost_per_kg_and_per_colony(self, authenticated_client, apiary):
        client, _ = authenticated_client
        client.post("/api/hives", json={"name": "Hive 1", "apiary_id": apiary["id"]})
        client.post("/api/hives", json={"name": "Hive 2", "apiary_id": apiary["id"]})
        client.post("/api/harvests", json={
            "apiary_id": apiary["id"], "harvest_date": str(date.today()), "amount_kg": 20.0,
        })
        client.post("/api/cashbook/entries", json={
            "apiary_id": apiary["id"],
            "booking_date": str(date.today()),
            "direction": "expense",
            "category": "feed",
            "amount_gross": 40.0,
            "amount_net": 40.0,
        })

        response = client.post("/api/honey-price-calculator/calculate", json={"apiary_id": apiary["id"]})

        assert response.status_code == 200
        data = response.json()
        assert data["total_relevant_costs"] == 40.0
        assert data["total_harvested_kg"] == 20.0
        assert data["colony_count"] == 2
        assert data["cost_per_kg"] == 2.0
        assert data["cost_per_colony"] == 20.0
        assert "simplification_note" in data

    def test_suggested_price_applies_margin(self, authenticated_client, apiary):
        client, _ = authenticated_client
        client.post("/api/harvests", json={
            "apiary_id": apiary["id"], "harvest_date": str(date.today()), "amount_kg": 10.0,
        })
        client.post("/api/cashbook/entries", json={
            "apiary_id": apiary["id"],
            "booking_date": str(date.today()),
            "direction": "expense",
            "category": "feed",
            "amount_gross": 20.0,
            "amount_net": 20.0,
        })

        response = client.post("/api/honey-price-calculator/calculate", json={
            "apiary_id": apiary["id"], "target_margin_percent": 50,
        })

        assert response.status_code == 200
        data = response.json()
        assert data["cost_per_kg"] == 2.0
        assert data["suggested_price_per_kg"] == 3.0

    def test_no_harvests_returns_null_cost_per_kg(self, authenticated_client, apiary):
        client, _ = authenticated_client
        response = client.post("/api/honey-price-calculator/calculate", json={"apiary_id": apiary["id"]})
        assert response.status_code == 200
        assert response.json()["cost_per_kg"] is None

    def test_includes_harvest_linked_only_through_hive(self, authenticated_client, apiary, db, test_user):
        from app.models.harvest import Harvest

        client, _ = authenticated_client
        hive = client.post("/api/hives", json={"name": "Harvest Hive", "apiary_id": apiary["id"]}).json()
        db.add(Harvest(owner_id=test_user.id, hive_id=hive["id"], harvest_date=date.today(), amount_kg=7.5))
        db.commit()

        response = client.post("/api/honey-price-calculator/calculate", json={"apiary_id": apiary["id"]})

        assert response.status_code == 200
        assert response.json()["total_harvested_kg"] == 7.5

    def test_cannot_access_other_users_apiary(self, client, authenticated_client, apiary, db):
        from app.core.security import get_password_hash
        from app.models.user import User

        outsider = User(
            username="pricing_outsider",
            email="pricing_outsider@example.com",
            hashed_password=get_password_hash("OutsiderPassword123!"),
            is_active=True,
            is_verified=True,
        )
        db.add(outsider)
        db.commit()

        response = client.post("/api/auth/login", data={"username": "pricing_outsider", "password": "OutsiderPassword123!"})
        client.headers["Authorization"] = f"Bearer {response.json()['access_token']}"

        response = client.post("/api/honey-price-calculator/calculate", json={"apiary_id": apiary["id"]})
        assert response.status_code == 404
