from app.schemas.review import ExamType, LLMConfig, ReviewReport, StudyGoal
from app.services.llm_providers.base import BaseLLMProvider


class MockLLMProvider(BaseLLMProvider):
    name = "mock"
    display_name = "本地整理模式"
    default_base_url = ""
    default_model = ""

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
        safe_draft.study_goal = study_goal
        safe_draft.exam_type = exam_type
        return safe_draft

    def test_connection(self, config: LLMConfig) -> str:
        return "连接成功"
