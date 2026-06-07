import re
from dataclasses import dataclass

from app.services.text_cleaner import clean_text

DEFAULT_CHAPTER = "未识别章节"

CHAPTER_PATTERNS = [
    re.compile(r"^\s*((?:第[一二三四五六七八九十百\d]+[章节篇])\s*[^\n]{0,40})\s*$"),
    re.compile(r"^\s*(Chapter\s+\d+[^\n]{0,50})\s*$", re.IGNORECASE),
    re.compile(r"^\s*(\d+(?:\.\d+){0,2}\s+[^\n]{2,50})\s*$"),
]
INLINE_CHAPTER_PATTERN = re.compile(
    r"^\s*((?:第[一二三四五六七八九十百\d]+[章节篇])\s*[^：:。]{0,24}?)(?=\s*(?:重点|考点|内容|[:：]|$))(.*)$"
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
        inline_match = INLINE_CHAPTER_PATTERN.match(line.strip())
        if inline_match:
            if current_lines:
                sections.append(
                    ChapterSection(
                        title=current_title,
                        text="\n".join(current_lines).strip(),
                    )
                )
            current_title = normalize_chapter_title(inline_match.group(1))
            rest = clean_text(inline_match.group(2))
            current_lines = [rest] if rest else []
            continue

        title = detect_chapter_title(line)
        if title:
            if current_lines:
                sections.append(
                    ChapterSection(
                        title=current_title,
                        text="\n".join(current_lines).strip(),
                    )
                )
            current_title = title
            current_lines = []
        else:
            current_lines.append(line)

    if current_lines or not sections:
        sections.append(
            ChapterSection(title=current_title, text="\n".join(current_lines).strip())
        )

    return [section for section in sections if section.text or section.title != DEFAULT_CHAPTER]


def detect_chapter_title(line: str) -> str | None:
    stripped = clean_text(line)
    if not stripped or len(stripped) > 80:
        return None

    for pattern in CHAPTER_PATTERNS:
        match = pattern.match(stripped)
        if match:
            return normalize_chapter_title(match.group(1))

    return None


def normalize_chapter_title(title: str) -> str:
    return clean_text(title.strip(" ：:"))
