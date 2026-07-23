from datetime import date

import pytest


@pytest.fixture
def apiary(authenticated_client):
    client, _ = authenticated_client
    response = client.post("/api/apiaries", json={"stock_number": "Treatment Apiary", "name": "Treatment Apiary"})
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def hive(authenticated_client, apiary):
    client, _ = authenticated_client
    response = client.post(
        "/api/hives", json={"name": "Treatment Hive", "apiary_id": apiary["id"], "stock_number": "TH-1"}
    )
    assert response.status_code == 201
    return response.json()


@pytest.mark.unit
@pytest.mark.api
class TestTreatmentJournalExport:
    def test_journal_export_json_includes_waiting_period_and_treater(self, authenticated_client, hive):
        client, _ = authenticated_client
        response = client.post(
            "/api/treatments",
            json={
                "hive_id": hive["id"],
                "started_at": str(date.today()),
                "product": "Ameisensaeure",
                "method": "Verdunster",
                "dosage": "60%",
                "waiting_period_days": 21,
            },
        )
        assert response.status_code == 201

        export_response = client.get("/api/treatments/journal/export")

        assert export_response.status_code == 200
        data = export_response.json()
        assert data["format"] == "journal-export-fields"
        assert len(data["items"]) == 1
        entry = data["items"][0]
        assert entry["waiting_period_days"] == 21
        assert entry["treater"] == "testuser"
        assert entry["product"] == "Ameisensaeure"
        assert "Treatment Hive" in entry["hive_label"]

    def test_journal_export_pdf_returns_pdf_with_content_disposition(self, authenticated_client, hive):
        client, _ = authenticated_client
        client.post(
            "/api/treatments",
            json={
                "hive_id": hive["id"],
                "started_at": str(date.today()),
                "product": "Oxalsaeure",
                "waiting_period_days": 0,
            },
        )

        year = date.today().year
        response = client.get(f"/api/treatments/journal/export.pdf?year={year}")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert response.headers["content-disposition"] == f'attachment; filename="bestandsbuch-{year}.pdf"'
        assert response.content.startswith(b"%PDF")

    def test_journal_export_pdf_requires_authentication(self, client):
        assert client.get("/api/treatments/journal/export.pdf").status_code == 401
