from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.schemas.user import AdminUserUpdate, UserResponse
from app.api.dependencies import get_current_active_user, get_current_admin_user
from app.core.config import get_settings
from app.crud.user import count_db_admins, get_user_by_id, list_users, update_user_admin
from app.db.database import get_db
from app.models.user import User
from app.core.logging import metrics
from app.crud.export import build_account_export

router = APIRouter()
export_router = APIRouter()
metrics_router = APIRouter()


def _apply_env_admin_flag(user: User) -> User:
    if user.email.lower() in get_settings().admin_emails_set:
        user.is_admin = True
    return user


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information."""
    return _apply_env_admin_flag(current_user)


@router.get("", response_model=list[UserResponse])
def list_admin_users(
    search: str | None = Query(default=None, max_length=120),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    return [_apply_env_admin_flag(user) for user in list_users(db, search=search)]


@router.patch("/{user_id}", response_model=UserResponse)
def update_admin_user(
    user_id: int,
    update: AdminUserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user.id == current_user.id and update.is_active is False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Admins cannot deactivate themselves")

    has_active_env_admin = any(
        admin.email.lower() in get_settings().admin_emails_set and admin.is_active
        for admin in list_users(db)
    )
    if user.is_admin and update.is_admin is False and count_db_admins(db) <= 1 and not has_active_env_admin:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Last database admin cannot be removed")

    return _apply_env_admin_flag(update_user_admin(db, user, update))


@export_router.get("/me/export")
def export_account_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    archive = build_account_export(db, current_user)
    return StreamingResponse(
        archive,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=beethinking-account-export.zip"},
    )


@metrics_router.get("/metrics")
def get_metrics(current_user: User = Depends(get_current_admin_user)):
    return dict(metrics)
