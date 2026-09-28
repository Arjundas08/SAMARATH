"""
Application settings using pydantic-settings.
"""
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "SAMARATH"
    APP_ENV: str = "development"
    APP_PORT: int = 8000
    APP_HOST: str = "0.0.0.0"
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/samarath"
    SYNC_DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/samarath"

    # Security
    SECRET_KEY: str = "samarath_sih26027_production_secret_key_change_in_prod"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    # Demonstration parameters
    DEFAULT_CORRIDOR: str = "VKC"
    TZ: str = "Asia/Kolkata"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
