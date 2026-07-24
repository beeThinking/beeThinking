from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user
from app.core.config import get_settings
from app.crud import push_subscription as push_subscription_crud
from app.db.database import get_db
from app.models.user import User
from app.schemas.push_subscription import (
    PushSubscriptionCreate,
    PushSubscriptionResponse,
    VapidPublicKeyResponse,
)

router = APIRouter()


@router.get("/vapid-public-key", response_model=VapidPublicKeyResponse)
def get_vapid_public_key():
    settings = get_settings()
    return {"public_key": settings.VAPID_PUBLIC_KEY or None, "enabled": settings.vapid_enabled}


@router.get("/subscriptions", response_model=list[PushSubscriptionResponse])
def list_subscriptions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return push_subscription_crud.list_subscriptions(db, user_id=current_user.id)


@router.post("/subscriptions", response_model=PushSubscriptionResponse, status_code=status.HTTP_201_CREATED)
def create_subscription(
    payload: PushSubscriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return push_subscription_crud.create_subscription(db, user_id=current_user.id, payload=payload)


@router.delete("/subscriptions/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subscription(
    subscription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if not push_subscription_crud.delete_subscription(db, user_id=current_user.id, subscription_id=subscription_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found")
