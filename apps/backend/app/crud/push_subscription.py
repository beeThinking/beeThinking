from sqlalchemy.orm import Session

from app.models.push_subscription import PushSubscription
from app.schemas.push_subscription import PushSubscriptionCreate


def create_subscription(db: Session, user_id: int, payload: PushSubscriptionCreate) -> PushSubscription:
    existing = db.query(PushSubscription).filter(PushSubscription.endpoint == payload.endpoint).first()
    if existing:
        existing.user_id = user_id
        existing.p256dh_key = payload.p256dh_key
        existing.auth_key = payload.auth_key
        existing.user_agent = payload.user_agent
        db.commit()
        db.refresh(existing)
        return existing
    subscription = PushSubscription(
        user_id=user_id,
        endpoint=payload.endpoint,
        p256dh_key=payload.p256dh_key,
        auth_key=payload.auth_key,
        user_agent=payload.user_agent,
    )
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    return subscription


def list_subscriptions(db: Session, user_id: int) -> list[PushSubscription]:
    return db.query(PushSubscription).filter(PushSubscription.user_id == user_id).all()


def delete_subscription(db: Session, user_id: int, subscription_id: int) -> bool:
    subscription = db.query(PushSubscription).filter(
        PushSubscription.id == subscription_id, PushSubscription.user_id == user_id
    ).first()
    if not subscription:
        return False
    db.delete(subscription)
    db.commit()
    return True
