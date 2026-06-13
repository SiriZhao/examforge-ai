from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.schemas.review import ExamType, LLMConfig, LLMErrorInfo, ReviewReport, StudyGoal


@dataclass
class LLMCallStats:
    provider: str
    model: str
    base_url: str
    enabled: bool
    prompt_chars: int
    material_chars: int
    started_at: str
    elapsed_ms: int | None = None
    http_status: int | None = None
    error_code: str | None = None
    error_summary: str | None = None
    fallback_used: bool = False


class LLMProviderError(RuntimeError):
    def __init__(self, error: LLMErrorInfo, *, http_status: int | None = None) -> None:
        super().__init__(error.message)
        self.error = error
        self.http_status = http_status


class BaseLLMProvider(ABC):
    name: str
    display_name: str
    default_base_url: str
    default_model: str

    @abstractmethod
    def enhance_report(
        self,
        materials_text: str,
        safe_draft: ReviewReport,
        config: LLMConfig,
        *,
        course_name: str | None = None,
        file_texts: list[tuple[str, str]] | None = None,
        study_goal: StudyGoal = "balanced",
        exam_type: ExamType = "unknown",
    ) -> ReviewReport:
        raise NotImplementedError

    @abstractmethod
    def test_connection(self, config: LLMConfig) -> str:
        raise NotImplementedError
