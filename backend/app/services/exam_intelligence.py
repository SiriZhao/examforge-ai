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
from app.services.concept_extractor import extract_formulas, extract_keywords
from app.services.question_extractor import extract_questions
from app.services.text_cleaner import clean_text
from app.services.text_quality import clean_topic_list, clean_topic_name, has_mojibake, looks_like_formula_fragment


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
    mock_exam = build_evidence_based_mock_exam(chapter_reviews, past_exam_analysis, past_exam_sources)
    anki_cards = build_anki_cards(chapter_reviews, past_exam_analysis)
    return past_exam_analysis, review_order, sprint_plans, mock_exam, anki_cards


def looks_like_past_exam(filename: str, text: str) -> bool:
    lowered_name = filename.lower()
    lowered_text = text.lower()
    name_hits = sum(token in lowered_name for token in ["exam", "past", "paper", "mock", "quiz", "test", "试卷", "真题", "往年", "考试", "练习"])
    text_hits = sum(
        token in lowered_text
        for token in ["multiple choice", "fill in", "short answer", "essay", "answer key", "选择", "填空", "判断", "简答", "论述", "计算", "证明", "总分"]
    )
    return name_hits >= 1 or text_hits >= 2 or len(extract_questions(text)) >= 4


def analyze_past_exams(sources: list[SourceMaterial], chapters: list[ChapterSection]) -> PastExamAnalysis:
    topic_scores: dict[tuple[str, str], int] = defaultdict(int)
    topic_types: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    topic_keywords: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    detected_files: list[PastExamFileAnalysis] = []

    for source in sources:
        questions = extract_questions(source.text)
        question_types = Counter(infer_natural_question_type(question.question, str(question.question_type)) for question in questions)
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
            chapter = clean_topic_name(question.chapter or infer_chapter_from_keywords(question.keywords, chapters)) or DEFAULT_CHAPTER
            keywords = clean_topic_list(question.keywords or extract_keywords(question.question, limit=6), limit=5)
            if not keywords:
                keywords = [clean_topic_name(chapter) or DEFAULT_CHAPTER]
            q_type = infer_natural_question_type(question.question, str(question.question_type))
            for keyword in keywords:
                key = (chapter, keyword)
                topic_scores[key] += 10 + question_type_weight(q_type)
                topic_types[key][q_type] += 1
                topic_keywords[key][keyword] += 1

    topics = []
    for (chapter, topic), score in sorted(topic_scores.items(), key=lambda item: item[1], reverse=True)[:12]:
        if not clean_topic_name(topic):
            continue
        topics.append(
            PastExamTopic(
                topic=topic,
                chapter=chapter,
                frequency=max(1, score // 10),
                question_types=[item for item, _ in topic_types[(chapter, topic)].most_common()],
                keywords=[item for item, _ in topic_keywords[(chapter, topic)].most_common(5)],
            )
        )

    summary = (
        f"已识别 {len(detected_files)} 个疑似往年题/练习题文件，并整理出 {len(topics)} 个反复出现的题型与考点线索。"
        if detected_files
        else "暂未识别出明确往年题文件。上传往年题后，系统可以更准确反推题型并生成模拟卷。"
    )
    return PastExamAnalysis(detected_files=detected_files, high_frequency_topics=topics, summary=summary)


def infer_natural_question_type(question: str, detected_type: str = "") -> str:
    text = clean_text(question)
    lower = text.lower()
    if "代码" in text or "程序" in text or "输出" in text or "debug" in lower:
        return "代码阅读与调试题"
    if "证明" in text or "推导" in text:
        return "推导证明题"
    if "计算" in text or "求" in text or any(symbol in text for symbol in ["=", "P(", "E(", "Var", "∫", "∑"]):
        if "概率" in text or "随机" in text or "分布" in text:
            return "概率建模与计算题"
        return "公式应用计算题"
    if "分析" in text or "解释" in text or "为什么" in text or "说明" in text:
        return "材料分析与解释题"
    if "比较" in text or "区别" in text or "辨析" in text:
        return "概念辨析题"
    if "实验" in text or "现象" in text or "误差" in text:
        return "实验观察分析题"
    if "选择" in detected_type or "choice" in lower:
        return "材料选择判断题"
    if "填" in detected_type or "blank" in lower:
        return "关键概念填空题"
    if "论述" in detected_type or "essay" in lower:
        return "论述框架题"
    return clean_topic_name(detected_type) or "综合问答题"


def question_type_weight(question_type: str) -> int:
    if any(token in question_type for token in ["计算", "证明", "推导", "编程", "实验", "分析"]):
        return 6
    if any(token in question_type for token in ["论述", "辨析"]):
        return 5
    return 3


def apply_priority_scores(
    chapter_reviews: list[ChapterReview],
    chapters: list[ChapterSection],
    sources: list[SourceMaterial],
    past_exam_analysis: PastExamAnalysis,
) -> None:
    all_text = "\n\n".join(source.text for source in sources)
    exam_topic_by_chapter = Counter()
    for topic in past_exam_analysis.high_frequency_topics:
        exam_topic_by_chapter[topic.chapter] += topic.frequency
    max_exam = max(exam_topic_by_chapter.values(), default=1)

    for review in chapter_reviews:
        keyword_hits = sum(all_text.lower().count(keyword.lower()) for keyword in review.keywords[:8])
        material_score = min(35, keyword_hits)
        exam_score = int((exam_topic_by_chapter.get(review.chapter, 0) / max_exam) * 45) if max_exam else 0
        score = max(review.importance, material_score + exam_score + min(20, len(review.keywords) * 2))
        review.material_frequency = keyword_hits
        review.past_exam_frequency = exam_topic_by_chapter.get(review.chapter, 0)
        review.weighted_score = min(100, score)
        review.importance = review.weighted_score
    chapter_reviews.sort(key=lambda item: item.importance, reverse=True)


def build_review_order(chapter_reviews: list[ChapterReview]) -> list[ReviewPlanItem]:
    return [
        ReviewPlanItem(
            chapter=review.chapter,
            importance=review.importance,
            reason=f"材料命中 {review.material_frequency} 次，往年题线索 {review.past_exam_frequency} 次；建议结合题型和错题优先复习。",
        )
        for review in sorted(chapter_reviews, key=lambda item: item.importance, reverse=True)
    ]


def build_sprint_plans(review_order: list[ReviewPlanItem]) -> list[SprintPlan]:
    top = review_order[:6] or [ReviewPlanItem(chapter=DEFAULT_CHAPTER, importance=0, reason="当前材料较少。")]
    return [
        SprintPlan(days=1, title="1 天速通计划", schedule=[f"优先复习 {item.chapter}，再做 1 道对应练习题。" for item in top[:3]]),
        SprintPlan(days=3, title="3 天冲刺计划", schedule=[
            "Day 1：整理核心概念和公式，完成 Anki 首轮复习。",
            "Day 2：按题型练习，重点处理往年题线索。",
            "Day 3：完成保守模拟卷，核对答案并回看易错点。",
        ]),
        SprintPlan(days=7, title="7 天系统复习计划", schedule=[
            "前 3 天：按专题建立知识结构。",
            "第 4-5 天：按题型训练并补足薄弱点。",
            "第 6 天：集中背诵 Anki 和公式/定义。",
            "第 7 天：做模拟卷并整理最后清单。",
        ]),
    ]


def build_evidence_based_mock_exam(
    chapter_reviews: list[ChapterReview],
    past_exam_analysis: PastExamAnalysis,
    past_exam_sources: list[SourceMaterial],
) -> GeneratedMockExam:
    questions: list[GeneratedExamQuestion] = []
    source_questions = [question for source in past_exam_sources for question in extract_questions(source.text)]
    type_order = [item for file in past_exam_analysis.detected_files for item in file.question_types]
    topic_order = past_exam_analysis.high_frequency_topics

    if source_questions:
        seen_types: set[str] = set()
        for index, source_question in enumerate(source_questions[:8], start=1):
            q_type = infer_natural_question_type(source_question.question, str(source_question.question_type))
            topic = clean_topic_list(source_question.keywords, limit=1)
            chapter = clean_topic_name(source_question.chapter) or (chapter_reviews[0].chapter if chapter_reviews else DEFAULT_CHAPTER)
            concept = topic[0] if topic else chapter
            if q_type in seen_types and len(questions) >= 3:
                continue
            seen_types.add(q_type)
            questions.append(
                GeneratedExamQuestion(
                    question_type=q_type,
                    type=q_type,
                    difficulty=source_question.difficulty,
                    question=build_practice_question_from_source(source_question.question, q_type, concept),
                    answer=build_grounded_answer(q_type, concept, chapter),
                    explanation=f"此题根据上传材料中的真实题干结构改写，重点检查 {concept} 的理解和应用。",
                    chapter=chapter,
                    concept=concept,
                    related_topic=concept,
                    source_hint="已参考上传的往年题型线索生成",
                    source_basis="来自往年题型线索",
                )
            )
            if len(questions) >= 6:
                break

    if len(questions) < 4:
        for item in topic_order[:6]:
            q_type = item.question_types[0] if item.question_types else "综合问答题"
            q_type = infer_natural_question_type(" ".join([item.topic, q_type]), q_type)
            questions.append(
                GeneratedExamQuestion(
                    question_type=q_type,
                    type=q_type,
                    difficulty="中等",
                    question=f"围绕“{item.topic}”，说明其核心含义、适用条件，并结合材料给出一个可能的考查角度。",
                    answer=f"应先解释 {item.topic} 的定义或方法，再说明它在 {item.chapter} 中的作用，最后补充典型考法或易错点。",
                    explanation="该题来自往年题高频考点线索，用于训练同类考法的答题结构。",
                    chapter=item.chapter,
                    concept=item.topic,
                    related_topic=item.topic,
                    source_hint="已参考上传的往年题型线索生成",
                    source_basis="来自往年题型线索",
                )
            )
            if len(questions) >= 6:
                break

    if not questions:
        for review in chapter_reviews[:4]:
            concept = next((item for item in review.keywords if clean_topic_name(item)), review.chapter)
            questions.append(
                conservative_question(review.chapter, concept)
            )

    return GeneratedMockExam(title="基于材料的保守练习卷", questions=dedupe_questions(questions)[:8])


def build_practice_question_from_source(source_question: str, question_type: str, concept: str) -> str:
    clean = clean_text(source_question)
    if len(clean) >= 18 and not has_mojibake(clean) and not looks_like_formula_fragment(clean):
        return f"参考同类题型：{clean[:180]}"
    return f"根据上传题型线索，围绕“{concept}”完成一道{question_type}，要求写出关键步骤和理由。"


def build_grounded_answer(question_type: str, concept: str, chapter: str) -> str:
    return f"参考答案应包含：1. 明确 {concept} 的含义；2. 结合 {chapter} 中的材料证据说明解题思路；3. 给出结论并标出易错点。"


def conservative_question(chapter: str, concept: str) -> GeneratedExamQuestion:
    return GeneratedExamQuestion(
        question_type="基于材料生成的保守练习题",
        type="基于材料生成的保守练习题",
        difficulty="基础",
        question=f"根据材料，解释“{concept}”在“{chapter}”中的含义、作用和一个可能考法。",
        answer=f"应回答 {concept} 的核心定义或方法，说明它与 {chapter} 的关系，并补充材料中出现的关键词或例题线索。",
        explanation="当前材料不足以稳定还原真实题型，因此使用保守练习题，避免编造往年题形式。",
        chapter=chapter,
        concept=concept,
        related_topic=concept,
        source_hint="基于材料生成，非真实往年题",
        source_basis="基于材料生成，非真实往年题",
    )


def dedupe_questions(questions: list[GeneratedExamQuestion]) -> list[GeneratedExamQuestion]:
    result: list[GeneratedExamQuestion] = []
    seen: set[str] = set()
    for question in questions:
        key = clean_text(question.question)[:80]
        if key in seen:
            continue
        seen.add(key)
        result.append(question)
    return result


def build_anki_cards(chapter_reviews: list[ChapterReview], past_exam_analysis: PastExamAnalysis) -> list[AnkiCard]:
    cards: list[AnkiCard] = []
    for topic in past_exam_analysis.high_frequency_topics[:10]:
        cards.append(
            AnkiCard(
                front=f"{topic.topic} 常见考法是什么？",
                back=f"{topic.topic} 常与 {topic.chapter} 相关。复习时先掌握定义或方法，再练习 {', '.join(topic.question_types) or '材料分析题'}，注意写出依据和步骤。",
                tags=tagify(topic.chapter, "题型线索"),
                card_type="question_pattern",
                priority=85,
                source_hint="来自往年题型线索",
            )
        )

    for chapter in chapter_reviews:
        formulas = [item for item in chapter.formulas if item]
        for formula in formulas[:2]:
            cards.append(
                AnkiCard(
                    front=f"{chapter.chapter} 中公式“{formula[:32]}”如何使用？",
                    back=f"先说明公式适用条件，再列出变量含义，最后结合题目数据代入。若 OCR 公式不完整，请回到原材料核对。",
                    tags=tagify(chapter.chapter, "公式"),
                    card_type="formula",
                    priority=80,
                    source_hint="来自材料公式/方法线索",
                )
            )
        for keyword in clean_topic_list(chapter.keywords, limit=3):
            cards.append(
                AnkiCard(
                    front=f"{keyword} 与 {chapter.chapter} 的关系是什么？",
                    back=f"{keyword} 是复习“{chapter.chapter}”时需要定位的核心概念。答题时应说明其定义、适用场景，并结合材料中的题干或例子展开。",
                    tags=tagify(chapter.chapter, "概念"),
                    card_type="definition",
                    priority=72,
                    source_hint="来自材料关键词线索",
                )
            )
            if len(cards) >= 36:
                return dedupe_anki(cards)
    return dedupe_anki(cards)


def dedupe_anki(cards: list[AnkiCard]) -> list[AnkiCard]:
    result: list[AnkiCard] = []
    seen: set[str] = set()
    for card in cards:
        if "关于 " in card.front and "需要掌握什么" in card.front:
            continue
        if len(card.front) < 6 or len(card.back) < 18:
            continue
        key = card.front.lower()
        if key in seen:
            continue
        seen.add(key)
        result.append(card)
    return result


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


def tagify(chapter: str, suffix: str) -> str:
    pieces = clean_topic_list([chapter, suffix], limit=2)
    return " ".join(pieces) or "ExamForge"
