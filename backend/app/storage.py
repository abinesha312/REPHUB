"""Storage backend interface and implementations."""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import BinaryIO
import shutil


class StorageBackend(ABC):
    """Abstract storage backend interface."""
    
    @abstractmethod
    def save(self, file: BinaryIO, path: str) -> str:
        """Save a file and return its storage path."""
        pass
    
    @abstractmethod
    def load(self, path: str) -> bytes:
        """Load a file from storage."""
        pass
    
    @abstractmethod
    def delete(self, path: str) -> None:
        """Delete a file from storage."""
        pass
    
    @abstractmethod
    def exists(self, path: str) -> bool:
        """Check if a file exists."""
        pass


class LocalFileStorage(StorageBackend):
    """Local filesystem storage implementation."""
    
    def __init__(self, root_dir: str):
        self.root = Path(root_dir)
        self.root.mkdir(parents=True, exist_ok=True)
    
    def save(self, file: BinaryIO, path: str) -> str:
        """Save file to local storage."""
        full_path = self.root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(full_path, 'wb') as f:
            shutil.copyfileobj(file, f)
        
        return str(path)
    
    def load(self, path: str) -> bytes:
        """Load file from local storage."""
        full_path = self.root / path
        with open(full_path, 'rb') as f:
            return f.read()
    
    def delete(self, path: str) -> None:
        """Delete file from local storage."""
        full_path = self.root / path
        if full_path.exists():
            full_path.unlink()
    
    def exists(self, path: str) -> bool:
        """Check if file exists."""
        return (self.root / path).exists()
    
    def get_full_path(self, path: str) -> Path:
        """Get absolute filesystem path."""
        return self.root / path


# Factory function
def get_storage_backend(root_dir: str) -> StorageBackend:
    """Get storage backend instance."""
    return LocalFileStorage(root_dir)
