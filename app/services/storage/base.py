from abc import ABC, abstractmethod


class BaseStorageService(ABC):
    @abstractmethod
    def save_file(self, content: bytes, filename: str, subfolder: str = "") -> str:
        """Saves content and returns a persistent storage path or key."""
        pass

    @abstractmethod
    def get_file(self, storage_path: str) -> bytes:
        """Retrieves raw content from the given storage path."""
        pass

    @abstractmethod
    def delete_file(self, storage_path: str) -> bool:
        """Deletes file at the given storage path."""
        pass

    @abstractmethod
    def file_exists(self, storage_path: str) -> bool:
        """Checks if file exists at the given storage path."""
        pass
