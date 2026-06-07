from collections import Counter, defaultdict

from app.schemas.review import ExamQuestion, QuestionType
from app.services.chapter_extractor import ChapterSection, DEFAULT_CHAPTER
from app.services.concept_extractor import extract_keywords
from app.services.text_cleaner import clean_list, clean_text, is_noise_term


def match_questions_to_chapters(
    questions: list[ExamQuestion], chapters: list[ChapterSection]
) -> dict[str, list[ExamQuestion]]:
    chapter_titles = [chapter.title for chapter in chapters] or [DEFAULT_CHAPTER]
    mapping: dict[str, list[ExamQuestion]] = {title: [] for title in chapter_titles}

    for question in questions:
        chapter = question.chapter or infer_chapter(question, chapters)
        if chapter not in mapping:
            mapping[chapter] = []
        mapping[chapter].append(question)

    return mapping


def infer_chapter(question: ExamQuestion, chapters: list[ChapterSection]) -> str:
    if not chapters:
        return DEFAULT_CHAPTER

    question_keywords = set(question.keywords)
    best_title = chapters[0].title
    best_score = -1
    for chapter in chapters:
        chapter_keywords = set(extract_keywords(chapter.text, limit=20))
        score = len(question_keywords & chapter_keywords)
        if score > best_score:
            best_title = chapter.title
            best_score = score
    return best_title


def count_question_types(questions: list[ExamQuestion]) -> list[QuestionType]:
    counts = Counter(question.question_type for question in questions)
    return [question_type for question_type, _ in counts.most_common()]


def high_frequency_points(
    chapter_questions: dict[str, list[ExamQuestion]], limit: int = 8
) -> list[str]:
    point_scores: dict[str, int] = defaultdict(int)
    for chapter, questions in chapter_questions.items():
        chapter_name = clean_text(chapter)
        for question in questions:
            for keyword in question.keywords:
                if is_noise_term(keyword):
                    continue
                point_scores[f"{chapter_name}：{clean_text(keyword)}"] += 1

    ranked = sorted(point_scores.items(), key=lambda item: item[1], reverse=True)
    return clean_list([point for point, _ in ranked], limit=limit)
