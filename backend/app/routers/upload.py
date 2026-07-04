import logging
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import settings
from app.schemas.review import UploadedFileInfo, UploadResponse
from app.services.cloud_runtime import runtime_dir

router = APIRouter()
logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {".pptx", ".pdf", ".docx", ".md", ".png", ".jpg", ".jpeg", ".txt"}
BLOCKED_EXTENSIONS = {".exe", ".bat", ".ps1", ".sh", ".js", ".zip", ".rar", ".7z", ".cmd", ".msi"}


@router.post("/upload", response_model=UploadResponse)
@router.post("/api/upload", response_model=UploadResponse)
async def upload_files(files: list[UploadFile] = File(...)) -> UploadResponse:
    if not files:
        raise HTTPException(status_code=400, detail="No files received.")
    if len(files) > settings.max_files_per_request:
        raise HTTPException(
            status_code=413,
            detail=f"Too many files. Max files per request: {settings.max_files_per_request}.",
        )

    logger.info("Upload started: file_count=%s", len(files))
    validated_files: list[tuple[str, str, bytes]] = []

    for file in files:
        original_filename = Path(file.filename or "upload").name
        suffix = Path(original_filename).suffix.lower()

        if suffix in BLOCKED_EXTENSIONS or suffix not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {suffix or 'unknown'}.")

        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail=f"Uploaded file is empty: {original_filename}.")
        if len(content) > settings.max_upload_bytes:
            raise HTTPException(
                status_code=413,
                detail=f"File is too large: {original_filename}. Max file size: {settings.max_upload_mb}MB.",
            )

        validated_files.append((original_filename, suffix, content))

    uploaded_files: list[UploadedFileInfo] = []
    upload_dir = runtime_dir(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    for original_filename, suffix, content in validated_files:
        saved_filename = f"{uuid4().hex}{suffix}"
        saved_path = upload_dir / saved_filename
        saved_path.write_bytes(content)

        uploaded_files.append(
            UploadedFileInfo(
                original_filename=original_filename,
                saved_filename=saved_filename,
                file_type=suffix,
                file_size=len(content),
                saved_path=f"uploads/{saved_filename}",
            )
        )

    logger.info("Upload completed: file_count=%s", len(uploaded_files))
    return UploadResponse(files=uploaded_files, message=f"Uploaded {len(uploaded_files)} file(s).")
