import logging
import time
from dataclasses import dataclass
from datetime import datetime

from app.schemas.review import (
    LLMContextStrategy,
    LLMConfig,
    LLMErrorInfo,
    LLMStatus,
    ReportSource,
    ReviewReport,
    StudyGoal,
    ExamType,
    DetailLevel,
    OutputStyle,
)
from app.services.llm_providers import get_llm_provider
from app.services.llm_providers.base import LLMProviderError
from app.services.review_planner import sanitize_report

logger = logging.getLogger(__name__)


@dataclass
class LLMEnhancementResult:
    report: ReviewReport
    report_source: ReportSource
    llm_status: LLMStatus
    fallback_used: bool
    llm_error: LLMErrorInfo | None
    llm_context_strategy: LLMContextStrategy


def generate_review_summary(
    parsed_materials: str,
    safe_draft: ReviewReport,
    config: LLMConfig,
    *,
    course_name: str | None = None,
    file_texts: list[tuple[str, str]] | None = None,
    study_goal: StudyGoal = "balanced",
    exam_type: ExamType = "unknown",
    detail_level: DetailLevel = "detailed",
    output_style: OutputStyle = "teaching_assistant",
) -> LLMEnhancementResult:
    provider_name = config.provider or "deepseek"
    enabled = bool(config.enabled)
    material_chars = len(parsed_materials)
    prompt_chars = 0

    if not enabled:
        log_llm_event(
            provider=provider_name,
            model=config.model,
            base_url=config.base_url,
            enabled=False,
            prompt_chars=0,
            material_chars=material_chars,
            fallback_used=False,
        )
        return LLMEnhancementResult(
            report=sanitize_report(safe_draft),
            report_source="rule_based",
            llm_status="disabled",
            fallback_used=False,
            llm_error=None,
            llm_context_strategy="disabled",
        )

    try:
        provider = get_llm_provider(provider_name)
        model = config.model or provider.default_model
        base_url = config.base_url or provider.default_base_url
        prompt_chars = min(len(parsed_materials), 30000)
        started = time.perf_counter()
        log_llm_event(
            provider=provider.display_name,
            model=model,
            base_url=base_url,
            enabled=True,
            prompt_chars=prompt_chars,
            material_chars=material_chars,
            fallback_used=False,
            request_started_at=datetime.now().isoformat(timespec="seconds"),
        )
        enhanced = provider.enhance_report(
            parsed_materials,
            safe_draft,
            config,
            course_name=course_name,
            file_texts=file_texts,
            study_goal=study_goal,
            exam_type=exam_type,
            detail_level=detail_level,
            output_style=output_style,
        )
        context_strategy = getattr(provider, "last_context_strategy", "direct")
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        log_llm_event(
            provider=provider.display_name,
            model=model,
            base_url=base_url,
            enabled=True,
            prompt_chars=prompt_chars,
            material_chars=material_chars,
            elapsed_ms=elapsed_ms,
            http_status=200,
            fallback_used=False,
        )
        return LLMEnhancementResult(
            report=sanitize_report(enhanced),
            report_source="llm_markdown_fallback" if enhanced.raw_markdown_fallback else "llm_enhanced",
            llm_status="success",
            fallback_used=False,
            llm_error=None,
            llm_context_strategy=context_strategy,
        )
    except LLMProviderError as exc:
        provider_label = exc.error.provider or provider_name
        log_llm_event(
            provider=provider_label,
            model=exc.error.model or config.model,
            base_url=config.base_url,
            enabled=True,
            prompt_chars=prompt_chars,
            material_chars=material_chars,
            http_status=exc.http_status,
            error_code=exc.error.code,
            error_summary=exc.error.message,
            fallback_used=True,
        )
        outline_report = try_improve_safe_draft_outline(
            parsed_materials,
            safe_draft,
            config,
            provider_name=provider_name,
            error_code=exc.error.code,
            course_name=course_name,
            file_texts=file_texts,
            study_goal=study_goal,
            exam_type=exam_type,
            detail_level=detail_level,
            output_style=output_style,
        )
        if outline_report is not None:
            return LLMEnhancementResult(
                report=outline_report,
                report_source="local_safe_draft_with_ai_outline",
                llm_status="failed",
                fallback_used=True,
                llm_error=exc.error,
                llm_context_strategy="failed",
            )
        return LLMEnhancementResult(
            report=sanitize_report(safe_draft),
            report_source="rule_based_with_llm_failed",
            llm_status="failed",
            fallback_used=True,
            llm_error=exc.error,
            llm_context_strategy="failed",
        )
    except Exception as exc:
        provider = get_llm_provider(provider_name)
        error = LLMErrorInfo(
            code="UNKNOWN_ERROR",
            message="调用大模型时发生未知错误。",
            suggestion="请查看后端日志中的错误摘要，并检查服务商配置、网络和模型名称。",
            provider=provider.display_name,
            model=config.model or provider.default_model,
            can_retry=True,
            fallback_used=True,
        )
        log_llm_event(
            provider=provider.display_name,
            model=error.model,
            base_url=config.base_url or provider.default_base_url,
            enabled=True,
            prompt_chars=prompt_chars,
            material_chars=material_chars,
            error_code=error.code,
            error_summary=str(exc)[:200],
            fallback_used=True,
        )
        outline_report = try_improve_safe_draft_outline(
            parsed_materials,
            safe_draft,
            config,
            provider_name=provider_name,
            error_code=error.code,
            course_name=course_name,
            file_texts=file_texts,
            study_goal=study_goal,
            exam_type=exam_type,
            detail_level=detail_level,
            output_style=output_style,
        )
        if outline_report is not None:
            return LLMEnhancementResult(
                report=outline_report,
                report_source="local_safe_draft_with_ai_outline",
                llm_status="failed",
                fallback_used=True,
                llm_error=error,
                llm_context_strategy="failed",
            )
        return LLMEnhancementResult(
            report=sanitize_report(safe_draft),
            report_source="rule_based_with_llm_failed",
            llm_status="failed",
            fallback_used=True,
            llm_error=error,
            llm_context_strategy="failed",
        )


def try_improve_safe_draft_outline(
    parsed_materials: str,
    safe_draft: ReviewReport,
    config: LLMConfig,
    *,
    provider_name: str,
    error_code: str,
    course_name: str | None,
    file_texts: list[tuple[str, str]] | None,
    study_goal: StudyGoal,
    exam_type: ExamType,
    detail_level: DetailLevel = "detailed",
    output_style: OutputStyle = "teaching_assistant",
) -> ReviewReport | None:
    if error_code in {"CONFIG_MISSING", "AUTH_FAILED"}:
        return None
    try:
        provider = get_llm_provider(provider_name)
        improve = getattr(provider, "improve_safe_draft_outline", None)
        if improve is None:
            return None
        improved = improve(
            parsed_materials,
            safe_draft,
            config,
            course_name=course_name,
            file_texts=file_texts,
            study_goal=study_goal,
            exam_type=exam_type,
            detail_level=detail_level,
            output_style=output_style,
        )
        logger.info("LLM outline naming fallback succeeded.")
        return sanitize_report(improved)
    except Exception as exc:
        logger.info("LLM outline naming fallback skipped: %s", str(exc)[:200])
        return None


def log_llm_event(
    *,
    provider: str,
    model: str | None,
    base_url: str | None,
    enabled: bool,
    prompt_chars: int,
    material_chars: int,
    fallback_used: bool,
    request_started_at: str | None = None,
    elapsed_ms: int | None = None,
    http_status: int | None = None,
    error_code: str | None = None,
    error_summary: str | None = None,
) -> None:
    logger.info(
        "LLM event: provider=%s model=%s base_url=%s enabled=%s prompt_chars=%s "
        "material_chars=%s request_started_at=%s elapsed_ms=%s http_status=%s "
        "error_code=%s error_summary=%s fallback_used=%s",
        provider,
        model,
        base_url,
        enabled,
        prompt_chars,
        material_chars,
        request_started_at,
        elapsed_ms,
        http_status,
        error_code,
        error_summary,
        fallback_used,
    )
