import pytest


@pytest.fixture
def apiary_and_hives(authenticated_client):
    client, _ = authenticated_client
    apiary = client.post("/api/apiaries", json={"name": "Stand Nord"}).json()
    hive_a = client.post("/api/hives", json={"name": "Volk 1", "apiary_id": apiary["id"]}).json()
    hive_b = client.post("/api/hives", json={"name": "Volk 2", "apiary_id": apiary["id"]}).json()
    return apiary, hive_a, hive_b


@pytest.mark.unit
def test_article_and_inventory_crud(authenticated_client):
    client, _ = authenticated_client
    article_response = client.post("/api/articles", json={
        "name": "Neutralglas 500g",
        "category": "honey",
        "sku": "HG-500",
        "unit": "piece",
        "weight_kg": 0.5,
    })
    assert article_response.status_code == 201
    article = article_response.json()

    item_response = client.post("/api/inventory-items", json={
        "article_id": article["id"],
        "quantity": 48,
        "unit": "piece",
        "price": 6.5,
        "batch_code": "F26",
    })
    assert item_response.status_code == 201
    item = item_response.json()
    assert item["article"]["name"] == "Neutralglas 500g"

    list_response = client.get("/api/inventory-items")
    assert list_response.status_code == 200
    assert list_response.json()[0]["id"] == item["id"]


@pytest.mark.unit
def test_feeding_and_stock_card(authenticated_client, apiary_and_hives):
    client, _ = authenticated_client
    apiary, hive, _ = apiary_and_hives
    feeding_response = client.post("/api/feedings", json={
        "apiary_id": apiary["id"],
        "hive_id": hive["id"],
        "date": "2026-06-09",
        "feed_type": "Futtersirup",
        "amount_kg_or_l": 2.5,
    })
    assert feeding_response.status_code == 201

    stock_card = client.get(f"/api/hives/{hive['id']}/stock-card")
    assert stock_card.status_code == 200
    data = stock_card.json()
    assert data["qr_url"] == f"/stock-card/{hive['id']}"
    assert any(event["type"] == "feeding" and event["title"] == "Futtersirup" for event in data["events"])


@pytest.mark.unit
def test_batch_action_creates_records_for_selected_hives(authenticated_client, apiary_and_hives):
    client, _ = authenticated_client
    apiary, hive_a, hive_b = apiary_and_hives
    response = client.post(f"/api/apiaries/{apiary['id']}/batch-actions/feeding", json={
        "hive_ids": [hive_a["id"], hive_b["id"]],
        "date": "2026-06-09",
        "feed_type": "Teig",
        "amount_kg_or_l": 1.2,
    })
    assert response.status_code == 200
    assert response.json()["created"] == 2
    feedings = client.get("/api/feedings").json()
    assert len(feedings) == 2


@pytest.mark.unit
def test_reports_return_aggregates(authenticated_client, apiary_and_hives):
    client, _ = authenticated_client
    apiary, hive, _ = apiary_and_hives
    client.post("/api/harvests", json={
        "apiary_id": apiary["id"],
        "hive_id": hive["id"],
        "harvest_date": "2026-06-09",
        "crop_type": "Sommerhonig",
        "amount_kg": 12.5,
    })
    client.post("/api/feedings", json={
        "apiary_id": apiary["id"],
        "hive_id": hive["id"],
        "date": "2026-06-09",
        "feed_type": "Sirup",
        "amount_kg_or_l": 3,
    })

    harvest = client.get("/api/reports/harvest-by-crop").json()
    feeding = client.get("/api/reports/feedings").json()

    assert harvest == [{"crop_type": "Sommerhonig", "amount_kg": 12.5}]
    assert feeding == [{"apiary_id": apiary["id"], "apiary_name": "Stand Nord", "amount_kg_or_l": 3.0}]
