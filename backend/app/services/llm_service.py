import logging
import time
from dataclasses import dataclass
from datetime import datetime

from app.schemas.review import (
    LLMConfig,
    LLMErrorInfo,
    LLMStatus,
    ReportSource,
    ReviewReport,
)
from app.services.llm_providers import get_llm_provider
from app.services.llm_providers.base import LLMProviderError
from app.services.llm_service_prompt import build_review_prompt
from app.services.review_planner import sanitize_report

logger = logging.getLogger(__name__)


@dataclass
class LLMEnhancementResult:
    report: ReviewReport
    report_source: ReportSource
    llm_status: LLMStatus
    fallback_used: bool
    llm_error: LLMErrorInfo | None


def generate_review_summary(
    parsed_materials: str,
    rule_report: ReviewReport,
    config: LLMConfig,
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
            report=sanitize_report(rule_report),
            report_source="rule_based",
            llm_status="disabled",
            fallback_used=False,
            llm_error=None,
        )

    try:
        provider = get_llm_provider(provider_name)
        model = config.model or provider.default_model
        base_url = config.base_url or provider.default_base_url
        prompt_chars = len(build_review_prompt(parsed_materials, rule_report))
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
        enhanced = provider.enhance_report(parsed_materials, rule_report, config)
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
            report_source="llm_enhanced",
            llm_status="success",
            fallback_used=False,
            llm_error=None,
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
        return LLMEnhancementResult(
            report=sanitize_report(rule_report),
            report_source="rule_based_with_llm_failed",
            llm_status="failed",
            fallback_used=True,
            llm_error=exc.error,
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
        return LLMEnhancementResult(
            report=sanitize_report(rule_report),
            report_source="rule_based_with_llm_failed",
            llm_status="failed",
            fallback_used=True,
            llm_error=error,
        )


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

