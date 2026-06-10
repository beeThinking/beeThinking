from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user
from app.crud import content as content_crud
from app.db.database import get_db
from app.models.user import User
from app.schemas.content import ContentPageCreate, ContentPageResponse, ContentPageUpdate

router = APIRouter()
admin_router = APIRouter()


@router.get("/pages/{slug}", response_model=ContentPageResponse)
def get_public_page(slug: str, locale: str = "de", db: Session = Depends(get_db)):
    page = content_crud.get_page(db, slug=slug, locale=locale, include_drafts=False)
    if not page:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content page not found")
    return page


@admin_router.get("/pages", response_model=list[ContentPageResponse])
def list_admin_pages(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return content_crud.list_pages(db, include_drafts=True)


@admin_router.post("/pages", response_model=ContentPageResponse, status_code=status.HTTP_201_CREATED)
def create_admin_page(
    page: ContentPageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return content_crud.create_page(db, page, updated_by_user_id=current_user.id)


@admin_router.put("/pages/{page_id}", response_model=ContentPageResponse)
def update_admin_page(
    page_id: int,
    page: ContentPageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    updated = content_crud.update_page(db, page_id, page, updated_by_user_id=current_user.id)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content page not found")
    return updated
