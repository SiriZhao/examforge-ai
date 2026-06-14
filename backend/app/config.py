from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

APP_VERSION = "0.3.1"


class Settings(BaseSettings):
    app_name: str = "ExamForge AI"
    app_version: str = APP_VERSION
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    upload_dir: Path = Path("uploads")
    output_dir: Path = Path("outputs")
    ocr_cache_dir: Path = Path("cache/ocr")

    model_config = SettingsConfigDict(env_file=".env", env_prefix="ERA_")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
