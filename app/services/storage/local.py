import os
import uuid
from pathlib import Path
from typing import Optional
from app.config import settings
from app.services.storage.base import BaseStorageService


class LocalStorageService(BaseStorageService):
    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = (base_dir or settings.STORAGE_LOCAL_DIR).resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _safe_resolve(self, storage_path: str) -> Path:
        """Resolve path and verify it doesn't escape base_dir (protection against path traversal)."""
        target = (self.base_dir / storage_path).resolve()
        if not str(target).startswith(str(self.base_dir)):
            raise ValueError(f"Path traversal detected: {storage_path}")
        return target

    def save_file(self, content: bytes, filename: str, subfolder: str = "") -> str:
        # Sanitize filename
        safe_name = Path(filename).name
        unique_name = f"{uuid.uuid4().hex}_{safe_name}"

        dest_dir = (self.base_dir / subfolder).resolve()
        if not str(dest_dir).startswith(str(self.base_dir)):
            raise ValueError(f"Path traversal detected in subfolder: {subfolder}")

        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_file = dest_dir / unique_name

        dest_file.write_bytes(content)

        # Return relative storage path
        relative_path = dest_file.relative_to(self.base_dir)
        return str(relative_path).replace("\\", "/")

    def get_file(self, storage_path: str) -> bytes:
        target = self._safe_resolve(storage_path)
        if not target.exists():
            raise FileNotFoundError(f"Storage file not found: {storage_path}")
        return target.read_bytes()

    def delete_file(self, storage_path: str) -> bool:
        target = self._safe_resolve(storage_path)
        if target.exists():
            target.unlink()
            return True
        return False

    def file_exists(self, storage_path: str) -> bool:
        try:
            target = self._safe_resolve(storage_path)
            return target.exists()
        except ValueError:
            return False
