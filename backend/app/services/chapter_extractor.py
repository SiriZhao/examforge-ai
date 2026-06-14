import re
from dataclasses import dataclass

from app.services.text_cleaner import clean_text
from app.services.text_quality import clean_topic_name, is_bad_heading_or_topic

DEFAULT_CHAPTER = "重要专题 1"

CHAPTER_PATTERNS = [
    re.compile(r"^\s*((?:第\s*)?[\d一二三四五六七八九十百]+[章节篇]\s*[^\n]{0,40})\s*$"),
    re.compile(r"^\s*(Chapter\s+\d+[^\n]{0,50})\s*$", re.IGNORECASE),
    re.compile(r"^\s*(Unit\s+\d+[^\n]{0,50})\s*$", re.IGNORECASE),
    re.compile(r"^\s*(Lecture\s+\d+[^\n]{0,50})\s*$", re.IGNORECASE),
    re.compile(r"^\s*(\d+(?:\.\d+){0,2}\s+[^\n]{2,50})\s*$"),
]

INLINE_CHAPTER_PATTERN = re.compile(
    r"^\s*((?:第\s*)?[\d一二三四五六七八九十百]+[章节篇]\s*[^。！？?：:]{0,32}?)(?=\s*(?:重点|考点|内容|[:：]|$))(.*)$"
)


@dataclass(frozen=True)
class ChapterSection:
    title: str
    text: str


def extract_chapters(text: str) -> list[ChapterSection]:
    lines = text.splitlines()
    sections: list[ChapterSection] = []
    current_title = DEFAULT_CHAPTER
    current_lines: list[str] = []

    for line in lines:
        stripped_line = line.strip()
        inline_match = INLINE_CHAPTER_PATTERN.match(stripped_line)
        if inline_match:
            inline_title = normalize_chapter_title(inline_match.group(1))
            if not is_bad_unit_title(inline_title):
                if current_lines:
                    sections.append(ChapterSection(title=current_title, text="\n".join(current_lines).strip()))
                current_title = inline_title
                rest = clean_text(inline_match.group(2))
                current_lines = [rest] if rest else []
                continue

        title = detect_chapter_title(line)
        if title:
            if current_lines:
                sections.append(ChapterSection(title=current_title, text="\n".join(current_lines).strip()))
            current_title = title
            current_lines = []
        else:
            current_lines.append(line)

    if current_lines or not sections:
        sections.append(ChapterSection(title=current_title, text="\n".join(current_lines).strip()))

    return [section for section in sections if section.text or section.title != DEFAULT_CHAPTER]


def detect_chapter_title(line: str) -> str | None:
    stripped = clean_unit_title(line)
    if is_bad_unit_title(stripped):
        return None

    for pattern in CHAPTER_PATTERNS:
        match = pattern.match(stripped)
        if match:
            title = normalize_chapter_title(match.group(1))
            return None if is_bad_unit_title(title) else title

    if 4 <= len(stripped) <= 32 and semantic_title_line(stripped):
        return stripped
    return None


def semantic_title_line(line: str) -> bool:
    if re.search(r"[。！？?；;]", line):
        return False
    if re.search(r"(定义|原理|方法|模型|分布|函数|结构|分类|实验|概率|统计|算法|系统|概论|复习|总结)$", line):
        return True
    if re.search(r"^[\u4e00-\u9fffA-Za-z0-9\s·-]{4,32}$", line) and re.search(r"[\u4e00-\u9fff]{2,}|[A-Za-z]{4,}", line):
        return True
    return False


def normalize_chapter_title(title: str) -> str:
    return clean_unit_title(title)


def clean_unit_title(title: str) -> str:
    cleaned = clean_text(title)
    cleaned = re.sub(r"^\s*(?:第?\s*)?\d+\s*(?:页|page)?\s*[./、:-]?\s*", "", cleaned, flags=re.I)
    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = cleaned.strip(" -_=+*/\\|:：,，;；.。")
    semantic = clean_topic_name(cleaned)
    return semantic or cleaned


def is_bad_unit_title(title: str) -> bool:
    stripped = clean_text(title).strip()
    if is_bad_heading_or_topic(stripped):
        return True
    if stripped == DEFAULT_CHAPTER:
        return False
    if len(stripped) <= 3 and not re.search(r"[\u4e00-\u9fffA-Za-z]{2,}", stripped):
        return True
    if len(stripped) > 48:
        return True
    if stripped.endswith(("?", "？", ",", "，", ";", "；", "(", "（", "+", "-", "=", "/")):
        return True
    if re.match(r"^(下列|以下|请选择|判断|计算|求|证明|简述|说明|分析)", stripped) and len(stripped) > 12:
        return True
    return False
