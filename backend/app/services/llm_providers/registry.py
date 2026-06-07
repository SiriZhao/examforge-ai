from app.services.llm_providers.base import BaseLLMProvider
from app.services.llm_providers.mock import MockLLMProvider
from app.services.llm_providers.openai_compatible import (
    CustomOpenAICompatibleLLMProvider,
    DeepSeekLLMProvider,
    OpenAICompatibleLLMProvider,
    QwenLLMProvider,
)

_PROVIDERS: dict[str, BaseLLMProvider] = {
    MockLLMProvider.name: MockLLMProvider(),
    OpenAICompatibleLLMProvider.name: OpenAICompatibleLLMProvider(),
    CustomOpenAICompatibleLLMProvider.name: CustomOpenAICompatibleLLMProvider(),
    DeepSeekLLMProvider.name: DeepSeekLLMProvider(),
    QwenLLMProvider.name: QwenLLMProvider(),
}


def get_llm_provider(name: str | None) -> BaseLLMProvider:
    provider_name = name or "deepseek"
    try:
        return _PROVIDERS[provider_name]
    except KeyError as exc:
        raise RuntimeError(f"不支持的大模型服务商：{provider_name}") from exc
