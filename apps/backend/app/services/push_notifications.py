"""Web Push notifications for task deadlines (#40).

Scope: task-deadline reminders only. Breeding-step push reminders are a
separate follow-up ticket once M7.5 lands.

Delivery: standard Web Push via VAPID (RFC8292), using `pywebpush`.
Scheduling: APScheduler running in-process (no extra infra service — fits the
current single-instance deployment). The scheduled job below checks for tasks
due in ~1 day and sends a reminder to each subscription of the task's
owner/assignee that hasn't already received one for that task.
"""

import json
import logging
from datetime import date, datetime, timedelta, timezone

from pywebpush import WebPushException, webpush
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.models.push_subscription import PushSubscription, TaskReminderLog
from app.models.task import Task, TaskStatus

logger = logging.getLogger(__name__)


class PushNotificationError(RuntimeError):
    pass


def send_web_push(subscription: PushSubscription, payload: dict, settings: Settings | None = None) -> None:
    settings = settings or get_settings()
    if not settings.vapid_enabled:
        raise PushNotificationError("VAPID keys are not configured")
    try:
        webpush(
            subscription_info={
                "endpoint": subscription.endpoint,
                "keys": {
                    "p256dh": subscription.p256dh_key,
                    "auth": subscription.auth_key,
                },
            },
            data=json.dumps(payload),
            vapid_private_key=settings.VAPID_PRIVATE_KEY,
            vapid_claims={"sub": f"mailto:{settings.VAPID_CONTACT_EMAIL}"},
        )
    except WebPushException as exc:
        raise PushNotificationError(str(exc)) from exc


def send_task_deadline_reminders(db: Session, settings: Settings | None = None, reference_date: date | None = None) -> int:
    """Send push reminders for tasks due in ~1 day. Returns count of pushes sent.

    Runs as an APScheduler job (see app.services.scheduler). Idempotent per
    (task_id, subscription_id) via TaskReminderLog.
    """
    settings = settings or get_settings()
    if not settings.vapid_enabled:
        return 0

    today = reference_date or datetime.now(timezone.utc).date()
    target_date = today + timedelta(days=1)

    tasks = (
        db.query(Task)
        .filter(Task.due_date == target_date, Task.status == TaskStatus.open)
        .all()
    )
    sent_count = 0
    for task in tasks:
        recipient_ids = {task.owner_id}
        if task.assignee_id:
            recipient_ids.add(task.assignee_id)
        subscriptions = (
            db.query(PushSubscription)
            .filter(PushSubscription.user_id.in_(recipient_ids))
            .all()
        )
        for subscription in subscriptions:
            already_sent = (
                db.query(TaskReminderLog)
                .filter(TaskReminderLog.task_id == task.id, TaskReminderLog.subscription_id == subscription.id)
                .first()
            )
            if already_sent:
                continue
            try:
                send_web_push(
                    subscription,
                    {
                        "title": "Aufgabe fällig morgen",
                        "body": task.title,
                        "task_id": task.id,
                    },
                    settings=settings,
                )
            except PushNotificationError as exc:
                logger.warning("Push notification failed for subscription %s: %s", subscription.id, exc)
                continue
            db.add(TaskReminderLog(task_id=task.id, subscription_id=subscription.id))
            subscription.last_reminder_sent_at = datetime.now(timezone.utc)
            sent_count += 1
    db.commit()
    return sent_count
