from datetime import date, timedelta

import pytest


@pytest.fixture
def apiary(authenticated_client):
    client, _ = authenticated_client
    response = client.post("/api/apiaries", json={"stock_number": "Selektion Apiary", "name": "Selektion Apiary"})
    assert response.status_code == 201
    return response.json()


def _create_hive(client, apiary_id, name, is_breeding_candidate=False):
    response = client.post(
        "/api/hives",
        json={"name": name, "apiary_id": apiary_id, "is_breeding_candidate": is_breeding_candidate},
    )
    assert response.status_code == 201
    return response.json()


@pytest.mark.unit
@pytest.mark.api
class TestBreedingSelection:
    def test_candidates_endpoint_requires_authentication(self, client):
        assert client.get("/api/breeding-selection/candidates").status_code == 401

    def test_only_breeding_candidates_are_ranked(self, authenticated_client, apiary):
        client, _ = authenticated_client
        candidate = _create_hive(client, apiary["id"], "Kandidat", is_breeding_candidate=True)
        _create_hive(client, apiary["id"], "Kein Kandidat", is_breeding_candidate=False)

        response = client.get("/api/breeding-selection/candidates")

        assert response.status_code == 200
        hive_ids = [item["hive_id"] for item in response.json()]
        assert hive_ids == [candidate["id"]]

    def test_no_weights_gives_zero_score(self, authenticated_client, apiary):
        client, _ = authenticated_client
        candidate = _create_hive(client, apiary["id"], "Kandidat", is_breeding_candidate=True)

        response = client.get("/api/breeding-selection/candidates")

        assert response.status_code == 200
        assert response.json()[0]["score"] == 0.0

    def test_bool_criterion_scores_as_zero_or_one(self, authenticated_client, apiary):
        client, _ = authenticated_client
        candidate = _create_hive(client, apiary["id"], "Kandidat", is_breeding_candidate=True)
        criteria = client.get("/api/inspection-criteria").json()
        # "Abgeschwärmt" is a custom bool criterion from the default seed (no field_key).
        bool_criterion = next(c for c in criteria if c["name"] == "Abgeschwärmt")

        weight_response = client.put(
            "/api/breeding-selection/weights", json={"criterion_id": bool_criterion["id"], "weight": 2.0}
        )
        assert weight_response.status_code == 200

        client.post(
            f"/api/hives/{candidate['id']}/inspections",
            json={
                "date": str(date.today()),
                "queen_seen": True,
                "criteria_values": {str(bool_criterion["id"]): True},
            },
        )

        response = client.get("/api/breeding-selection/candidates")

        assert response.status_code == 200
        assert response.json()[0]["score"] == pytest.approx(2.0)

    def test_select_criterion_uses_option_scores(self, authenticated_client, apiary):
        client, _ = authenticated_client
        candidate = _create_hive(client, apiary["id"], "Kandidat", is_breeding_candidate=True)
        criteria = client.get("/api/inspection-criteria").json()
        select_criterion = next(c for c in criteria if c["name"] == "Futterart")

        client.put(
            f"/api/inspection-criteria/{select_criterion['id']}",
            json={"option_scores": {"Honig": 5, "Futterteig": 3, "Futtersirup": 1, "Kein Futter": 0}},
        )
        client.put(
            "/api/breeding-selection/weights", json={"criterion_id": select_criterion["id"], "weight": 1.0}
        )

        client.post(
            f"/api/hives/{candidate['id']}/inspections",
            json={
                "date": str(date.today()),
                "queen_seen": True,
                "criteria_values": {str(select_criterion["id"]): "Honig"},
            },
        )

        response = client.get("/api/breeding-selection/candidates")

        assert response.status_code == 200
        assert response.json()[0]["score"] == pytest.approx(5.0)

    def test_text_criterion_is_excluded_from_scoring(self, authenticated_client, apiary):
        client, _ = authenticated_client
        candidate = _create_hive(client, apiary["id"], "Kandidat", is_breeding_candidate=True)
        text_criterion = client.post(
            "/api/inspection-criteria", json={"name": "Freitext", "value_type": "text"}
        ).json()

        client.put(
            "/api/breeding-selection/weights", json={"criterion_id": text_criterion["id"], "weight": 5.0}
        )
        client.post(
            f"/api/hives/{candidate['id']}/inspections",
            json={
                "date": str(date.today()),
                "queen_seen": True,
                "criteria_values": {str(text_criterion["id"]): "Freitext-Wert"},
            },
        )

        response = client.get("/api/breeding-selection/candidates")

        assert response.status_code == 200
        assert response.json()[0]["score"] == 0.0

    def test_only_latest_inspection_is_used(self, authenticated_client, apiary):
        client, _ = authenticated_client
        candidate = _create_hive(client, apiary["id"], "Kandidat", is_breeding_candidate=True)
        criteria = client.get("/api/inspection-criteria").json()
        bool_criterion = next(c for c in criteria if c["name"] == "Abgeschwärmt")

        client.put(
            "/api/breeding-selection/weights", json={"criterion_id": bool_criterion["id"], "weight": 1.0}
        )

        old_date = date.today() - timedelta(days=30)
        client.post(
            f"/api/hives/{candidate['id']}/inspections",
            json={
                "date": str(old_date),
                "queen_seen": True,
                "criteria_values": {str(bool_criterion["id"]): True},
            },
        )
        latest_date = date.today()
        client.post(
            f"/api/hives/{candidate['id']}/inspections",
            json={
                "date": str(latest_date),
                "queen_seen": True,
                "criteria_values": {str(bool_criterion["id"]): False},
            },
        )

        response = client.get("/api/breeding-selection/candidates")

        assert response.status_code == 200
        candidate_result = response.json()[0]
        assert candidate_result["score"] == 0.0
        assert candidate_result["latest_inspection_date"] == str(latest_date)

    def test_candidates_ranked_by_score_descending(self, authenticated_client, apiary):
        client, _ = authenticated_client
        strong = _create_hive(client, apiary["id"], "Stark", is_breeding_candidate=True)
        weak = _create_hive(client, apiary["id"], "Schwach", is_breeding_candidate=True)
        criteria = client.get("/api/inspection-criteria").json()
        bool_criterion = next(c for c in criteria if c["name"] == "Abgeschwärmt")

        client.put(
            "/api/breeding-selection/weights", json={"criterion_id": bool_criterion["id"], "weight": 1.0}
        )
        client.post(
            f"/api/hives/{strong['id']}/inspections",
            json={"date": str(date.today()), "queen_seen": True, "criteria_values": {str(bool_criterion["id"]): True}},
        )
        client.post(
            f"/api/hives/{weak['id']}/inspections",
            json={"date": str(date.today()), "queen_seen": True, "criteria_values": {str(bool_criterion["id"]): False}},
        )

        response = client.get("/api/breeding-selection/candidates")

        assert response.status_code == 200
        ranked_ids = [item["hive_id"] for item in response.json()]
        assert ranked_ids == [strong["id"], weak["id"]]

    def test_weights_crud(self, authenticated_client, apiary):
        client, _ = authenticated_client
        criteria = client.get("/api/inspection-criteria").json()
        criterion = criteria[0]

        create_response = client.put(
            "/api/breeding-selection/weights", json={"criterion_id": criterion["id"], "weight": 3.0}
        )
        assert create_response.status_code == 200
        assert create_response.json()["weight"] == 3.0

        list_response = client.get("/api/breeding-selection/weights")
        assert list_response.status_code == 200
        assert len(list_response.json()) == 1

        update_response = client.put(
            "/api/breeding-selection/weights", json={"criterion_id": criterion["id"], "weight": 4.5}
        )
        assert update_response.json()["weight"] == 4.5

        delete_response = client.delete(f"/api/breeding-selection/weights/{criterion['id']}")
        assert delete_response.status_code == 204
        assert client.get("/api/breeding-selection/weights").json() == []
