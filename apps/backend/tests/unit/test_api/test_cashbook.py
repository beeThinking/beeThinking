import pytest


def _entry_payload(**overrides) -> dict:
    payload = {
        "booking_date": "2026-06-11",
        "direction": "income",
        "category": "honey",
        "title": "Honigverkauf",
        "amount_gross": 119.0,
        "tax_rate": 19.0,
        "amount_net": 100.0,
    }
    payload.update(overrides)
    return payload


@pytest.mark.unit
@pytest.mark.api
class TestCashbookEntries:
    def test_update_entry(self, authenticated_client):
        client, _ = authenticated_client
        entry = client.post("/api/cashbook/entries", json=_entry_payload()).json()

        response = client.put(
            f"/api/cashbook/entries/{entry['id']}",
            json={"title": "Honigverkauf Markt", "amount_gross": 238.0, "amount_net": 200.0},
        )

        assert response.status_code == 200
        assert response.json()["title"] == "Honigverkauf Markt"
        assert response.json()["amount_gross"] == 238.0

    def test_delete_entry(self, authenticated_client):
        client, _ = authenticated_client
        entry = client.post("/api/cashbook/entries", json=_entry_payload()).json()

        assert client.delete(f"/api/cashbook/entries/{entry['id']}").status_code == 204
        assert client.get("/api/cashbook/entries").json() == []

    def test_update_missing_entry_returns_404(self, authenticated_client):
        client, _ = authenticated_client

        response = client.put("/api/cashbook/entries/9999", json={"title": "Nope"})

        assert response.status_code == 404

    def test_summary_aggregates_income_and_expenses(self, authenticated_client):
        client, _ = authenticated_client
        client.post("/api/cashbook/entries", json=_entry_payload())
        client.post(
            "/api/cashbook/entries",
            json=_entry_payload(
                direction="expense",
                category="material",
                title="Gläser",
                amount_gross=59.5,
                amount_net=50.0,
            ),
        )

        response = client.get("/api/cashbook/summary?from_date=2026-01-01&to_date=2026-12-31")

        assert response.status_code == 200
        summary = response.json()
        assert summary["income"] == 100.0
        assert summary["expenses"] == 50.0
        assert summary["surplus"] == 50.0

    def test_entries_require_authentication(self, client):
        assert client.get("/api/cashbook/entries").status_code == 401
