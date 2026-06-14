from datetime import datetime

from app.schemas.review import AnkiCard, ChapterReview, ExamQuestion, ExamType, ReviewReport, StudyGoal
from app.services.chapter_extractor import ChapterSection, DEFAULT_CHAPTER, clean_unit_title, extract_chapters, is_bad_unit_title
from app.services.concept_extractor import extract_formulas, extract_keywords
from app.services.exam_intelligence import build_exam_intelligence
from app.services.frequency_analyzer import count_question_types, high_frequency_points, match_questions_to_chapters
from app.services.question_extractor import extract_questions
from app.services.text_cleaner import clean_list, clean_report_text, clean_text
from app.services.text_quality import clean_formula_text, clean_topic_list

INSUFFICIENT_MESSAGE = "当前材料不足，无法可靠判断。"


def generate_review_report(
    content: str,
    title: str = "期末复习资料包",
    focus: str | None = None,
    file_texts: list[tuple[str, str]] | None = None,
    study_goal: StudyGoal = "balanced",
    exam_type: ExamType = "unknown",
) -> ReviewReport:
    normalized_content = clean_report_text(content)
    chapters = extract_chapters(normalized_content)
    questions = extract_questions(normalized_content)
    chapter_questions = match_questions_to_chapters(questions, chapters)
    chapter_reviews = build_chapter_reviews(chapters, chapter_questions)
    past_exam_analysis, review_order, sprint_plans, mock_exam, anki_cards = build_exam_intelligence(
        chapters,
        chapter_reviews,
        file_texts,
    )
    high_points = high_frequency_points(chapter_questions)
    anki_cards = ensure_local_anki_cards(anki_cards, chapter_reviews, high_points, study_goal=study_goal, exam_type=exam_type)
    adapt_mock_exam(mock_exam, study_goal, exam_type)
    insufficient = detect_insufficient_materials(normalized_content, chapters, questions, high_points)

    if not normalized_content:
        summary = INSUFFICIENT_MESSAGE
    elif insufficient:
        summary = f"已根据当前材料生成本地安全底稿。{INSUFFICIENT_MESSAGE}"
    else:
        summary = (
            f"已识别 {len(chapter_reviews)} 个复习专题、{len(questions)} 道疑似题目，"
            f"以及 {len(past_exam_analysis.high_frequency_topics)} 个往年题/题干高频线索。"
            f"{study_goal_summary(study_goal)}{exam_type_summary(exam_type)}"
        )

    report_title = title if not focus else f"{title}：{focus}"
    return sanitize_report(
        ReviewReport(
            title=clean_text(report_title),
            summary=summary,
            study_goal=study_goal,
            exam_type=exam_type,
            chapters=chapter_reviews,
            past_exam_analysis=past_exam_analysis,
            review_order=review_order,
            sprint_plans=sprint_plans,
            mock_exam=mock_exam,
            anki_cards=anki_cards,
            high_frequency_points=high_points or [INSUFFICIENT_MESSAGE],
            sprint_checklist=build_sprint_checklist(chapter_reviews, high_points, study_goal=study_goal, exam_type=exam_type),
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
    for index, chapter in enumerate(chapters, start=1):
        title = safe_display_title(chapter.title or DEFAULT_CHAPTER, extract_keywords(chapter.text, limit=6), index)
        questions = chapter_questions.get(chapter.title, [])
        frequency = len(questions)
        importance = calculate_importance(frequency, max_frequency, chapter.text)
        keywords = extract_keywords(chapter.text, limit=10)
        formulas = extract_formulas(chapter.text, limit=6)
        examples = [question.question for question in questions[:3]]
        reviews.append(
            ChapterReview(
                chapter=title,
                importance=importance,
                material_frequency=0,
                past_exam_frequency=0,
                weighted_score=importance,
                keywords=keywords or [INSUFFICIENT_MESSAGE],
                formulas=formulas,
                question_types=count_question_types(questions),
                examples=examples or [INSUFFICIENT_MESSAGE],
                frequency=frequency,
                review_advice=make_chapter_advice(title, importance, questions),
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
    keyword_bonus = 20 if any(word.lower() in chapter_text.lower() for word in ["key point", "important", "must know", "review", "exam", "重点", "必考", "常考"]) else 0
    content_bonus = min(len(chapter_text) // 200, 20)
    return min(100, frequency_score + keyword_bonus + content_bonus)


def make_chapter_advice(chapter: str, importance: int, questions: list[ExamQuestion]) -> str:
    chapter_name = clean_text(chapter or DEFAULT_CHAPTER)
    if not questions and importance < 20:
        return INSUFFICIENT_MESSAGE
    types = "、".join(str(item) for item in count_question_types(questions)) or "基础概念题"
    if importance >= 70:
        return f"{chapter_name} 是高优先级内容。建议先复习核心概念，再集中练习{types}。"
    if importance >= 40:
        return f"{chapter_name} 是中等优先级内容。建议在高优先级专题后复习，并练习{types}。"
    return f"根据当前材料，{chapter_name} 暂时属于较低优先级内容。建议考前快速浏览关键词。"


def build_sprint_checklist(
    chapter_reviews: list[ChapterReview],
    high_points: list[str],
    *,
    study_goal: StudyGoal = "balanced",
    exam_type: ExamType = "unknown",
) -> list[str]:
    ordered = sorted(chapter_reviews, key=lambda item: item.importance, reverse=True)
    checklist = goal_exam_checklist_prefix(study_goal, exam_type)
    checklist.extend(
        [
            "优先复习重要度最高的 3 个专题，并整理一页回忆提纲。",
            "把高频考点改写成自测问题，再回到笔记中查漏补缺。",
            "每一种高频题型至少练习 1 道题，并核对答案和解析。",
        ]
    )
    for chapter in ordered[:3]:
        checklist.append(f"优先专题：{chapter.chapter}（{chapter.importance}/100）。")
    for point in high_points[:3]:
        checklist.append(f"回顾高频考点：{point}")
    if not chapter_reviews or all(item.frequency == 0 for item in chapter_reviews):
        checklist.append(INSUFFICIENT_MESSAGE)
    return clean_list(checklist, fallback=INSUFFICIENT_MESSAGE)


def build_low_priority(chapter_reviews: list[ChapterReview]) -> list[str]:
    low = [review.chapter for review in chapter_reviews if review.importance < 30 and review.frequency == 0]
    return clean_list(low) or ["暂未识别出明确的低优先级专题。"]


def ensure_local_anki_cards(
    cards: list[AnkiCard],
    chapter_reviews: list[ChapterReview],
    high_points: list[str],
    *,
    study_goal: StudyGoal = "balanced",
    exam_type: ExamType = "unknown",
) -> list[AnkiCard]:
    result = list(cards)
    seen = {card.front.strip() for card in result}
    for point in high_points[:8]:
        front = f"{point} 是什么？"
        if point and point != INSUFFICIENT_MESSAGE and front not in seen:
            result.append(
                AnkiCard(
                    front=front,
                    back=f"结合材料复习 {point} 的定义、特征、常见考法和易错点。",
                    tags="本地安全底稿 高频考点",
                    card_type="definition",
                    priority=85,
                    source_hint="来自高频考点线索",
                )
            )
            seen.add(front)
    for chapter in chapter_reviews[:6]:
        keywords = [item for item in chapter.keywords if item != INSUFFICIENT_MESSAGE]
        if keywords:
            front = f"{chapter.chapter} 需要优先掌握哪些关键词？"
            if front not in seen:
                result.append(
                    AnkiCard(
                        front=front,
                        back="、".join(keywords[:8]),
                        tags="本地安全底稿 关键词",
                        card_type="comparison",
                        priority=75,
                        source_hint="来自材料关键词",
                    )
                )
                seen.add(front)
        front = f"{chapter.chapter} 常见复习切入点是什么？"
        if front not in seen and chapter.review_advice and chapter.review_advice != INSUFFICIENT_MESSAGE:
            result.append(
                AnkiCard(
                    front=front,
                    back=chapter.review_advice,
                    tags="本地安全底稿 复习建议",
                    card_type="procedure",
                    priority=70,
                    source_hint="来自本地安全底稿",
                )
            )
            seen.add(front)
    append_goal_anki_cards(result, seen, chapter_reviews, study_goal, exam_type)
    return result


def append_goal_anki_cards(
    result: list[AnkiCard],
    seen: set[str],
    chapter_reviews: list[ChapterReview],
    study_goal: StudyGoal,
    exam_type: ExamType,
) -> None:
    if study_goal in {"anki_focused", "memorization"}:
        for chapter in chapter_reviews[:8]:
            for keyword in [item for item in chapter.keywords if item != INSUFFICIENT_MESSAGE][:3]:
                front = f"{keyword} 容易和哪些概念混淆？"
                if front not in seen:
                    result.append(
                        AnkiCard(
                            front=front,
                            back=f"请结合 {chapter.chapter} 的上下文，比较 {keyword} 的定义、适用条件和常见误区。",
                            tags="本地安全底稿 易混点",
                            card_type="pitfall",
                            priority=80,
                            source_hint="来自复习目标：重点背诵/Anki",
                        )
                    )
                    seen.add(front)
    if exam_type == "programming":
        front = "编程考试复习时每道代码题要检查哪些边界条件？"
        if front not in seen:
            result.append(
                AnkiCard(
                    front=front,
                    back="检查空输入、重复值、极大/极小规模、类型转换、循环边界和异常分支。",
                    tags="编程考试 边界条件",
                    card_type="code",
                    priority=85,
                    source_hint="来自考试类型：编程考试",
                )
            )


def adapt_mock_exam(mock_exam, study_goal: StudyGoal, exam_type: ExamType) -> None:
    for question in mock_exam.questions:
        question.type = question.type or question.question_type
        question.related_topic = question.related_topic or question.concept or question.chapter
        if study_goal == "past_exam_focused":
            question.source_hint = question.source_hint or "根据往年题型线索生成"
        elif exam_type == "programming":
            question.source_hint = question.source_hint or "根据编程考试常见题型生成"
            if "代码" not in question.question_type and "编程" not in question.question_type:
                question.question_type = "代码阅读/实现训练题"
                question.type = question.question_type
        elif exam_type == "open_book":
            question.source_hint = question.source_hint or "根据开卷考试综合分析需求生成"
        elif exam_type == "closed_book":
            question.source_hint = question.source_hint or "来自闭卷考试高频记忆与快速答题需求"
        else:
            question.source_hint = question.source_hint or "来自材料高频概念和题型线索"


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
    if report.high_frequency_points == [INSUFFICIENT_MESSAGE]:
        report.high_frequency_points = [INSUFFICIENT_MESSAGE]
    else:
        report.high_frequency_points = clean_topic_list(report.high_frequency_points, limit=12) or [INSUFFICIENT_MESSAGE]
    report.sprint_checklist = clean_list(report.sprint_checklist, fallback=INSUFFICIENT_MESSAGE, limit=14)
    report.low_priority = clean_list(report.low_priority, fallback="暂未识别出明确的低优先级专题。")
    report.insufficient_materials = clean_list(report.insufficient_materials)
    for index, chapter in enumerate(report.chapters, start=1):
        chapter.chapter = safe_display_title(chapter.chapter, chapter.keywords, index)
        chapter.importance = max(0, min(100, chapter.importance))
        chapter.weighted_score = max(0, min(100, chapter.weighted_score or chapter.importance))
        chapter.keywords = clean_topic_list(chapter.keywords, limit=12) or [INSUFFICIENT_MESSAGE]
        chapter.formulas = clean_list([clean_formula_text(item) for item in chapter.formulas], limit=8)
        chapter.examples = clean_list(chapter.examples, fallback=INSUFFICIENT_MESSAGE, limit=5)
        chapter.review_advice = clean_text(chapter.review_advice)
    for index, item in enumerate(report.review_order, start=1):
        if is_bad_unit_title(item.chapter):
            item.chapter = f"重要专题 {index}"
    report.review_order = report.review_order[:12]
    report.sprint_plans = report.sprint_plans[:3]
    report.anki_cards = dedupe_anki_cards(report.anki_cards)[:60]
    return report


def dedupe_anki_cards(cards: list[AnkiCard]) -> list[AnkiCard]:
    seen: set[str] = set()
    result: list[AnkiCard] = []
    for card in cards:
        front = clean_text(card.front)
        if not front or front in seen:
            continue
        card.front = front[:120]
        card.back = clean_text(card.back)
        card.tags = card.tags if isinstance(card.tags, str) else " ".join(card.tags)
        seen.add(front)
        result.append(card)
    return result


def safe_display_title(raw_title: str, keywords: list[str], index: int) -> str:
    title = clean_unit_title(raw_title)
    if not is_bad_unit_title(title):
        return title
    semantic_keywords = [
        clean_text(keyword)
        for keyword in keywords
        if keyword and keyword != INSUFFICIENT_MESSAGE and not is_bad_unit_title(keyword)
    ]
    if semantic_keywords:
        return "、".join(semantic_keywords[:3])
    return f"重要专题 {max(1, index)}"


def goal_exam_checklist_prefix(study_goal: StudyGoal, exam_type: ExamType) -> list[str]:
    items: list[str] = []
    if study_goal == "one_day_sprint":
        items.append("1 天速通：先背最高频定义/公式，再完成少量高价值题，最后用 Anki 复盘错点。")
    elif study_goal == "three_day_sprint":
        items.append("3 天冲刺：Day 1 打基础，Day 2 刷题型，Day 3 模拟和查漏补缺。")
    elif study_goal == "seven_day_plan":
        items.append("7 天系统复习：前 4 天搭结构，第 5-6 天训练题型，第 7 天模拟和回顾。")
    elif study_goal == "anki_focused":
        items.append("Anki 整理：优先把定义、公式、易混点和题型套路拆成可复习卡片。")
    elif study_goal == "practice_heavy":
        items.append("重点刷题：按题型训练，做完必须核对答案和解析。")
    elif study_goal == "past_exam_focused":
        items.append("往年题抓重点：优先复习在往年题或疑似试卷中反复出现的考点，不承诺押题。")
    if exam_type == "programming":
        items.append("编程考试：额外练习代码阅读、输出判断、函数补全、Debug 和边界条件。")
    elif exam_type == "closed_book":
        items.append("闭卷考试：优先背定义、公式、易混点和高频简答框架。")
    elif exam_type == "open_book":
        items.append("开卷考试：重点训练材料定位、综合分析和答题框架。")
    elif exam_type == "essay_based":
        items.append("论述型考试：为高频主题准备比较分析框架、论点和例证。")
    return items


def study_goal_summary(study_goal: StudyGoal) -> str:
    return {
        "one_day_sprint": "本次按 1 天速通组织，突出必背和高价值题。",
        "three_day_sprint": "本次按 3 天冲刺组织，兼顾基础、刷题和模拟。",
        "seven_day_plan": "本次按 7 天系统复习组织，强调完整结构和持续复盘。",
        "memorization": "本次偏重点背诵，突出定义、公式、对比和易混点。",
        "practice_heavy": "本次偏重点刷题，突出题型、步骤和解析。",
        "anki_focused": "本次偏向 Anki 整理，增加可导出的记忆卡片。",
        "past_exam_focused": "本次偏向根据往年题抓重点，提高题型线索权重。",
        "balanced": "本次按平衡模式组织，兼顾专题、题型、模拟卷和 Anki。",
    }.get(study_goal, "")


def exam_type_summary(exam_type: ExamType) -> str:
    return {
        "closed_book": "考试类型按闭卷处理，强调记忆、定义、公式和快速答题。",
        "open_book": "考试类型按开卷处理，强调材料定位、综合分析和答题框架。",
        "programming": "考试类型按编程考试处理，强调代码阅读、调试、实现和边界条件。",
        "lab_exam": "考试类型按实验考试处理，强调原理、步骤、现象、数据和误差。",
        "essay_based": "考试类型按论文/论述型处理，强调论述框架和论据组织。",
        "oral_presentation": "考试类型按口试/展示处理，强调表达结构和关键概念解释。",
        "coursework_report": "考试类型按课程论文/报告处理，强调结构、证据和论证。",
        "computer_based": "考试类型按机考处理，强调题型速度和步骤稳定性。",
        "unknown": "",
    }.get(exam_type, "")
