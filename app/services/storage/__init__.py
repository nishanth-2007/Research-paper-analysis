from app.config import settings
from app.services.storage.base import BaseStorageService
from app.services.storage.local import LocalStorageService


def get_storage_service() -> BaseStorageService:
    # Future expansion: S3StorageService when settings.STORAGE_BACKEND == "s3"
    return LocalStorageService()


__all__ = ["BaseStorageService", "LocalStorageService", "get_storage_service"]
