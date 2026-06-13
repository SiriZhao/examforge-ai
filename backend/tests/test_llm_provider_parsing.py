from app.services.llm_providers.openai_compatible import (
    extract_json_object,
    normalize_review_payload,
    tolerant_parse_llm_report,
)


def test_extract_json_object_accepts_fenced_json() -> None:
    data = extract_json_object('```json\n{"title":"报告","chapters":[]}\n```')

    assert data["title"] == "报告"


def test_tolerant_parse_accepts_json_variants_and_markdown() -> None:
    pure = tolerant_parse_llm_report('{"title":"纯 JSON","chapters":[]}')
    explained = tolerant_parse_llm_report('下面是报告：\n{"title":"带说明 JSON","chapters":[]}\n请查收。')
    fenced = tolerant_parse_llm_report('```json\n{"title":"代码块 JSON","chapters":[]}\n```')
    markdown = tolerant_parse_llm_report(
        """
# 植物学期末复习资料包

## 复习导览
先复习植物形态结构，再复习分类和实验观察。

## 知识结构
### 植物形态结构与功能
掌握根、茎、叶、花、果实、种子的结构与功能。

## 高频考点
- 维管束结构
- 被子植物分类特征
- 花程式与花图式

## 题型分析
- 概念辨析题：比较导管与筛管。
- 图示识别题：识别根尖分区。
- 分类归纳题：根据形态特征判断类群。

## 模拟题与答案
题目1：说明双子叶植物茎的初生结构。
答案：表皮、皮层和维管柱组成，维管束环状排列。
题目2：比较单子叶与双子叶植物叶脉。
答案：单子叶多平行脉，双子叶多网状脉。
题目3：如何识别被子植物重要类群？
答案：结合花、果实、叶序和胚珠等特征判断。

## Anki 卡片
- 正面：导管的功能是什么？ 背面：运输水分和无机盐。
- 正面：筛管的功能是什么？ 背面：运输有机物。
- 正面：根尖分区有哪些？ 背面：根冠、分生区、伸长区、成熟区。

## 考前冲刺计划
- 1 天：背高频概念，练图示识别。
- 3 天：按形态、分类、实验分三轮复习。
""".strip()
    )

    assert pure["title"] == "纯 JSON"
    assert explained["title"] == "带说明 JSON"
    assert fenced["title"] == "代码块 JSON"
    assert markdown["_raw_markdown_fallback"] is True
    assert markdown["markdown"].startswith("# 植物学期末复习资料包")


def test_tolerant_parse_rejects_unusable_garbage() -> None:
    try:
        tolerant_parse_llm_report("ok ??? ...")
    except ValueError:
        return

    raise AssertionError("unusable garbage should not be parsed as a report")


def test_normalize_review_payload_preserves_custom_question_types() -> None:
    data = {
        "chapters": [
            {
                "importance": "120",
                "frequency": "3",
                "question_types": ["选择题", "unknown"],
            }
        ]
    }

    normalize_review_payload(data)

    assert data["chapters"][0]["importance"] == 100
    assert data["chapters"][0]["question_types"] == ["选择题", "unknown"]
