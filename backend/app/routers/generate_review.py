import logging
from collections.abc import Callable
from uuid import uuid4

from fastapi import APIRouter, HTTPException

from app.config import settings
from app.schemas.review import GenerateReviewRequest, GenerateReviewResponse
from app.services.export_service import ExportError, export_anki_csv, export_review_report
from app.services.file_parser import ParseError, parse_file
from app.services.generator import generate_markdown_review
from app.services.llm_service import generate_review_summary
from app.services.llm_service_prompt import MAX_LLM_INPUT_CHARS
from app.services.ocr_service import OCRError
from app.services.review_planner import generate_review_report
from app.services.upload_resolver import (
    UploadResolveError,
    UploadedFileNotFoundError,
    resolve_uploaded_file,
)

router = APIRouter()
logger = logging.getLogger(__name__)
ProgressCallback = Callable[[int, str], None]


@router.post("/generate-review", response_model=GenerateReviewResponse)
def generate_review(request: GenerateReviewRequest) -> GenerateReviewResponse:
    return build_generate_review_response(request)


def build_generate_review_response(
    request: GenerateReviewRequest,
    progress_callback: ProgressCallback | None = None,
) -> GenerateReviewResponse:
    if not request.files:
        raise HTTPException(status_code=400, detail="请至少上传一个文件后再生成复习资料。")

    parsed_files = []
    total_files = len(request.files)
    for file_index, file_ref in enumerate(request.files, start=1):
        try:
            if progress_callback:
                progress_callback(
                    10 + int(((file_index - 1) / max(total_files, 1)) * 45),
                    f"正在解析第 {file_index}/{total_files} 个文件。本地 OCR 处理扫描 PDF 可能较慢，请耐心等待。",
                )
            logger.info("Generate-review parse started: file_ref=%s", file_ref)
            path = resolve_uploaded_file(file_ref)

            def parse_progress(message: str, ratio: float | None) -> None:
                if not progress_callback:
                    return
                file_ratio = ratio or 0
                percent = 10 + int(
                    ((file_index - 1 + file_ratio) / max(total_files, 1)) * 55
                )
                progress_callback(min(65, percent), message)

            if progress_callback:
                parsed_files.append(parse_file(path, request.ocr_config, parse_progress))
            else:
                parsed_files.append(parse_file(path, request.ocr_config))
            logger.info("Generate-review parse completed: file_ref=%s", file_ref)
        except UploadedFileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except UploadResolveError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except (ParseError, OCRError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    combined_text = "\n\n".join(parsed.raw_text for parsed in parsed_files)
    file_texts = [(parsed.filename, parsed.raw_text) for parsed in parsed_files]
    report_title = request.course_name or request.title
    if progress_callback:
        progress_callback(68, "正在识别章节、题型和高频考点。")
    logger.info("Report generation started: file_count=%s", len(parsed_files))
    report = generate_review_report(combined_text, title=report_title, file_texts=file_texts)
    logger.info("Report generation completed: chapter_count=%s", len(report.chapters))

    if progress_callback:
        if request.llm_config.enabled:
            if len(combined_text) > MAX_LLM_INPUT_CHARS:
                progress_callback(
                    78,
                    "资料较长，正在自动压缩处理。系统会提取章节结构、高频考点和代表性内容后再进行大模型增强。",
                )
            else:
                progress_callback(78, "正在调用大模型增强复习资料，通常需要几十秒。")
        else:
            progress_callback(78, "正在生成规则版复习报告。")
    llm_result = generate_review_summary(combined_text, report, request.llm_config)
    report = llm_result.report

    if progress_callback:
        progress_callback(86, "正在生成 Markdown / Word / PDF 下载文件。")
    markdown = generate_markdown_review(report)
    output_basename = f"review-{uuid4().hex}"
    export_formats = request.export_formats or [request.export_format]
    if "md" not in export_formats:
        export_formats = ["md", *export_formats]

    download_links = {}
    anki_csv_download_path = None
    try:
        anki_path = export_anki_csv(report, settings.output_dir, output_basename)
        anki_csv_download_path = f"/download/{anki_path.name}"
        for export_index, export_format in enumerate(export_formats, start=1):
            if progress_callback:
                export_progress = 86 + int((export_index / max(len(export_formats), 1)) * 12)
                progress_callback(export_progress, f"正在导出 {export_format.upper()} 文件。")
            logger.info("Export started: format=%s", export_format)
            output_path = export_review_report(
                report=report,
                markdown=markdown,
                output_dir=settings.output_dir,
                basename=output_basename,
                export_format=export_format,
            )
            download_links[export_format] = f"/download/{output_path.name}"
            logger.info("Export completed: format=%s filename=%s", export_format, output_path.name)
    except ExportError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if progress_callback:
        progress_callback(100, "已完成。")
    return GenerateReviewResponse(
        review_report=report,
        markdown=markdown,
        download_path=download_links.get(request.export_format) or next(iter(download_links.values())),
        download_links=download_links,
        anki_csv_download_path=anki_csv_download_path,
        export_format=request.export_format,
        report_source=llm_result.report_source,
        llm_status=llm_result.llm_status,
        fallback_used=llm_result.fallback_used,
        llm_error=llm_result.llm_error,
        llm_context_strategy=llm_result.llm_context_strategy,
    )
