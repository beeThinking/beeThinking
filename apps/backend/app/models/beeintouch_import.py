from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.sql import func

from app.db.database import Base


class BeeIntouchImportRun(Base):
    __tablename__ = "beeintouch_import_runs"
    __table_args__ = (
        UniqueConstraint("source_name", "source_hash", name="uq_beeintouch_import_source_hash"),
    )

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    source_name = Column(String, nullable=False)
    source_hash = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending")
    imported_count = Column(Integer, nullable=False, default=0)
    error_count = Column(Integer, nullable=False, default=0)
    summary = Column(Text, nullable=True)
    error_text = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True), nullable=True)


class BeeIntouchImportError(Base):
    __tablename__ = "beeintouch_import_errors"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("beeintouch_import_runs.id"), nullable=False, index=True)
    source_name = Column(String, nullable=False)
    page_number = Column(Integer, nullable=True)
    row_number = Column(Integer, nullable=True)
    target_type = Column(String, nullable=True)
    message = Column(Text, nullable=False)
    raw_text = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

