from datetime import date

import pytest


@pytest.fixture
def apiary(authenticated_client):
    client, _ = authenticated_client
    response = client.post("/api/apiaries", json={"stock_number": "Entity Apiary", "name": "Entity Apiary"})
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def hive(authenticated_client, apiary):
    client, _ = authenticated_client
    response = client.post("/api/hives", json={"name": "Entity Hive", "apiary_id": apiary["id"]})
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def inspection(authenticated_client, hive):
    client, _ = authenticated_client
    response = client.post(
        f"/api/hives/{hive['id']}/inspections",
        json={"date": str(date.today()), "queen_seen": True},
    )
    assert response.status_code == 201
    return response.json()


@pytest.mark.unit
class TestTasksApi:
    def test_task_crud_and_complete(self, authenticated_client, hive, apiary):
        client, _ = authenticated_client
        response = client.post(
            "/api/tasks",
            json={
                "title": "Check feed",
                "hive_id": hive["id"],
                "apiary_id": apiary["id"],
                "due_date": str(date.today()),
                "priority": "high",
            },
        )
        assert response.status_code == 201
        task = response.json()

        assert client.get("/api/tasks").json()[0]["title"] == "Check feed"

        response = client.put(f"/api/tasks/{task['id']}", json={"title": "Check feed stores"})
        assert response.status_code == 200
        assert response.json()["title"] == "Check feed stores"

        response = client.post(f"/api/tasks/{task['id']}/complete")
        assert response.status_code == 200
        assert response.json()["status"] == "done"
        assert response.json()["completed_at"] is not None

        assert client.delete(f"/api/tasks/{task['id']}").status_code == 204
        assert client.get(f"/api/tasks/{task['id']}").status_code == 404

    def test_task_rejects_foreign_hive(self, authenticated_client, multiple_test_users, db):
        from app.models.apiary import Apiary
        from app.models.hive import Hive

        client, _ = authenticated_client
        other_apiary = Apiary(stock_number="Other", name="Other", owner_id=multiple_test_users[0].id)
        db.add(other_apiary)
        db.commit()
        db.refresh(other_apiary)
        other_hive = Hive(name="Other Hive", owner_id=multiple_test_users[0].id, apiary_id=other_apiary.id)
        db.add(other_hive)
        db.commit()
        db.refresh(other_hive)

        response = client.post("/api/tasks", json={"title": "Nope", "hive_id": other_hive.id})

        assert response.status_code == 404


@pytest.mark.unit
class TestQueensApi:
    def test_queen_crud(self, authenticated_client, hive):
        client, _ = authenticated_client
        response = client.post("/api/queens", json={"hive_id": hive["id"], "year": 2026, "name": "Blue"})
        assert response.status_code == 201
        queen = response.json()

        assert client.get("/api/queens").json()[0]["id"] == queen["id"]
        assert client.get(f"/api/queens/{queen['id']}").status_code == 200

        response = client.put(f"/api/queens/{queen['id']}", json={"marking_color": "blue"})
        assert response.status_code == 200
        assert response.json()["marking_color"] == "blue"

        assert client.delete(f"/api/queens/{queen['id']}").status_code == 204


@pytest.mark.unit
class TestTreatmentsApi:
    def test_treatment_crud(self, authenticated_client, hive):
        client, _ = authenticated_client
        response = client.post(
            "/api/treatments",
            json={"hive_id": hive["id"], "started_at": str(date.today()), "product": "Oxalic acid"},
        )
        assert response.status_code == 201
        treatment = response.json()

        assert client.get("/api/treatments").json()[0]["product"] == "Oxalic acid"

        response = client.put(f"/api/treatments/{treatment['id']}", json={"dosage": "30 ml"})
        assert response.status_code == 200
        assert response.json()["dosage"] == "30 ml"

        assert client.delete(f"/api/treatments/{treatment['id']}").status_code == 204

    def test_treatment_stores_weather_context(self, authenticated_client, hive, apiary):
        client, _ = authenticated_client
        windows = client.post(f"/api/apiaries/{apiary['id']}/varroa-weather/refresh").json()

        response = client.post(
            "/api/treatments",
            json={
                "hive_id": hive["id"],
                "started_at": str(date.today()),
                "product": "Formic acid",
                "weather_window_id": windows[0]["id"],
            },
        )

        assert response.status_code == 201
        assert response.json()["weather_rating"] == windows[0]["rating"]

        journal = client.get("/api/treatments/journal/export")
        assert journal.status_code == 200
        assert journal.json()["items"][0]["weather_source"] == windows[0]["source"]


@pytest.mark.unit
class TestVarroaWeatherApi:
    def test_apiary_varroa_weather_and_hive_assistant(self, authenticated_client, hive, apiary):
        client, _ = authenticated_client

        response = client.get(f"/api/apiaries/{apiary['id']}/varroa-weather")
        assert response.status_code == 200
        assert len(response.json()) == 5
        assert response.json()[0]["treatment_type"] == "formic_acid_short"

        assistant = client.get(f"/api/hives/{hive['id']}/varroa-assistant")
        assert assistant.status_code == 200
        assert "Planungshilfe" in assistant.json()["disclaimer"]


@pytest.mark.unit
class TestHarvestsApi:
    def test_harvest_crud(self, authenticated_client, hive, apiary):
        client, _ = authenticated_client
        response = client.post(
            "/api/harvests",
            json={
                "hive_id": hive["id"],
                "apiary_id": apiary["id"],
                "harvest_date": str(date.today()),
                "amount_kg": 12.5,
            },
        )
        assert response.status_code == 201
        harvest = response.json()

        assert client.get("/api/harvests").json()[0]["amount_kg"] == 12.5

        response = client.put(f"/api/harvests/{harvest['id']}", json={"batch_code": "SPRING-1"})
        assert response.status_code == 200
        assert response.json()["batch_code"] == "SPRING-1"

        assert client.delete(f"/api/harvests/{harvest['id']}").status_code == 204


@pytest.mark.unit
class TestPhotosApi:
    def test_photo_create_list_get_delete(self, authenticated_client, hive, inspection):
        client, _ = authenticated_client
        response = client.post(
            "/api/photos",
            json={
                "hive_id": hive["id"],
                "inspection_id": inspection["id"],
                "object_key": "hives/1/photo.jpg",
                "filename": "photo.jpg",
                "content_type": "image/jpeg",
                "size_bytes": 12345,
            },
        )
        assert response.status_code == 201
        photo = response.json()

        assert client.get("/api/photos").json()[0]["filename"] == "photo.jpg"
        assert client.get(f"/api/photos/{photo['id']}").status_code == 200
        assert client.delete(f"/api/photos/{photo['id']}").status_code == 204

    def test_photo_upload_validates_and_deletes_object(self, authenticated_client, hive, monkeypatch):
        from app.api import photos as photos_api

        client, _ = authenticated_client
        uploaded = []
        deleted = []
        monkeypatch.setattr(photos_api, "upload_photo_object", lambda key, file, size, content_type: uploaded.append(key))
        monkeypatch.setattr(photos_api, "delete_object", deleted.append)

        response = client.post(
            "/api/photos/upload",
            data={"hive_id": str(hive["id"])},
            files={"file": ("hive.jpg", b"image-data", "image/jpeg")},
        )

        assert response.status_code == 201
        assert uploaded == [response.json()["object_key"]]
        assert client.delete(f"/api/photos/{response.json()['id']}").status_code == 204
        assert deleted == uploaded

    def test_photo_upload_rejects_unsupported_type(self, authenticated_client, hive):
        client, _ = authenticated_client

        response = client.post(
            "/api/photos/upload",
            data={"hive_id": str(hive["id"])},
            files={"file": ("payload.txt", b"not-an-image", "text/plain")},
        )

        assert response.status_code == 415


@pytest.mark.unit
class TestDashboardAndTimeline:
    def test_dashboard_summary_and_hive_timeline(self, authenticated_client, hive):
        client, _ = authenticated_client
        client.post("/api/tasks", json={"title": "Inspect", "hive_id": hive["id"]})
        client.post(
            f"/api/hives/{hive['id']}/inspections",
            json={"date": str(date.today()), "queen_seen": True},
        )

        summary = client.get("/api/dashboard/summary")
        assert summary.status_code == 200
        assert summary.json()["hive_count"] == 1
        assert summary.json()["open_task_count"] == 1

        timeline = client.get(f"/api/hives/{hive['id']}/timeline")
        assert timeline.status_code == 200
        assert {event["type"] for event in timeline.json()} >= {"task", "inspection"}
