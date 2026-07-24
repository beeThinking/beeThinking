from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class PushSubscription(Base):
    """Web Push subscription storage (#40). Scope: task-deadline reminders only for now.

    Breeding-step push reminders are a separate follow-up ticket once M7.5 lands.
    """

    __tablename__ = "push_subscriptions"
    __table_args__ = (UniqueConstraint("endpoint", name="uq_push_subscriptions_endpoint"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    endpoint = Column(Text, nullable=False)
    p256dh_key = Column(String, nullable=False)
    auth_key = Column(String, nullable=False)
    user_agent = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_reminder_sent_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User")


class TaskReminderLog(Base):
    """Tracks which task deadline reminders were already sent to avoid duplicate pushes."""

    __tablename__ = "task_reminder_logs"
    __table_args__ = (UniqueConstraint("task_id", "subscription_id", name="uq_task_reminder_task_subscription"),)

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    subscription_id = Column(Integer, ForeignKey("push_subscriptions.id", ondelete="CASCADE"), nullable=False, index=True)
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
