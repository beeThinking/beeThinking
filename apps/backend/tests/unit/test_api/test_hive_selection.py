from datetime import date

import pytest


@pytest.fixture
def apiary(authenticated_client):
    client, _ = authenticated_client
    response = client.post("/api/apiaries", json={"stock_number": "Selection Stand"})
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def stars_criterion(authenticated_client):
    client, _ = authenticated_client
    response = client.post("/api/inspection-criteria", json={
        "name": "Sanftmut",
        "value_type": "stars",
    })
    assert response.status_code == 201
    return response.json()


def _make_hive(client, apiary_id, name, tags=None):
    payload = {"name": name, "apiary_id": apiary_id}
    if tags is not None:
        payload["tags"] = tags
    response = client.post("/api/hives", json=payload)
    assert response.status_code == 201
    return response.json()


def _add_inspection(client, hive_id, criterion_id, value):
    response = client.post(f"/api/hives/{hive_id}/inspections", json={
        "date": str(date.today()),
        "criteria_values": {str(criterion_id): value},
    })
    assert response.status_code == 201
    return response.json()


@pytest.mark.unit
class TestHiveSelectionFilter:
    def test_filter_by_criterion_average(self, authenticated_client, apiary, stars_criterion):
        client, _ = authenticated_client
        gentle_hive = _make_hive(client, apiary["id"], "Gentle Hive")
        aggressive_hive = _make_hive(client, apiary["id"], "Aggressive Hive")
        _add_inspection(client, gentle_hive["id"], stars_criterion["id"], 5)
        _add_inspection(client, aggressive_hive["id"], stars_criterion["id"], 1)

        response = client.post("/api/hive-selection/filter", json={
            "criteria": [{"criterion_id": stars_criterion["id"], "min_average": 3}],
        })

        assert response.status_code == 200
        hive_ids = [c["hive_id"] for c in response.json()]
        assert gentle_hive["id"] in hive_ids
        assert aggressive_hive["id"] not in hive_ids

    def test_filter_by_tags(self, authenticated_client, apiary):
        client, _ = authenticated_client
        tagged_hive = _make_hive(client, apiary["id"], "Tagged Hive", tags=["breeding"])
        untagged_hive = _make_hive(client, apiary["id"], "Untagged Hive")

        response = client.post("/api/hive-selection/filter", json={"tags": ["breeding"]})

        assert response.status_code == 200
        hive_ids = [c["hive_id"] for c in response.json()]
        assert tagged_hive["id"] in hive_ids
        assert untagged_hive["id"] not in hive_ids

    def test_average_uses_full_history_not_just_latest(self, authenticated_client, apiary, stars_criterion):
        client, _ = authenticated_client
        hive = _make_hive(client, apiary["id"], "History Hive")
        _add_inspection(client, hive["id"], stars_criterion["id"], 1)
        _add_inspection(client, hive["id"], stars_criterion["id"], 5)

        response = client.post("/api/hive-selection/filter", json={
            "criteria": [{"criterion_id": stars_criterion["id"]}],
        })

        assert response.status_code == 200
        candidate = next(c for c in response.json() if c["hive_id"] == hive["id"])
        assert candidate["criterion_averages"][str(stars_criterion["id"])] == 3.0
        assert candidate["inspection_count"] == 2

    def test_requires_auth(self, client):
        assert client.post("/api/hive-selection/filter", json={}).status_code == 401


@pytest.mark.unit
class TestHiveSelectionBatchTasks:
    def test_batch_create_tasks_for_selection(self, authenticated_client, apiary):
        client, _ = authenticated_client
        hive_a = _make_hive(client, apiary["id"], "Hive A")
        hive_b = _make_hive(client, apiary["id"], "Hive B")

        response = client.post("/api/hive-selection/batch-tasks", json={
            "hive_ids": [hive_a["id"], hive_b["id"]],
            "title": "Requeen check",
        })

        assert response.status_code == 201
        assert len(response.json()["created_task_ids"]) == 2

        tasks = client.get("/api/tasks").json()
        titles = [t["title"] for t in tasks if t["hive_id"] in {hive_a["id"], hive_b["id"]}]
        assert titles.count("Requeen check") == 2

    def test_batch_create_rejects_unknown_hive(self, authenticated_client, apiary):
        client, _ = authenticated_client
        hive_a = _make_hive(client, apiary["id"], "Hive A")

        response = client.post("/api/hive-selection/batch-tasks", json={
            "hive_ids": [hive_a["id"], 999999],
            "title": "Requeen check",
        })

        assert response.status_code == 404
