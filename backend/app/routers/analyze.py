from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.config import settings
from app.schemas.review import AnalyzeRequest, ReviewReport
from app.services.analyzer import analyze_content
from app.services.file_parser import parse_file_to_text

router = APIRouter()


@router.post("/", response_model=ReviewReport)
def analyze_file(request: AnalyzeRequest) -> ReviewReport:
    matches = list(settings.upload_dir.glob(f"{request.file_id}.*"))
    if not matches:
        raise HTTPException(status_code=404, detail="上传文件不存在。")

    path: Path = matches[0]
    content = parse_file_to_text(path)
    return analyze_content(request.file_id, content, request.focus)
