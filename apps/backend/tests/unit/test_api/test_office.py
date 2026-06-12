import pytest


@pytest.mark.unit
@pytest.mark.api
def test_office_partner_document_and_exports(authenticated_client):
    client, _ = authenticated_client

    partner_response = client.post(
        "/api/office/partners",
        json={"partner_type": "customer", "name": "Hofladen Mitte", "email": "hof@example.com"},
    )
    assert partner_response.status_code == 201
    partner = partner_response.json()

    entry_response = client.post(
        "/api/cashbook/entries",
        json={
            "booking_date": "2026-06-11",
            "direction": "income",
            "category": "honey",
            "title": "Honigverkauf",
            "invoice_number": "R-2026-001",
            "partner_id": partner["id"],
            "amount_gross": 119.0,
            "tax_rate": 19.0,
            "amount_net": 100.0,
        },
    )
    assert entry_response.status_code == 201
    assert entry_response.json()["partner_id"] == partner["id"]

    document_response = client.post(
        "/api/office/documents",
        json={
            "partner_id": partner["id"],
            "document_type": "invoice",
            "status": "sent",
            "document_number": "R-2026-001",
            "title": "Honigverkauf",
            "document_date": "2026-06-11",
            "amount_gross": 119.0,
            "tax_rate": 19.0,
            "amount_net": 100.0,
            "line_items": [{"description": "Honig", "quantity": 1, "unit_price": 119.0, "tax_rate": 19.0}],
        },
    )
    assert document_response.status_code == 201
    assert document_response.json()["line_items"][0]["description"] == "Honig"

    dashboard_response = client.get("/api/office/dashboard?year=2026&month=6")
    assert dashboard_response.status_code == 200
    dashboard = dashboard_response.json()
    assert dashboard["income"] == 119.0
    assert dashboard["balance"] == 119.0
    assert dashboard["categories"][0]["category"] == "honey"

    csv_response = client.get("/api/office/cashbook/export.csv?year=2026")
    assert csv_response.status_code == 200
    assert csv_response.headers["content-type"].startswith("text/csv")
    assert "Honigverkauf" in csv_response.text

    pdf_response = client.get("/api/office/cashbook/report.pdf?year=2026")
    assert pdf_response.status_code == 200
    assert pdf_response.headers["content-type"] == "application/pdf"
    assert pdf_response.content.startswith(b"%PDF")
