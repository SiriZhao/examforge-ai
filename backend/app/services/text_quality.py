import re
from urllib.parse import quote

from app.services.text_cleaner import clean_text

FORMULA_SYMBOLS = set("=+-*/%^√∑∫≤≥<>[]{}()（）,.，;；:：|\\")
BAD_TITLE_LITERALS = {"未识别章节", "其他", "未知", "每题", "的值", "系主任 出卷人", "则袋中白球的", "N/A", "NA", "none", "null"}
MOJIBAKE_MARKERS = ("锟", "鎵", "锘", "Ã", "ä", "å", "ç", "�", "鈭", "鈮", "閿", "莽", "氓")
WINDOWS_FORBIDDEN_FILENAME_CHARS = r'\/:*?"<>|'


def semantic_word_count(text: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]{2,}|[A-Za-z]{3,}", text or ""))


def symbol_ratio(text: str) -> float:
    compact = re.sub(r"\s+", "", text or "")
    if not compact:
        return 1.0
    symbols = sum(1 for char in compact if char in FORMULA_SYMBOLS or char.isdigit())
    return symbols / len(compact)


def has_mojibake(text: str) -> bool:
    return any(marker in (text or "") for marker in MOJIBAKE_MARKERS)


def looks_like_formula_fragment(text: str) -> bool:
    value = clean_text(text or "")
    compact = re.sub(r"\s+", "", value)
    if not compact:
        return False

    formula_signal = bool(
        re.search(
            r"(?:P\s*\(|E\s*\(|Var\s*\(|D\s*\(|\\frac|\\sum|\\int|[=+\-*/%^√∑∫≤≥<>]|[□])",
            value,
            re.I,
        )
    )
    if not formula_signal:
        return False

    words = semantic_word_count(value)
    ratio = symbol_ratio(value)
    if "□" in value:
        return True
    if len(compact) <= 18 and ratio >= 0.45 and words < 2:
        return True
    if ratio >= 0.62 and words < 3:
        return True
    if re.search(r"[=+\-*/%^,，;；:(（]$", compact):
        return True
    if re.fullmatch(r"[\dA-Za-z\s=+\-*/%^√∑∫≤≥<>\[\]{}()（）.,，;；:：|\\□]+", value) and words < 2:
        return True
    return False


def clean_formula_text(text: str) -> str:
    value = clean_text(text or "")
    value = value.replace("□", "")
    value = re.sub(r"\s+", " ", value)
    value = re.sub(r"([=+\-*/%^√∑∫≤≥<>])\s+", r"\1 ", value)
    value = re.sub(r"\s+([=+\-*/%^√∑∫≤≥<>])", r" \1", value)
    return value.strip(" ,，;；")


def is_bad_heading_or_topic(text: str) -> bool:
    value = clean_text(text or "")
    if not value:
        return True
    if value in BAD_TITLE_LITERALS:
        return True
    if has_mojibake(value):
        return True
    if looks_like_formula_fragment(value):
        return True
    if len(value) <= 3 and semantic_word_count(value) == 0:
        return True
    if re.fullmatch(r"[\d\s._#-]+", value):
        return True
    if re.fullmatch(r"[a-fA-F0-9]{8,}", value):
        return True
    if re.search(r"^[A-D][.、)]", value):
        return True
    if re.search(r"[=+\-*/%^,，;；:：({（\[]$", value):
        return True
    if len(value) > 40 and re.search(r"[。！？?]|(下列|以下|计算|证明|分析|求)", value):
        return True
    if value in {"每题", "的值"}:
        return True
    return False


def clean_topic_name(text: str) -> str:
    value = clean_text(text or "")
    value = re.sub(r"^\s*(?:第?\s*)?\d+\s*(?:页|page)?\s*[.、:-]?\s*", "", value, flags=re.I)
    value = re.sub(r"\s+", " ", value)
    value = value.strip(" -_=+*/\\|:：,，;；.。")
    return "" if is_bad_heading_or_topic(value) else value


def clean_topic_list(items: list[str], limit: int = 12) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for item in items:
        value = clean_topic_name(str(item))
        key = value.lower()
        if not value or key in seen:
            continue
        seen.add(key)
        result.append(value)
        if len(result) >= limit:
            break
    return result


def safe_download_stem(course_name: str | None, suffix: str) -> str:
    base = clean_text(course_name or "")
    base = re.sub(f"[{re.escape(WINDOWS_FORBIDDEN_FILENAME_CHARS)}]", "", base)
    base = re.sub(r"\s+", "_", base).strip("._ ")
    if not base:
        base = "ExamForgeAI"
    base = base[:60].strip("._ ")
    return f"{base}_{suffix}"


def safe_download_filename(course_name: str | None, suffix: str, ext: str) -> str:
    extension = ext if ext.startswith(".") else f".{ext}"
    return f"{safe_download_stem(course_name, suffix)}{extension}"


def content_disposition_header(filename: str) -> str:
    fallback = filename.encode("ascii", "ignore").decode("ascii") or "ExamForgeAI_download"
    fallback = fallback.replace('"', "")
    return f'attachment; filename="{fallback}"; filename*=UTF-8\'\'{quote(filename)}'
