from datetime import date, datetime, timedelta, timezone

import pytest

from app.core.security import get_password_hash
from app.models.apiary_member import ApiaryMember, ApiaryMemberRole
from app.models.task import Task
from app.models.user import User


def _login(client, username, password):
    response = client.post("/api/auth/login", data={"username": username, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def teammate(db):
    user = User(
        username="teammate",
        email="teammate@example.com",
        hashed_password=get_password_hash("TeammatePassword123!"),
        is_active=True,
        is_verified=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def shared_apiary(authenticated_client, db, teammate):
    client, _ = authenticated_client
    response = client.post("/api/apiaries", json={"stock_number": "Shared Stand", "name": "Shared Stand"})
    assert response.status_code == 201
    apiary = response.json()
    db.add(ApiaryMember(
        apiary_id=apiary["id"],
        user_id=teammate.id,
        role=ApiaryMemberRole.member,
        accepted_at=datetime.now(timezone.utc),
    ))
    db.commit()
    return apiary


@pytest.mark.unit
class TestTaskMembershipVisibility:
    def test_apiary_member_sees_owner_created_task(self, client, authenticated_client, shared_apiary, teammate):
        owner_client, _ = authenticated_client
        response = owner_client.post("/api/tasks", json={
            "apiary_id": shared_apiary["id"],
            "title": "Team task",
        })
        assert response.status_code == 201
        task_id = response.json()["id"]

        client.headers["Authorization"] = f"Bearer {_login(client, 'teammate', 'TeammatePassword123!')}"
        response = client.get("/api/tasks")
        assert response.status_code == 200
        assert any(task["id"] == task_id for task in response.json())

        response = client.get(f"/api/tasks/{task_id}")
        assert response.status_code == 200

    def test_apiary_member_sees_task_via_hive(self, client, authenticated_client, shared_apiary, teammate):
        owner_client, _ = authenticated_client
        hive = owner_client.post("/api/hives", json={"name": "Shared Hive", "apiary_id": shared_apiary["id"]}).json()
        task = owner_client.post("/api/tasks", json={"hive_id": hive["id"], "title": "Hive task"}).json()

        client.headers["Authorization"] = f"Bearer {_login(client, 'teammate', 'TeammatePassword123!')}"
        response = client.get("/api/tasks")
        assert response.status_code == 200
        assert any(t["id"] == task["id"] for t in response.json())

    def test_non_member_cannot_see_task(self, client, authenticated_client, db):
        owner_client, _ = authenticated_client
        apiary = owner_client.post("/api/apiaries", json={"stock_number": "Private Stand"}).json()
        task = owner_client.post("/api/tasks", json={"apiary_id": apiary["id"], "title": "Private task"}).json()

        outsider = User(
            username="outsider",
            email="outsider@example.com",
            hashed_password=get_password_hash("OutsiderPassword123!"),
            is_active=True,
            is_verified=True,
        )
        db.add(outsider)
        db.commit()

        client.headers["Authorization"] = f"Bearer {_login(client, 'outsider', 'OutsiderPassword123!')}"
        response = client.get("/api/tasks")
        assert response.status_code == 200
        assert all(t["id"] != task["id"] for t in response.json())
        assert client.get(f"/api/tasks/{task['id']}").status_code == 404

    def test_viewer_cannot_modify_or_complete_or_delete_scoped_task(
        self, client, authenticated_client, shared_apiary, teammate, db
    ):
        owner_client, _ = authenticated_client
        membership = db.query(ApiaryMember).filter_by(apiary_id=shared_apiary["id"], user_id=teammate.id).one()
        membership.role = ApiaryMemberRole.viewer
        db.commit()
        task = owner_client.post("/api/tasks", json={"apiary_id": shared_apiary["id"], "title": "Read only"}).json()

        client.headers["Authorization"] = f"Bearer {_login(client, 'teammate', 'TeammatePassword123!')}"

        assert client.put(f"/api/tasks/{task['id']}", json={"title": "Changed"}).status_code == 403
        assert client.post(f"/api/tasks/{task['id']}/complete").status_code == 403
        assert client.delete(f"/api/tasks/{task['id']}").status_code == 403
        assert owner_client.get(f"/api/tasks/{task['id']}").json()["status"] == "open"

    def test_nonexistent_task_write_routes_return_not_found(self, authenticated_client):
        client, _ = authenticated_client
        task_id = 999999

        assert client.put(f"/api/tasks/{task_id}", json={"title": "Changed"}).status_code == 404
        assert client.post(f"/api/tasks/{task_id}/complete").status_code == 404
        assert client.delete(f"/api/tasks/{task_id}").status_code == 404

    def test_revoked_member_cannot_modify_or_delete_scoped_task(
        self, client, authenticated_client, shared_apiary, teammate, db
    ):
        owner_client, _ = authenticated_client
        first_task = owner_client.post("/api/tasks", json={"apiary_id": shared_apiary["id"], "title": "Update"}).json()
        second_task = owner_client.post("/api/tasks", json={"apiary_id": shared_apiary["id"], "title": "Delete"}).json()
        membership = db.query(ApiaryMember).filter_by(apiary_id=shared_apiary["id"], user_id=teammate.id).one()
        db.delete(membership)
        db.commit()

        client.headers["Authorization"] = f"Bearer {_login(client, 'teammate', 'TeammatePassword123!')}"

        assert client.put(f"/api/tasks/{first_task['id']}", json={"title": "Changed"}).status_code == 403
        assert client.post(f"/api/tasks/{first_task['id']}/complete").status_code == 403
        assert client.delete(f"/api/tasks/{second_task['id']}").status_code == 403

    def test_rejects_mismatched_apiary_and_hive_on_task_create_and_update(
        self, authenticated_client, db, teammate
    ):
        client, _ = authenticated_client
        first_apiary = client.post("/api/apiaries", json={"stock_number": "First"}).json()
        second_apiary = client.post("/api/apiaries", json={"stock_number": "Second"}).json()
        hive = client.post("/api/hives", json={"name": "First hive", "apiary_id": first_apiary["id"]}).json()
        db.add_all([
            ApiaryMember(
                apiary_id=first_apiary["id"],
                user_id=teammate.id,
                role=ApiaryMemberRole.member,
                accepted_at=datetime.now(timezone.utc),
            ),
            ApiaryMember(
                apiary_id=second_apiary["id"],
                user_id=teammate.id,
                role=ApiaryMemberRole.member,
                accepted_at=datetime.now(timezone.utc),
            ),
        ])
        db.commit()

        response = client.post("/api/tasks", json={
            "apiary_id": second_apiary["id"],
            "hive_id": hive["id"],
            "title": "Mismatched create",
        })
        assert response.status_code == 404

        task = client.post("/api/tasks", json={"apiary_id": first_apiary["id"], "title": "Valid"}).json()
        response = client.put(f"/api/tasks/{task['id']}", json={
            "apiary_id": second_apiary["id"],
            "hive_id": hive["id"],
        })
        assert response.status_code == 404
        assert client.get(f"/api/tasks/{task['id']}").json()["apiary_id"] == first_apiary["id"]

        delegation_task = client.post("/api/tasks", json={
            "apiary_id": second_apiary["id"],
            "title": "Delegation mismatch",
        }).json()
        db_task = db.query(Task).filter_by(id=delegation_task["id"]).one()
        db_task.hive_id = hive["id"]
        db.commit()

        response = client.post(f"/api/tasks/{delegation_task['id']}/delegate", json={"assignee_id": teammate.id})
        assert response.status_code == 404


@pytest.mark.unit
class TestFeedingHarvestCashbookMembershipVisibility:
    def test_apiary_member_sees_feedings_and_harvests(self, client, authenticated_client, shared_apiary, teammate):
        owner_client, _ = authenticated_client
        feeding = owner_client.post("/api/feedings", json={
            "apiary_id": shared_apiary["id"],
            "date": str(date.today()),
            "feed_type": "Futtersirup",
            "amount_kg_or_l": 2.0,
        }).json()
        harvest = owner_client.post("/api/harvests", json={
            "apiary_id": shared_apiary["id"],
            "harvest_date": str(date.today()),
            "amount_kg": 5.0,
        }).json()

        client.headers["Authorization"] = f"Bearer {_login(client, 'teammate', 'TeammatePassword123!')}"
        feedings = client.get("/api/feedings").json()
        harvests = client.get("/api/harvests").json()
        assert any(f["id"] == feeding["id"] for f in feedings)
        assert any(h["id"] == harvest["id"] for h in harvests)
        assert client.get(f"/api/feedings/{feeding['id']}").status_code == 200
        assert client.get(f"/api/harvests/{harvest['id']}").status_code == 200

    def test_apiary_member_sees_cashbook_entries(self, client, authenticated_client, shared_apiary, teammate):
        owner_client, _ = authenticated_client
        entry = owner_client.post("/api/cashbook/entries", json={
            "apiary_id": shared_apiary["id"],
            "booking_date": str(date.today()),
            "direction": "expense",
            "category": "feed",
            "amount_gross": 10.0,
            "amount_net": 10.0,
        }).json()

        client.headers["Authorization"] = f"Bearer {_login(client, 'teammate', 'TeammatePassword123!')}"
        response = client.get("/api/cashbook/entries")
        assert response.status_code == 200
        assert any(e["id"] == entry["id"] for e in response.json())

    def test_non_member_does_not_see_shared_apiary_records(self, client, authenticated_client, db):
        owner_client, _ = authenticated_client
        apiary = owner_client.post("/api/apiaries", json={"stock_number": "Private Stand 2"}).json()
        feeding = owner_client.post("/api/feedings", json={
            "apiary_id": apiary["id"],
            "date": str(date.today()),
            "feed_type": "Futtersirup",
            "amount_kg_or_l": 1.0,
        }).json()

        outsider = User(
            username="outsider2",
            email="outsider2@example.com",
            hashed_password=get_password_hash("OutsiderPassword123!"),
            is_active=True,
            is_verified=True,
        )
        db.add(outsider)
        db.commit()

        client.headers["Authorization"] = f"Bearer {_login(client, 'outsider2', 'OutsiderPassword123!')}"
        response = client.get("/api/feedings")
        assert response.status_code == 200
        assert all(f["id"] != feeding["id"] for f in response.json())


@pytest.mark.unit
class TestTaskDelegationAndRecurrence:
    def test_delegate_task_sets_assignee_and_flag(self, authenticated_client, teammate, db):
        client, _ = authenticated_client
        apiary = client.post("/api/apiaries", json={"stock_number": "Delegation Stand"}).json()
        db.add(ApiaryMember(
            apiary_id=apiary["id"],
            user_id=teammate.id,
            role=ApiaryMemberRole.member,
            accepted_at=datetime.now(timezone.utc),
        ))
        db.commit()
        task = client.post("/api/tasks", json={"apiary_id": apiary["id"], "title": "Delegate me"}).json()

        response = client.post(f"/api/tasks/{task['id']}/delegate", json={"assignee_id": teammate.id})

        assert response.status_code == 200
        data = response.json()
        assert data["assignee_id"] == teammate.id
        assert data["delegated_at"] is not None

    def test_rejects_delegation_to_non_member(self, authenticated_client, teammate):
        client, _ = authenticated_client
        apiary = client.post("/api/apiaries", json={"stock_number": "Private delegation"}).json()
        task = client.post("/api/tasks", json={"apiary_id": apiary["id"], "title": "Private task"}).json()

        response = client.post(f"/api/tasks/{task['id']}/delegate", json={"assignee_id": teammate.id})

        assert response.status_code == 404

    def test_rejects_non_self_assignment_for_personal_task(self, authenticated_client, teammate):
        client, _ = authenticated_client

        response = client.post("/api/tasks", json={"title": "Personal task", "assignee_id": teammate.id})

        assert response.status_code == 404

    def test_revoked_member_cannot_access_creator_scoped_task(self, client, authenticated_client, shared_apiary, teammate, db):
        owner_client, owner_token = authenticated_client
        task = owner_client.post("/api/tasks", json={"apiary_id": shared_apiary["id"], "title": "Scoped task"}).json()
        membership = db.query(ApiaryMember).filter_by(apiary_id=shared_apiary["id"], user_id=teammate.id).one()
        db.delete(membership)
        db.commit()

        client.headers["Authorization"] = f"Bearer {owner_token}"
        assert client.get(f"/api/tasks/{task['id']}").status_code == 200
        client.headers["Authorization"] = f"Bearer {_login(client, 'teammate', 'TeammatePassword123!')}"
        assert client.get(f"/api/tasks/{task['id']}").status_code == 404
        assert all(item["id"] != task["id"] for item in client.get("/api/tasks").json())

    def test_assignee_can_acknowledge_delegation(self, client, authenticated_client, shared_apiary, teammate):
        owner_client, _ = authenticated_client
        task = owner_client.post("/api/tasks", json={"apiary_id": shared_apiary["id"], "title": "Delegate me"}).json()
        owner_client.post(f"/api/tasks/{task['id']}/delegate", json={"assignee_id": teammate.id})

        client.headers["Authorization"] = f"Bearer {_login(client, 'teammate', 'TeammatePassword123!')}"
        response = client.post(f"/api/tasks/{task['id']}/delegation-seen")
        assert response.status_code == 200
        assert response.json()["delegation_seen_at"] is not None

    def test_create_task_with_valid_recurrence_rule(self, authenticated_client):
        client, _ = authenticated_client
        response = client.post("/api/tasks", json={
            "title": "Weekly inspection",
            "due_date": str(date.today()),
            "recurrence_rule": "FREQ=WEEKLY;COUNT=4",
        })
        assert response.status_code == 201
        assert response.json()["recurrence_rule"] == "FREQ=WEEKLY;COUNT=4"

    def test_create_task_with_invalid_recurrence_rule_fails(self, authenticated_client):
        client, _ = authenticated_client
        response = client.post("/api/tasks", json={
            "title": "Broken recurrence",
            "recurrence_rule": "NOT-A-VALID-RRULE",
        })
        assert response.status_code == 422

    def test_occurrences_expand_recurring_task(self, authenticated_client):
        client, _ = authenticated_client
        start = date.today()
        response = client.post("/api/tasks", json={
            "title": "Weekly inspection",
            "due_date": str(start),
            "recurrence_rule": "FREQ=WEEKLY;COUNT=4",
        })
        assert response.status_code == 201

        response = client.get("/api/tasks/occurrences", params={
            "range_start": str(start),
            "range_end": str(start + timedelta(days=60)),
        })
        assert response.status_code == 200
