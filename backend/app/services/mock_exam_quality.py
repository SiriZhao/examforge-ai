from collections import Counter

from app.schemas.review import GeneratedExamQuestion, ReviewReport
from app.services.text_cleaner import clean_text
from app.services.text_quality import clean_topic_name, has_mojibake, looks_like_formula_fragment

BAD_OPTION_MARKERS = {"核心定义", "无关细节", "相反说法", "随机例子"}
GENERIC_STEMS = ("以下哪一项最能解释", "下列哪一项最能解释", "关于", "需要掌握什么")


def mock_exam_quality_failures(report: ReviewReport) -> list[str]:
    questions = report.mock_exam.questions
    failures: list[str] = []
    if not questions:
        return ["missing_mock_exam"]
    if len(questions) < 3 and not report.insufficient_materials:
        failures.append("too_few_questions")

    type_counts = Counter(question.question_type or question.type for question in questions)
    most_common = type_counts.most_common(1)[0][1] if type_counts else 0
    if len(questions) >= 4 and most_common / len(questions) >= 0.8 and not report.past_exam_analysis.detected_files:
        failures.append("too_many_same_question_types")

    generic_count = 0
    answer_a_count = 0
    stem_counter: Counter[str] = Counter()
    for question in questions:
        text = clean_text(question.question)
        stem_counter[text[:24]] += 1
        if len(text) < 15:
            failures.append("short_question")
        if has_mojibake(text) or looks_like_formula_fragment(text):
            failures.append("noisy_question")
        if any(marker in text for marker in GENERIC_STEMS):
            generic_count += 1
        if not clean_text(question.answer):
            failures.append("missing_answer")
        if not clean_text(question.explanation):
            failures.append("missing_explanation")
        if not clean_topic_name(question.related_topic or question.concept or question.chapter):
            failures.append("missing_related_topic")
        if question.options and BAD_OPTION_MARKERS.intersection(set(question.options)):
            failures.append("template_options")
        if clean_text(question.answer).startswith(("A", "Ａ")):
            answer_a_count += 1

    if generic_count >= max(2, len(questions) // 2):
        failures.append("too_many_generic_templates")
    if answer_a_count >= 3 and answer_a_count == len(questions):
        failures.append("all_answers_are_a")
    if any(count >= 3 for count in stem_counter.values()):
        failures.append("repeated_question_stems")
    return sorted(set(failures))


def ensure_mock_exam_quality(report: ReviewReport) -> tuple[ReviewReport, list[str]]:
    failures = mock_exam_quality_failures(report)
    if not failures:
        return report, []

    report.mock_exam.questions = build_conservative_questions(report)
    report.mock_exam.title = "基于材料的保守练习卷"
    report.overview = {
        **report.overview,
        "mock_exam_mode": "conservative",
        "mock_exam_quality_failures": failures,
    }
    return report, failures


def build_conservative_questions(report: ReviewReport) -> list[GeneratedExamQuestion]:
    topics = []
    topics.extend(report.high_frequency_points[:6])
    topics.extend(topic.topic for topic in report.past_exam_analysis.high_frequency_topics[:6])
    if not topics:
        topics.extend(chapter.chapter for chapter in report.chapters[:6])

    result: list[GeneratedExamQuestion] = []
    for index, raw_topic in enumerate(topics[:6], start=1):
        topic = clean_topic_name(raw_topic) or f"核心专题 {index}"
        chapter = next((item.chapter for item in report.chapters if topic in item.chapter or topic in item.keywords), "")
        q_type = "基于材料生成的保守练习题"
        if report.question_types:
            q_type = report.question_types[(index - 1) % len(report.question_types)].name
        result.append(
            GeneratedExamQuestion(
                question_type=q_type,
                type=q_type,
                difficulty="基础" if index <= 2 else "中等",
                question=f"根据材料，说明“{topic}”的核心含义、适用场景，并写出一个可能的考查角度。",
                answer=f"应围绕 {topic} 的定义或方法展开，结合材料中的关键词、公式、题干或例子说明其作用，并给出清晰结论。",
                explanation="该题为保守练习题，用于在缺少可靠 AI 模拟卷时保持可复习性，非真实往年题。",
                chapter=chapter or topic,
                concept=topic,
                related_topic=topic,
                source_hint="基于材料生成，非真实往年题",
                source_basis="基于材料生成，非真实往年题",
            )
        )
    return result


def anki_quality_failures(report: ReviewReport) -> list[str]:
    failures: list[str] = []
    seen: set[str] = set()
    for card in report.anki_cards:
        front = clean_text(card.front)
        back = clean_text(card.back)
        if front in seen:
            failures.append("duplicate_cards")
        seen.add(front)
        if "关于 " in front and "需要掌握什么" in front:
            failures.append("generic_front")
        if len(front) < 6 or len(front) > 100:
            failures.append("bad_front_length")
        if len(back) < 18 or ("所属章节：" in back and "常见题型：" in back and len(back) < 80):
            failures.append("weak_back")
        if has_mojibake(front + back):
            failures.append("garbled_card")
    return sorted(set(failures))
