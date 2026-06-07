import httpx
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.review import LLMConfig
from app.services.llm_providers.openai_compatible import normalize_base_url
from app.services.llm_service import generate_review_summary
from app.services.review_planner import generate_review_report


MATERIALS = """
Chapter 1 Photosynthesis
Key points: chloroplast, light reaction, Calvin cycle.
1. Multiple choice: Which stage produces ATP?
"""


def llm_response_for(report) -> httpx.Response:
    return httpx.Response(
        200,
        json={
            "choices": [
                {
                    "message": {
                        "content": report.model_dump_json(ensure_ascii=False),
                    }
                }
            ]
        },
    )


def test_deepseek_default_model_is_v4_flash() -> None:
    config = LLMConfig(provider="deepseek", api_key="sk-test", enabled=True)
    report = generate_review_report(MATERIALS)
    result = generate_review_summary("", report, LLMConfig(enabled=False))

    assert result.llm_status == "disabled"
    assert normalize_base_url("https://api.deepseek.com") == "https://api.deepseek.com/v1"
    assert config.model is None


def test_llm_success_with_deepseek_v4_flash(monkeypatch) -> None:
    report = generate_review_report(MATERIALS)
    captured = {}

    def fake_post(url, json, headers, timeout):
        captured["url"] = url
        captured["model"] = json["model"]
        captured["authorization"] = headers["Authorization"]
        return llm_response_for(report)

    monkeypatch.setattr("app.services.llm_providers.openai_compatible.httpx.post", fake_post)
    result = generate_review_summary(
        MATERIALS,
        report,
        LLMConfig(provider="deepseek", api_key="sk-correct", enabled=True),
    )

    assert result.llm_status == "success"
    assert result.report_source == "llm_enhanced"
    assert result.fallback_used is False
    assert captured["url"] == "https://api.deepseek.com/v1/chat/completions"
    assert captured["model"] == "deepseek-v4-flash"
    assert captured["authorization"] == "Bearer sk-correct"


def test_manual_deepseek_chat_model_is_not_overwritten(monkeypatch) -> None:
    report = generate_review_report(MATERIALS)
    captured = {}

    def fake_post(url, json, headers, timeout):
        captured["model"] = json["model"]
        return llm_response_for(report)

    monkeypatch.setattr("app.services.llm_providers.openai_compatible.httpx.post", fake_post)
    result = generate_review_summary(
        MATERIALS,
        report,
        LLMConfig(provider="deepseek", model="deepseek-chat", api_key="sk-correct", enabled=True),
    )

    assert result.llm_status == "success"
    assert captured["model"] == "deepseek-chat"


def test_llm_model_not_found_falls_back(monkeypatch) -> None:
    report = generate_review_report(MATERIALS)

    def fake_post(url, json, headers, timeout):
        return httpx.Response(404, text='{"error":{"message":"model not found"}}')

    monkeypatch.setattr("app.services.llm_providers.openai_compatible.httpx.post", fake_post)
    result = generate_review_summary(
        MATERIALS,
        report,
        LLMConfig(provider="deepseek", model="wrong-model", api_key="sk-correct", enabled=True),
    )

    assert result.llm_status == "failed"
    assert result.report_source == "rule_based_with_llm_failed"
    assert result.fallback_used is True
    assert result.llm_error
    assert result.llm_error.code == "MODEL_NOT_FOUND"


def test_llm_timeout_falls_back(monkeypatch) -> None:
    report = generate_review_report(MATERIALS)

    def fake_post(url, json, headers, timeout):
        raise httpx.TimeoutException("timeout")

    monkeypatch.setattr("app.services.llm_providers.openai_compatible.httpx.post", fake_post)
    result = generate_review_summary(
        MATERIALS,
        report,
        LLMConfig(provider="deepseek", api_key="sk-correct", enabled=True),
    )

    assert result.llm_status == "failed"
    assert result.fallback_used is True
    assert result.llm_error
    assert result.llm_error.code == "TIMEOUT"


def test_context_too_long_falls_back(monkeypatch) -> None:
    report = generate_review_report(MATERIALS)
    monkeypatch.setattr(
        "app.services.llm_providers.openai_compatible.build_review_prompt",
        lambda materials, rule_report: "太长" * 20000,
    )
    result = generate_review_summary(
        MATERIALS,
        report,
        LLMConfig(provider="deepseek", api_key="sk-correct", enabled=True),
    )

    assert result.llm_status == "failed"
    assert result.fallback_used is True
    assert result.llm_error
    assert result.llm_error.code == "CONTEXT_TOO_LONG"


def test_llm_test_endpoint_success(monkeypatch) -> None:
    def fake_post(url, json, headers, timeout):
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": "连接成功"}}]},
        )

    monkeypatch.setattr("app.services.llm_providers.openai_compatible.httpx.post", fake_post)
    response = TestClient(app).post(
        "/api/llm/test",
        json={
            "provider": "deepseek",
            "api_key": "sk-correct",
            "base_url": "https://api.deepseek.com",
            "model": "deepseek-v4-flash",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["model"] == "deepseek-v4-flash"


def test_llm_test_endpoint_failure(monkeypatch) -> None:
    def fake_post(url, json, headers, timeout):
        return httpx.Response(401, text="unauthorized")

    monkeypatch.setattr("app.services.llm_providers.openai_compatible.httpx.post", fake_post)
    response = TestClient(app).post(
        "/api/llm/test",
        json={
            "provider": "deepseek",
            "api_key": "sk-wrong",
            "base_url": "https://api.deepseek.com",
            "model": "deepseek-v4-flash",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is False
    assert body["error"]["code"] == "AUTH_FAILED"

