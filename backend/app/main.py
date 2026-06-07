from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import analyze, chat, download, export, generate_review, generate_review_jobs, llm, mock_exam, parse, upload
from app.utils.error_handlers import register_error_handlers
from app.utils.logging_config import configure_logging


def ensure_runtime_directories() -> None:
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    settings.output_dir.mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    ensure_runtime_directories()
    yield


configure_logging()
app = FastAPI(title=settings.app_name, lifespan=lifespan)
register_error_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, tags=["upload"])
app.include_router(parse.router, tags=["parse"])
app.include_router(generate_review.router, tags=["generate-review"])
app.include_router(generate_review_jobs.router, tags=["generate-review"])
app.include_router(llm.router)
app.include_router(chat.router, tags=["chat"])
app.include_router(mock_exam.router, tags=["mock-exam"])
app.include_router(download.router, tags=["download"])
app.include_router(analyze.router, prefix="/api/analyze", tags=["analyze"])
app.include_router(export.router, prefix="/api/export", tags=["export"])


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
