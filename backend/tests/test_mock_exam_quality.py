from app.schemas.review import AnkiCard, GeneratedExamQuestion, GeneratedMockExam
from app.services.exam_intelligence import build_exam_intelligence
from app.services.mock_exam_quality import anki_quality_failures, ensure_mock_exam_quality, mock_exam_quality_failures
from app.services.review_planner import generate_review_report


PAST_EXAM_TEXT = """
概率论往年题
1. 设随机变量 X 的分布函数为 F(x)，求 P(1<X<2)，并说明计算依据。
2. 已知 X 与 Y 相互独立，证明 E(XY)=E(X)E(Y)。
3. 根据样本均值和方差，计算总体均值的置信区间。
4. 写出条件概率 P(A|B) 的定义，并用贝叶斯公式解释检测问题。
"""


def test_mock_exam_uses_past_exam_question_types() -> None:
    report = generate_review_report(PAST_EXAM_TEXT, title="概率论", file_texts=[("概率论往年题.pdf", PAST_EXAM_TEXT)])

    question_types = {question.question_type for question in report.mock_exam.questions}
    assert len(question_types) > 1
    assert not all(question_type == "选择题" for question_type in question_types)
    assert any("往年题型线索" in question.source_basis for question in report.mock_exam.questions)
    assert all(question.related_topic for question in report.mock_exam.questions)
    assert all(question.explanation for question in report.mock_exam.questions)
    assert not any("以下哪一项最能解释" in question.question for question in report.mock_exam.questions)


def test_low_quality_mock_exam_is_replaced_by_conservative_questions() -> None:
    report = generate_review_report(PAST_EXAM_TEXT, title="概率论")
    report.mock_exam = GeneratedMockExam(
        title="bad",
        questions=[
            GeneratedExamQuestion(
                question_type="选择题",
                question="以下哪一项最能解释 X？A. 核心定义 B. 无关细节 C. 相反说法 D. 随机例子",
                answer="A",
                explanation="",
            )
            for _ in range(4)
        ],
    )

    assert "missing_explanation" in mock_exam_quality_failures(report)
    fixed, failures = ensure_mock_exam_quality(report)

    assert failures
    assert fixed.overview["mock_exam_mode"] == "conservative"
    assert all(question.answer != "A" for question in fixed.mock_exam.questions)
    assert all(question.source_basis for question in fixed.mock_exam.questions)


def test_generic_anki_cards_are_marked_low_quality() -> None:
    report = generate_review_report(PAST_EXAM_TEXT, title="概率论")
    report.anki_cards = [
        AnkiCard(front="关于 随机变量 需要掌握什么？", back="所属章节：随机变量。常见题型：计算题。", tags="随机变量")
    ]

    failures = anki_quality_failures(report)

    assert "generic_front" in failures
    assert "weak_back" in failures
