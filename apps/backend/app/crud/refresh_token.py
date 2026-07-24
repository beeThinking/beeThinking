from datetime import datetime, timedelta, timezone
import hmac
import hashlib
import secrets

from sqlalchemy import update
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.refresh_token import RefreshToken
from app.models.user import User


def _hash_secret(secret: str) -> str:
    return hashlib.sha256(secret.encode("utf-8")).hexdigest()


def _parse_token(raw_token: str) -> tuple[str, str] | None:
    token_id, separator, secret = raw_token.partition(".")
    if not separator or not token_id or not secret or "." in secret:
        return None
    return token_id, secret


def _get_record(db: Session, raw_token: str) -> RefreshToken | None:
    token_parts = _parse_token(raw_token)
    if token_parts is None:
        return None
    token_id, secret = token_parts
    record = db.query(RefreshToken).filter(RefreshToken.token_id == token_id).first()
    if record is None or not hmac.compare_digest(record.token_hash, _hash_secret(secret)):
        return None
    return record


def _revoke_family(db: Session, record: RefreshToken, now: datetime) -> None:
    db.execute(
        update(RefreshToken)
        .where(RefreshToken.family_id == record.family_id, RefreshToken.revoked_at.is_(None))
        .values(revoked_at=now)
    )
    db.execute(
        update(RefreshToken)
        .where(RefreshToken.id == record.id)
        .values(reuse_detected=True)
    )


def issue_refresh_token(db: Session, user: User, family_id: str | None = None) -> tuple[str, RefreshToken]:
    token_id = secrets.token_urlsafe(24)
    secret = secrets.token_urlsafe(48)
    record = RefreshToken(
        token_id=token_id,
        user_id=user.id,
        family_id=family_id or secrets.token_hex(32),
        token_hash=_hash_secret(secret),
        expires_at=datetime.now(timezone.utc) + timedelta(days=get_settings().REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(record)
    db.flush()
    return f"{token_id}.{secret}", record


def rotate_refresh_token(db: Session, raw_token: str) -> tuple[User, str] | None:
    db.rollback()
    with db.begin():
        record = _get_record(db, raw_token)
        if record is None:
            return None
        now = datetime.now(timezone.utc)
        expires_at = record.expires_at.replace(tzinfo=timezone.utc) if record.expires_at.tzinfo is None else record.expires_at
        if record.revoked_at is not None:
            if record.replaced_by_id is not None:
                _revoke_family(db, record, now)
            return None
        if expires_at <= now or not record.user.is_active:
            db.execute(
                update(RefreshToken)
                .where(RefreshToken.id == record.id, RefreshToken.revoked_at.is_(None))
                .values(revoked_at=now)
            )
            return None
        result = db.execute(
            update(RefreshToken)
            .where(RefreshToken.id == record.id, RefreshToken.revoked_at.is_(None))
            .values(revoked_at=now)
        )
        if result.rowcount != 1:
            _revoke_family(db, record, now)
            return None
        new_raw_token, replacement = issue_refresh_token(db, record.user, record.family_id)
        db.execute(
            update(RefreshToken)
            .where(RefreshToken.id == record.id)
            .values(replaced_by_id=replacement.id)
        )
        return record.user, new_raw_token


def revoke_refresh_token(db: Session, raw_token: str) -> None:
    db.rollback()
    with db.begin():
        record = _get_record(db, raw_token)
        if record is not None:
            db.execute(
                update(RefreshToken)
                .where(RefreshToken.id == record.id, RefreshToken.revoked_at.is_(None))
                .values(revoked_at=datetime.now(timezone.utc))
            )
