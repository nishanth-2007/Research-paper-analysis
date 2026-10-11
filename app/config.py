from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_NAME: str = "Research Paper Automation & Journal Readiness Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str = "sqlite:///./research_platform.db"
    DB_ECHO: bool = False

    # Security & Auth
    SECRET_KEY: str = "super-secret-production-key-change-in-production-12345678"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    ALLOWED_ORIGINS: List[str] = ["*"]

    # Storage
    STORAGE_BACKEND: str = "local"  # "local" or "s3"
    STORAGE_LOCAL_DIR: Path = Path("./storage")
    S3_BUCKET_NAME: Optional[str] = None
    S3_ENDPOINT_URL: Optional[str] = None
    S3_ACCESS_KEY: Optional[str] = None
    S3_SECRET_KEY: Optional[str] = None
    S3_REGION: str = "us-east-1"

    # Ingestion Constraints
    MAX_UPLOAD_SIZE_BYTES: int = 50 * 1024 * 1024  # 50 MB
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".docx"]

    # AI / LLM Evaluation Engine
    LLM_PROVIDER: str = "mock"  # "mock", "openai", "gemini", "anthropic"
    LLM_API_KEY: Optional[str] = None
    LLM_MODEL_NAME: str = "gpt-4o-mini"
    LLM_TEMPERATURE: float = 0.1
    LLM_TIMEOUT_SECONDS: int = 45

    # RAG / Vector Engine
    EMBEDDING_PROVIDER: str = "deterministic"  # "deterministic", "openai", "sentence_transformers"
    EMBEDDING_DIMENSION: int = 384
    VECTOR_TOP_K: int = 5

    # Background Workers
    ASYNC_PROCESSING_MODE: str = "threaded"  # "threaded" or "celery"
    REDIS_URL: Optional[str] = "redis://localhost:6379/0"


settings = Settings()

# Ensure local storage path exists
if settings.STORAGE_BACKEND == "local":
    settings.STORAGE_LOCAL_DIR.mkdir(parents=True, exist_ok=True)
