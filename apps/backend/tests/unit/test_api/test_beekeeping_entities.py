from datetime import date

import pytest


@pytest.fixture
def apiary(authenticated_client):
    client, _ = authenticated_client
    response = client.post("/api/apiaries", json={"name": "Entity Apiary"})
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
        other_apiary = Apiary(name="Other", owner_id=multiple_test_users[0].id)
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
