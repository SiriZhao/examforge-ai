from app.services.llm_providers import get_llm_provider


def test_chinese_llm_providers_are_registered() -> None:
    assert get_llm_provider("deepseek").name == "deepseek"
    assert get_llm_provider("qwen").name == "qwen"
