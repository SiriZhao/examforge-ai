from app.services.concept_extractor import extract_formulas, extract_keywords
from app.services.generator import generate_markdown_review
from app.services.question_extractor import extract_questions
from app.services.review_planner import (
    INSUFFICIENT_MESSAGE,
    generate_review_report,
)


SAMPLE_MATERIAL = """
Chapter 1 Photosynthesis
Key points: chloroplast, light reaction, Calvin cycle, ATP, NADPH.
1. Multiple choice: Which stage produces ATP and NADPH? A. Light reaction B. Germination C. Pollination D. Dormancy
2. Short answer: Explain why the Calvin cycle depends on light reactions.

Chapter 2 Plant Transport
Key points: xylem, phloem, stomata, guard cells, transpiration.
1. Fill in the blank: The tissue that transports sugar is ____.
2. Essay: Discuss the trade-off between gas exchange and water loss in leaves.
"""


def test_extract_questions_by_rule() -> None:
    questions = extract_questions(SAMPLE_MATERIAL)

    assert len(questions) >= 4
    assert any("Multiple choice" in question.question for question in questions)
    assert any("Fill in the blank" in question.question for question in questions)


def test_extract_keywords_and_formulas() -> None:
    keywords = extract_keywords(SAMPLE_MATERIAL)
    formulas = extract_formulas("Common formula: energy = ATP + NADPH")

    assert "Photosynthesis" in keywords or "chloroplast" in keywords
    assert any("ATP" in formula for formula in formulas)


def test_generate_review_report_with_exam_intelligence() -> None:
    report = generate_review_report(
        SAMPLE_MATERIAL,
        title="Plant Biology Final Review",
        file_texts=[
            ("lecture_notes.md", SAMPLE_MATERIAL),
            ("demo_past_exam.md", SAMPLE_MATERIAL),
        ],
    )

    assert report.title == "Plant Biology Final Review"
    assert "已识别" in report.summary
    assert len(report.chapters) == 2
    assert all(0 <= chapter.importance <= 100 for chapter in report.chapters)
    assert report.past_exam_analysis.detected_files
    assert report.past_exam_analysis.high_frequency_topics
    assert report.review_order
    assert {plan.days for plan in report.sprint_plans} == {1, 3, 7}
    assert report.mock_exam.questions
    assert {"选择题", "填空题", "简答题", "论述题"} <= {
        question.question_type for question in report.mock_exam.questions
    }
    assert report.anki_cards
    assert report.anki_cards[0].front
    assert report.anki_cards[0].back
    assert report.anki_cards[0].tags


def test_report_marks_insufficient_materials() -> None:
    report = generate_review_report("tiny")

    assert INSUFFICIENT_MESSAGE in report.summary
    assert any(INSUFFICIENT_MESSAGE in item for item in report.insufficient_materials)
    assert report.high_frequency_points == [INSUFFICIENT_MESSAGE]


def test_generate_markdown_review_contains_star_features() -> None:
    report = generate_review_report(
        SAMPLE_MATERIAL,
        title="Plant Biology Final Review",
        file_texts=[("demo_past_exam.md", SAMPLE_MATERIAL)],
    )
    markdown = generate_markdown_review(report)

    assert "# Plant Biology Final Review" in markdown
    assert "## 往年题高频考点分析" in markdown
    assert "## 推荐复习顺序" in markdown
    assert "## 考前冲刺计划" in markdown
    assert "## 模拟卷" in markdown
    assert "## Anki 卡片预览" in markdown
