"""
GripWise Backend — Application configuration via environment variables.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from pathlib import Path


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).with_name(".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App
    ENVIRONMENT: str = "development"
    SECRET_KEY: str = "change-me-in-production-use-a-long-random-string"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24      # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ENABLE_PARTNER_PROGRAMMES: bool = False

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://gripwise:gripwise@localhost:5432/gripwise"
    DATABASE_URL_SYNC: str = "postgresql://gripwise:gripwise@localhost:5432/gripwise"

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # File storage
    IMAGE_DIR: str = "uploads"
    MAX_IMAGE_SIZE_MB: int = 10

    # AI
    INFERENCE_PROVIDER: str = "mock"   # "mock" | "cv_pipeline"


settings = Settings()
