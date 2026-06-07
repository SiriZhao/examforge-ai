import json
import re
import time
from datetime import datetime

import httpx
from pydantic import ValidationError

from app.schemas.review import LLMConfig, LLMErrorInfo, ReviewReport
from app.services.llm_providers.base import BaseLLMProvider, LLMProviderError
from app.services.llm_service_prompt import (
    CONTEXT_TOO_LONG_MESSAGE,
    build_review_prompt,
)

MAX_PROMPT_CHARS = 28000


class OpenAICompatibleLLMProvider(BaseLLMProvider):
    name = "openai"
    display_name = "OpenAI"
    default_base_url = "https://api.openai.com/v1"
    default_model = "gpt-4o-mini"
    needs_v1_suffix = True

    def enhance_report(
        self,
        materials_text: str,
        rule_report: ReviewReport,
        config: LLMConfig,
    ) -> ReviewReport:
        endpoint, model = self.prepare_request(config)
        prompt = build_review_prompt(materials_text, rule_report)
        if len(prompt) > MAX_PROMPT_CHARS:
            raise self.error(
                "CONTEXT_TOO_LONG",
                "当前资料过长，系统已生成规则版报告。",
                CONTEXT_TOO_LONG_MESSAGE,
                config,
                model=model,
            )

        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "你是大学期末复习资料生成助手。只输出一个合法 JSON 对象，"
                        "不要输出 Markdown，不要输出解释。所有面向用户的字段必须使用简体中文。"
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        }
        content = self.post_chat_completions(endpoint, config.api_key or "", payload, timeout=90)
        try:
            data = extract_json_object(content)
            normalize_review_payload(data)
            return ReviewReport.model_validate(data)
        except (json.JSONDecodeError, KeyError, TypeError, ValidationError) as exc:
            raise self.error(
                "RESPONSE_PARSE_ERROR",
                "大模型返回内容无法解析为复习报告。",
                "请重试，或切换模型后再生成。系统已保留规则版报告。",
                config,
                model=model,
            ) from exc

    def test_connection(self, config: LLMConfig) -> str:
        endpoint, model = self.prepare_request(config)
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": "请只回复：连接成功"},
            ],
            "temperature": 0,
            "max_tokens": 20,
        }
        return self.post_chat_completions(endpoint, config.api_key or "", payload, timeout=20)

    def prepare_request(self, config: LLMConfig) -> tuple[str, str]:
        api_key = (config.api_key or "").strip()
        if not api_key:
            raise self.error(
                "CONFIG_MISSING",
                "大模型配置缺少 API Key。",
                "请在高级设置中填写 API Key，或关闭大模型增强使用规则模式。",
                config,
            )
        base_url = normalize_base_url(config.base_url or self.default_base_url, needs_v1=self.needs_v1_suffix)
        model = (config.model or self.default_model).strip()
        if not model:
            raise self.error(
                "CONFIG_MISSING",
                "大模型配置缺少模型名称。",
                self.model_suggestion(),
                config,
            )
        return f"{base_url}/chat/completions", model

    def post_chat_completions(
        self,
        endpoint: str,
        api_key: str,
        payload: dict,
        *,
        timeout: int,
    ) -> str:
        try:
            response = httpx.post(
                endpoint,
                json=payload,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                timeout=timeout,
            )
            if response.status_code >= 400:
                raise self.http_error(response, payload.get("model"))
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except LLMProviderError:
            raise
        except httpx.TimeoutException as exc:
            raise self.error(
                "TIMEOUT",
                "大模型请求超时。",
                "请稍后重试，或检查网络、代理和服务商状态。系统已保留规则版报告。",
                None,
                model=str(payload.get("model") or ""),
            ) from exc
        except httpx.NetworkError as exc:
            raise self.error(
                "NETWORK_ERROR",
                "无法连接到大模型服务。",
                "请检查 Base URL、网络连接、代理设置和服务商状态。",
                None,
                model=str(payload.get("model") or ""),
            ) from exc
        except (json.JSONDecodeError, KeyError, TypeError) as exc:
            raise self.error(
                "RESPONSE_PARSE_ERROR",
                "大模型服务返回格式不符合预期。",
                "请重试，或切换服务商和模型后再试。",
                None,
                model=str(payload.get("model") or ""),
            ) from exc
        except Exception as exc:
            raise self.error(
                "UNKNOWN_ERROR",
                "调用大模型时发生未知错误。",
                "请查看后端日志中的错误摘要，并检查服务商配置。",
                None,
                model=str(payload.get("model") or ""),
            ) from exc

    def http_error(self, response: httpx.Response, model: object) -> LLMProviderError:
        status = response.status_code
        message = safe_provider_message(response.text)
        if status in {401, 403}:
            code = "AUTH_FAILED"
            user_message = "认证失败。请确认 API Key 是否有效，或当前服务商是否要求不同的 Base URL。"
            suggestion = self.auth_suggestion()
        elif status == 404:
            code = "MODEL_NOT_FOUND"
            user_message = "大模型调用失败：模型名称可能不存在或当前账号无权限。"
            suggestion = self.model_suggestion()
        elif status == 429:
            code = "RATE_LIMITED"
            user_message = "大模型服务触发限流。"
            suggestion = "请稍后重试，或检查当前服务商的额度和并发限制。"
        elif status in {400, 413} and re.search(r"context|token|length|too long", message, re.I):
            code = "CONTEXT_TOO_LONG"
            user_message = "当前资料过长，系统已生成规则版报告。"
            suggestion = CONTEXT_TOO_LONG_MESSAGE
        else:
            code = "UNKNOWN_ERROR"
            user_message = f"大模型服务返回 HTTP {status}。"
            suggestion = f"请检查服务商控制台、模型名称和 Base URL。错误摘要：{message[:160]}"
        return self.error(
            code,
            user_message,
            suggestion,
            None,
            model=str(model or ""),
            http_status=status,
        )

    def error(
        self,
        code: str,
        message: str,
        suggestion: str,
        config: LLMConfig | None,
        *,
        model: str | None = None,
        http_status: int | None = None,
    ) -> LLMProviderError:
        error = LLMErrorInfo(
            code=code,  # type: ignore[arg-type]
            message=message,
            suggestion=suggestion,
            provider=self.display_name,
            model=model or ((config.model if config else None) or self.default_model),
            can_retry=code not in {"CONFIG_MISSING"},
            fallback_used=True,
        )
        return LLMProviderError(error, http_status=http_status)

    def model_suggestion(self) -> str:
        return "请检查模型名称，例如 deepseek-v4-flash、gpt-4o-mini 或 qwen-plus。"

    def auth_suggestion(self) -> str:
        return "请确认 API Key、Base URL 和账号权限是否匹配。"


class CustomOpenAICompatibleLLMProvider(OpenAICompatibleLLMProvider):
    name = "custom_openai_compatible"
    display_name = "OpenAI-compatible 自定义接口"
    default_base_url = ""
    default_model = ""

    def prepare_request(self, config: LLMConfig) -> tuple[str, str]:
        if not (config.base_url or "").strip():
            raise self.error(
                "CONFIG_MISSING",
                "自定义接口缺少 Base URL。",
                "请填写兼容 OpenAI Chat Completions 的接口地址。",
                config,
            )
        return super().prepare_request(config)


class DeepSeekLLMProvider(OpenAICompatibleLLMProvider):
    name = "deepseek"
    display_name = "DeepSeek"
    default_base_url = "https://api.deepseek.com"
    default_model = "deepseek-v4-flash"

    def model_suggestion(self) -> str:
        return "当前 DeepSeek 模型名称可能不可用。建议尝试 deepseek-v4-flash，或检查 DeepSeek 控制台当前支持的模型名称。"

    def auth_suggestion(self) -> str:
        return "如果你使用 DeepSeek，建议 Base URL 填写 https://api.deepseek.com，模型名称填写 deepseek-v4-flash。"


class QwenLLMProvider(OpenAICompatibleLLMProvider):
    name = "qwen"
    display_name = "通义千问 / Qwen"
    default_base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    default_model = "qwen-plus"


def normalize_base_url(base_url: str, *, needs_v1: bool = True) -> str:
    cleaned = (base_url or "").strip().rstrip("/")
    cleaned = re.sub(r"/chat/completions/?$", "", cleaned)
    if needs_v1 and not re.search(r"/v1$", cleaned):
        cleaned = f"{cleaned}/v1"
    return cleaned


def extract_json_object(content: str) -> dict:
    cleaned = content.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, re.DOTALL)
    if fenced:
        cleaned = fenced.group(1)
    else:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start >= 0 and end > start:
            cleaned = cleaned[start : end + 1]
    data = json.loads(cleaned)
    if not isinstance(data, dict):
        raise TypeError("LLM JSON root must be an object.")
    return data


def normalize_review_payload(data: dict) -> None:
    valid_types = {"选择题", "填空题", "判断题", "计算题", "简答题", "论述题", "未知"}
    type_aliases = {
        "choice": "选择题",
        "single_choice": "选择题",
        "multiple_choice": "选择题",
        "选择": "选择题",
        "填空": "填空题",
        "判断": "判断题",
        "计算": "计算题",
        "简答": "简答题",
        "论述": "论述题",
    }
    for chapter in data.get("chapters", []) or []:
        normalized_types = []
        for item in chapter.get("question_types", []) or []:
            text = str(item).strip()
            normalized_types.append(type_aliases.get(text, text if text in valid_types else "未知"))
        chapter["question_types"] = normalized_types
        chapter["importance"] = clamp_int(chapter.get("importance", 0), 0, 100)
        chapter["frequency"] = max(0, clamp_int(chapter.get("frequency", 0), 0, 100000))


def clamp_int(value: object, low: int, high: int) -> int:
    try:
        number = int(float(value))
    except (TypeError, ValueError):
        return low
    return max(low, min(high, number))


def safe_provider_message(text: str) -> str:
    if not text:
        return ""
    redacted = re.sub(r"Bearer\s+[A-Za-z0-9._-]+", "Bearer ***", text)
    redacted = re.sub(r"sk-[A-Za-z0-9_-]+", mask_api_key, redacted)
    return redacted[:300]


def mask_api_key(match: re.Match[str]) -> str:
    value = match.group(0)
    return f"{value[:3]}****{value[-4:]}" if len(value) > 8 else "***"

