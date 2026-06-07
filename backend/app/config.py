from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Exam Review Agent"
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    upload_dir: Path = Path("uploads")
    output_dir: Path = Path("outputs")

    model_config = SettingsConfigDict(env_file=".env", env_prefix="ERA_")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
