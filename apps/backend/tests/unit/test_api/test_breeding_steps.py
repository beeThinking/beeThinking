from datetime import date, timedelta

import pytest


@pytest.fixture
def apiary(authenticated_client):
    client, _ = authenticated_client
    response = client.post("/api/apiaries", json={"stock_number": "Kalender Apiary", "name": "Kalender Apiary"})
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def herkunftsvolk(authenticated_client, apiary):
    client, _ = authenticated_client
    response = client.post("/api/hives", json={"name": "Herkunftsvolk", "apiary_id": apiary["id"]})
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def zuchtreihe(authenticated_client, apiary, herkunftsvolk):
    client, _ = authenticated_client
    response = client.post(
        "/api/zuchtreihen",
        json={"name": "Kalender Reihe", "apiary_id": apiary["id"], "herkunftsvolk_id": herkunftsvolk["id"]},
    )
    assert response.status_code == 201
    return response.json()


EXPECTED_OFFSETS = {
    "pflegevolk_vorbereiten": -1,
    "umlarven": 0,
    "annahmekontrolle": 1,
    "kaefigen_1": 10,
    "kaefigen_2": 11,
    "schlupf": 12,
    "voelkchen_bilden": 13,
    "belegstelle": 15,
    "abholen": 30,
}


@pytest.mark.unit
@pytest.mark.api
class TestBreedingStepGeneration:
    def test_generate_steps_from_umlarven_date(self, authenticated_client, zuchtreihe):
        client, _ = authenticated_client
        umlarven_date = date(2026, 6, 1)

        response = client.post(
            f"/api/zuchtreihen/{zuchtreihe['id']}/steps/generate",
            json={"umlarven_date": str(umlarven_date)},
        )

        assert response.status_code == 201
        steps = response.json()
        assert len(steps) == 9
        by_name = {step["name"]: step["date"] for step in steps}
        for name, offset in EXPECTED_OFFSETS.items():
            expected_date = str(umlarven_date + timedelta(days=offset))
            assert by_name[name] == expected_date

    def test_generate_steps_twice_conflicts(self, authenticated_client, zuchtreihe):
        client, _ = authenticated_client
        client.post(
            f"/api/zuchtreihen/{zuchtreihe['id']}/steps/generate",
            json={"umlarven_date": str(date(2026, 6, 1))},
        )

        response = client.post(
            f"/api/zuchtreihen/{zuchtreihe['id']}/steps/generate",
            json={"umlarven_date": str(date(2026, 6, 1))},
        )

        assert response.status_code == 409

    def test_editing_step_date_does_not_cascade(self, authenticated_client, zuchtreihe):
        client, _ = authenticated_client
        steps = client.post(
            f"/api/zuchtreihen/{zuchtreihe['id']}/steps/generate",
            json={"umlarven_date": str(date(2026, 6, 1))},
        ).json()
        umlarven_step = next(step for step in steps if step["name"] == "umlarven")
        annahmekontrolle_step = next(step for step in steps if step["name"] == "annahmekontrolle")

        new_date = str(date(2026, 6, 3))
        update_response = client.put(
            f"/api/zuchtreihen/{zuchtreihe['id']}/steps/{umlarven_step['id']}",
            json={"date": new_date},
        )
        assert update_response.status_code == 200
        assert update_response.json()["date"] == new_date

        unchanged = client.get(f"/api/zuchtreihen/{zuchtreihe['id']}/steps").json()
        still_annahmekontrolle = next(step for step in unchanged if step["name"] == "annahmekontrolle")
        assert still_annahmekontrolle["date"] == annahmekontrolle_step["date"]

    def test_create_single_step_manually(self, authenticated_client, zuchtreihe):
        client, _ = authenticated_client

        response = client.post(
            f"/api/zuchtreihen/{zuchtreihe['id']}/steps",
            json={"name": "umlarven", "date": str(date(2026, 7, 1)), "notes": "erste Runde"},
        )

        assert response.status_code == 201
        assert response.json()["notes"] == "erste Runde"

    def test_delete_step(self, authenticated_client, zuchtreihe):
        client, _ = authenticated_client
        step = client.post(
            f"/api/zuchtreihen/{zuchtreihe['id']}/steps",
            json={"name": "umlarven", "date": str(date(2026, 7, 1))},
        ).json()

        response = client.delete(f"/api/zuchtreihen/{zuchtreihe['id']}/steps/{step['id']}")

        assert response.status_code == 204
        remaining = client.get(f"/api/zuchtreihen/{zuchtreihe['id']}/steps").json()
        assert remaining == []


@pytest.mark.unit
@pytest.mark.api
class TestBreedingStepTaskCreation:
    def test_generating_steps_creates_one_task_per_step(self, authenticated_client, zuchtreihe, herkunftsvolk):
        client, _ = authenticated_client

        client.post(
            f"/api/zuchtreihen/{zuchtreihe['id']}/steps/generate",
            json={"umlarven_date": str(date(2026, 6, 1))},
        )

        tasks_response = client.get("/api/tasks")
        assert tasks_response.status_code == 200
        breeding_tasks = [task for task in tasks_response.json() if task["source"] == "breeding"]
        assert len(breeding_tasks) == 9
        assert all(task["hive_id"] == herkunftsvolk["id"] for task in breeding_tasks)

    def test_manual_step_creates_a_task(self, authenticated_client, zuchtreihe):
        client, _ = authenticated_client

        step = client.post(
            f"/api/zuchtreihen/{zuchtreihe['id']}/steps",
            json={"name": "umlarven", "date": str(date(2026, 7, 1))},
        ).json()

        assert step["task_id"] is not None
        task = client.get("/api/tasks").json()
        matching = [t for t in task if t["id"] == step["task_id"]]
        assert len(matching) == 1
        assert matching[0]["source"] == "breeding"
        assert matching[0]["due_date"] == str(date(2026, 7, 1))

    def test_updating_step_date_updates_linked_task(self, authenticated_client, zuchtreihe):
        client, _ = authenticated_client
        step = client.post(
            f"/api/zuchtreihen/{zuchtreihe['id']}/steps",
            json={"name": "umlarven", "date": str(date(2026, 7, 1))},
        ).json()

        client.put(
            f"/api/zuchtreihen/{zuchtreihe['id']}/steps/{step['id']}",
            json={"date": str(date(2026, 7, 5))},
        )

        task = client.get(f"/api/tasks/{step['task_id']}").json()
        assert task["due_date"] == str(date(2026, 7, 5))

    def test_deleting_step_deletes_linked_task(self, authenticated_client, zuchtreihe):
        client, _ = authenticated_client
        step = client.post(
            f"/api/zuchtreihen/{zuchtreihe['id']}/steps",
            json={"name": "umlarven", "date": str(date(2026, 7, 1))},
        ).json()

        client.delete(f"/api/zuchtreihen/{zuchtreihe['id']}/steps/{step['id']}")

        assert client.get(f"/api/tasks/{step['task_id']}").status_code == 404
