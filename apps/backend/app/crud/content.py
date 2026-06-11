from sqlalchemy.orm import Session

from app.models.content import AppText, ContentPage, ContentSection
from app.schemas.content import AppTextCreate, AppTextUpdate, ContentPageCreate, ContentPageUpdate


def list_pages(db: Session, include_drafts: bool = False) -> list[ContentPage]:
    query = db.query(ContentPage)
    if not include_drafts:
        query = query.filter(ContentPage.status == "published")
    return query.order_by(ContentPage.slug, ContentPage.locale).all()


def get_page(db: Session, slug: str, locale: str = "de", include_drafts: bool = False) -> ContentPage | None:
    query = db.query(ContentPage).filter(ContentPage.slug == slug, ContentPage.locale == locale)
    if not include_drafts:
        query = query.filter(ContentPage.status == "published")
    return query.first()


def create_page(db: Session, page: ContentPageCreate, updated_by_user_id: int) -> ContentPage:
    data = page.model_dump(exclude={"sections"})
    db_page = ContentPage(**data, updated_by_user_id=updated_by_user_id)
    db_page.sections = [ContentSection(**section.model_dump()) for section in page.sections]
    db.add(db_page)
    db.commit()
    db.refresh(db_page)
    return db_page


def update_page(db: Session, page_id: int, update: ContentPageUpdate, updated_by_user_id: int) -> ContentPage | None:
    db_page = db.query(ContentPage).filter(ContentPage.id == page_id).first()
    if not db_page:
        return None
    data = update.model_dump(exclude_unset=True, exclude={"sections"})
    for field, value in data.items():
        setattr(db_page, field, value)
    if update.sections is not None:
        db_page.sections = [ContentSection(**section.model_dump()) for section in update.sections]
    db_page.updated_by_user_id = updated_by_user_id
    db.commit()
    db.refresh(db_page)
    return db_page


def list_app_texts(db: Session, include_drafts: bool = False, locale: str | None = None) -> list[AppText]:
    query = db.query(AppText)
    if locale:
        query = query.filter(AppText.locale == locale)
    if not include_drafts:
        query = query.filter(AppText.status == "published")
    return query.order_by(AppText.key, AppText.locale).all()


def get_app_text(db: Session, text_id: int) -> AppText | None:
    return db.query(AppText).filter(AppText.id == text_id).first()


def get_app_text_by_key(db: Session, key: str, locale: str) -> AppText | None:
    return db.query(AppText).filter(AppText.key == key, AppText.locale == locale).first()


def upsert_app_text(db: Session, text: AppTextCreate, updated_by_user_id: int) -> AppText:
    db_text = get_app_text_by_key(db, text.key, text.locale)
    if not db_text:
        db_text = AppText(**text.model_dump(), updated_by_user_id=updated_by_user_id)
        db.add(db_text)
    else:
        for field, value in text.model_dump().items():
            setattr(db_text, field, value)
        db_text.updated_by_user_id = updated_by_user_id
    db.commit()
    db.refresh(db_text)
    return db_text


def update_app_text(db: Session, text_id: int, update: AppTextUpdate, updated_by_user_id: int) -> AppText | None:
    db_text = get_app_text(db, text_id)
    if not db_text:
        return None
    for field, value in update.model_dump(exclude_unset=True).items():
        setattr(db_text, field, value)
    db_text.updated_by_user_id = updated_by_user_id
    db.commit()
    db.refresh(db_text)
    return db_text
