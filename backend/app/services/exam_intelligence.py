from collections import Counter, defaultdict
from dataclasses import dataclass

from app.schemas.review import (
    AnkiCard,
    ChapterReview,
    GeneratedExamQuestion,
    GeneratedMockExam,
    PastExamAnalysis,
    PastExamFileAnalysis,
    PastExamTopic,
    ReviewPlanItem,
    SprintPlan,
)
from app.services.chapter_extractor import ChapterSection, DEFAULT_CHAPTER
from app.services.concept_extractor import extract_keywords
from app.services.question_extractor import extract_questions
from app.services.text_cleaner import clean_list, clean_text


QUESTION_TYPE_WEIGHTS = {
    "选择题": 1.0,
    "填空题": 0.9,
    "判断题": 0.7,
    "计算题": 1.3,
    "简答题": 1.4,
    "论述题": 1.7,
    "未知": 0.6,
}


@dataclass(frozen=True)
class SourceMaterial:
    filename: str
    text: str


def build_exam_intelligence(
    chapters: list[ChapterSection],
    chapter_reviews: list[ChapterReview],
    file_texts: list[tuple[str, str]] | None,
) -> tuple[PastExamAnalysis, list[ReviewPlanItem], list[SprintPlan], GeneratedMockExam, list[AnkiCard]]:
    sources = [SourceMaterial(filename=name, text=text) for name, text in (file_texts or [])]
    if not sources:
        sources = [SourceMaterial(filename="combined_materials", text="\n\n".join(ch.text for ch in chapters))]

    past_exam_sources = [source for source in sources if looks_like_past_exam(source.filename, source.text)]
    past_exam_analysis = analyze_past_exams(past_exam_sources, chapters)
    apply_priority_scores(chapter_reviews, chapters, sources, past_exam_analysis)
    review_order = build_review_order(chapter_reviews)
    sprint_plans = build_sprint_plans(review_order)
    mock_exam = build_balanced_mock_exam(chapter_reviews, past_exam_analysis)
    anki_cards = build_anki_cards(chapter_reviews, past_exam_analysis)
    return past_exam_analysis, review_order, sprint_plans, mock_exam, anki_cards


def looks_like_past_exam(filename: str, text: str) -> bool:
    lowered_name = filename.lower()
    lowered_text = text.lower()
    name_hits = sum(
        token in lowered_name
        for token in ["exam", "past", "paper", "mock", "quiz", "test", "试卷", "真题", "往年", "考试"]
    )
    text_hits = sum(
        token in lowered_text
        for token in [
            "multiple choice",
            "fill in the blank",
            "short answer",
            "essay",
            "answer key",
            "选择题",
            "填空题",
            "简答题",
            "论述题",
            "总分",
            "考试时间",
        ]
    )
    question_count = len(extract_questions(text))
    return name_hits >= 1 or text_hits >= 2 or question_count >= 4


def analyze_past_exams(
    sources: list[SourceMaterial],
    chapters: list[ChapterSection],
) -> PastExamAnalysis:
    topic_scores: dict[tuple[str, str], int] = defaultdict(int)
    topic_types: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    topic_keywords: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    detected_files: list[PastExamFileAnalysis] = []

    for source in sources:
        questions = extract_questions(source.text)
        question_types = Counter(str(question.question_type) for question in questions)
        matched_chapters = Counter(question.chapter or infer_chapter_from_keywords(question.keywords, chapters) for question in questions)
        confidence = min(100, 35 + len(questions) * 8 + len(question_types) * 8)

        detected_files.append(
            PastExamFileAnalysis(
                filename=source.filename,
                confidence=confidence,
                question_count=len(questions),
                question_types=[item for item, _ in question_types.most_common()],
                matched_chapters=[item for item, _ in matched_chapters.most_common(5)],
            )
        )

        for question in questions:
            chapter = question.chapter or infer_chapter_from_keywords(question.keywords, chapters)
            keywords = clean_list(question.keywords or extract_keywords(question.question, limit=4), limit=4)
            if not keywords:
                keywords = [chapter]
            for keyword in keywords:
                key = (chapter or DEFAULT_CHAPTER, keyword)
                topic_scores[key] += int(question_type_weight(str(question.question_type)) * 10)
                topic_types[key][str(question.question_type)] += 1
                topic_keywords[key][keyword] += 1

    ranked_topics = sorted(topic_scores.items(), key=lambda item: item[1], reverse=True)
    topics = [
        PastExamTopic(
            topic=clean_text(topic),
            chapter=clean_text(chapter or DEFAULT_CHAPTER),
            frequency=max(1, score // 10),
            question_types=[item for item, _ in topic_types[(chapter, topic)].most_common()],
            keywords=[item for item, _ in topic_keywords[(chapter, topic)].most_common(5)],
        )
        for (chapter, topic), score in ranked_topics[:10]
    ]

    if detected_files:
        summary = f"已识别 {len(detected_files)} 个疑似往年题文件，并整理出 {len(topics)} 个反复出现的考试考点。"
    else:
        summary = "暂未识别出明显的往年题文件。上传往年题后，可以获得更准确的高频考点分析。"

    return PastExamAnalysis(
        detected_files=detected_files,
        high_frequency_topics=topics,
        summary=summary,
    )


def apply_priority_scores(
    chapter_reviews: list[ChapterReview],
    chapters: list[ChapterSection],
    sources: list[SourceMaterial],
    past_exam_analysis: PastExamAnalysis,
) -> None:
    non_exam_text = "\n\n".join(source.text for source in sources if not looks_like_past_exam(source.filename, source.text))
    if not non_exam_text:
        non_exam_text = "\n\n".join(source.text for source in sources)

    exam_topic_by_chapter = Counter()
    type_weight_by_chapter = Counter()
    for topic in past_exam_analysis.high_frequency_topics:
        exam_topic_by_chapter[topic.chapter] += topic.frequency
        type_weight_by_chapter[topic.chapter] += sum(question_type_weight(item) for item in topic.question_types) or 1

    max_material = 1
    material_counts: dict[str, int] = {}
    for review in chapter_reviews:
        title_hits = non_exam_text.lower().count(review.chapter.lower()) if review.chapter else 0
        keyword_hits = sum(non_exam_text.lower().count(keyword.lower()) for keyword in review.keywords[:8])
        chapter_text_hits = next((len(ch.text) // 180 for ch in chapters if ch.title == review.chapter), 0)
        material_count = max(0, title_hits + keyword_hits + chapter_text_hits)
        material_counts[review.chapter] = material_count
        max_material = max(max_material, material_count)

    max_exam = max(exam_topic_by_chapter.values(), default=1)
    max_type_weight = max(type_weight_by_chapter.values(), default=1)

    for review in chapter_reviews:
        material_frequency = material_counts.get(review.chapter, 0)
        past_exam_frequency = exam_topic_by_chapter.get(review.chapter, 0)
        material_score = (material_frequency / max_material) * 35
        exam_score = (past_exam_frequency / max_exam) * 45 if max_exam else 0
        type_score = (type_weight_by_chapter.get(review.chapter, 0) / max_type_weight) * 20 if max_type_weight else 0
        score = int(round(material_score + exam_score + type_score))
        review.material_frequency = material_frequency
        review.past_exam_frequency = past_exam_frequency
        review.weighted_score = min(100, max(score, review.importance))
        review.importance = review.weighted_score

    chapter_reviews.sort(key=lambda item: item.importance, reverse=True)


def build_review_order(chapter_reviews: list[ChapterReview]) -> list[ReviewPlanItem]:
    return [
        ReviewPlanItem(
            chapter=review.chapter,
            importance=review.importance,
            reason=(
                f"材料命中 {review.material_frequency} 次，往年题命中 {review.past_exam_frequency} 次，"
                f"题型包括 {'、'.join(str(item) for item in review.question_types) or '未知'}。"
            ),
        )
        for review in sorted(chapter_reviews, key=lambda item: item.importance, reverse=True)
    ]


def build_sprint_plans(review_order: list[ReviewPlanItem]) -> list[SprintPlan]:
    top = review_order[:6] or [ReviewPlanItem(chapter=DEFAULT_CHAPTER, importance=0, reason="当前材料不足。")]
    one_day = [f"{index + 1}. 优先复习 {item.chapter}（{item.importance}/100）。" for index, item in enumerate(top[:3])]

    three_day = []
    chunks = [top[:2], top[2:4], top[4:6]]
    for day, items in enumerate(chunks, start=1):
        names = "、".join(item.chapter for item in items) if items else "错题、薄弱点和导出报告"
        three_day.append(f"第 {day} 天：集中复习 {names}；最后用主动回忆题自测。")

    seven_day = []
    for day in range(1, 8):
        item = top[(day - 1) % len(top)]
        seven_day.append(f"第 {day} 天：复习 {item.chapter}，制作记忆卡片，并重做 1 道考试风格题。")

    return [
        SprintPlan(days=1, title="1 天紧急冲刺", schedule=one_day),
        SprintPlan(days=3, title="3 天均衡冲刺", schedule=three_day),
        SprintPlan(days=7, title="7 天完整冲刺", schedule=seven_day),
    ]


def build_balanced_mock_exam(
    chapter_reviews: list[ChapterReview],
    past_exam_analysis: PastExamAnalysis,
) -> GeneratedMockExam:
    ordered = sorted(chapter_reviews, key=lambda item: item.importance, reverse=True)
    topics = past_exam_analysis.high_frequency_topics
    if not ordered:
        return GeneratedMockExam(title="模拟卷", questions=[])

    specs = [
        ("选择题", 4),
        ("填空题", 3),
        ("简答题", 3),
        ("论述题", 1),
    ]
    questions: list[GeneratedExamQuestion] = []
    topic_index = 0
    for question_type, count in specs:
        for _ in range(count):
            chapter = ordered[len(questions) % len(ordered)]
            concept = (
                topics[topic_index % len(topics)].topic
                if topics
                else (chapter.keywords[0] if chapter.keywords else chapter.chapter)
            )
            topic_index += 1
            questions.append(
                GeneratedExamQuestion(
                    question_type=question_type,
                    question=make_mock_question(question_type, chapter.chapter, concept),
                    answer=make_mock_answer(question_type, chapter.chapter, concept),
                    chapter=chapter.chapter,
                    concept=concept,
                )
            )
    return GeneratedMockExam(title="ExamForge AI 模拟卷", questions=questions)


def build_anki_cards(
    chapter_reviews: list[ChapterReview],
    past_exam_analysis: PastExamAnalysis,
) -> list[AnkiCard]:
    cards: list[AnkiCard] = []
    for topic in past_exam_analysis.high_frequency_topics[:12]:
        cards.append(
            AnkiCard(
                front=f"关于 {topic.topic} 需要掌握什么？",
                back=f"所属章节：{topic.chapter}。常见题型：{'、'.join(topic.question_types) or '未知'}。",
                tags=tagify(topic.chapter, "past_exam"),
            )
        )

    for chapter in chapter_reviews:
        for keyword in chapter.keywords[:3]:
            cards.append(
                AnkiCard(
                    front=f"解释：{keyword}",
                    back=f"{keyword} 是 {chapter.chapter} 的关键概念。复习建议：{chapter.review_advice}",
                    tags=tagify(chapter.chapter, "concept"),
                )
            )
            if len(cards) >= 24:
                return cards
    return cards


def infer_chapter_from_keywords(keywords: list[str], chapters: list[ChapterSection]) -> str:
    if not chapters:
        return DEFAULT_CHAPTER
    keyword_set = {keyword.lower() for keyword in keywords}
    best = chapters[0].title
    best_score = -1
    for chapter in chapters:
        chapter_words = {keyword.lower() for keyword in extract_keywords(chapter.text, limit=20)}
        score = len(keyword_set & chapter_words)
        if score > best_score:
            best = chapter.title
            best_score = score
    return best or DEFAULT_CHAPTER


def question_type_weight(question_type: str) -> float:
    normalized = normalize_question_type(question_type)
    return QUESTION_TYPE_WEIGHTS.get(normalized, QUESTION_TYPE_WEIGHTS["未知"])


def normalize_question_type(question_type: str) -> str:
    lower = question_type.lower()
    if "选择" in question_type or "choice" in lower:
        return "选择题"
    if "填" in question_type or "blank" in lower:
        return "填空题"
    if "判断" in question_type:
        return "判断题"
    if "计算" in question_type:
        return "计算题"
    if "论" in question_type or "essay" in lower:
        return "论述题"
    if "答" in question_type or "answer" in lower:
        return "简答题"
    return "未知"


def make_mock_question(question_type: str, chapter: str, concept: str) -> str:
    if question_type == "选择题":
        return f"以下哪一项最能解释 {chapter} 中的“{concept}”？A. 核心定义 B. 无关细节 C. 相反说法 D. 随机例子"
    if question_type == "填空题":
        return f"在 {chapter} 中，与“{concept}”相关的核心结论是：______。"
    if question_type == "论述题":
        return f"结合材料论述“{concept}”如何影响 {chapter} 的主要考试逻辑，并说明常见误区。"
    return f"解释 {chapter} 中的“{concept}”，并说明它可能如何出现在考试题中。"


def make_mock_answer(question_type: str, chapter: str, concept: str) -> str:
    if question_type == "选择题":
        return f"参考答案：A。应选择最符合“{concept}”定义、条件和考试语境的选项。"
    if question_type == "填空题":
        return f"参考答案：填写 {chapter} 中与“{concept}”对应的核心术语或结论。"
    if question_type == "论述题":
        return f"参考答案：先定义“{concept}”，再联系 {chapter}，比较相关概念，并指出常见考试陷阱。"
    return f"参考答案：说明“{concept}”的定义、在 {chapter} 中的作用，并补充一个例子或适用边界。"


def tagify(chapter: str, suffix: str) -> str:
    safe = "".join(char.lower() if char.isalnum() else "_" for char in chapter).strip("_")
    return f"{safe or 'chapter'} {suffix}"
