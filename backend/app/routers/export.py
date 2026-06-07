from fastapi import APIRouter, HTTPException

from app.config import settings
from app.schemas.review import ExportRequest, ExportResponse
from app.services.analyzer import analyze_content
from app.services.export_service import write_output
from app.services.file_parser import parse_file_to_text
from app.services.generator import generate_markdown_review

router = APIRouter()


@router.post("/", response_model=ExportResponse)
def export_review(request: ExportRequest) -> ExportResponse:
    if request.format != "markdown":
        raise HTTPException(status_code=400, detail="当前只支持 Markdown 导出。")

    matches = list(settings.upload_dir.glob(f"{request.file_id}.*"))
    if not matches:
        raise HTTPException(status_code=404, detail="上传文件不存在。")

    content = parse_file_to_text(matches[0])
    analysis = analyze_content(request.file_id, content, None)
    output = generate_markdown_review(analysis)
    output_path = write_output(settings.output_dir, request.file_id, output)
    return ExportResponse(file_id=request.file_id, output_path=f"/download/{output_path.name}")
