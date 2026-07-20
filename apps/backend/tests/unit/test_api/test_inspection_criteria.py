from datetime import date

import pytest


@pytest.fixture
def apiary(authenticated_client):
    client, _ = authenticated_client
    response = client.post("/api/apiaries", json={"stock_number": "Criteria Apiary", "name": "Criteria Apiary"})
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def hive(authenticated_client, apiary):
    client, _ = authenticated_client
    response = client.post("/api/hives", json={"name": "Criteria Hive", "apiary_id": apiary["id"]})
    assert response.status_code == 201
    return response.json()


@pytest.mark.unit
@pytest.mark.api
class TestInspectionCriteriaApi:
    def test_first_access_seeds_default_catalog(self, authenticated_client):
        client, _ = authenticated_client

        response = client.get("/api/inspection-criteria")

        assert response.status_code == 200
        criteria = response.json()
        assert len(criteria) >= 8
        names = [criterion["name"] for criterion in criteria]
        assert "Sanftmut" in names
        assert "Abgeschwärmt" in names
        futterart = next(criterion for criterion in criteria if criterion["name"] == "Futterart")
        assert futterart["value_type"] == "select"
        assert "Futterteig" in futterart["options"]

    def test_seeding_happens_only_once(self, authenticated_client):
        client, _ = authenticated_client

        first = client.get("/api/inspection-criteria").json()
        second = client.get("/api/inspection-criteria").json()

        assert len(first) == len(second)

    def test_create_custom_criterion(self, authenticated_client):
        client, _ = authenticated_client

        response = client.post(
            "/api/inspection-criteria",
            json={"name": "Pollenversorgung", "section": "allg_befund", "value_type": "stars", "sort_order": 90},
        )

        assert response.status_code == 201
        assert response.json()["name"] == "Pollenversorgung"

    def test_update_pick_list_options(self, authenticated_client):
        client, _ = authenticated_client
        criteria = client.get("/api/inspection-criteria").json()
        futterart = next(criterion for criterion in criteria if criterion["value_type"] == "select")

        response = client.put(
            f"/api/inspection-criteria/{futterart['id']}",
            json={"options": ["Honig", "Futterteig", "Futtersirup", "Kein Futter", "Bienenfutterteig Eigenbau"]},
        )

        assert response.status_code == 200
        assert "Bienenfutterteig Eigenbau" in response.json()["options"]

    def test_deactivate_criterion_hides_it_from_active_list(self, authenticated_client):
        client, _ = authenticated_client
        criteria = client.get("/api/inspection-criteria").json()
        target = criteria[0]

        response = client.put(f"/api/inspection-criteria/{target['id']}", json={"is_active": False})
        assert response.status_code == 200

        active = client.get("/api/inspection-criteria?include_inactive=false").json()
        assert all(criterion["id"] != target["id"] for criterion in active)

    def test_delete_criterion(self, authenticated_client):
        client, _ = authenticated_client
        client.get("/api/inspection-criteria")
        created = client.post(
            "/api/inspection-criteria",
            json={"name": "Temporär", "value_type": "bool"},
        ).json()

        assert client.delete(f"/api/inspection-criteria/{created['id']}").status_code == 204
        remaining = client.get("/api/inspection-criteria").json()
        assert all(criterion["name"] != "Temporär" for criterion in remaining)

    def test_invalid_value_type_rejected(self, authenticated_client):
        client, _ = authenticated_client

        response = client.post(
            "/api/inspection-criteria",
            json={"name": "Bad", "value_type": "emoji"},
        )

        assert response.status_code == 422

    def test_criteria_require_authentication(self, client):
        assert client.get("/api/inspection-criteria").status_code == 401


@pytest.mark.unit
@pytest.mark.api
class TestInspectionWithCriteriaValues:
    def test_inspection_stores_criteria_values_and_weight(self, authenticated_client, hive):
        client, _ = authenticated_client
        criteria = client.get("/api/inspection-criteria").json()
        sanftmut = next(criterion for criterion in criteria if criterion["name"] == "Sanftmut")

        response = client.post(
            f"/api/hives/{hive['id']}/inspections",
            json={
                "date": str(date.today()),
                "queen_seen": True,
                "hive_weight_kg": 42.5,
                "criteria_values": {str(sanftmut["id"]): 5},
            },
        )

        assert response.status_code == 201
        inspection = response.json()
        assert inspection["hive_weight_kg"] == 42.5
        assert inspection["criteria_values"] == {str(sanftmut["id"]): 5}

        fetched = client.get(f"/api/hives/{hive['id']}/inspections/{inspection['id']}")
        assert fetched.json()["criteria_values"] == {str(sanftmut["id"]): 5}
