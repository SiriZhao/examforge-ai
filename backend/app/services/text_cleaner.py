import re

OCR_NOISE_WORDS = {
    "ROR",
    "RAR",
    "GERD",
    "CEA",
    "BRA",
    "WAR",
    "RARE",
    "FALSE",
    "TRUE",
    "MA",
}

ENGLISH_WHITELIST = {
    "DNA",
    "RNA",
    "ATP",
    "NADH",
    "PCR",
    "PDF",
    "PPT",
    "AI",
    "OCR",
    "API",
}


def clean_text(value: str) -> str:
    text = re.sub(r"\s+", " ", value or "").strip()
    text = re.sub(r"[�]+", "", text)
    text = re.sub(r"\b(?:%s)\b" % "|".join(OCR_NOISE_WORDS), "", text)
    text = re.sub(r"\s+([，。；：？！、])", r"\1", text)
    text = re.sub(r"([（【《])\s+", r"\1", text)
    text = re.sub(r"\s+([）】》])", r"\1", text)
    return re.sub(r"\s{2,}", " ", text).strip(" ：:;-，、")


def is_noise_term(value: str) -> bool:
    term = clean_text(value)
    if not term:
        return True
    upper = term.upper()
    if upper in OCR_NOISE_WORDS:
        return True
    if re.fullmatch(r"[A-Z]{2,6}", term) and upper not in ENGLISH_WHITELIST:
        return True
    if re.fullmatch(r"[a-fA-F0-9]{16,}", term):
        return True
    if re.fullmatch(r"[A-Za-z0-9_-]{20,}", term):
        return True
    if re.fullmatch(r"[A-Za-z]{1,2}", term):
        return True
    if len(term) <= 1:
        return True
    return False


def clean_list(items: list[str], fallback: str | None = None, limit: int | None = None) -> list[str]:
    cleaned: list[str] = []
    seen: set[str] = set()
    for item in items:
        value = clean_text(str(item))
        if is_noise_term(value) or value in seen:
            continue
        cleaned.append(value)
        seen.add(value)
        if limit and len(cleaned) >= limit:
            break
    if not cleaned and fallback:
        return [fallback]
    return cleaned


def clean_report_text(value: str) -> str:
    lines = [clean_text(line) for line in (value or "").splitlines()]
    return "\n".join(line for line in lines if line)
