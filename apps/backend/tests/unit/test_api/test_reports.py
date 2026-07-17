from datetime import date

import pytest


@pytest.fixture
def apiary(authenticated_client):
    client, _ = authenticated_client
    response = client.post("/api/apiaries", json={"stock_number": "Report Apiary", "name": "Report Apiary"})
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def hive(authenticated_client, apiary):
    client, _ = authenticated_client
    response = client.post("/api/hives", json={"name": "Report Hive", "apiary_id": apiary["id"]})
    assert response.status_code == 201
    return response.json()


@pytest.mark.unit
@pytest.mark.api
class TestReportsApi:
    def test_yearly_report(self, authenticated_client, apiary, hive):
        client, _ = authenticated_client
        year = date.today().year
        client.post(
            "/api/harvests",
            json={
                "apiary_id": apiary["id"],
                "hive_id": hive["id"],
                "harvest_date": f"{year}-06-09",
                "crop_type": "Sommerhonig",
                "amount_kg": 12.5,
            },
        )

        response = client.get(f"/api/reports/yearly?year={year}")

        assert response.status_code == 200

    def test_harvest_by_apiary(self, authenticated_client, apiary, hive):
        client, _ = authenticated_client
        client.post(
            "/api/harvests",
            json={
                "apiary_id": apiary["id"],
                "hive_id": hive["id"],
                "harvest_date": "2026-06-09",
                "crop_type": "Sommerhonig",
                "amount_kg": 12.5,
            },
        )

        response = client.get("/api/reports/harvest-by-apiary")

        assert response.status_code == 200
        rows = response.json()
        assert len(rows) == 1
        assert rows[0]["amount_kg"] == 12.5

    def test_varroa_report_filters_by_date(self, authenticated_client, hive):
        client, _ = authenticated_client
        client.post(
            f"/api/hives/{hive['id']}/inspections",
            json={"date": "2026-05-01", "varroa_count": 12},
        )
        client.post(
            f"/api/hives/{hive['id']}/inspections",
            json={"date": "2026-07-01", "varroa_count": 4},
        )

        all_rows = client.get("/api/reports/varroa").json()
        filtered_rows = client.get("/api/reports/varroa?from_date=2026-06-01").json()

        assert len(all_rows) == 2
        assert len(filtered_rows) == 1
        assert filtered_rows[0]["varroa_count"] == 4.0

    def test_reports_require_authentication(self, client):
        assert client.get("/api/reports/varroa").status_code == 401
