from functools import lru_cache
import json
from pathlib import Path
from typing import Literal

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

APP_VERSION = "0.5.1"
AppMode = Literal["local_dev", "desktop", "cloud"]


class Settings(BaseSettings):
    app_name: str = "Campus AI Workspace"
    app_version: str = APP_VERSION
    app_mode: AppMode = Field(default="local_dev", validation_alias=AliasChoices("APP_MODE", "ERA_APP_MODE"))
    public_base_url: str = Field(default="", validation_alias=AliasChoices("PUBLIC_BASE_URL", "ERA_PUBLIC_BASE_URL"))
    cors_origins: list[str] = Field(default=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ], validation_alias=AliasChoices("CORS_ORIGINS", "ERA_CORS_ORIGINS"))
    max_upload_mb: int = Field(default=50, validation_alias=AliasChoices("MAX_UPLOAD_MB", "ERA_MAX_UPLOAD_MB"))
    max_files_per_request: int = Field(default=10, validation_alias=AliasChoices("MAX_FILES_PER_REQUEST", "ERA_MAX_FILES_PER_REQUEST"))
    request_timeout_seconds: int = Field(default=120, validation_alias=AliasChoices("REQUEST_TIMEOUT_SECONDS", "ERA_REQUEST_TIMEOUT_SECONDS"))
    job_timeout_seconds: int = Field(default=600, validation_alias=AliasChoices("JOB_TIMEOUT_SECONDS", "ERA_JOB_TIMEOUT_SECONDS"))
    temp_file_ttl_hours: int = Field(default=24, validation_alias=AliasChoices("TEMP_FILE_TTL_HOURS", "ERA_TEMP_FILE_TTL_HOURS"))
    storage_dir: Path = Field(default=Path("."), validation_alias=AliasChoices("STORAGE_DIR", "ERA_STORAGE_DIR"))
    upload_dir: Path = Field(default=Path("uploads"), validation_alias=AliasChoices("UPLOAD_DIR", "ERA_UPLOAD_DIR"))
    output_dir: Path = Field(default=Path("outputs"), validation_alias=AliasChoices("OUTPUT_DIR", "ERA_OUTPUT_DIR"))
    ocr_cache_dir: Path = Field(default=Path("cache/ocr"), validation_alias=AliasChoices("OCR_CACHE_DIR", "ERA_OCR_CACHE_DIR"))
    enable_local_ocr: bool = Field(default=True, validation_alias=AliasChoices("ENABLE_LOCAL_OCR", "ERA_ENABLE_LOCAL_OCR"))
    enable_rapidocr: bool = Field(default=True, validation_alias=AliasChoices("ENABLE_RAPIDOCR", "ERA_ENABLE_RAPIDOCR"))
    enable_tesseract: bool = Field(default=False, validation_alias=AliasChoices("ENABLE_TESSERACT", "ERA_ENABLE_TESSERACT"))
    enable_cloud_safe_mode: bool = Field(default=False, validation_alias=AliasChoices("ENABLE_CLOUD_SAFE_MODE", "ERA_ENABLE_CLOUD_SAFE_MODE"))
    default_llm_provider: str = Field(default="deepseek", validation_alias=AliasChoices("DEFAULT_LLM_PROVIDER", "ERA_DEFAULT_LLM_PROVIDER"))
    default_llm_model: str = Field(default="deepseek-v4-flash", validation_alias=AliasChoices("DEFAULT_LLM_MODEL", "ERA_DEFAULT_LLM_MODEL"))
    default_llm_base_url: str = Field(default="https://api.deepseek.com", validation_alias=AliasChoices("DEFAULT_LLM_BASE_URL", "ERA_DEFAULT_LLM_BASE_URL"))
    deepseek_api_key: str = Field(default="", validation_alias=AliasChoices("DEEPSEEK_API_KEY", "ERA_DEEPSEEK_API_KEY"))
    openai_api_key: str = Field(default="", validation_alias=AliasChoices("OPENAI_API_KEY", "ERA_OPENAI_API_KEY"))
    environment: str = Field(default="development", validation_alias=AliasChoices("ENVIRONMENT"))
    database_url: str = Field(default="sqlite:///./workspace.db", validation_alias=AliasChoices("DATABASE_URL"))
    redis_url: str = Field(default="", validation_alias=AliasChoices("REDIS_URL"))
    enable_python_tool: bool = Field(default=False, validation_alias=AliasChoices("ENABLE_PYTHON_TOOL"))
    free_daily_messages: int = Field(default=20, validation_alias=AliasChoices("FREE_DAILY_MESSAGES"))
    llm_context_budget_chars: int = Field(default=120000, validation_alias=AliasChoices("LLM_CONTEXT_BUDGET_CHARS", "ERA_LLM_CONTEXT_BUDGET_CHARS"))
    llm_chunk_chars: int = Field(default=18000, validation_alias=AliasChoices("LLM_CHUNK_CHARS", "ERA_LLM_CHUNK_CHARS"))
    llm_chunk_overlap_chars: int = Field(default=1200, validation_alias=AliasChoices("LLM_CHUNK_OVERLAP_CHARS", "ERA_LLM_CHUNK_OVERLAP_CHARS"))
    llm_max_chunks_per_round: int = Field(default=8, validation_alias=AliasChoices("LLM_MAX_CHUNKS_PER_ROUND", "ERA_LLM_MAX_CHUNKS_PER_ROUND"))
    llm_max_repair_calls: int = Field(default=1, validation_alias=AliasChoices("LLM_MAX_REPAIR_CALLS", "ERA_LLM_MAX_REPAIR_CALLS"))
    llm_enable_chunk_summary: bool = Field(default=True, validation_alias=AliasChoices("LLM_ENABLE_CHUNK_SUMMARY", "ERA_LLM_ENABLE_CHUNK_SUMMARY"))
    llm_enable_final_synthesis: bool = Field(default=True, validation_alias=AliasChoices("LLM_ENABLE_FINAL_SYNTHESIS", "ERA_LLM_ENABLE_FINAL_SYNTHESIS"))

    model_config = SettingsConfigDict(env_file=".env")

    @property
    def max_upload_bytes(self) -> int:
        return max(1, self.max_upload_mb) * 1024 * 1024

    @property
    def llm_server_configured(self) -> bool:
        return bool(self.deepseek_api_key or self.openai_api_key)

    @property
    def normalized_cors_origins(self) -> list[str]:
        raw = self.cors_origins
        if isinstance(raw, str):
            text = raw.strip()
            if not text:
                return []
            try:
                parsed = json.loads(text)
                if isinstance(parsed, list):
                    return [str(item).strip() for item in parsed if str(item).strip()]
            except json.JSONDecodeError:
                return [item.strip() for item in text.split(",") if item.strip()]
        return raw


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

