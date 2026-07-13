from datetime import datetime, timezone

import pytest
from app.models.apiary import Apiary
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
class TestListApiaries:
    def test_list_empty(self, authenticated_client):
        client, _ = authenticated_client
        response = client.get("/api/apiaries")
        assert response.status_code == 200
        assert response.json() == []

    def test_requires_auth(self, client):
        assert client.get("/api/apiaries").status_code == 401

    def test_list_returns_only_own_apiaries(self, authenticated_client, multiple_test_users, db):
        client, _ = authenticated_client
        db.add(Apiary(stock_number="Other Apiary", name="Other Apiary", owner_id=multiple_test_users[0].id))
        db.commit()

        response = client.get("/api/apiaries")

        assert response.status_code == 200
        assert response.json() == []


@pytest.mark.unit
class TestCreateApiary:
    def test_create_minimal(self, authenticated_client):
        client, _ = authenticated_client
        response = client.post("/api/apiaries", json={"stock_number": "Garden", "name": "Garden"})
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Garden"
        assert data["hive_count"] == 0

    def test_create_full(self, authenticated_client):
        client, _ = authenticated_client
        payload = {
            "stock_number": "Forest Stand",
            "name": "Forest Stand",
            "address": "Waldweg 1, 12345 Musterstadt",
            "latitude": 48.1374,
            "longitude": 11.5755,
            "notes": "Near the oak trees"
        }
        response = client.post("/api/apiaries", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["address"] == "Waldweg 1, 12345 Musterstadt"
        assert data["latitude"] == 48.1374

    def test_create_empty_stock_number_fails(self, authenticated_client):
        client, _ = authenticated_client
        assert client.post("/api/apiaries", json={"stock_number": ""}).status_code == 422

    def test_create_invalid_gps_fails(self, authenticated_client):
        client, _ = authenticated_client
        assert client.post("/api/apiaries", json={"stock_number": "X", "latitude": 999}).status_code == 422


@pytest.mark.unit
class TestGetApiary:
    def test_get(self, authenticated_client, apiary):
        client, _ = authenticated_client
        response = client.get(f"/api/apiaries/{apiary['id']}")
        assert response.status_code == 200
        assert response.json()["name"] == apiary["name"]

    def test_get_not_found(self, authenticated_client):
        client, _ = authenticated_client
        assert client.get("/api/apiaries/99999").status_code == 404

    def test_get_other_user_apiary_returns_404(self, authenticated_client, multiple_test_users, db):
        client, _ = authenticated_client
        other_apiary = Apiary(stock_number="Other Apiary", name="Other Apiary", owner_id=multiple_test_users[0].id)
        db.add(other_apiary)
        db.commit()
        db.refresh(other_apiary)

        response = client.get(f"/api/apiaries/{other_apiary.id}")

        assert response.status_code == 404


@pytest.mark.unit
class TestUpdateApiary:
    def test_update(self, authenticated_client, apiary):
        client, _ = authenticated_client
        response = client.put(f"/api/apiaries/{apiary['id']}", json={"name": "Updated", "notes": "Changed"})
        assert response.status_code == 200
        assert response.json()["name"] == "Updated"

    def test_update_not_found(self, authenticated_client):
        client, _ = authenticated_client
        assert client.put("/api/apiaries/99999", json={"stock_number": "X"}).status_code == 404

    def test_update_other_user_apiary_returns_404(self, authenticated_client, multiple_test_users, db):
        client, _ = authenticated_client
        other_apiary = Apiary(stock_number="Other Apiary", name="Other Apiary", owner_id=multiple_test_users[0].id)
        db.add(other_apiary)
        db.commit()
        db.refresh(other_apiary)

        response = client.put(f"/api/apiaries/{other_apiary.id}", json={"name": "Changed"})
        db.refresh(other_apiary)

        assert response.status_code == 404
        assert other_apiary.name == "Other Apiary"

    def test_viewer_cannot_update_shared_apiary(self, authenticated_client, apiary, multiple_test_users, db):
        client, _ = authenticated_client
        viewer = multiple_test_users[0]
        db.add(ApiaryMember(apiary_id=apiary["id"], user_id=viewer.id, role=ApiaryMemberRole.viewer, accepted_at=datetime.now(timezone.utc)))
        db.commit()
        authenticate_as(client, viewer, "password0")

        assert client.get(f"/api/apiaries/{apiary['id']}").status_code == 200
        response = client.put(f"/api/apiaries/{apiary['id']}", json={"name": "Forbidden"})

        assert response.status_code == 404
        assert db.get(Apiary, apiary["id"]).name == apiary["name"]


@pytest.mark.unit
class TestDeleteApiary:
    def test_delete(self, authenticated_client, apiary):
        client, _ = authenticated_client
        assert client.delete(f"/api/apiaries/{apiary['id']}").status_code == 204
        assert client.get(f"/api/apiaries/{apiary['id']}").status_code == 404

    def test_delete_not_found(self, authenticated_client):
        client, _ = authenticated_client
        assert client.delete("/api/apiaries/99999").status_code == 404

    def test_delete_other_user_apiary_returns_404(self, authenticated_client, multiple_test_users, db):
        client, _ = authenticated_client
        other_apiary = Apiary(stock_number="Other Apiary", name="Other Apiary", owner_id=multiple_test_users[0].id)
        db.add(other_apiary)
        db.commit()
        db.refresh(other_apiary)

        response = client.delete(f"/api/apiaries/{other_apiary.id}")

        assert response.status_code == 404
        assert db.get(Apiary, other_apiary.id) is not None

    def test_viewer_cannot_delete_shared_apiary(self, authenticated_client, apiary, multiple_test_users, db):
        client, _ = authenticated_client
        viewer = multiple_test_users[0]
        db.add(ApiaryMember(apiary_id=apiary["id"], user_id=viewer.id, role=ApiaryMemberRole.viewer, accepted_at=datetime.now(timezone.utc)))
        db.commit()
        authenticate_as(client, viewer, "password0")

        response = client.delete(f"/api/apiaries/{apiary['id']}")

        assert response.status_code == 404
        assert db.get(Apiary, apiary["id"]) is not None


@pytest.mark.unit
class TestApiaryHiveCount:
    def test_hive_count_reflects_hives(self, authenticated_client, apiary):
        client, _ = authenticated_client
        client.post("/api/hives", json={"name": "H1", "apiary_id": apiary["id"]})
        client.post("/api/hives", json={"name": "H2", "apiary_id": apiary["id"]})
        response = client.get(f"/api/apiaries/{apiary['id']}")
        assert response.json()["hive_count"] == 2


@pytest.mark.unit
class TestApiaryInvitations:
    def test_invitation_requires_acceptance_before_access(self, authenticated_client, apiary, multiple_test_users):
        client, _ = authenticated_client
        invited_user = multiple_test_users[0]

        invite_response = client.post(
            f"/api/apiaries/{apiary['id']}/members",
            json={"username_or_email": invited_user.email, "role": "member"},
        )
        assert invite_response.status_code == 201
        invitation = invite_response.json()
        assert invitation["accepted_at"] is None
        assert invitation["user"]["username"] == invited_user.username

        authenticate_as(client, invited_user, "password0")
        assert client.get(f"/api/apiaries/{apiary['id']}").status_code == 404
        invitations = client.get("/api/apiaries/invitations")
        assert invitations.status_code == 200
        assert invitations.json()[0]["apiary"]["stock_number"] == apiary["stock_number"]

        accepted = client.post(f"/api/apiaries/invitations/{invitation['id']}/accept")
        assert accepted.status_code == 200
        assert accepted.json()["accepted_at"] is not None
        assert client.get(f"/api/apiaries/{apiary['id']}").status_code == 200

    def test_invitation_can_be_declined(self, authenticated_client, apiary, multiple_test_users):
        client, _ = authenticated_client
        invited_user = multiple_test_users[0]
        invitation = client.post(
            f"/api/apiaries/{apiary['id']}/members",
            json={"username_or_email": invited_user.username, "role": "viewer"},
        ).json()
        authenticate_as(client, invited_user, "password0")

        assert client.delete(f"/api/apiaries/invitations/{invitation['id']}").status_code == 204
        assert client.get("/api/apiaries/invitations").json() == []
        assert client.get(f"/api/apiaries/{apiary['id']}").status_code == 404

    def test_owner_role_and_owner_membership_are_protected(self, authenticated_client, apiary, test_user):
        client, _ = authenticated_client
        members = client.get(f"/api/apiaries/{apiary['id']}/members").json()
        owner_member = next(member for member in members if member["user_id"] == test_user.id)

        self_invite = client.post(
            f"/api/apiaries/{apiary['id']}/members",
            json={"username_or_email": test_user.username, "role": "member"},
        )
        assert self_invite.status_code == 400
        assert client.put(
            f"/api/apiaries/{apiary['id']}/members/{owner_member['id']}",
            json={"role": "viewer"},
        ).status_code == 400
        assert client.delete(f"/api/apiaries/{apiary['id']}/members/{owner_member['id']}").status_code == 400
