from datetime import timedelta
from typing import BinaryIO
from uuid import uuid4

from app.core.config import get_settings

try:
    from minio import Minio
except ImportError:  # pragma: no cover - exercised only when dependency is missing locally.
    Minio = None


class StorageUnavailableError(RuntimeError):
    pass


def get_storage_client():
    if Minio is None:
        raise StorageUnavailableError("Install the minio package to use photo uploads")
    settings = get_settings()
    return Minio(
        settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=settings.MINIO_SECURE,
    )


def ensure_bucket() -> None:
    settings = get_settings()
    client = get_storage_client()
    if not client.bucket_exists(settings.MINIO_BUCKET):
        client.make_bucket(settings.MINIO_BUCKET)


def build_object_key(owner_id: int, filename: str) -> str:
    suffix = filename.rsplit(".", 1)[-1] if "." in filename else "bin"
    return f"users/{owner_id}/photos/{uuid4().hex}.{suffix}"


def upload_photo_object(object_key: str, file: BinaryIO, size: int, content_type: str) -> None:
    settings = get_settings()
    ensure_bucket()
    get_storage_client().put_object(
        settings.MINIO_BUCKET,
        object_key,
        file,
        length=size,
        content_type=content_type,
    )


def get_photo_url(object_key: str) -> str:
    settings = get_settings()
    return get_storage_client().presigned_get_object(
        settings.MINIO_BUCKET,
        object_key,
        expires=timedelta(minutes=15),
    )
