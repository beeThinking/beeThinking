from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.sql import func

from app.db.database import Base


class GoogleCalendarConnection(Base):
    __tablename__ = "google_calendar_connections"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    refresh_token_encrypted = Column(Text, nullable=False)
    calendar_id = Column(String, nullable=False)
    calendar_name = Column(String, nullable=False, default="BeeThinking")
    connected_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_sync_at = Column(DateTime(timezone=True), nullable=True)
    last_error = Column(Text, nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class GoogleCalendarEvent(Base):
    __tablename__ = "google_calendar_events"
    __table_args__ = (
        UniqueConstraint("user_id", "task_id", name="uq_google_calendar_event_user_task"),
        UniqueConstraint("user_id", "google_event_id", name="uq_google_calendar_event_user_google"),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    task_id = Column(Integer, nullable=False, index=True)
    google_event_id = Column(String, nullable=False)
    synced_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class GoogleOAuthState(Base):
    __tablename__ = "google_oauth_states"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    state_hash = Column(String(64), nullable=False, unique=True, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
