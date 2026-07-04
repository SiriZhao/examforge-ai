from fastapi import APIRouter

from app.config import settings
from app.schemas.review import LLMErrorInfo, LLMTestRequest, LLMTestResponse
from app.services.llm_providers import get_llm_provider
from app.services.llm_providers.base import LLMProviderError

router = APIRouter(prefix="/api/llm", tags=["llm"])


@router.post("/test", response_model=LLMTestResponse)
def test_llm_connection(request: LLMTestRequest) -> LLMTestResponse:
    if not request.api_key and settings.llm_server_configured:
        request = request.model_copy(deep=True)
        request.provider = request.provider or settings.default_llm_provider
        request.model = request.model or settings.default_llm_model
        request.base_url = request.base_url or settings.default_llm_base_url
        request.api_key = settings.deepseek_api_key if request.provider == "deepseek" else settings.openai_api_key
    provider = get_llm_provider(request.provider)
    model = request.model or provider.default_model
    try:
        provider.test_connection(request)
        return LLMTestResponse(
            ok=True,
            provider=provider.display_name,
            model=model,
            message="大模型连接成功，可以重新生成复习资料。",
        )
    except LLMProviderError as exc:
        return LLMTestResponse(
            ok=False,
            provider=exc.error.provider or provider.display_name,
            model=exc.error.model or model,
            error=exc.error,
        )
    except Exception as exc:
        return LLMTestResponse(
            ok=False,
            provider=provider.display_name,
            model=model,
            error=LLMErrorInfo(
                code="UNKNOWN_ERROR",
                message="测试大模型连接时发生未知错误。",
                suggestion=f"请检查 Base URL、模型名称、网络和代理设置。错误摘要：{str(exc)[:120]}",
                provider=provider.display_name,
                model=model,
                can_retry=True,
                fallback_used=False,
            ),
        )
