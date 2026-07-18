import pytest


def _create_article(client, **overrides) -> dict:
    payload = {"name": "Honigglas 500g", "category": "material", "unit": "piece"}
    payload.update(overrides)
    response = client.post("/api/articles", json=payload)
    assert response.status_code == 201
    return response.json()


@pytest.mark.unit
@pytest.mark.api
class TestArticlesApi:
    def test_update_article(self, authenticated_client):
        client, _ = authenticated_client
        article = _create_article(client)

        response = client.put(f"/api/articles/{article['id']}", json={"name": "Honigglas 250g"})

        assert response.status_code == 200
        assert response.json()["name"] == "Honigglas 250g"

    def test_delete_article(self, authenticated_client):
        client, _ = authenticated_client
        article = _create_article(client)

        assert client.delete(f"/api/articles/{article['id']}").status_code == 204
        assert client.get(f"/api/articles/{article['id']}").status_code == 404

    def test_missing_article_returns_404(self, authenticated_client):
        client, _ = authenticated_client

        assert client.get("/api/articles/9999").status_code == 404


@pytest.mark.unit
@pytest.mark.api
class TestInventoryItemsApi:
    def test_update_inventory_item(self, authenticated_client):
        client, _ = authenticated_client
        article = _create_article(client)
        item = client.post(
            "/api/inventory-items",
            json={"article_id": article["id"], "quantity": 10, "unit": "piece"},
        ).json()

        response = client.put(f"/api/inventory-items/{item['id']}", json={"quantity": 4})

        assert response.status_code == 200
        assert response.json()["quantity"] == 4

    def test_delete_inventory_item(self, authenticated_client):
        client, _ = authenticated_client
        article = _create_article(client)
        item = client.post(
            "/api/inventory-items",
            json={"article_id": article["id"], "quantity": 10},
        ).json()

        assert client.delete(f"/api/inventory-items/{item['id']}").status_code == 204
        assert client.get(f"/api/inventory-items/{item['id']}").status_code == 404

    def test_inventory_requires_authentication(self, client):
        assert client.get("/api/inventory-items").status_code == 401
        assert client.get("/api/articles").status_code == 401
