"""In-process APScheduler wiring for scheduled jobs (#40: task-deadline push reminders).

No external scheduler infra — fits the current single-instance deployment.
Started from app.main on FastAPI startup, stopped on shutdown.
"""

import logging

from apscheduler.schedulers.background import BackgroundScheduler

from app.core.config import get_settings
from app.db.database import SessionLocal
from app.services.push_notifications import send_task_deadline_reminders

logger = logging.getLogger(__name__)

_scheduler: BackgroundScheduler | None = None


def _run_task_deadline_reminders_job() -> None:
    settings = get_settings()
    if not settings.vapid_enabled:
        return
    db = SessionLocal()
    try:
        sent = send_task_deadline_reminders(db, settings=settings)
        if sent:
            logger.info("Sent %s task-deadline push reminders", sent)
    finally:
        db.close()


def start_scheduler() -> BackgroundScheduler | None:
    global _scheduler
    settings = get_settings()
    if not settings.vapid_enabled:
        return None
    if _scheduler is not None:
        return _scheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(_run_task_deadline_reminders_job, "interval", hours=1, id="task_deadline_reminders")
    scheduler.start()
    _scheduler = scheduler
    return scheduler


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
