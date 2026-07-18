from datetime import date

import pytest


@pytest.fixture
def apiary(authenticated_client):
    client, _ = authenticated_client
    response = client.post("/api/apiaries", json={"stock_number": "M2 Apiary", "name": "M2 Apiary"})
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def second_apiary(authenticated_client):
    client, _ = authenticated_client
    response = client.post("/api/apiaries", json={"stock_number": "M2 Apiary B", "name": "M2 Apiary B"})
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def hive(authenticated_client, apiary):
    client, _ = authenticated_client
    response = client.post(
        "/api/hives",
        json={
            "name": "Volk 11",
            "apiary_id": apiary["id"],
            "stock_number": "11",
            "colony_kind": "ableger",
            "established_at": "2026-05-15",
            "tags": ["sanft", "zucht"],
        },
    )
    assert response.status_code == 201
    return response.json()


@pytest.mark.unit
@pytest.mark.api
class TestHiveStockCardFields:
    def test_create_stores_stockkarte_fields(self, hive):
        assert hive["stock_number"] == "11"
        assert hive["colony_kind"] == "ableger"
        assert hive["established_at"] == "2026-05-15"
        assert hive["tags"] == ["sanft", "zucht"]

    def test_update_stockkarte_fields(self, authenticated_client, hive):
        client, _ = authenticated_client

        response = client.put(
            f"/api/hives/{hive['id']}",
            json={"colony_kind": "wirtschaftsvolk", "tags": ["sanft"]},
        )

        assert response.status_code == 200
        assert response.json()["colony_kind"] == "wirtschaftsvolk"
        assert response.json()["tags"] == ["sanft"]

    def test_invalid_colony_kind_rejected(self, authenticated_client, apiary):
        client, _ = authenticated_client

        response = client.post(
            "/api/hives",
            json={"name": "Bad", "apiary_id": apiary["id"], "colony_kind": "queen_castle"},
        )

        assert response.status_code == 422


@pytest.mark.unit
@pytest.mark.api
class TestHiveMove:
    def test_move_changes_apiary_and_documents_event(self, authenticated_client, hive, second_apiary):
        client, _ = authenticated_client

        response = client.post(
            f"/api/hives/{hive['id']}/move",
            json={"target_apiary_id": second_apiary["id"], "date": str(date.today())},
        )

        assert response.status_code == 200
        assert response.json()["apiary_id"] == second_apiary["id"]

        history = client.get(f"/api/hives/{hive['id']}/history").json()
        moved = [event for event in history if event["event_type"] == "moved"]
        assert len(moved) == 1
        assert moved[0]["metadata_json"]["to_apiary_id"] == second_apiary["id"]

    def test_move_to_unknown_apiary_returns_404(self, authenticated_client, hive):
        client, _ = authenticated_client

        response = client.post(
            f"/api/hives/{hive['id']}/move",
            json={"target_apiary_id": 9999, "date": str(date.today())},
        )

        assert response.status_code == 404

    def test_batch_move(self, authenticated_client, apiary, second_apiary):
        client, _ = authenticated_client
        hive_ids = []
        for name in ("Volk A", "Volk B"):
            created = client.post("/api/hives", json={"name": name, "apiary_id": apiary["id"]})
            hive_ids.append(created.json()["id"])

        response = client.post(
            f"/api/apiaries/{apiary['id']}/batch-actions/move",
            json={"hive_ids": hive_ids, "date": str(date.today()), "target_apiary_id": second_apiary["id"]},
        )

        assert response.status_code == 200
        assert response.json()["created"] == 2
        for hive_id in hive_ids:
            assert client.get(f"/api/hives/{hive_id}").json()["apiary_id"] == second_apiary["id"]


@pytest.mark.unit
@pytest.mark.api
class TestHiveCopy:
    def test_copy_duplicates_master_data(self, authenticated_client, hive):
        client, _ = authenticated_client

        response = client.post(
            f"/api/hives/{hive['id']}/copy",
            json={"date": str(date.today()), "name": "Volk 12", "stock_number": "12"},
        )

        assert response.status_code == 201
        copy = response.json()
        assert copy["id"] != hive["id"]
        assert copy["name"] == "Volk 12"
        assert copy["stock_number"] == "12"
        assert copy["colony_kind"] == hive["colony_kind"]
        assert copy["apiary_id"] == hive["apiary_id"]

        history = client.get(f"/api/hives/{copy['id']}/history").json()
        assert any(event["event_type"] == "copied" for event in history)

    def test_copy_default_name(self, authenticated_client, hive):
        client, _ = authenticated_client

        response = client.post(f"/api/hives/{hive['id']}/copy", json={"date": str(date.today())})

        assert response.status_code == 201
        assert "Kopie" in response.json()["name"]


@pytest.mark.unit
@pytest.mark.api
class TestRequeen:
    def test_requeen_replaces_active_queen_and_documents_event(self, authenticated_client, hive):
        client, _ = authenticated_client
        first = client.post(
            f"/api/hives/{hive['id']}/requeen",
            json={"date": str(date.today()), "year": 2025, "marking_color": "blau"},
        )
        assert first.status_code == 201

        second = client.post(
            f"/api/hives/{hive['id']}/requeen",
            json={"date": str(date.today()), "year": 2026, "marking_color": "grün", "reason": "Alte Königin schwach"},
        )
        assert second.status_code == 201

        queens = client.get(f"/api/queens?hive_id={hive['id']}").json()
        active = [queen for queen in queens if queen["is_active"]]
        assert len(active) == 1
        assert active[0]["year"] == 2026

        history = client.get(f"/api/hives/{hive['id']}/history").json()
        requeened = [event for event in history if event["event_type"] == "requeened"]
        assert len(requeened) == 2
        assert any(
            event["metadata_json"]["reason"] == "Alte Königin schwach" for event in requeened
        )


@pytest.mark.unit
@pytest.mark.api
class TestVarroaChecks:
    def test_varroa_check_crud_and_timeline(self, authenticated_client, hive):
        client, _ = authenticated_client

        response = client.post(
            "/api/varroa-checks",
            json={
                "hive_id": hive["id"],
                "date": str(date.today()),
                "method": "Gemülldiagnose",
                "mite_count": 12,
                "mites_per_day": 4.0,
            },
        )
        assert response.status_code == 201
        check = response.json()

        update = client.put(f"/api/varroa-checks/{check['id']}", json={"mite_count": 15})
        assert update.status_code == 200
        assert update.json()["mite_count"] == 15

        timeline = client.get(f"/api/hives/{hive['id']}/timeline").json()
        check_events = [event for event in timeline if event["type"] == "varroa_check"]
        assert len(check_events) == 1
        assert check_events[0]["mite_count"] == 15

        assert client.delete(f"/api/varroa-checks/{check['id']}").status_code == 204
        assert client.get(f"/api/varroa-checks/{check['id']}").status_code == 404

    def test_varroa_check_rejects_foreign_hive(self, authenticated_client, multiple_test_users, db):
        from app.models.apiary import Apiary
        from app.models.hive import Hive

        client, _ = authenticated_client
        other_apiary = Apiary(stock_number="Foreign", name="Foreign", owner_id=multiple_test_users[0].id)
        db.add(other_apiary)
        db.commit()
        other_hive = Hive(name="Foreign Hive", owner_id=multiple_test_users[0].id, apiary_id=other_apiary.id)
        db.add(other_hive)
        db.commit()

        response = client.post(
            "/api/varroa-checks",
            json={"hive_id": other_hive.id, "date": str(date.today()), "mite_count": 1},
        )

        assert response.status_code == 404

    def test_varroa_checks_require_authentication(self, client):
        assert client.get("/api/varroa-checks").status_code == 401
