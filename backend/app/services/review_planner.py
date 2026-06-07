from datetime import datetime

from app.schemas.review import ChapterReview, ExamQuestion, ReviewReport
from app.services.chapter_extractor import ChapterSection, DEFAULT_CHAPTER, extract_chapters
from app.services.concept_extractor import extract_formulas, extract_keywords
from app.services.exam_intelligence import build_exam_intelligence
from app.services.frequency_analyzer import (
    count_question_types,
    high_frequency_points,
    match_questions_to_chapters,
)
from app.services.question_extractor import extract_questions
from app.services.text_cleaner import clean_list, clean_report_text, clean_text

INSUFFICIENT_MESSAGE = "当前材料不足，无法可靠判断。"


def generate_review_report(
    content: str,
    title: str = "期末复习资料包",
    focus: str | None = None,
    file_texts: list[tuple[str, str]] | None = None,
) -> ReviewReport:
    normalized_content = clean_report_text(content)
    chapters = extract_chapters(normalized_content)
    questions = extract_questions(normalized_content)
    chapter_questions = match_questions_to_chapters(questions, chapters)
    chapter_reviews = build_chapter_reviews(chapters, chapter_questions)
    (
        past_exam_analysis,
        review_order,
        sprint_plans,
        mock_exam,
        anki_cards,
    ) = build_exam_intelligence(chapters, chapter_reviews, file_texts)
    high_points = high_frequency_points(chapter_questions)
    insufficient = detect_insufficient_materials(
        normalized_content, chapters, questions, high_points
    )

    if not normalized_content:
        summary = INSUFFICIENT_MESSAGE
    elif insufficient:
        summary = f"已根据当前材料生成规则版复习报告。{INSUFFICIENT_MESSAGE}"
    else:
        summary = (
            f"已识别 {len(chapter_reviews)} 个章节/主题、"
            f"{len(questions)} 道疑似考试题，以及 "
            f"{len(past_exam_analysis.high_frequency_topics)} 个反复出现的往年题考点。"
            "建议按照章节优先级、冲刺计划、模拟卷和 Anki 卡片进行复习。"
        )

    report_title = title if not focus else f"{title}：{focus}"
    return sanitize_report(
        ReviewReport(
            title=clean_text(report_title),
            summary=summary,
            chapters=chapter_reviews,
            past_exam_analysis=past_exam_analysis,
            review_order=review_order,
            sprint_plans=sprint_plans,
            mock_exam=mock_exam,
            anki_cards=anki_cards,
            high_frequency_points=high_points or [INSUFFICIENT_MESSAGE],
            sprint_checklist=build_sprint_checklist(chapter_reviews, high_points),
            low_priority=build_low_priority(chapter_reviews),
            insufficient_materials=insufficient,
            generated_at=datetime.now().isoformat(timespec="seconds"),
        )
    )


def build_chapter_reviews(
    chapters: list[ChapterSection],
    chapter_questions: dict[str, list[ExamQuestion]],
) -> list[ChapterReview]:
    reviews: list[ChapterReview] = []
    max_frequency = max((len(items) for items in chapter_questions.values()), default=0)

    for chapter in chapters:
        questions = chapter_questions.get(chapter.title, [])
        frequency = len(questions)
        importance = calculate_importance(frequency, max_frequency, chapter.text)
        keywords = extract_keywords(chapter.text, limit=10)
        formulas = extract_formulas(chapter.text, limit=6)
        examples = [question.question for question in questions[:3]]

        reviews.append(
            ChapterReview(
                chapter=chapter.title or DEFAULT_CHAPTER,
                importance=importance,
                material_frequency=0,
                past_exam_frequency=0,
                weighted_score=importance,
                keywords=keywords or [INSUFFICIENT_MESSAGE],
                formulas=formulas,
                question_types=count_question_types(questions),
                examples=examples or [INSUFFICIENT_MESSAGE],
                frequency=frequency,
                review_advice=make_chapter_advice(chapter.title, importance, questions),
            )
        )

    if not reviews:
        reviews.append(
            ChapterReview(
                chapter=DEFAULT_CHAPTER,
                importance=0,
                material_frequency=0,
                past_exam_frequency=0,
                weighted_score=0,
                keywords=[INSUFFICIENT_MESSAGE],
                formulas=[],
                question_types=[],
                examples=[INSUFFICIENT_MESSAGE],
                frequency=0,
                review_advice=INSUFFICIENT_MESSAGE,
            )
        )

    return reviews


def calculate_importance(frequency: int, max_frequency: int, chapter_text: str) -> int:
    frequency_score = 0 if max_frequency == 0 else int((frequency / max_frequency) * 60)
    keyword_bonus = 20 if any(
        word.lower() in chapter_text.lower()
        for word in ["key point", "important", "must know", "review", "exam", "重点", "必考", "常考"]
    ) else 0
    content_bonus = min(len(chapter_text) // 200, 20)
    return min(100, frequency_score + keyword_bonus + content_bonus)


def make_chapter_advice(
    chapter: str, importance: int, questions: list[ExamQuestion]
) -> str:
    chapter_name = clean_text(chapter or DEFAULT_CHAPTER)
    if not questions and importance < 20:
        return INSUFFICIENT_MESSAGE

    types = "、".join(str(item) for item in count_question_types(questions)) or "基础概念题"
    if importance >= 70:
        return f"{chapter_name} 是高优先级内容。建议先复习本章，整理核心概念，再集中练习{types}。"
    if importance >= 40:
        return f"{chapter_name} 是中等优先级内容。建议在高优先级章节之后复习，并练习{types}。"
    return f"根据当前材料，{chapter_name} 暂时属于较低优先级。建议浏览关键词，考前再快速回顾。"


def build_sprint_checklist(
    chapter_reviews: list[ChapterReview], high_points: list[str]
) -> list[str]:
    ordered = sorted(chapter_reviews, key=lambda item: item.importance, reverse=True)
    checklist = [
        "优先复习重要度最高的 3 个章节，并整理一页回忆提纲。",
        "把高频考点改写成自测问题，再回到笔记中查漏补缺。",
        "每一种高频题型至少练习 1 道题。",
    ]
    for chapter in ordered[:3]:
        checklist.append(f"优先章节：{chapter.chapter}（{chapter.importance}/100）。")
    for point in high_points[:3]:
        checklist.append(f"回顾高频考点：{point}")
    if not chapter_reviews or all(item.frequency == 0 for item in chapter_reviews):
        checklist.append(INSUFFICIENT_MESSAGE)
    return clean_list(checklist, fallback=INSUFFICIENT_MESSAGE)


def build_low_priority(chapter_reviews: list[ChapterReview]) -> list[str]:
    low = [
        review.chapter
        for review in chapter_reviews
        if review.importance < 30 and review.frequency == 0
    ]
    return clean_list(low) or ["暂未识别出明确的低优先级章节。"]


def detect_insufficient_materials(
    content: str,
    chapters: list[ChapterSection],
    questions: list[ExamQuestion],
    high_points: list[str],
) -> list[str]:
    insufficient: list[str] = []
    if len(content) < 100:
        insufficient.append(INSUFFICIENT_MESSAGE)
    if not chapters or all(not chapter.text.strip() for chapter in chapters):
        insufficient.append(f"章节证据较弱。{INSUFFICIENT_MESSAGE}")
    if not questions:
        insufficient.append(f"题目证据较弱。{INSUFFICIENT_MESSAGE}")
    if not high_points:
        insufficient.append(f"高频考点证据较弱。{INSUFFICIENT_MESSAGE}")
    return insufficient


def sanitize_report(report: ReviewReport) -> ReviewReport:
    report.title = clean_text(report.title)
    report.summary = clean_text(report.summary)
    report.high_frequency_points = clean_list(
        report.high_frequency_points,
        fallback=INSUFFICIENT_MESSAGE,
        limit=12,
    )
    report.sprint_checklist = clean_list(
        report.sprint_checklist,
        fallback=INSUFFICIENT_MESSAGE,
        limit=14,
    )
    report.low_priority = clean_list(report.low_priority, fallback="暂未识别出明确的低优先级章节。")
    report.insufficient_materials = clean_list(report.insufficient_materials)

    for chapter in report.chapters:
        chapter.chapter = clean_text(chapter.chapter) or DEFAULT_CHAPTER
        chapter.importance = max(0, min(100, chapter.importance))
        chapter.weighted_score = max(0, min(100, chapter.weighted_score or chapter.importance))
        chapter.keywords = clean_list(chapter.keywords, fallback=INSUFFICIENT_MESSAGE, limit=12)
        chapter.formulas = clean_list(chapter.formulas, limit=8)
        chapter.examples = clean_list(chapter.examples, fallback=INSUFFICIENT_MESSAGE, limit=5)
        chapter.review_advice = clean_text(chapter.review_advice)

    report.review_order = report.review_order[:12]
    report.sprint_plans = report.sprint_plans[:3]
    report.anki_cards = report.anki_cards[:30]
    return report
