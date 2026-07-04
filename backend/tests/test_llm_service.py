import httpx
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.review import LLMConfig
from app.services.llm_providers.openai_compatible import normalize_base_url
from app.services.llm_service_prompt import (
    MAX_CHUNK_CHARS,
    MAX_LLM_INPUT_CHARS,
    build_review_prompt,
    prepare_llm_context,
    split_material_chunks,
)
from app.services.generator import generate_markdown_review
from app.services.llm_quality import validate_report_quality
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


def ai_report_json() -> str:
    return """
{
  "title": "概率论期末复习资料包",
  "summary": "本资料包围绕随机变量、概率分布、参数估计和假设检验进行重组，优先练习计算与统计推断题。",
  "overview": {
    "exam_strategy": "先掌握分布与随机变量，再练参数估计和假设检验。",
    "material_summary": "材料包含概率分布、抽样分布、估计与检验。",
    "priority_advice": "优先复习同时出现在课件和题干中的专题。"
  },
  "study_units": [
    {
      "name": "概率分布与随机变量",
      "reason": "材料多次出现二项分布、正态分布和随机变量函数。",
      "priority": 92,
      "must_know": ["分布函数与密度函数", "常见离散与连续分布"],
      "key_points": ["二项分布", "正态分布", "期望与方差"],
      "formulas_or_methods": ["E(X)", "Var(X)"],
      "common_exam_angles": ["分布识别与概率计算"],
      "pitfalls": ["把概率密度当概率"],
      "how_to_review": "先背常见分布形式，再做概率计算题。"
    },
    {
      "name": "参数估计与区间估计",
      "reason": "题干经常要求估计均值和置信区间。",
      "priority": 86,
      "must_know": ["点估计", "置信区间"],
      "key_points": ["样本均值", "置信水平"],
      "formulas_or_methods": ["均值区间估计公式"],
      "common_exam_angles": ["套用公式计算区间"],
      "pitfalls": ["混淆标准差和标准误"],
      "how_to_review": "整理公式适用条件并练 2 道计算题。"
    },
    {
      "name": "假设检验的解题套路",
      "reason": "材料强调原假设、备择假设和拒绝域。",
      "priority": 88,
      "must_know": ["原假设与备择假设", "显著性水平"],
      "key_points": ["检验统计量", "p 值"],
      "formulas_or_methods": ["Z 检验", "t 检验"],
      "common_exam_angles": ["给定样本判断是否拒绝原假设"],
      "pitfalls": ["把不拒绝误写成接受"],
      "how_to_review": "按五步法练习完整书写。"
    }
  ],
  "question_types": [
    {
      "name": "概念辨析题",
      "evidence": "材料反复区分分布函数、密度函数和概率。",
      "features": ["要求解释概念差异", "常配合判断或简答"],
      "related_topics": ["概率分布与随机变量"],
      "answer_strategy": "先给定义，再说明区别和适用场景。",
      "sample_questions": ["说明概率密度函数与概率的区别。"]
    },
    {
      "name": "公式套用计算题",
      "evidence": "题干包含均值、方差、置信区间等计算线索。",
      "features": ["给定参数", "要求代入公式"],
      "related_topics": ["参数估计与区间估计"],
      "answer_strategy": "写出公式、代入数据、保留计算过程。",
      "sample_questions": ["已知样本均值和方差，计算均值置信区间。"]
    },
    {
      "name": "条件概率建模题",
      "evidence": "材料出现条件概率、独立性和贝叶斯公式。",
      "features": ["需要先建立事件关系"],
      "related_topics": ["概率分布与随机变量"],
      "answer_strategy": "先定义事件，再写条件概率公式。",
      "sample_questions": ["根据检测结果计算后验概率。"]
    },
    {
      "name": "统计推断分析题",
      "evidence": "往年题要求解释检验结论。",
      "features": ["需要解释结论含义"],
      "related_topics": ["假设检验的解题套路"],
      "answer_strategy": "按假设、统计量、拒绝域、结论四步写。",
      "sample_questions": ["判断新工艺是否显著提高均值。"]
    }
  ],
  "past_exam_analysis": {
    "detected_files": [],
    "high_frequency_topics": [
      {"topic": "置信区间", "chapter": "参数估计与区间估计", "frequency": 3, "question_types": ["公式套用计算题"], "keywords": ["置信水平"]}
    ],
    "summary": "题目线索显示计算题和统计推断分析题优先级较高。"
  },
  "review_order": [
    {"chapter": "概率分布与随机变量", "importance": 92, "reason": "基础且反复出现"},
    {"chapter": "假设检验的解题套路", "importance": 88, "reason": "题目综合性较强"},
    {"chapter": "参数估计与区间估计", "importance": 86, "reason": "公式计算高频"}
  ],
  "sprint_plans": [
    {"days": 1, "title": "1 天冲刺计划", "schedule": ["上午复习分布公式", "下午练估计和检验", "晚上背 Anki"]},
    {"days": 3, "title": "3 天复习计划", "schedule": ["第 1 天分布", "第 2 天估计", "第 3 天检验"]},
    {"days": 7, "title": "7 天复习计划", "schedule": ["前 3 天打基础", "中 2 天刷题", "后 2 天模拟"]}
  ],
  "mock_exam": {
    "title": "概率论模拟卷",
    "questions": [
      {"question_type": "概念辨析题", "difficulty": "基础", "question": "说明概率密度函数与概率的区别。", "answer": "密度函数描述连续变量分布，单点概率为 0，区间积分才是概率。", "explanation": "考查连续型随机变量。", "chapter": "概率分布与随机变量", "concept": "密度函数"},
      {"question_type": "公式套用计算题", "difficulty": "中等", "question": "给定样本均值和标准误，计算 95% 置信区间。", "answer": "按均值 ± 临界值 × 标准误计算。", "explanation": "考查区间估计公式。", "chapter": "参数估计与区间估计", "concept": "置信区间"},
      {"question_type": "统计推断分析题", "difficulty": "提高", "question": "给定检验统计量和显著性水平，判断是否拒绝原假设。", "answer": "比较统计量和拒绝域，若落入拒绝域则拒绝原假设。", "explanation": "考查假设检验步骤。", "chapter": "假设检验的解题套路", "concept": "拒绝域"}
    ]
  },
  "anki_cards": [
    {"front": "连续型随机变量单点概率是多少？", "back": "通常为 0，区间积分才表示概率。", "tags": "概率分布"},
    {"front": "置信区间的一般形式是什么？", "back": "估计量 ± 临界值 × 标准误。", "tags": "参数估计"},
    {"front": "假设检验的基本步骤有哪些？", "back": "提出假设、选统计量、定拒绝域、作结论。", "tags": "假设检验"}
  ],
  "high_frequency_points": ["置信区间", "假设检验", "概率分布"],
  "sprint_checklist": ["背常见分布公式", "练置信区间计算", "按步骤写假设检验"],
  "low_priority": ["材料中只出现一次的扩展阅读"],
  "insufficient_materials": [],
  "markdown": "# 概率论期末复习资料包\\n\\n## 复习导览\\n先复习概率分布与随机变量，再进入参数估计和假设检验。\\n\\n## 知识结构\\n### 概率分布与随机变量\\n具体掌握二项分布、正态分布、期望与方差。\\n\\n### 参数估计与区间估计\\n重点练习置信区间计算。\\n\\n### 假设检验的解题套路\\n按五步法完成判断与解释。\\n\\n## 考点与题型\\n概念辨析题、公式套用计算题、条件概率建模题、统计推断分析题。\\n\\n## 模拟卷\\n题目包含答案和解析。\\n\\n## Anki 卡片\\n卡片已结构化。\\n",
  "generated_at": "2026-06-07T00:00:00"
}
""".strip()


def llm_response_from_json(text: str) -> httpx.Response:
    return httpx.Response(200, json={"choices": [{"message": {"content": text}}]})


def test_deepseek_default_model_is_v4_flash() -> None:
    config = LLMConfig(provider="deepseek", api_key="sk-test", enabled=True)
    report = generate_review_report(MATERIALS)
    result = generate_review_summary("", report, LLMConfig(enabled=False))

    assert result.llm_status == "disabled"
    assert normalize_base_url("https://api.deepseek.com") == "https://api.deepseek.com/v1"
    assert config.model is None


def test_prompt_prioritizes_quality_and_does_not_force_fixed_types() -> None:
    report = generate_review_report(MATERIALS)
    prompt = build_review_prompt(
        {"course_name": "demo", "files": [], "global_signals": {}, "chunks": []},
        report,
        [],
        detail_level="detailed",
        output_style="practice_training",
    )

    assert "不要把题型强行归入固定题型库" in prompt
    assert "质量优先于节省 token" in prompt
    assert "优先参考真实题干结构和题型线索" in prompt
    assert "不要固定套用" in prompt
    assert "生成详细度：detailed" in prompt
    assert "输出风格：practice_training" in prompt
    assert "像刷题训练册一样组织" in prompt


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
        lambda *args, **kwargs: "太长" * 25000,
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


def test_short_text_does_not_trigger_compression() -> None:
    report = generate_review_report(MATERIALS)
    prepared = prepare_llm_context(MATERIALS, report)

    assert prepared.text == MATERIALS
    assert prepared.needs_chunking is False
    assert prepared.chunk_count == 0


def test_long_text_triggers_prepare_llm_context() -> None:
    report = generate_review_report(MATERIALS)
    long_text = ("Chapter 1 Photosynthesis\nKey points: chloroplast, ATP.\n" * 900)
    prepared = prepare_llm_context(long_text, report)

    assert len(long_text) > MAX_LLM_INPUT_CHARS
    assert prepared.compressed_chars <= MAX_LLM_INPUT_CHARS
    assert "本地安全底稿" in prepared.text


def test_very_long_text_triggers_chunk_summarize(monkeypatch) -> None:
    report = generate_review_report(MATERIALS)
    very_long_text = (
        "Chapter 1 Photosynthesis\n"
        "1. Multiple choice: Which stage produces ATP?\n"
        "Key points: chloroplast, light reaction, Calvin cycle.\n\n"
        * 1200
    )
    calls = {"summary": 0, "final": 0}

    def fake_post(url, json, headers, timeout):
        if "max_tokens" in json:
            calls["summary"] += 1
            return httpx.Response(
                200,
                json={"choices": [{"message": {"content": "章节：光合作用；考点：ATP；题型：选择题。"}}]},
            )
        calls["final"] += 1
        return llm_response_for(report)

    monkeypatch.setattr("app.services.llm_providers.openai_compatible.httpx.post", fake_post)
    result = generate_review_summary(
        very_long_text,
        report,
        LLMConfig(provider="deepseek", api_key="sk-correct", enabled=True),
    )

    assert split_material_chunks(very_long_text)
    assert all(len(chunk) <= MAX_CHUNK_CHARS for chunk in split_material_chunks(very_long_text))
    assert result.llm_status == "success"
    assert result.fallback_used is False
    assert result.llm_context_strategy == "chunked"
    assert calls["summary"] > 0
    assert calls["final"] == 1


def test_chunk_summary_failure_falls_back(monkeypatch) -> None:
    report = generate_review_report(MATERIALS)
    very_long_text = (
        "Chapter 1 Photosynthesis\n"
        "1. Multiple choice: Which stage produces ATP?\n"
        "Key points: chloroplast, light reaction, Calvin cycle.\n\n"
        * 1200
    )

    def fake_post(url, json, headers, timeout):
        if "max_tokens" in json:
            raise httpx.TimeoutException("timeout")
        return llm_response_for(report)

    monkeypatch.setattr("app.services.llm_providers.openai_compatible.httpx.post", fake_post)
    result = generate_review_summary(
        very_long_text,
        report,
        LLMConfig(provider="deepseek", api_key="sk-correct", enabled=True),
    )

    assert result.llm_status == "failed"
    assert result.fallback_used is True
    assert result.llm_error
    assert result.llm_error.code == "CONTEXT_TOO_LONG"


def test_compressible_long_text_does_not_directly_trigger_context_too_long(monkeypatch) -> None:
    report = generate_review_report(MATERIALS)
    long_text = ("Chapter 1 Photosynthesis\nKey points: chloroplast, ATP.\n" * 900)

    def fake_post(url, json, headers, timeout):
        return llm_response_for(report)

    monkeypatch.setattr("app.services.llm_providers.openai_compatible.httpx.post", fake_post)
    result = generate_review_summary(
        long_text,
        report,
        LLMConfig(provider="deepseek", api_key="sk-correct", enabled=True),
    )

    assert result.llm_status == "success"
    assert result.fallback_used is False
    assert result.llm_error is None
    assert result.llm_context_strategy in {"compressed", "direct"}


def test_llm_accepts_self_named_study_units_and_question_types(monkeypatch) -> None:
    report = generate_review_report(MATERIALS)
    captured = {}

    def fake_post(url, json, headers, timeout):
        captured["prompt"] = json["messages"][-1]["content"]
        return llm_response_from_json(ai_report_json())

    monkeypatch.setattr("app.services.llm_providers.openai_compatible.httpx.post", fake_post)
    result = generate_review_summary(
        MATERIALS,
        report,
        LLMConfig(provider="deepseek", api_key="sk-correct", enabled=True),
    )

    unit_names = [unit.name for unit in result.report.study_units]
    type_names = [item.name for item in result.report.question_types]
    assert result.llm_status == "success"
    assert "概率分布与随机变量" in unit_names
    assert "参数估计与区间估计" in unit_names
    assert "假设检验的解题套路" in unit_names
    assert {"概念辨析题", "公式套用计算题", "条件概率建模题", "统计推断分析题"} <= set(type_names)
    assert "不要把题型强行归入固定题型库" in captured["prompt"]


def test_low_quality_llm_output_triggers_repair(monkeypatch) -> None:
    report = generate_review_report(MATERIALS)
    calls = {"final": 0, "repair": 0}

    def fake_post(url, json, headers, timeout):
        prompt = json["messages"][-1]["content"]
        if "待修复报告 JSON" in prompt:
            calls["repair"] += 1
            return llm_response_from_json(ai_report_json())
        calls["final"] += 1
        return llm_response_from_json(
            '{"title":"空泛报告","summary":"认真复习，多做练习。","chapters":[],"mock_exam":{"title":"模拟卷","questions":[]},"anki_cards":[]}'
        )

    monkeypatch.setattr("app.services.llm_providers.openai_compatible.httpx.post", fake_post)
    result = generate_review_summary(
        MATERIALS,
        report,
        LLMConfig(provider="deepseek", api_key="sk-correct", enabled=True),
    )

    assert result.llm_status == "success"
    assert result.report.title == "概率论期末复习资料包"
    assert result.report.quality
    assert result.report.quality.quality_score >= 75
    assert calls == {"final": 1, "repair": 1}


def test_low_quality_repair_failure_falls_back(monkeypatch) -> None:
    report = generate_review_report(MATERIALS)

    def fake_post(url, json, headers, timeout):
        return llm_response_from_json(
            '{"title":"空泛报告","summary":"认真复习，多做练习。","chapters":[],"mock_exam":{"title":"模拟卷","questions":[]},"anki_cards":[]}'
        )

    monkeypatch.setattr("app.services.llm_providers.openai_compatible.httpx.post", fake_post)
    result = generate_review_summary(
        MATERIALS,
        report,
        LLMConfig(provider="deepseek", api_key="sk-correct", enabled=True),
    )

    assert result.llm_status == "failed"
    assert result.fallback_used is True
    assert result.llm_error
    assert result.llm_error.code == "QUALITY_FAILED"
    assert result.report.title == report.title


def test_llm_outline_naming_improves_safe_draft_after_quality_failure(monkeypatch) -> None:
    report = generate_review_report(MATERIALS)

    def fake_post(url, json, headers, timeout):
        system = json["messages"][0]["content"]
        prompt = json["messages"][-1]["content"]
        if "轻量专题命名" in system or "专题命名" in prompt:
            return llm_response_from_json(
                '{"study_units":['
                '{"name":"Python 函数与控制流","reason":"函数、分支和循环是复习主线","priority":90,'
                '"key_points":["函数定义","条件分支","循环控制"],"how_to_review":"先梳理语法，再做代码阅读题。"},'
                '{"name":"植物形态结构与分类","reason":"形态识别和分类线索适合合并复习","priority":80,'
                '"key_points":["形态结构","分类依据"],"how_to_review":"结合图示和关键词记忆。"}'
                ']}'
            )
        return llm_response_from_json(
            '{"title":"空泛报告","summary":"认真复习，多做练习。","chapters":[],"mock_exam":{"title":"模拟卷","questions":[]},"anki_cards":[]}'
        )

    monkeypatch.setattr("app.services.llm_providers.openai_compatible.httpx.post", fake_post)
    result = generate_review_summary(
        MATERIALS,
        report,
        LLMConfig(provider="deepseek", api_key="sk-correct", enabled=True),
    )

    assert result.report_source == "local_safe_draft_with_ai_outline"
    assert result.llm_status == "failed"
    assert result.fallback_used is True
    assert [unit.name for unit in result.report.study_units][:2] == ["Python 函数与控制流", "植物形态结构与分类"]
    assert result.report.chapters[0].chapter == "Python 函数与控制流"


def test_long_document_uses_chunk_insights(monkeypatch) -> None:
    report = generate_review_report(MATERIALS)
    very_long_text = (
        "Chapter Probability Distribution\n"
        "1. Calculate the confidence interval and explain the hypothesis test.\n"
        "Definition: random variable. Formula: E(X), Var(X).\n\n"
        * 1300
    )
    prompts: list[str] = []

    def fake_post(url, json, headers, timeout):
        prompt = json["messages"][-1]["content"]
        prompts.append(prompt)
        if "chunk_insight" in prompt and "分块：" in prompt:
            return httpx.Response(
                200,
                json={
                    "choices": [
                        {
                            "message": {
                                "content": "本块主题：概率分布。可考点：置信区间。可能题型：公式套用计算题。可转 Anki：置信区间公式。"
                            }
                        }
                    ]
                },
            )
        return llm_response_from_json(ai_report_json())

    monkeypatch.setattr("app.services.llm_providers.openai_compatible.httpx.post", fake_post)
    result = generate_review_summary(
        very_long_text,
        report,
        LLMConfig(provider="deepseek", api_key="sk-correct", enabled=True),
    )

    assert result.llm_status == "success"
    assert result.llm_context_strategy == "chunked"
    assert any("可转 Anki 的问答" in prompt for prompt in prompts)
    assert any("chunk_insights" in prompt for prompt in prompts)
    assert len(result.report.mock_exam.questions) >= 3


def test_export_prefers_final_report_markdown_and_structured_anki() -> None:
    report = generate_review_report(MATERIALS)
    payload = __import__("json").loads(ai_report_json())
    from app.services.llm_providers.openai_compatible import normalize_review_payload
    from app.schemas.review import ReviewReport

    normalize_review_payload(payload)
    final_report = ReviewReport.model_validate(payload)
    markdown = generate_markdown_review(final_report)

    assert markdown.startswith("# 概率论期末复习资料包")
    assert "chunk_insight" not in markdown
    assert final_report.anki_cards[0].front == "连续型随机变量单点概率是多少？"
    assert report.anki_cards != final_report.anki_cards


def test_quality_validation_accepts_creative_complete_report() -> None:
    payload = __import__("json").loads(ai_report_json())
    from app.services.llm_providers.openai_compatible import normalize_review_payload
    from app.schemas.review import ReviewReport

    normalize_review_payload(payload)
    report = ReviewReport.model_validate(payload)
    quality = validate_report_quality(report, MATERIALS)

    assert quality.quality_score >= 75
    assert quality.quality_failures == []


def test_study_goal_and_exam_type_affect_local_safe_draft() -> None:
    report = generate_review_report(
        MATERIALS + "\n\nPython function output debug code boundary condition.",
        study_goal="practice_heavy",
        exam_type="programming",
    )

    assert report.study_goal == "practice_heavy"
    assert report.exam_type == "programming"
    assert any("编程考试" in item or "代码" in item for item in report.sprint_checklist)
    assert any(question.source_hint for question in report.mock_exam.questions)


def test_quality_score_changes_with_study_goal() -> None:
    report = generate_review_report(MATERIALS, study_goal="balanced")
    balanced = validate_report_quality(report, MATERIALS, study_goal="balanced")
    anki_focused = validate_report_quality(report, MATERIALS, study_goal="anki_focused")

    assert balanced.quality_score != anki_focused.quality_score
    assert balanced.anki_quality_score == anki_focused.anki_quality_score
