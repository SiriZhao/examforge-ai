from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.config import settings

router = APIRouter()


@router.get("/download/{filename}")
def download_file(filename: str) -> FileResponse:
    safe_name = Path(filename).name
    if safe_name != filename:
        raise HTTPException(status_code=400, detail="下载文件名无效。")

    output_root = settings.output_dir.resolve()
    file_path = (settings.output_dir / safe_name).resolve()
    try:
        file_path.relative_to(output_root)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="下载路径无效。") from exc

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="下载文件不存在。")

    return FileResponse(path=file_path, filename=safe_name)
