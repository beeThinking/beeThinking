import enum

from sqlalchemy import Boolean, Column, Date, DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class ArticleCategory(str, enum.Enum):
    honey = "honey"
    finished_product = "finished_product"
    feed = "feed"
    material = "material"


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category = Column(Enum(ArticleCategory), default=ArticleCategory.material, nullable=False)
    name = Column(String, nullable=False)
    sku = Column(String, nullable=True)
    weight_kg = Column(Float, nullable=True)
    unit = Column(String, nullable=False, default="piece")
    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owner = relationship("User", back_populates="articles")
    inventory_items = relationship("InventoryItem", back_populates="article", cascade="all, delete-orphan")


class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=True)
    quantity = Column(Float, nullable=False, default=0)
    unit = Column(String, nullable=False, default="piece")
    price = Column(Float, nullable=True)
    best_before = Column(Date, nullable=True)
    batch_code = Column(String, nullable=True)
    archived = Column(Boolean, default=False, nullable=False)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owner = relationship("User", back_populates="inventory_items")
    article = relationship("Article", back_populates="inventory_items")
    batch = relationship("Batch", back_populates="inventory_items")
