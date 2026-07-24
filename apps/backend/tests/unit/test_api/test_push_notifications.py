from datetime import date, timedelta
from unittest.mock import patch

import pytest

from app.core.config import Settings
from app.models.push_subscription import PushSubscription
from app.models.task import Task
from app.services.push_notifications import send_task_deadline_reminders


def vapid_settings() -> Settings:
    return Settings(
        DATABASE_URL="sqlite://",
        SECRET_KEY="test-secret",
        VAPID_PUBLIC_KEY="public-key",
        VAPID_PRIVATE_KEY="private-key",
        VAPID_CONTACT_EMAIL="test@example.com",
    )


@pytest.mark.unit
class TestVapidPublicKeyEndpoint:
    def test_disabled_by_default(self, client):
        response = client.get("/api/push/vapid-public-key")
        assert response.status_code == 200
        assert response.json()["enabled"] is False


@pytest.mark.unit
class TestPushSubscriptionCrud:
    def test_create_and_list_subscription(self, authenticated_client):
        client, _ = authenticated_client
        response = client.post("/api/push/subscriptions", json={
            "endpoint": "https://push.example.com/abc",
            "p256dh_key": "p256dh",
            "auth_key": "auth",
        })
        assert response.status_code == 201

        response = client.get("/api/push/subscriptions")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_delete_subscription(self, authenticated_client):
        client, _ = authenticated_client
        created = client.post("/api/push/subscriptions", json={
            "endpoint": "https://push.example.com/xyz",
            "p256dh_key": "p256dh",
            "auth_key": "auth",
        }).json()

        assert client.delete(f"/api/push/subscriptions/{created['id']}").status_code == 204
        assert client.get("/api/push/subscriptions").json() == []

    def test_requires_auth(self, client):
        assert client.get("/api/push/subscriptions").status_code == 401


@pytest.mark.unit
class TestTaskDeadlineReminders:
    def test_sends_reminder_for_task_due_tomorrow(self, db, test_user):
        subscription = PushSubscription(
            user_id=test_user.id,
            endpoint="https://push.example.com/reminder",
            p256dh_key="p256dh",
            auth_key="auth",
        )
        db.add(subscription)
        task = Task(
            owner_id=test_user.id,
            title="Varroa check",
            due_date=date.today() + timedelta(days=1),
        )
        db.add(task)
        db.commit()

        with patch("app.services.push_notifications.webpush") as mock_webpush:
            sent = send_task_deadline_reminders(db, settings=vapid_settings())

        assert sent == 1
        mock_webpush.assert_called_once()

    def test_does_not_duplicate_reminder(self, db, test_user):
        subscription = PushSubscription(
            user_id=test_user.id,
            endpoint="https://push.example.com/reminder2",
            p256dh_key="p256dh",
            auth_key="auth",
        )
        db.add(subscription)
        task = Task(
            owner_id=test_user.id,
            title="Varroa check",
            due_date=date.today() + timedelta(days=1),
        )
        db.add(task)
        db.commit()

        with patch("app.services.push_notifications.webpush"):
            first = send_task_deadline_reminders(db, settings=vapid_settings())
            second = send_task_deadline_reminders(db, settings=vapid_settings())

        assert first == 1
        assert second == 0

    def test_no_reminder_when_vapid_disabled(self, db, test_user):
        task = Task(
            owner_id=test_user.id,
            title="Varroa check",
            due_date=date.today() + timedelta(days=1),
        )
        db.add(task)
        db.commit()

        sent = send_task_deadline_reminders(db, settings=Settings(DATABASE_URL="sqlite://", SECRET_KEY="test-secret"))

        assert sent == 0
