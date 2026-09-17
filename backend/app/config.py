"""Application configuration."""
import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/resumerepo"
    
    # Storage
    storage_root: str = "./storage"
    
    # Embedding
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimension: int = 384  # all-MiniLM-L6-v2 dimension
    
    # API
    api_prefix: str = "/api"
    
    # CORS
    cors_origins: list = ["http://localhost:5173", "http://localhost:3000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


def get_settings() -> Settings:
    """Get application settings singleton."""
    return Settings()
