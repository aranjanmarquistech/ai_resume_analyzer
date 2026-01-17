from __future__ import annotations

from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    RESUME_API_KEY: str = ""
    CORS_ORIGINS: str = "*"
    MAX_UPLOAD_BYTES: int = 10 * 1024 * 1024
    API_VERSION: str = "1.0.0"

    model_config = ConfigDict(env_file=".env")


settings = Settings()
