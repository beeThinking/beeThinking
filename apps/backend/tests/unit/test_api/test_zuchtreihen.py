import pytest


@pytest.fixture
def apiary(authenticated_client):
    client, _ = authenticated_client
    response = client.post("/api/apiaries", json={"stock_number": "Zucht Apiary", "name": "Zucht Apiary"})
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def herkunftsvolk(authenticated_client, apiary):
    client, _ = authenticated_client
    response = client.post("/api/hives", json={"name": "Herkunftsvolk", "apiary_id": apiary["id"]})
    assert response.status_code == 201
    return response.json()


@pytest.mark.unit
@pytest.mark.api
class TestZuchtreiheCrud:
    def test_create_zuchtreihe(self, authenticated_client, apiary, herkunftsvolk):
        client, _ = authenticated_client

        response = client.post(
            "/api/zuchtreihen",
            json={
                "name": "Zuchtreihe 2026-A",
                "apiary_id": apiary["id"],
                "herkunftsvolk_id": herkunftsvolk["id"],
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Zuchtreihe 2026-A"
        assert data["apiary_id"] == apiary["id"]
        assert data["herkunftsvolk_id"] == herkunftsvolk["id"]
        assert data["steps"] == []

    def test_create_zuchtreihe_requires_owned_apiary(self, authenticated_client):
        client, _ = authenticated_client

        response = client.post("/api/zuchtreihen", json={"name": "X", "apiary_id": 9999})

        assert response.status_code == 404

    def test_list_zuchtreihen(self, authenticated_client, apiary):
        client, _ = authenticated_client
        client.post("/api/zuchtreihen", json={"name": "A", "apiary_id": apiary["id"]})
        client.post("/api/zuchtreihen", json={"name": "B", "apiary_id": apiary["id"]})

        response = client.get("/api/zuchtreihen")

        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_list_zuchtreihen_filter_by_apiary(self, authenticated_client, apiary):
        client, _ = authenticated_client
        other_apiary = client.post("/api/apiaries", json={"stock_number": "Other", "name": "Other"}).json()
        client.post("/api/zuchtreihen", json={"name": "A", "apiary_id": apiary["id"]})
        client.post("/api/zuchtreihen", json={"name": "B", "apiary_id": other_apiary["id"]})

        response = client.get(f"/api/zuchtreihen?apiary_id={apiary['id']}")

        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["name"] == "A"

    def test_get_zuchtreihe(self, authenticated_client, apiary):
        client, _ = authenticated_client
        created = client.post("/api/zuchtreihen", json={"name": "A", "apiary_id": apiary["id"]}).json()

        response = client.get(f"/api/zuchtreihen/{created['id']}")

        assert response.status_code == 200
        assert response.json()["id"] == created["id"]

    def test_get_missing_zuchtreihe_returns_404(self, authenticated_client):
        client, _ = authenticated_client
        response = client.get("/api/zuchtreihen/9999")
        assert response.status_code == 404

    def test_update_zuchtreihe(self, authenticated_client, apiary):
        client, _ = authenticated_client
        created = client.post("/api/zuchtreihen", json={"name": "A", "apiary_id": apiary["id"]}).json()

        response = client.put(f"/api/zuchtreihen/{created['id']}", json={"name": "Renamed"})

        assert response.status_code == 200
        assert response.json()["name"] == "Renamed"

    def test_delete_zuchtreihe(self, authenticated_client, apiary):
        client, _ = authenticated_client
        created = client.post("/api/zuchtreihen", json={"name": "A", "apiary_id": apiary["id"]}).json()

        response = client.delete(f"/api/zuchtreihen/{created['id']}")

        assert response.status_code == 204
        assert client.get(f"/api/zuchtreihen/{created['id']}").status_code == 404

    def test_zuchtreihen_require_authentication(self, client):
        assert client.get("/api/zuchtreihen").status_code == 401


@pytest.mark.unit
@pytest.mark.api
class TestZuchtreiheCounters:
    def test_create_with_counters_and_success_rates(self, authenticated_client, apiary):
        client, _ = authenticated_client

        response = client.post(
            "/api/zuchtreihen",
            json={
                "name": "Counter Test",
                "apiary_id": apiary["id"],
                "anzahl_larven": 20,
                "anzahl_angenommen": 15,
                "anzahl_geschluepft": 12,
                "anzahl_begattet": 10,
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["anzahl_larven"] == 20
        assert data["success_rate_angenommen"] == pytest.approx(75.0)
        assert data["success_rate_geschluepft"] == pytest.approx(80.0)
        assert data["success_rate_begattet"] == pytest.approx(83.33, rel=1e-2)

    def test_success_rate_is_none_without_counters(self, authenticated_client, apiary):
        client, _ = authenticated_client

        response = client.post("/api/zuchtreihen", json={"name": "No Counters", "apiary_id": apiary["id"]})

        assert response.status_code == 201
        data = response.json()
        assert data["success_rate_angenommen"] is None
        assert data["success_rate_geschluepft"] is None
        assert data["success_rate_begattet"] is None

    def test_update_counters_recomputes_rates(self, authenticated_client, apiary):
        client, _ = authenticated_client
        created = client.post(
            "/api/zuchtreihen",
            json={"name": "Update Counters", "apiary_id": apiary["id"], "anzahl_larven": 10, "anzahl_angenommen": 5},
        ).json()
        assert created["success_rate_angenommen"] == pytest.approx(50.0)

        response = client.put(f"/api/zuchtreihen/{created['id']}", json={"anzahl_angenommen": 8})

        assert response.status_code == 200
        assert response.json()["success_rate_angenommen"] == pytest.approx(80.0)

    def test_counters_are_manual_no_dependency_on_steps(self, authenticated_client, apiary):
        client, _ = authenticated_client
        created = client.post(
            "/api/zuchtreihen",
            json={"name": "Manual Counters", "apiary_id": apiary["id"], "anzahl_larven": 30},
        ).json()

        assert created["steps"] == []
        assert created["anzahl_larven"] == 30
