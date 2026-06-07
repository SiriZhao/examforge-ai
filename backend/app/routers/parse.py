import logging

from fastapi import APIRouter, HTTPException

from app.schemas.review import ParseRequest, ParseResponse
from app.services.file_parser import ParseError, parse_file
from app.services.ocr_service import OCRError
from app.services.upload_resolver import (
    UploadResolveError,
    UploadedFileNotFoundError,
    resolve_uploaded_file,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/parse", response_model=ParseResponse)
def parse_uploaded_files(request: ParseRequest) -> ParseResponse:
    if not request.files:
        raise HTTPException(status_code=400, detail="No files provided for parsing.")

    parsed_files = []
    for file_ref in request.files:
        try:
            logger.info("Parse started: file_ref=%s", file_ref)
            path = resolve_uploaded_file(file_ref)
            parsed_files.append(parse_file(path, request.ocr_config))
            logger.info("Parse completed: file_ref=%s", file_ref)
        except UploadedFileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except UploadResolveError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except (ParseError, OCRError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    return ParseResponse(
        files=parsed_files,
        message=f"已成功解析 {len(parsed_files)} 个文件。",
    )
