import logging
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import settings
from app.schemas.review import UploadedFileInfo, UploadResponse

router = APIRouter()
logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {".pptx", ".pdf", ".docx", ".md", ".png", ".jpg", ".jpeg"}
MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024


@router.post("/upload", response_model=UploadResponse)
async def upload_files(files: list[UploadFile] = File(...)) -> UploadResponse:
    if not files:
        raise HTTPException(status_code=400, detail="没有收到上传文件。")

    logger.info("Upload started: file_count=%s", len(files))
    validated_files: list[tuple[str, str, bytes]] = []

    for file in files:
        original_filename = file.filename or ""
        suffix = Path(original_filename).suffix.lower()

        if suffix not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件类型：{suffix or '未知'}。",
            )

        content = await file.read()
        if not content:
            raise HTTPException(
                status_code=400,
                detail=f"上传文件为空：{original_filename}。",
            )
        if len(content) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"文件过大：{original_filename}。单个文件最大 50MB。",
            )

        validated_files.append((original_filename, suffix, content))

    uploaded_files: list[UploadedFileInfo] = []
    settings.upload_dir.mkdir(parents=True, exist_ok=True)

    for original_filename, suffix, content in validated_files:
        saved_filename = f"{uuid4().hex}{suffix}"
        saved_path = settings.upload_dir / saved_filename
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
    return UploadResponse(
        files=uploaded_files,
        message=f"已成功上传 {len(uploaded_files)} 个文件。",
    )
