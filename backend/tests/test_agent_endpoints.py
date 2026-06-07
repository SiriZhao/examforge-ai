from fastapi.testclient import TestClient

from app.main import app
from app.services.review_planner import generate_review_report


SAMPLE_REPORT = generate_review_report(
    """
第一章 极限与连续
重点：函数极限、连续性。
1. 选择题：下列关于函数连续性的说法正确的是哪一项？
2. 计算题：计算 lim x=0 sin(x)/x。
""",
    title="高数复习",
)


def test_chat_returns_high_frequency_points() -> None:
    client = TestClient(app)

    response = client.post(
        "/chat",
        json={
            "message": "高频考点",
            "review_report": SAMPLE_REPORT.model_dump(),
            "history": [],
        },
    )

    assert response.status_code == 200
    assert "高频考点" in response.json()["reply"]


def test_generate_mock_exam_returns_questions() -> None:
    client = TestClient(app)

    response = client.post(
        "/generate-mock-exam",
        json={"review_report": SAMPLE_REPORT.model_dump(), "count": 3},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["questions"]
    assert body["questions"][0]["chapter"] == "第一章 极限与连续"
    assert "已生成" in body["message"]
