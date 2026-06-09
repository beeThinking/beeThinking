from typing import Optional

from sqlalchemy.orm import Session

from app.models.inventory import Article, InventoryItem
from app.schemas.inventory import ArticleCreate, ArticleUpdate, InventoryItemCreate, InventoryItemUpdate


def get_articles(db: Session, owner_id: int) -> list[Article]:
    return db.query(Article).filter(Article.owner_id == owner_id).order_by(Article.category, Article.name).all()


def get_article(db: Session, article_id: int, owner_id: int) -> Optional[Article]:
    return db.query(Article).filter(Article.id == article_id, Article.owner_id == owner_id).first()


def create_article(db: Session, article: ArticleCreate, owner_id: int) -> Article:
    db_article = Article(**article.model_dump(), owner_id=owner_id)
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article


def update_article(db: Session, article_id: int, owner_id: int, article_update: ArticleUpdate) -> Optional[Article]:
    db_article = get_article(db, article_id, owner_id)
    if not db_article:
        return None
    for field, value in article_update.model_dump(exclude_unset=True).items():
        setattr(db_article, field, value)
    db.commit()
    db.refresh(db_article)
    return db_article


def delete_article(db: Session, article_id: int, owner_id: int) -> bool:
    db_article = get_article(db, article_id, owner_id)
    if not db_article:
        return False
    db.delete(db_article)
    db.commit()
    return True


def get_inventory_items(db: Session, owner_id: int, include_archived: bool = False) -> list[InventoryItem]:
    query = db.query(InventoryItem).filter(InventoryItem.owner_id == owner_id)
    if not include_archived:
        query = query.filter(InventoryItem.archived.is_(False))
    return query.join(Article).order_by(Article.category, Article.name, InventoryItem.best_before.asc().nulls_last()).all()


def get_inventory_item(db: Session, item_id: int, owner_id: int) -> Optional[InventoryItem]:
    return db.query(InventoryItem).filter(InventoryItem.id == item_id, InventoryItem.owner_id == owner_id).first()


def create_inventory_item(db: Session, item: InventoryItemCreate, owner_id: int) -> Optional[InventoryItem]:
    data = item.model_dump()
    if not get_article(db, data["article_id"], owner_id):
        return None
    db_item = InventoryItem(**data, owner_id=owner_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def update_inventory_item(db: Session, item_id: int, owner_id: int, item_update: InventoryItemUpdate) -> Optional[InventoryItem]:
    db_item = get_inventory_item(db, item_id, owner_id)
    if not db_item:
        return None
    data = item_update.model_dump(exclude_unset=True)
    if "article_id" in data and not get_article(db, data["article_id"], owner_id):
        return None
    for field, value in data.items():
        setattr(db_item, field, value)
    db.commit()
    db.refresh(db_item)
    return db_item


def delete_inventory_item(db: Session, item_id: int, owner_id: int) -> bool:
    db_item = get_inventory_item(db, item_id, owner_id)
    if not db_item:
        return False
    db.delete(db_item)
    db.commit()
    return True
