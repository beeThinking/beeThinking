from datetime import date

import pytest


@pytest.fixture
def apiary(authenticated_client):
    client, _ = authenticated_client
    response = client.post("/api/apiaries", json={"stock_number": "Analytics Stand"})
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def hive(authenticated_client, apiary):
    client, _ = authenticated_client
    response = client.post("/api/hives", json={"name": "Analytics Hive", "apiary_id": apiary["id"]})
    assert response.status_code == 201
    return response.json()


@pytest.mark.unit
class TestHiveAnalytics:
    def test_kpi_counters_aggregate_harvest_and_feeding(self, authenticated_client, apiary, hive):
        client, _ = authenticated_client
        client.post("/api/harvests", json={
            "apiary_id": apiary["id"], "hive_id": hive["id"], "harvest_date": str(date.today()), "amount_kg": 5.0,
        })
        client.post("/api/harvests", json={
            "apiary_id": apiary["id"], "hive_id": hive["id"], "harvest_date": str(date.today()), "amount_kg": 3.0,
        })
        client.post("/api/feedings", json={
            "apiary_id": apiary["id"], "hive_id": hive["id"], "date": str(date.today()),
            "feed_type": "Sirup", "amount_kg_or_l": 2.0,
        })

        response = client.get(f"/api/hives/{hive['id']}/analytics")

        assert response.status_code == 200
        data = response.json()
        assert data["kpi"]["total_harvest_kg"] == 8.0
        assert data["kpi"]["total_feeding_kg_or_l"] == 2.0

    def test_grouping_by_month_produces_chart_points(self, authenticated_client, apiary, hive):
        client, _ = authenticated_client
        client.post("/api/harvests", json={
            "apiary_id": apiary["id"], "hive_id": hive["id"], "harvest_date": str(date.today()), "amount_kg": 4.0,
        })

        response = client.get(f"/api/hives/{hive['id']}/analytics", params={"grouping": "month"})

        assert response.status_code == 200
        chart = response.json()["chart"]
        assert len(chart) == 1
        assert chart[0]["harvest_kg"] == 4.0

    def test_date_range_filter_excludes_out_of_range_records(self, authenticated_client, apiary, hive):
        client, _ = authenticated_client
        client.post("/api/harvests", json={
            "apiary_id": apiary["id"], "hive_id": hive["id"], "harvest_date": "2020-01-01", "amount_kg": 10.0,
        })
        client.post("/api/harvests", json={
            "apiary_id": apiary["id"], "hive_id": hive["id"], "harvest_date": str(date.today()), "amount_kg": 2.0,
        })

        response = client.get(f"/api/hives/{hive['id']}/analytics", params={
            "from_date": str(date.today()),
        })

        assert response.status_code == 200
        assert response.json()["kpi"]["total_harvest_kg"] == 2.0

    def test_invalid_grouping_rejected(self, authenticated_client, hive):
        client, _ = authenticated_client
        response = client.get(f"/api/hives/{hive['id']}/analytics", params={"grouping": "hour"})
        assert response.status_code == 422

    def test_404_for_unknown_hive(self, authenticated_client):
        client, _ = authenticated_client
        assert client.get("/api/hives/999999/analytics").status_code == 404

    def test_requires_auth(self, client):
        assert client.get("/api/hives/1/analytics").status_code == 401
