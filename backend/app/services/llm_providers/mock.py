from app.schemas.review import LLMConfig, ReviewReport
from app.services.llm_providers.base import BaseLLMProvider


class MockLLMProvider(BaseLLMProvider):
    name = "mock"
    display_name = "规则模式"
    default_base_url = ""
    default_model = ""

    def enhance_report(
        self,
        materials_text: str,
        rule_report: ReviewReport,
        config: LLMConfig,
    ) -> ReviewReport:
        return rule_report

    def test_connection(self, config: LLMConfig) -> str:
        return "连接成功"
