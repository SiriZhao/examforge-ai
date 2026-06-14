import re
from collections import Counter

from app.services.text_cleaner import clean_list, is_noise_term
from app.services.text_quality import clean_formula_text, clean_topic_name

STOPWORDS = {
    "考点",
    "题目",
    "答案",
    "解析",
    "要求",
    "说明",
    "课程",
    "复习",
    "章节",
    "重点",
    "考试",
    "材料",
    "下列",
    "正确",
    "错误",
    "哪些",
    "属于",
    "包括",
    "特征",
    "选择题",
    "填空题",
    "判断题",
    "计算题",
    "简答题",
    "论述题",
}

CHINESE_TERM_PATTERN = re.compile(r"[\u4e00-\u9fff]{2,10}")
ENGLISH_TERM_PATTERN = re.compile(r"\b[A-Za-z][A-Za-z0-9_-]{2,}\b")
FORMULA_PATTERN = re.compile(
    r"(?:[A-Za-z][A-Za-z0-9_]*\s*=+\s*[^，。；;\n]{1,80}|"
    r"[\u4e00-\u9fff]{1,8}\s*[:：]\s*[^，。；;\n]*(?:\+|-|\*|/|\^|=)[^，。；;\n]*)"
)


def extract_keywords(text: str, limit: int = 12) -> list[str]:
    tokens = CHINESE_TERM_PATTERN.findall(text) + ENGLISH_TERM_PATTERN.findall(text)
    candidates = []
    for token in tokens:
        value = token.strip()
        if value in STOPWORDS or value.lower() in STOPWORDS or is_noise_term(value) or not clean_topic_name(value):
            continue
        candidates.append(value)
    counts = Counter(candidates)
    return clean_list([term for term, _ in counts.most_common(limit * 2)], limit=limit)


def extract_formulas(text: str, limit: int = 8) -> list[str]:
    formulas: list[str] = []
    seen: set[str] = set()
    for match in FORMULA_PATTERN.findall(text):
        formula = clean_formula_text(match.strip())
        if formula and formula not in seen:
            formulas.append(formula)
            seen.add(formula)
        if len(formulas) >= limit:
            break
    return formulas
