from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from app.models.apiary_member import ApiaryMember, ApiaryMemberRole


def authenticate_as(client, user, password):
    response = client.post("/api/auth/login", data={"username": user.username, "password": password})
    assert response.status_code == 200
    client.headers["Authorization"] = f"Bearer {response.json()['access_token']}"


@pytest.fixture
def apiary(authenticated_client):
    client, _ = authenticated_client
    response = client.post("/api/apiaries", json={"stock_number": "Test Apiary", "name": "Test Apiary"})
    assert response.status_code == 201
    return response.json()


@pytest.mark.unit
class TestListHives:
    def test_list_hives_empty(self, authenticated_client):
        client, _ = authenticated_client
        response = client.get("/api/hives")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_hives_returns_only_own_hives(self, authenticated_client, apiary):
        client, _ = authenticated_client
        client.post("/api/hives", json={"name": "My Hive", "type": "langstroth", "status": "active", "apiary_id": apiary["id"]})
        response = client.get("/api/hives")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_list_hives_requires_auth(self, client: TestClient):
        response = client.get("/api/hives")
        assert response.status_code == 401

    def test_member_can_list_shared_hives(self, authenticated_client, apiary, multiple_test_users, db):
        client, _ = authenticated_client
        hive = client.post("/api/hives", json={"name": "Shared Hive", "apiary_id": apiary["id"]}).json()
        member = multiple_test_users[0]
        db.add(ApiaryMember(apiary_id=apiary["id"], user_id=member.id, role=ApiaryMemberRole.member, accepted_at=datetime.now(timezone.utc)))
        db.commit()
        authenticate_as(client, member, "password0")

        response = client.get("/api/hives")

        assert response.status_code == 200
        assert [item["id"] for item in response.json()] == [hive["id"]]


@pytest.mark.unit
class TestCreateHive:
    def test_create_hive_minimal(self, authenticated_client, apiary):
        client, _ = authenticated_client
        response = client.post("/api/hives", json={"name": "Alpha", "apiary_id": apiary["id"]})
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Alpha"
        assert data["status"] == "active"
        assert data["type"] == "langstroth"
        assert "id" in data
        assert "owner_id" in data

    def test_create_hive_full(self, authenticated_client, apiary):
        client, _ = authenticated_client
        payload = {
            "name": "Beta Hive",
            "type": "dadant",
            "status": "active",
            "notes": "Strong colony",
            "apiary_id": apiary["id"]
        }
        response = client.post("/api/hives", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Beta Hive"
        assert data["type"] == "dadant"
        assert data["notes"] == "Strong colony"

    def test_create_hive_empty_name_fails(self, authenticated_client, apiary):
        client, _ = authenticated_client
        response = client.post("/api/hives", json={"name": "", "apiary_id": apiary["id"]})
        assert response.status_code == 422

    def test_create_hive_requires_auth(self, client: TestClient):
        response = client.post("/api/hives", json={"name": "No Auth", "apiary_id": 1})
        assert response.status_code == 401

    def test_member_can_create_hive_for_shared_apiary_owner(self, authenticated_client, apiary, multiple_test_users, db, test_user):
        client, _ = authenticated_client
        member = multiple_test_users[0]
        db.add(ApiaryMember(apiary_id=apiary["id"], user_id=member.id, role=ApiaryMemberRole.member, accepted_at=datetime.now(timezone.utc)))
        db.commit()
        authenticate_as(client, member, "password0")

        response = client.post("/api/hives", json={"name": "Member Hive", "apiary_id": apiary["id"]})

        assert response.status_code == 201
        assert response.json()["owner_id"] == test_user.id

    def test_viewer_cannot_create_hive(self, authenticated_client, apiary, multiple_test_users, db):
        client, _ = authenticated_client
        viewer = multiple_test_users[0]
        db.add(ApiaryMember(apiary_id=apiary["id"], user_id=viewer.id, role=ApiaryMemberRole.viewer, accepted_at=datetime.now(timezone.utc)))
        db.commit()
        authenticate_as(client, viewer, "password0")

        assert client.post("/api/hives", json={"name": "Forbidden", "apiary_id": apiary["id"]}).status_code == 404

    def test_viewer_cannot_create_activity_for_shared_hive(self, authenticated_client, apiary, multiple_test_users, db):
        client, _ = authenticated_client
        hive = client.post("/api/hives", json={"name": "Shared Hive", "apiary_id": apiary["id"]}).json()
        viewer = multiple_test_users[0]
        db.add(ApiaryMember(apiary_id=apiary["id"], user_id=viewer.id, role=ApiaryMemberRole.viewer, accepted_at=datetime.now(timezone.utc)))
        db.commit()
        authenticate_as(client, viewer, "password0")

        assert client.post("/api/tasks", json={"title": "Forbidden", "hive_id": hive["id"]}).status_code == 404


@pytest.mark.unit
class TestGetHive:
    def test_get_hive(self, authenticated_client, apiary):
        client, _ = authenticated_client
        created = client.post("/api/hives", json={"name": "Gamma", "apiary_id": apiary["id"]}).json()
        response = client.get(f"/api/hives/{created['id']}")
        assert response.status_code == 200
        assert response.json()["name"] == "Gamma"

    def test_get_hive_not_found(self, authenticated_client):
        client, _ = authenticated_client
        response = client.get("/api/hives/99999")
        assert response.status_code == 404

    def test_get_hive_of_other_user_returns_404(self, authenticated_client, multiple_test_users, db):
        client, _ = authenticated_client
        from app.models.hive import Hive
        from app.models.apiary import Apiary
        other_apiary = Apiary(stock_number="Other Apiary", name="Other Apiary", owner_id=multiple_test_users[0].id)
        db.add(other_apiary)
        db.commit()
        db.refresh(other_apiary)
        other_hive = Hive(name="Other Hive", owner_id=multiple_test_users[0].id, apiary_id=other_apiary.id)
        db.add(other_hive)
        db.commit()
        db.refresh(other_hive)
        response = client.get(f"/api/hives/{other_hive.id}")
        assert response.status_code == 404


@pytest.mark.unit
class TestUpdateHive:
    def test_update_hive(self, authenticated_client, apiary):
        client, _ = authenticated_client
        created = client.post("/api/hives", json={"name": "Delta", "apiary_id": apiary["id"]}).json()
        response = client.put(f"/api/hives/{created['id']}", json={"name": "Delta Updated", "status": "inactive"})
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Delta Updated"
        assert data["status"] == "inactive"

    def test_update_hive_not_found(self, authenticated_client):
        client, _ = authenticated_client
        response = client.put("/api/hives/99999", json={"name": "X"})
        assert response.status_code == 404

    def test_update_other_user_hive_returns_404(self, authenticated_client, multiple_test_users, db):
        client, _ = authenticated_client
        from app.models.hive import Hive
        from app.models.apiary import Apiary
        other_apiary = Apiary(stock_number="Other Apiary", name="Other Apiary", owner_id=multiple_test_users[0].id)
        db.add(other_apiary)
        db.commit()
        db.refresh(other_apiary)
        other_hive = Hive(name="Other Hive", owner_id=multiple_test_users[0].id, apiary_id=other_apiary.id)
        db.add(other_hive)
        db.commit()
        db.refresh(other_hive)

        response = client.put(f"/api/hives/{other_hive.id}", json={"name": "Changed"})
        db.refresh(other_hive)

        assert response.status_code == 404
        assert other_hive.name == "Other Hive"

    def test_partial_update_preserves_fields(self, authenticated_client, apiary):
        client, _ = authenticated_client
        created = client.post("/api/hives", json={"name": "Epsilon", "notes": "Forest notes", "apiary_id": apiary["id"]}).json()
        response = client.put(f"/api/hives/{created['id']}", json={"status": "inactive"})
        assert response.status_code == 200
        data = response.json()
        assert data["notes"] == "Forest notes"
        assert data["status"] == "inactive"


@pytest.mark.unit
class TestDeleteHive:
    def test_delete_hive(self, authenticated_client, apiary):
        client, _ = authenticated_client
        created = client.post("/api/hives", json={"name": "Zeta", "apiary_id": apiary["id"]}).json()
        response = client.delete(f"/api/hives/{created['id']}")
        assert response.status_code == 204
        assert client.get(f"/api/hives/{created['id']}").status_code == 404

    def test_delete_hive_not_found(self, authenticated_client):
        client, _ = authenticated_client
        response = client.delete("/api/hives/99999")
        assert response.status_code == 404

    def test_delete_other_user_hive_returns_404(self, authenticated_client, multiple_test_users, db):
        client, _ = authenticated_client
        from app.models.hive import Hive
        from app.models.apiary import Apiary
        other_apiary = Apiary(stock_number="Other Apiary", name="Other Apiary", owner_id=multiple_test_users[0].id)
        db.add(other_apiary)
        db.commit()
        db.refresh(other_apiary)
        other_hive = Hive(name="Other Hive", owner_id=multiple_test_users[0].id, apiary_id=other_apiary.id)
        db.add(other_hive)
        db.commit()
        db.refresh(other_hive)

        response = client.delete(f"/api/hives/{other_hive.id}")

        assert response.status_code == 404
        assert db.get(Hive, other_hive.id) is not None

    def test_viewer_cannot_delete_shared_hive(self, authenticated_client, apiary, multiple_test_users, db):
        client, _ = authenticated_client
        hive = client.post("/api/hives", json={"name": "Shared Hive", "apiary_id": apiary["id"]}).json()
        viewer = multiple_test_users[0]
        db.add(ApiaryMember(apiary_id=apiary["id"], user_id=viewer.id, role=ApiaryMemberRole.viewer, accepted_at=datetime.now(timezone.utc)))
        db.commit()
        authenticate_as(client, viewer, "password0")

        assert client.delete(f"/api/hives/{hive['id']}").status_code == 404

    def test_hard_delete_rejects_hive_with_history(self, authenticated_client, apiary):
        client, _ = authenticated_client
        created = client.post("/api/hives", json={"name": "History Hive", "apiary_id": apiary["id"]}).json()
        client.post(f"/api/hives/{created['id']}/inspections", json={"date": "2026-06-05", "queen_seen": True})

        response = client.delete(f"/api/hives/{created['id']}")

        assert response.status_code == 409


@pytest.mark.unit
class TestHiveLifecycle:
    def test_archive_hive_moves_it_out_of_active_list(self, authenticated_client, apiary):
        client, _ = authenticated_client
        created = client.post("/api/hives", json={"name": "Archive Hive", "apiary_id": apiary["id"]}).json()

        response = client.post(
            f"/api/hives/{created['id']}/archive",
            json={"reason": "season done", "date": "2026-06-05", "note": "archive"},
        )

        assert response.status_code == 200
        assert response.json()["is_active"] is False
        assert response.json()["status"] == "archived"
        assert all(item["id"] != created["id"] for item in client.get("/api/hives").json())
        assert any(item["id"] == created["id"] for item in client.get("/api/hives?status=archived").json())
        history = client.get(f"/api/hives/{created['id']}/history").json()
        assert any(event["event_type"] == "archived" for event in history)

    def test_merge_hive_links_source_and_target(self, authenticated_client, apiary):
        client, _ = authenticated_client
        source = client.post("/api/hives", json={"name": "Source", "apiary_id": apiary["id"]}).json()
        target = client.post("/api/hives", json={"name": "Target", "apiary_id": apiary["id"]}).json()

        response = client.post(
            f"/api/hives/{source['id']}/merge",
            json={"reason": "merged", "date": "2026-06-05", "target_hive_id": target["id"]},
        )

        assert response.status_code == 200
        assert response.json()["status"] == "merged"
        assert response.json()["merged_into_hive_id"] == target["id"]
        target_history = client.get(f"/api/hives/{target['id']}/history").json()
        assert any(event["event_type"] == "merge_received" for event in target_history)

    def test_yearly_report_can_include_archived_losses(self, authenticated_client, apiary):
        client, _ = authenticated_client
        created = client.post("/api/hives", json={"name": "Loss Hive", "apiary_id": apiary["id"]}).json()
        client.post(f"/api/hives/{created['id']}/dissolve", json={"reason": "dead", "date": "2026-06-05"})

        report = client.get("/api/reports/yearly?year=2026&include_archived=true")

        assert report.status_code == 200
        assert report.json()["losses"] == 1
