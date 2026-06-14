import logging
from collections.abc import Callable
from fastapi import APIRouter, HTTPException

from app.config import settings
from app.schemas.review import (
    GenerateReviewRequest,
    GenerateReviewResponse,
    GenerationSummary,
    ReoptimizeReviewRequest,
    ReoptimizeReviewResponse,
)
from app.services.export_service import (
    ExportError,
    anki_download_filename,
    export_anki_csv,
    export_review_report,
    report_download_filename,
)
from app.services.file_parser import ParseError, parse_file
from app.services.generator import generate_markdown_review
from app.services.llm_service import generate_review_summary
from app.services.llm_service_prompt import MAX_LLM_INPUT_CHARS
from app.services.llm_quality import validate_report_quality
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


@router.post("/review/reoptimize", response_model=ReoptimizeReviewResponse)
@router.post("/api/review/reoptimize", response_model=ReoptimizeReviewResponse)
def reoptimize_review(request: ReoptimizeReviewRequest) -> ReoptimizeReviewResponse:
    original = request.current_report
    evidence_text = request.evidence_text or original.markdown or generate_markdown_review(original)
    optimized = original.model_copy(deep=True)
    optimized.study_goal = request.original_study_goal
    optimized.exam_type = request.original_exam_type
    apply_optimization_goal(optimized, request.optimization_goal)

    if request.llm_config.enabled:
        llm_result = generate_review_summary(
            evidence_text,
            optimized,
            request.llm_config,
            course_name=optimized.title,
            file_texts=[("current_report.md", evidence_text)],
            study_goal=request.original_study_goal,
            exam_type=request.original_exam_type,
        )
        candidate = llm_result.report
    else:
        candidate = optimized

    quality = validate_report_quality(
        candidate,
        evidence_text,
        study_goal=request.original_study_goal,
        exam_type=request.original_exam_type,
    )
    candidate.quality = quality.to_model()
    if quality.quality_score < 50:
        original_quality = validate_report_quality(
            original,
            evidence_text,
            study_goal=request.original_study_goal,
            exam_type=request.original_exam_type,
        ).to_model()
        original.quality = original_quality
        return ReoptimizeReviewResponse(
            review_report=original,
            markdown=generate_markdown_review(original),
            optimized=False,
            message="优化结果质量不足，已保留原报告。",
            quality=original_quality,
        )

    candidate.markdown = generate_markdown_review(candidate, prefer_existing=False)
    return ReoptimizeReviewResponse(
        review_report=candidate,
        markdown=candidate.markdown,
        optimized=True,
        message="已基于当前报告完成再优化，未重新 OCR 或重新解析文件。",
        quality=quality.to_model(),
    )


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
                percent = 10 + int(((file_index - 1 + file_ratio) / max(total_files, 1)) * 55)
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
        progress_callback(68, "正在构建本地安全底稿：提取材料结构、题干线索、关键词和高频考点。")
    logger.info("Safe draft generation started: file_count=%s", len(parsed_files))
    safe_draft = generate_review_report(
        combined_text,
        title=report_title,
        file_texts=file_texts,
        study_goal=request.study_goal,
        exam_type=request.exam_type,
    )
    logger.info("Safe draft generation completed: chapter_count=%s", len(safe_draft.chapters))

    if progress_callback:
        if request.llm_config.enabled:
            if len(combined_text) > MAX_LLM_INPUT_CHARS:
                progress_callback(
                    78,
                    "资料较长，正在进行分块理解与全局重组。系统会先提取题干、考点、定义、公式和 Anki 候选，再进行 AI 深度整理。",
                )
            else:
                progress_callback(78, "正在调用大模型进行 AI 深度整理，通常需要几十秒。")
        else:
            progress_callback(78, "正在生成本地安全底稿。")

    llm_result = generate_review_summary(
        combined_text,
        safe_draft,
        request.llm_config,
        course_name=report_title,
        file_texts=file_texts,
        study_goal=request.study_goal,
        exam_type=request.exam_type,
    )
    report = llm_result.report
    report.study_goal = request.study_goal
    report.exam_type = request.exam_type
    quality = validate_report_quality(
        report,
        combined_text,
        study_goal=request.study_goal,
        exam_type=request.exam_type,
        file_count=len(parsed_files),
    )
    report.quality = quality.to_model()

    if progress_callback:
        progress_callback(86, "正在生成 Markdown / Word / PDF 下载文件。")
    markdown = generate_markdown_review(report)
    export_formats = request.export_formats or [request.export_format]
    if "md" not in export_formats:
        export_formats = ["md", *export_formats]

    download_links = {}
    anki_csv_download_path = None
    try:
        anki_path = export_anki_csv(report, settings.output_dir, anki_download_filename(report_title))
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
                basename=report_download_filename(report_title, export_format).rsplit(".", 1)[0],
                export_format=export_format,
            )
            download_links[export_format] = f"/download/{output_path.name}"
            logger.info("Export completed: format=%s filename=%s", export_format, output_path.name)
    except ExportError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if progress_callback:
        progress_callback(100, "已完成。")
    generation_summary = build_generation_summary(parsed_files, report, llm_result)
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
        generation_summary=generation_summary,
    )


def build_generation_summary(parsed_files, report, llm_result) -> GenerationSummary:
    pages = [page for parsed in parsed_files for page in parsed.pages]
    pages_text = [page for page in pages if page.source == "text_extract" and page.text.strip()]
    pages_ocr = [page for page in pages if page.source == "ocr_fallback" and page.text.strip()]
    pages_skipped = [page for page in pages if page.source == "ocr_fallback" and not page.text.strip()]
    cache_hits = sum(1 for parsed in parsed_files if getattr(parsed, "ocr_cache_used", False))
    notes: list[str] = []
    for parsed in parsed_files:
        notes.extend(getattr(parsed, "warnings", []) or [])
    if pages_text and not pages_ocr:
        notes.append("已检测到文字版 PDF 或可直接提取文本的材料，跳过不必要 OCR。")
    if llm_result.fallback_used:
        notes.append("AI 深度整理未完全成功，已保留本地安全底稿。")
    return GenerationSummary(
        files_processed=len(parsed_files),
        pages_total=len(pages),
        pages_text_extracted=len(pages_text),
        pages_ocr_processed=len(pages_ocr),
        pages_ocr_skipped=len(pages_skipped),
        ocr_cache_hits=cache_hits,
        evidence_chunks=max(1, sum(max(1, len(parsed.raw_text) // 1800) for parsed in parsed_files)) if parsed_files else 0,
        detected_study_units=len(report.study_units) or len(report.chapters),
        detected_question_types=len(report.question_types),
        mock_questions_count=len(report.mock_exam.questions),
        anki_cards_count=len(report.anki_cards),
        llm_calls=1 if llm_result.llm_status == "success" else 0,
        fallback_used=llm_result.fallback_used,
        final_report_source=llm_result.report_source,
        notes=notes[:12],
    )


def apply_optimization_goal(report, optimization_goal: str) -> None:
    report.overview = {**report.overview, "reoptimized_for": optimization_goal}
    if optimization_goal == "concise":
        report.low_priority = (report.low_priority or []) + ["已压缩低频背景内容，优先保留高频考点、题型和冲刺清单。"]
        report.review_order = report.review_order[:6]
    elif optimization_goal in {"memorization", "anki"}:
        report.anki_cards = dedupe_anki_cards(report.anki_cards)
        for card in report.anki_cards:
            card.priority = max(card.priority, 75)
            card.card_type = card.card_type or "definition"
    elif optimization_goal in {"practice", "exam_like"}:
        for question in report.mock_exam.questions:
            question.source_hint = question.source_hint or "来自当前报告中的考点和题型线索"
            question.related_topic = question.related_topic or question.concept or question.chapter
    elif optimization_goal == "sprint":
        report.sprint_checklist = report.sprint_checklist[:12] or ["先复习最高优先级专题", "完成模拟题并核对答案", "用 Anki 复盘易错点"]
    report.markdown = generate_markdown_review(report, prefer_existing=False)


def dedupe_anki_cards(cards):
    seen: set[str] = set()
    deduped = []
    for card in cards:
        key = card.front.strip()
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(card)
    return deduped
