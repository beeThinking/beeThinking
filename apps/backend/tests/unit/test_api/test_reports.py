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


@pytest.mark.unit
@pytest.mark.api
class TestReportsPdfExports:
    def _create_article(self, client, **overrides) -> dict:
        payload = {"name": "Honigglas 500g", "category": "material", "unit": "piece"}
        payload.update(overrides)
        response = client.post("/api/articles", json=payload)
        assert response.status_code == 201
        return response.json()

    def _create_inventory_item(self, client, article_id, **overrides) -> dict:
        payload = {"article_id": article_id, "quantity": 10, "unit": "piece"}
        payload.update(overrides)
        response = client.post("/api/inventory-items", json=payload)
        assert response.status_code == 201
        return response.json()

    def test_inventory_material_pdf(self, authenticated_client):
        client, _ = authenticated_client
        article = self._create_article(client, name="Eimer 25kg", category="material")
        self._create_inventory_item(client, article["id"])

        response = client.get("/api/reports/inventory-material.pdf")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert 'filename="bestand-materiallager.pdf"' in response.headers["content-disposition"]
        assert response.content.startswith(b"%PDF")

    def test_inventory_finished_goods_pdf(self, authenticated_client):
        client, _ = authenticated_client
        article = self._create_article(client, name="Bluetenhonig 500g", category="honey")
        self._create_inventory_item(client, article["id"])

        response = client.get("/api/reports/inventory-finished-goods.pdf")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert 'filename="bestand-fertigprodukte.pdf"' in response.headers["content-disposition"]

    def test_feedings_pdf(self, authenticated_client, apiary):
        client, _ = authenticated_client
        client.post(
            "/api/feedings",
            json={"apiary_id": apiary["id"], "date": "2026-03-01", "amount_kg_or_l": 2.5, "feed_type": "Sirup"},
        )

        response = client.get("/api/reports/feedings.pdf")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert 'filename="fuetterungs-report.pdf"' in response.headers["content-disposition"]
