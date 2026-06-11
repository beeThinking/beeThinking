from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class ContentPage(Base):
    __tablename__ = "content_pages"
    __table_args__ = (UniqueConstraint("slug", "locale", name="uq_content_pages_slug_locale"),)

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, nullable=False, index=True)
    locale = Column(String, nullable=False, default="de")
    title = Column(String, nullable=False)
    eyebrow = Column(String, nullable=True)
    lead = Column(Text, nullable=True)
    cta_label = Column(String, nullable=True)
    cta_link = Column(String, nullable=True)
    status = Column(String, nullable=False, default="draft")
    updated_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    sections = relationship(
        "ContentSection",
        back_populates="page",
        cascade="all, delete-orphan",
        order_by="ContentSection.sort_order",
    )
    updated_by = relationship("User", back_populates="content_updates")


class ContentSection(Base):
    __tablename__ = "content_sections"

    id = Column(Integer, primary_key=True, index=True)
    page_id = Column(Integer, ForeignKey("content_pages.id"), nullable=False)
    sort_order = Column(Integer, nullable=False, default=0)
    heading = Column(String, nullable=False)
    body = Column(Text, nullable=False)

    page = relationship("ContentPage", back_populates="sections")


class AppText(Base):
    __tablename__ = "app_texts"
    __table_args__ = (UniqueConstraint("key", "locale", name="uq_app_texts_key_locale"),)

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, nullable=False, index=True)
    locale = Column(String, nullable=False, default="de", index=True)
    value = Column(Text, nullable=False)
    status = Column(String, nullable=False, default="draft")
    updated_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
