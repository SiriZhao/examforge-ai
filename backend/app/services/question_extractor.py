import re

from app.schemas.review import DifficultyLevel, ExamQuestion, QuestionType
from app.services.chapter_extractor import DEFAULT_CHAPTER, extract_chapters
from app.services.concept_extractor import extract_keywords
from app.services.text_cleaner import clean_text

QUESTION_TYPE_PATTERNS: list[tuple[QuestionType, re.Pattern[str]]] = [
    ("选择题", re.compile(r"(选择题|单选|多选|请选择|下列.*(?:正确|错误)|\b[A-D][.、])")),
    ("填空题", re.compile(r"(填空题|填空|____|_{2,}|（\s*）|\(\s*\))")),
    ("判断题", re.compile(r"(判断题|判断|对错|正确与否|√|×)")),
    ("计算题", re.compile(r"(计算题|计算|求解|证明|推导|公式|=|\+|-|\*|/|\^)")),
    ("简答题", re.compile(r"(简答题|简述|说明|解释|为什么|如何理解)")),
    ("论述题", re.compile(r"(论述题|论述|分析|评价|结合.*谈|综合阐述)")),
]

QUESTION_START_PATTERN = re.compile(
    r"^\s*(?:\d+[.、]|[（(]?\d+[）)]|[一二三四五六七八九十]+[、.])\s*(.+)"
)
QUESTION_LABEL_PATTERN = re.compile(
    r"(选择题|单选|多选|填空题|判断题|计算题|简答题|论述题)"
)


def extract_questions(text: str) -> list[ExamQuestion]:
    questions: list[ExamQuestion] = []
    for section in extract_chapters(text):
        chunks = split_question_chunks(section.text)
        for chunk in chunks:
            question = clean_text(chunk)
            if not question:
                continue
            questions.append(
                ExamQuestion(
                    question=question,
                    question_type=detect_question_type(question),
                    chapter=section.title if section.title else DEFAULT_CHAPTER,
                    difficulty=estimate_difficulty(question),
                    keywords=extract_keywords(question, limit=6),
                )
            )
    return questions


def split_question_chunks(text: str) -> list[str]:
    chunks: list[str] = []
    current: list[str] = []

    for line in text.splitlines():
        stripped = clean_text(line)
        if not stripped:
            continue
        if QUESTION_START_PATTERN.match(stripped) and current:
            chunks.append("\n".join(current))
            current = [stripped]
        else:
            current.append(stripped)

    if current:
        chunks.append("\n".join(current))

    return [chunk for chunk in chunks if looks_like_question(chunk)]


def looks_like_question(text: str) -> bool:
    cleaned = clean_text(text)
    if QUESTION_LABEL_PATTERN.search(cleaned):
        return True
    return bool(QUESTION_START_PATTERN.match(cleaned)) and len(cleaned) >= 8


def detect_question_type(text: str) -> QuestionType:
    for question_type, pattern in QUESTION_TYPE_PATTERNS:
        if pattern.search(text):
            return question_type
    return "未知"


def estimate_difficulty(text: str) -> DifficultyLevel:
    if re.search(r"(综合|推导|证明|论述|设计|分析|评价|复杂)", text):
        return "困难"
    if re.search(r"(计算|解释|比较|说明|应用|简述)", text):
        return "中等"
    if len(text) <= 40 or re.search(r"(选择|填空|判断)", text):
        return "简单"
    return "中等"
