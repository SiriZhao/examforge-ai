from __future__ import annotations

import re
from dataclasses import dataclass, field

from app.schemas.review import ReviewReport


@dataclass
class EngineQualityCheck:
    is_empty: bool
    coverage_ratio: float
    missing_sections: list[str] = field(default_factory=list)
    duplicate_sections: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)


def check_output_quality(report: ReviewReport, expected_sections: list[str]) -> EngineQualityCheck:
    body = _report_body(report)
    is_empty = len(body.strip()) < 80
    report_sections = _report_sections(report)
    expected = _unique(expected_sections)
    matched: list[str] = []
    missing: list[str] = []
    normalized_body = _normalize(body)
    for section in expected:
        key = _normalize(section)
        if key and (key in normalized_body or any(_token_overlap(key, _normalize(item)) >= 0.6 for item in report_sections)):
            matched.append(section)
        else:
            missing.append(section)
    coverage = len(matched) / len(expected) if expected else (0.0 if is_empty else 1.0)
    duplicates = _duplicates(report_sections)
    warnings: list[str] = []
    failures: list[str] = []
    if is_empty:
        failures.append("生成内容为空或过短。")
    if len(expected) >= 3 and coverage < 0.5:
        failures.append(f"章节覆盖不足：仅覆盖 {len(matched)}/{len(expected)} 个已识别章节。")
    elif len(expected) >= 2 and coverage < 0.8:
        warnings.append(f"部分章节未覆盖：已覆盖 {len(matched)}/{len(expected)} 个已识别章节。")
    if duplicates:
        warnings.append(f"检测到重复章节或专题：{'、'.join(duplicates[:5])}。")
    return EngineQualityCheck(is_empty, round(coverage, 4), missing, duplicates, warnings, failures)


def _report_body(report: ReviewReport) -> str:
    return "\n".join(
        [
            report.title,
            report.summary,
            report.markdown,
            *[unit.name + " " + " ".join(unit.key_points) for unit in report.study_units],
            *[chapter.chapter + " " + " ".join(chapter.keywords) for chapter in report.chapters],
        ]
    )


def _report_sections(report: ReviewReport) -> list[str]:
    if report.study_units:
        return [unit.name for unit in report.study_units if unit.name.strip()]
    return [chapter.chapter for chapter in report.chapters if chapter.chapter.strip()]


def _duplicates(items: list[str]) -> list[str]:
    duplicates: list[str] = []
    normalized: list[tuple[str, str]] = []
    for item in items:
        key = _normalize(item)
        if any(key == other or _token_overlap(key, other) >= 0.9 for _, other in normalized):
            duplicates.append(item)
        else:
            normalized.append((item, key))
    return duplicates


def _normalize(text: str) -> str:
    return re.sub(r"[^\u4e00-\u9fffA-Za-z0-9]+", "", text).casefold()


def _token_overlap(left: str, right: str) -> float:
    if not left or not right:
        return 0.0
    if left in right or right in left:
        return min(len(left), len(right)) / max(len(left), len(right))
    left_tokens = set(re.findall(r"[\u4e00-\u9fff]{2,4}|[a-z0-9]{3,}", left))
    right_tokens = set(re.findall(r"[\u4e00-\u9fff]{2,4}|[a-z0-9]{3,}", right))
    return len(left_tokens & right_tokens) / max(1, len(left_tokens | right_tokens))


def _unique(items: list[str]) -> list[str]:
    output: list[str] = []
    seen: set[str] = set()
    for item in items:
        key = _normalize(item)
        if key and key not in seen:
            seen.add(key)
            output.append(item)
    return output
