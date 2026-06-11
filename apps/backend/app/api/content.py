from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_admin_user
from app.crud import content as content_crud
from app.db.database import get_db
from app.models.user import User
from app.schemas.content import AppTextCreate, AppTextResponse, AppTextUpdate, ContentPageCreate, ContentPageResponse, ContentPageUpdate

router = APIRouter()
admin_router = APIRouter()


@router.get("/pages/{slug}", response_model=ContentPageResponse)
def get_public_page(slug: str, locale: str = "de", db: Session = Depends(get_db)):
    page = content_crud.get_page(db, slug=slug, locale=locale, include_drafts=False)
    if not page:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content page not found")
    return page


@router.get("/app-texts", response_model=dict[str, str])
def get_public_app_texts(locale: str = "de", db: Session = Depends(get_db)):
    texts = content_crud.list_app_texts(db, include_drafts=False, locale=locale)
    return {text.key: text.value for text in texts}


@admin_router.get("/pages", response_model=list[ContentPageResponse])
def list_admin_pages(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    return content_crud.list_pages(db, include_drafts=True)


@admin_router.post("/pages", response_model=ContentPageResponse, status_code=status.HTTP_201_CREATED)
def create_admin_page(
    page: ContentPageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    return content_crud.create_page(db, page, updated_by_user_id=current_user.id)


@admin_router.put("/pages/{page_id}", response_model=ContentPageResponse)
def update_admin_page(
    page_id: int,
    page: ContentPageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    updated = content_crud.update_page(db, page_id, page, updated_by_user_id=current_user.id)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content page not found")
    return updated


@admin_router.get("/app-texts", response_model=list[AppTextResponse])
def list_admin_app_texts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    return content_crud.list_app_texts(db, include_drafts=True)


@admin_router.post("/app-texts", response_model=AppTextResponse, status_code=status.HTTP_201_CREATED)
def upsert_admin_app_text(
    text: AppTextCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    return content_crud.upsert_app_text(db, text, updated_by_user_id=current_user.id)


@admin_router.put("/app-texts/{text_id}", response_model=AppTextResponse)
def update_admin_app_text(
    text_id: int,
    text: AppTextUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    updated = content_crud.update_app_text(db, text_id, text, updated_by_user_id=current_user.id)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="App text not found")
    return updated
