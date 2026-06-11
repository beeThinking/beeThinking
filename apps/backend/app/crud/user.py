from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import AdminUserUpdate, UserCreate
from app.core.security import get_password_hash, verify_password
from typing import Optional
from app.core.config import get_settings


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username."""
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def list_users(db: Session, search: str | None = None) -> list[User]:
    query = db.query(User)
    if search:
        pattern = f"%{search}%"
        query = query.filter(or_(User.username.ilike(pattern), User.email.ilike(pattern)))
    return query.order_by(User.created_at.desc(), User.id.desc()).all()


def create_user(db: Session, user: UserCreate) -> User:
    """Create a new user."""
    settings = get_settings()
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        is_verified=not settings.EMAIL_CONFIRMATION_ENABLED,  # Auto-verify if email not enabled
        is_admin=user.email.lower() in settings.admin_emails_set,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Authenticate a user."""
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def update_user_admin(db: Session, user: User, update: AdminUserUpdate) -> User:
    data = update.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


def count_db_admins(db: Session) -> int:
    return db.query(User).filter(User.is_admin.is_(True), User.is_active.is_(True)).count()
