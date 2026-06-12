import pytest
from datetime import date
from app.models.apiary import Apiary
from app.models.hive import Hive
from app.models.inspection import Inspection


@pytest.fixture
def apiary(authenticated_client):
    client, _ = authenticated_client
    response = client.post("/api/apiaries", json={"stock_number": "Test Apiary", "name": "Test Apiary"})
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def hive(authenticated_client, apiary):
    client, _ = authenticated_client
    response = client.post("/api/hives", json={"name": "Test Hive", "apiary_id": apiary["id"]})
    assert response.status_code == 201
    return response.json()


@pytest.mark.unit
class TestListInspections:
    def test_list_empty(self, authenticated_client, hive):
        client, _ = authenticated_client
        response = client.get(f"/api/hives/{hive['id']}/inspections")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_requires_auth(self, authenticated_client, apiary):
        client, _ = authenticated_client
        # Create a fresh client without auth header
        from fastapi.testclient import TestClient
        from app.main import app
        unauth_client = TestClient(app)
        hive_id = client.post("/api/hives", json={"name": "Auth Test Hive", "apiary_id": apiary["id"]}).json()["id"]
        response = unauth_client.get(f"/api/hives/{hive_id}/inspections")
        assert response.status_code == 401

    def test_list_unknown_hive_returns_404(self, authenticated_client):
        client, _ = authenticated_client
        response = client.get("/api/hives/99999/inspections")
        assert response.status_code == 404

    def test_list_other_user_hive_returns_404(self, authenticated_client, multiple_test_users, db):
        client, _ = authenticated_client
        other_apiary = Apiary(stock_number="Other Apiary", name="Other Apiary", owner_id=multiple_test_users[0].id)
        db.add(other_apiary)
        db.commit()
        db.refresh(other_apiary)
        other_hive = Hive(name="Other Hive", owner_id=multiple_test_users[0].id, apiary_id=other_apiary.id)
        db.add(other_hive)
        db.commit()
        db.refresh(other_hive)

        response = client.get(f"/api/hives/{other_hive.id}/inspections")

        assert response.status_code == 404


@pytest.mark.unit
class TestCreateInspection:
    def test_create_minimal(self, authenticated_client, hive):
        client, _ = authenticated_client
        response = client.post(
            f"/api/hives/{hive['id']}/inspections",
            json={"date": str(date.today()), "queen_seen": True}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["queen_seen"] is True
        assert data["hive_id"] == hive["id"]
        assert "id" in data

    def test_create_full(self, authenticated_client, hive):
        client, _ = authenticated_client
        payload = {
            "date": str(date.today()),
            "queen_seen": False,
            "brood_strength": 7,
            "varroa_count": 2.5,
            "food_stores": 8,
            "swarm_cells": "play_cups",
            "mood": "calm",
            "strength": "strong",
            "weather": "Sunny",
            "next_steps": "Check again next week",
            "notes": "Looks healthy"
        }
        response = client.post(f"/api/hives/{hive['id']}/inspections", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["brood_strength"] == 7
        assert data["varroa_count"] == 2.5
        assert data["food_stores"] == 8
        assert data["swarm_cells"] == "play_cups"
        assert data["mood"] == "calm"
        assert data["strength"] == "strong"
        assert data["weather"] == "Sunny"
        assert data["next_steps"] == "Check again next week"

    def test_create_stores_weather_snapshot(self, authenticated_client, monkeypatch):
        client, _ = authenticated_client
        apiary = client.post(
            "/api/apiaries",
            json={"stock_number": "Weather Apiary", "name": "Weather Apiary", "latitude": 48.1374, "longitude": 11.5755},
        ).json()
        hive = client.post("/api/hives", json={"name": "Weather Hive", "apiary_id": apiary["id"]}).json()

        class Response:
            def raise_for_status(self):
                return None

            def json(self):
                return {
                    "current": {
                        "temperature_2m": 21.4,
                        "relative_humidity_2m": 58,
                        "precipitation": 0,
                        "weather_code": 2,
                        "wind_speed_10m": 8.5,
                    }
                }

        def fake_get(url, params, timeout):
            assert url == "https://api.open-meteo.com/v1/forecast"
            assert params["latitude"] == 48.1374
            assert params["longitude"] == 11.5755
            assert "temperature_2m" in params["current"]
            return Response()

        monkeypatch.setattr("app.services.inspection_weather.requests.get", fake_get)

        response = client.post(
            f"/api/hives/{hive['id']}/inspections",
            json={"date": str(date.today()), "queen_seen": True},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["weather"] == "Teilweise bewölkt · 21.4 °C · 58 % rF · Wind 8.5 km/h"
        assert data["weather_temperature"] == 21.4
        assert data["weather_humidity"] == 58
        assert data["weather_wind_speed"] == 8.5
        assert data["weather_precipitation"] == 0
        assert data["weather_code"] == 2
        assert data["weather_source"] == "open-meteo"
        assert data["weather_fetched_at"] is not None

    def test_create_critical_inspection_creates_tasks(self, authenticated_client, hive):
        client, _ = authenticated_client
        response = client.post(
            f"/api/hives/{hive['id']}/inspections",
            json={
                "date": str(date.today()),
                "queen_seen": False,
                "food_stores": 2,
                "varroa_count": 12,
                "swarm_cells": "queen_cells",
                "strength": "weak",
            },
        )
        assert response.status_code == 201

        tasks = client.get("/api/tasks").json()
        assert {task["title"] for task in tasks} == {
            "Check food stores",
            "Review varroa treatment",
            "Check queen status",
            "Perform swarm control",
        }

    def test_create_invalid_brood_strength(self, authenticated_client, hive):
        client, _ = authenticated_client
        response = client.post(
            f"/api/hives/{hive['id']}/inspections",
            json={"date": str(date.today()), "brood_strength": 11}
        )
        assert response.status_code == 422

    def test_create_unknown_hive_returns_404(self, authenticated_client):
        client, _ = authenticated_client
        response = client.post(
            "/api/hives/99999/inspections",
            json={"date": str(date.today())}
        )
        assert response.status_code == 404

    def test_create_on_other_user_hive_returns_404(self, authenticated_client, multiple_test_users, db):
        client, _ = authenticated_client
        other_apiary = Apiary(stock_number="Other Apiary", name="Other Apiary", owner_id=multiple_test_users[0].id)
        db.add(other_apiary)
        db.commit()
        db.refresh(other_apiary)
        other_hive = Hive(name="Other Hive", owner_id=multiple_test_users[0].id, apiary_id=other_apiary.id)
        db.add(other_hive)
        db.commit()
        db.refresh(other_hive)

        response = client.post(
            f"/api/hives/{other_hive.id}/inspections",
            json={"date": str(date.today()), "queen_seen": True},
        )

        assert response.status_code == 404


@pytest.mark.unit
class TestGetInspection:
    def test_get_inspection(self, authenticated_client, hive):
        client, _ = authenticated_client
        created = client.post(
            f"/api/hives/{hive['id']}/inspections",
            json={"date": str(date.today()), "queen_seen": True}
        ).json()
        response = client.get(f"/api/hives/{hive['id']}/inspections/{created['id']}")
        assert response.status_code == 200
        assert response.json()["id"] == created["id"]

    def test_get_not_found(self, authenticated_client, hive):
        client, _ = authenticated_client
        response = client.get(f"/api/hives/{hive['id']}/inspections/99999")
        assert response.status_code == 404

    def test_get_other_user_inspection_returns_404(self, authenticated_client, multiple_test_users, db):
        client, _ = authenticated_client
        other_apiary = Apiary(stock_number="Other Apiary", name="Other Apiary", owner_id=multiple_test_users[0].id)
        db.add(other_apiary)
        db.commit()
        db.refresh(other_apiary)
        other_hive = Hive(name="Other Hive", owner_id=multiple_test_users[0].id, apiary_id=other_apiary.id)
        db.add(other_hive)
        db.commit()
        db.refresh(other_hive)
        other_inspection = Inspection(hive_id=other_hive.id, date=date.today(), queen_seen=True)
        db.add(other_inspection)
        db.commit()
        db.refresh(other_inspection)

        response = client.get(f"/api/hives/{other_hive.id}/inspections/{other_inspection.id}")

        assert response.status_code == 404


@pytest.mark.unit
class TestUpdateInspection:
    def test_update(self, authenticated_client, hive):
        client, _ = authenticated_client
        created = client.post(
            f"/api/hives/{hive['id']}/inspections",
            json={"date": str(date.today()), "queen_seen": False}
        ).json()
        response = client.put(
            f"/api/hives/{hive['id']}/inspections/{created['id']}",
            json={"queen_seen": True, "notes": "Updated"}
        )
        assert response.status_code == 200
        assert response.json()["queen_seen"] is True
        assert response.json()["notes"] == "Updated"

    def test_update_not_found(self, authenticated_client, hive):
        client, _ = authenticated_client
        response = client.put(
            f"/api/hives/{hive['id']}/inspections/99999",
            json={"queen_seen": True}
        )
        assert response.status_code == 404

    def test_update_other_user_inspection_returns_404(self, authenticated_client, multiple_test_users, db):
        client, _ = authenticated_client
        other_apiary = Apiary(stock_number="Other Apiary", name="Other Apiary", owner_id=multiple_test_users[0].id)
        db.add(other_apiary)
        db.commit()
        db.refresh(other_apiary)
        other_hive = Hive(name="Other Hive", owner_id=multiple_test_users[0].id, apiary_id=other_apiary.id)
        db.add(other_hive)
        db.commit()
        db.refresh(other_hive)
        other_inspection = Inspection(hive_id=other_hive.id, date=date.today(), queen_seen=False)
        db.add(other_inspection)
        db.commit()
        db.refresh(other_inspection)

        response = client.put(
            f"/api/hives/{other_hive.id}/inspections/{other_inspection.id}",
            json={"queen_seen": True},
        )
        db.refresh(other_inspection)

        assert response.status_code == 404
        assert other_inspection.queen_seen is False


@pytest.mark.unit
class TestDeleteInspection:
    def test_delete(self, authenticated_client, hive):
        client, _ = authenticated_client
        created = client.post(
            f"/api/hives/{hive['id']}/inspections",
            json={"date": str(date.today())}
        ).json()
        response = client.delete(f"/api/hives/{hive['id']}/inspections/{created['id']}")
        assert response.status_code == 204
        assert client.get(f"/api/hives/{hive['id']}/inspections/{created['id']}").status_code == 404

    def test_delete_not_found(self, authenticated_client, hive):
        client, _ = authenticated_client
        response = client.delete(f"/api/hives/{hive['id']}/inspections/99999")
        assert response.status_code == 404

    def test_delete_other_user_inspection_returns_404(self, authenticated_client, multiple_test_users, db):
        client, _ = authenticated_client
        other_apiary = Apiary(stock_number="Other Apiary", name="Other Apiary", owner_id=multiple_test_users[0].id)
        db.add(other_apiary)
        db.commit()
        db.refresh(other_apiary)
        other_hive = Hive(name="Other Hive", owner_id=multiple_test_users[0].id, apiary_id=other_apiary.id)
        db.add(other_hive)
        db.commit()
        db.refresh(other_hive)
        other_inspection = Inspection(hive_id=other_hive.id, date=date.today(), queen_seen=True)
        db.add(other_inspection)
        db.commit()
        db.refresh(other_inspection)

        response = client.delete(f"/api/hives/{other_hive.id}/inspections/{other_inspection.id}")

        assert response.status_code == 404
        assert db.get(Inspection, other_inspection.id) is not None
