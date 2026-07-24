import pytest


def _create_article(client, category="honey", **overrides) -> dict:
    payload = {"name": "Honigglas 500g", "category": category, "unit": "piece"}
    payload.update(overrides)
    response = client.post("/api/articles", json=payload)
    assert response.status_code == 201
    return response.json()


def _create_inventory_item(client, article_id, quantity=10, **overrides) -> dict:
    payload = {"article_id": article_id, "quantity": quantity, "unit": "piece"}
    payload.update(overrides)
    response = client.post("/api/inventory-items", json=payload)
    assert response.status_code == 201
    return response.json()


def _create_customer(client, **overrides) -> dict:
    payload = {"partner_type": "customer", "name": "Hofladen Mitte"}
    payload.update(overrides)
    response = client.post("/api/office/partners", json=payload)
    assert response.status_code == 201
    return response.json()


@pytest.mark.unit
@pytest.mark.api
class TestCreateSale:
    def test_create_sale_decrements_stock_and_creates_cashbook_entry(self, authenticated_client):
        client, _ = authenticated_client
        article = _create_article(client)
        item = _create_inventory_item(client, article["id"], quantity=10)

        response = client.post(
            "/api/sales",
            json={
                "sale_date": "2026-07-01",
                "items": [{"inventory_item_id": item["id"], "quantity": 3, "unit_price_gross": 8.0}],
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["amount_gross"] == pytest.approx(24.0)
        assert data["vat_rate"] == pytest.approx(0.07)
        assert data["amount_net"] == pytest.approx(round(24.0 / 1.07, 2))
        assert data["cashbook_entry_id"] is not None

        item_after = client.get(f"/api/inventory-items/{item['id']}").json()
        assert item_after["quantity"] == pytest.approx(7)

        entries = client.get("/api/cashbook/entries").json()
        assert len(entries) == 1
        assert entries[0]["category"] == "honey_sales"
        assert entries[0]["direction"] == "income"
        assert entries[0]["amount_gross"] == pytest.approx(24.0)
        assert entries[0]["tax_rate"] == pytest.approx(7.0)

    def test_create_sale_defaults_standard_vat_for_non_honey_article(self, authenticated_client):
        client, _ = authenticated_client
        article = _create_article(client, category="material")
        item = _create_inventory_item(client, article["id"], quantity=10)

        response = client.post(
            "/api/sales",
            json={"items": [{"inventory_item_id": item["id"], "quantity": 1, "unit_price_gross": 10.0}]},
        )

        assert response.status_code == 201
        assert response.json()["vat_rate"] == pytest.approx(0.19)

    def test_create_sale_allows_vat_rate_override(self, authenticated_client):
        client, _ = authenticated_client
        article = _create_article(client)
        item = _create_inventory_item(client, article["id"], quantity=10)

        response = client.post(
            "/api/sales",
            json={
                "vat_rate": 0.19,
                "items": [{"inventory_item_id": item["id"], "quantity": 1, "unit_price_gross": 10.0}],
            },
        )

        assert response.status_code == 201
        assert response.json()["vat_rate"] == pytest.approx(0.19)

    def test_create_sale_rejects_insufficient_stock(self, authenticated_client):
        client, _ = authenticated_client
        article = _create_article(client)
        item = _create_inventory_item(client, article["id"], quantity=2)

        response = client.post(
            "/api/sales",
            json={"items": [{"inventory_item_id": item["id"], "quantity": 5, "unit_price_gross": 8.0}]},
        )

        assert response.status_code == 409
        item_after = client.get(f"/api/inventory-items/{item['id']}").json()
        assert item_after["quantity"] == pytest.approx(2)
        assert client.get("/api/cashbook/entries").json() == []

    def test_create_sale_rejects_inventory_item_not_owned(self, authenticated_client, multiple_test_users, db):
        client, _ = authenticated_client
        from app.models.inventory import Article, InventoryItem

        other_article = Article(owner_id=multiple_test_users[0].id, category="honey", name="Foreign", unit="piece")
        db.add(other_article)
        db.commit()
        db.refresh(other_article)
        other_item = InventoryItem(owner_id=multiple_test_users[0].id, article_id=other_article.id, quantity=10, unit="piece")
        db.add(other_item)
        db.commit()
        db.refresh(other_item)

        response = client.post(
            "/api/sales",
            json={"items": [{"inventory_item_id": other_item.id, "quantity": 1, "unit_price_gross": 5.0}]},
        )

        assert response.status_code == 400

    def test_create_sale_with_partner_requires_customer_type(self, authenticated_client):
        client, _ = authenticated_client
        article = _create_article(client)
        item = _create_inventory_item(client, article["id"], quantity=10)
        supplier = _create_customer(client, partner_type="supplier", name="Lieferant")

        response = client.post(
            "/api/sales",
            json={
                "partner_id": supplier["id"],
                "items": [{"inventory_item_id": item["id"], "quantity": 1, "unit_price_gross": 8.0}],
            },
        )

        assert response.status_code == 400

    def test_create_sale_with_valid_customer_partner(self, authenticated_client):
        client, _ = authenticated_client
        article = _create_article(client)
        item = _create_inventory_item(client, article["id"], quantity=10)
        customer = _create_customer(client)

        response = client.post(
            "/api/sales",
            json={
                "partner_id": customer["id"],
                "items": [{"inventory_item_id": item["id"], "quantity": 1, "unit_price_gross": 8.0}],
            },
        )

        assert response.status_code == 201
        assert response.json()["partner_id"] == customer["id"]

    def test_sales_require_authentication(self, client):
        assert client.get("/api/sales").status_code == 401


@pytest.mark.unit
@pytest.mark.api
class TestDeleteSale:
    def test_delete_sale_restores_stock_and_removes_cashbook_entry(self, authenticated_client):
        client, _ = authenticated_client
        article = _create_article(client)
        item = _create_inventory_item(client, article["id"], quantity=10)
        sale = client.post(
            "/api/sales",
            json={"items": [{"inventory_item_id": item["id"], "quantity": 4, "unit_price_gross": 8.0}]},
        ).json()

        response = client.delete(f"/api/sales/{sale['id']}")

        assert response.status_code == 204
        item_after = client.get(f"/api/inventory-items/{item['id']}").json()
        assert item_after["quantity"] == pytest.approx(10)
        assert client.get("/api/cashbook/entries").json() == []
        assert client.get(f"/api/sales/{sale['id']}").status_code == 404

    def test_delete_missing_sale_returns_404(self, authenticated_client):
        client, _ = authenticated_client
        assert client.delete("/api/sales/9999").status_code == 404


@pytest.mark.unit
@pytest.mark.api
class TestSalesReport:
    def test_report_groups_by_article_within_date_range(self, authenticated_client):
        client, _ = authenticated_client
        article = _create_article(client)
        item = _create_inventory_item(client, article["id"], quantity=20)

        client.post(
            "/api/sales",
            json={
                "sale_date": "2026-07-01",
                "items": [{"inventory_item_id": item["id"], "quantity": 3, "unit_price_gross": 8.0}],
            },
        )
        client.post(
            "/api/sales",
            json={
                "sale_date": "2026-07-15",
                "items": [{"inventory_item_id": item["id"], "quantity": 2, "unit_price_gross": 8.0}],
            },
        )
        client.post(
            "/api/sales",
            json={
                "sale_date": "2026-08-01",
                "items": [{"inventory_item_id": item["id"], "quantity": 10, "unit_price_gross": 8.0}],
            },
        )

        response = client.get("/api/sales/report?from_date=2026-07-01&to_date=2026-07-31")

        assert response.status_code == 200
        rows = response.json()
        assert len(rows) == 1
        assert rows[0]["article_id"] == article["id"]
        assert rows[0]["quantity"] == pytest.approx(5)
        assert rows[0]["amount_gross"] == pytest.approx(40.0)


@pytest.mark.unit
@pytest.mark.api
class TestSaleCashbookIntegration:
    def test_cashbook_summary_reflects_sale_income_exactly_once(self, authenticated_client):
        client, _ = authenticated_client
        article = _create_article(client)
        item = _create_inventory_item(client, article["id"], quantity=10)

        client.post(
            "/api/sales",
            json={
                "sale_date": "2026-07-01",
                "items": [{"inventory_item_id": item["id"], "quantity": 3, "unit_price_gross": 8.0}],
            },
        )

        response = client.get("/api/cashbook/summary?from_date=2026-01-01&to_date=2026-12-31")

        assert response.status_code == 200
        summary = response.json()
        expected_net = round(24.0 / 1.07, 2)
        assert summary["income"] == pytest.approx(expected_net)
        assert summary["expenses"] == 0.0
