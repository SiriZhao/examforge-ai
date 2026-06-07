from app.services.llm_providers.openai_compatible import (
    extract_json_object,
    normalize_review_payload,
)


def test_extract_json_object_accepts_fenced_json() -> None:
    data = extract_json_object('```json\n{"title":"报告","chapters":[]}\n```')

    assert data["title"] == "报告"


def test_normalize_review_payload_accepts_question_type_aliases() -> None:
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
    assert data["chapters"][0]["question_types"] == ["选择题", "未知"]

