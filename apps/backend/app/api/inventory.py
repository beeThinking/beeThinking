from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user
from app.crud import inventory as inventory_crud
from app.db.database import get_db
from app.models.user import User
from app.schemas.inventory import (
    ArticleCreate,
    ArticleResponse,
    ArticleUpdate,
    InventoryItemCreate,
    InventoryItemResponse,
    InventoryItemUpdate,
)

articles_router = APIRouter()
items_router = APIRouter()


@articles_router.get("", response_model=list[ArticleResponse])
def list_articles(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return inventory_crud.get_articles(db, owner_id=current_user.id)


@articles_router.post("", response_model=ArticleResponse, status_code=status.HTTP_201_CREATED)
def create_article(article: ArticleCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return inventory_crud.create_article(db, article=article, owner_id=current_user.id)


@articles_router.get("/{article_id}", response_model=ArticleResponse)
def get_article(article_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    db_article = inventory_crud.get_article(db, article_id=article_id, owner_id=current_user.id)
    if not db_article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    return db_article


@articles_router.put("/{article_id}", response_model=ArticleResponse)
def update_article(
    article_id: int,
    article_update: ArticleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_article = inventory_crud.update_article(db, article_id=article_id, owner_id=current_user.id, article_update=article_update)
    if not db_article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    return db_article


@articles_router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_article(article_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    if not inventory_crud.delete_article(db, article_id=article_id, owner_id=current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")


@items_router.get("", response_model=list[InventoryItemResponse])
def list_inventory_items(
    include_archived: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return inventory_crud.get_inventory_items(db, owner_id=current_user.id, include_archived=include_archived)


@items_router.post("", response_model=InventoryItemResponse, status_code=status.HTTP_201_CREATED)
def create_inventory_item(
    item: InventoryItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_item = inventory_crud.create_inventory_item(db, item=item, owner_id=current_user.id)
    if not db_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    return db_item


@items_router.get("/{item_id}", response_model=InventoryItemResponse)
def get_inventory_item(item_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    db_item = inventory_crud.get_inventory_item(db, item_id=item_id, owner_id=current_user.id)
    if not db_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory item not found")
    return db_item


@items_router.put("/{item_id}", response_model=InventoryItemResponse)
def update_inventory_item(
    item_id: int,
    item_update: InventoryItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_item = inventory_crud.update_inventory_item(db, item_id=item_id, owner_id=current_user.id, item_update=item_update)
    if not db_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory item not found")
    return db_item


@items_router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_inventory_item(item_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    if not inventory_crud.delete_inventory_item(db, item_id=item_id, owner_id=current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory item not found")
