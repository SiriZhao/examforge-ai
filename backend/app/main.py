from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routers import analyze, chat, download, export, generate_review, generate_review_jobs, llm, mock_exam, parse, upload
from app.services.cloud_runtime import (
    cleanup_runtime_files,
    ensure_runtime_directories,
    frontend_static_dir,
    is_ocr_available,
    is_storage_writable,
)
from app.utils.error_handlers import register_error_handlers
from app.utils.logging_config import configure_logging


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    ensure_runtime_directories()
    cleanup_runtime_files()
    yield


configure_logging()
app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)
register_error_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.normalized_cors_origins or ["http://localhost:5173", "http://127.0.0.1:5173"],
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
@app.get("/api/health")
def health_check() -> dict[str, str | bool]:
    return {
        "status": "ok",
        "version": settings.app_version,
        "mode": settings.app_mode,
        "app_mode": settings.app_mode,
        "llm_server_configured": settings.llm_server_configured,
        "llm_provider_configured": settings.llm_server_configured,
        "default_llm_model": settings.default_llm_model,
        "ocr_available": is_ocr_available(),
        "storage_writable": is_storage_writable(),
        "public_base_url": settings.public_base_url,
    }


static_dir = frontend_static_dir()
if (static_dir / "index.html").exists():
    assets_dir = static_dir / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")


@app.get("/{full_path:path}", include_in_schema=False)
def serve_frontend(full_path: str, request: Request) -> FileResponse:
    if full_path.startswith(("api/", "download/", "upload", "generate-review", "generate-review-jobs")):
        # Let FastAPI's 404 response handle unknown API-like routes instead of serving the SPA.
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Not found")
    index = static_dir / "index.html"
    if index.exists():
        return FileResponse(index)
    from fastapi import HTTPException

    raise HTTPException(status_code=404, detail="Frontend build not found. Run npm run build first.")

