import re
from collections import Counter
from dataclasses import asdict, dataclass, field

from app.schemas.review import ReviewReport
from app.services.llm_service_prompt import MAX_CHUNK_CHARS, MAX_CHUNKS, clean_lines, split_material_chunks
from app.services.text_quality import clean_formula_text, clean_topic_list, clean_topic_name, looks_like_formula_fragment


@dataclass
class EvidenceFile:
    filename: str
    file_type_guess: str
    text_length: int
    ocr_quality_guess: str
    important_fragments: list[str] = field(default_factory=list)
    possible_titles: list[str] = field(default_factory=list)
    possible_questions: list[str] = field(default_factory=list)
    possible_formulas: list[str] = field(default_factory=list)
    possible_definitions: list[str] = field(default_factory=list)
    possible_keywords: list[str] = field(default_factory=list)


@dataclass
class EvidenceChunk:
    chunk_id: str
    source_file: str
    raw_excerpt: str
    cleaned_excerpt: str
    local_summary: str
    key_terms: list[str] = field(default_factory=list)
    possible_exam_value: int = 0


@dataclass
class EvidencePack:
    course_name: str
    files: list[EvidenceFile]
    global_signals: dict
    chunks: list[EvidenceChunk]

    def to_dict(self) -> dict:
        return asdict(self)


def build_evidence_pack(
    materials_text: str,
    safe_draft: ReviewReport,
    *,
    course_name: str | None = None,
    file_texts: list[tuple[str, str]] | None = None,
) -> EvidencePack:
    files_source = file_texts or [("合并材料", materials_text)]
    evidence_files = [build_evidence_file(filename, text) for filename, text in files_source]
    all_titles = clean_topic_list([title for item in evidence_files for title in item.possible_titles], 30)
    all_questions = dedupe([question for item in evidence_files for question in item.possible_questions], 60)
    all_keywords = clean_topic_list([keyword for item in evidence_files for keyword in item.possible_keywords], 60)
    frequent_terms = extract_frequent_terms(materials_text, 40)
    detected_exam_materials = [
        item.filename
        for item in evidence_files
        if item.file_type_guess in {"往年题", "试卷", "练习题"}
        or len(item.possible_questions) >= 3
    ]
    chunks = build_evidence_chunks(files_source)
    return EvidencePack(
        course_name=course_name or safe_draft.title,
        files=evidence_files,
        global_signals={
            "frequent_terms": frequent_terms,
            "repeated_phrases": extract_repeated_phrases(materials_text),
            "possible_titles": all_titles,
            "possible_exam_topics": clean_topic_list(safe_draft.high_frequency_points + all_keywords[:20], 40),
            "possible_question_clusters": cluster_question_candidates(all_questions),
            "detected_exam_materials": detected_exam_materials,
            "safe_draft_review_order": [
                {"name": item.chapter, "importance": item.importance, "reason": item.reason}
                for item in safe_draft.review_order[:12]
            ],
            "safe_draft_high_frequency_topics": [
                {
                    "topic": item.topic,
                    "chapter": item.chapter,
                    "frequency": item.frequency,
                    "question_types": item.question_types,
                }
                for item in safe_draft.past_exam_analysis.high_frequency_topics[:20]
            ],
        },
        chunks=chunks,
    )


def build_evidence_file(filename: str, text: str) -> EvidenceFile:
    cleaned = clean_lines(text)
    joined = "\n".join(cleaned)
    questions = extract_question_candidates(joined, 30)
    return EvidenceFile(
        filename=filename,
        file_type_guess=guess_file_type(filename, joined, questions),
        text_length=len(text),
        ocr_quality_guess=guess_ocr_quality(text),
        important_fragments=select_fragments(cleaned, 18),
        possible_titles=extract_possible_titles(cleaned, filename),
        possible_questions=questions,
        possible_formulas=extract_formulas(joined, 20),
        possible_definitions=extract_definitions(cleaned, 20),
        possible_keywords=extract_frequent_terms(joined, 24),
    )


def build_evidence_chunks(file_texts: list[tuple[str, str]]) -> list[EvidenceChunk]:
    chunks: list[EvidenceChunk] = []
    for filename, text in file_texts:
        for index, chunk in enumerate(split_material_chunks(text), start=1):
            cleaned_lines = clean_lines(chunk)
            cleaned = "\n".join(cleaned_lines)
            terms = extract_frequent_terms(cleaned, 10)
            questions = extract_question_candidates(cleaned, 8)
            exam_value = min(100, len(questions) * 12 + len(terms) * 3 + score_exam_words(cleaned))
            chunks.append(
                EvidenceChunk(
                    chunk_id=f"{len(chunks) + 1}",
                    source_file=filename,
                    raw_excerpt=chunk[:1200],
                    cleaned_excerpt=cleaned[:2200],
                    local_summary=make_local_summary(cleaned, terms, questions),
                    key_terms=terms,
                    possible_exam_value=exam_value,
                )
            )
    return sorted(chunks, key=lambda item: item.possible_exam_value, reverse=True)[:MAX_CHUNKS]


def guess_file_type(filename: str, text: str, questions: list[str]) -> str:
    name = filename.lower()
    signals = f"{name}\n{text[:2000]}".lower()
    if re.search(r"past|exam|paper|往年|真题|试卷|期末|quiz|midterm", signals):
        return "往年题"
    if re.search(r"\.pptx?$|lecture|slides|课件|讲义", name):
        return "课件"
    if re.search(r"\.png$|\.jpe?g$|scan|扫描", name):
        return "图片"
    if len(questions) >= 5:
        return "练习题"
    return "文档"


def guess_ocr_quality(text: str) -> str:
    if not text.strip():
        return "无文本"
    odd = len(re.findall(r"[�□■]{1,}|[A-Z]{8,}", text))
    ratio = odd / max(len(text), 1)
    if ratio > 0.02:
        return "可能存在较多 OCR 噪声"
    if ratio > 0.005:
        return "可能存在少量 OCR 噪声"
    return "文本质量较稳定"


def extract_possible_titles(lines: list[str], filename: str) -> list[str]:
    candidates = [re.sub(r"[_-]+", " ", filename.rsplit(".", 1)[0]).strip()]
    for line in lines:
        if 4 <= len(line) <= 48 and (
            re.search(r"^(第.+章|第.+节|Chapter|Unit|Lecture|Topic|\d+[\.\s])", line, re.I)
            or line.endswith(("概述", "原理", "方法", "模型", "分析", "复习", "总结"))
            or (line.count(" ") <= 5 and not line.endswith(("。", ".", "；", ";")))
        ):
            candidates.append(line)
    return clean_topic_list(candidates, 24)


def extract_question_candidates(text: str, limit: int) -> list[str]:
    candidates: list[str] = []
    pattern = re.compile(
        r"(?m)(?:^|\n)\s*(?:\d+[\.\、)]|[一二三四五六七八九十]+[、.])\s*(.{8,260}(?:\?|？|。|；|;|$))"
    )
    for match in pattern.finditer(text):
        question = match.group(1).strip()
        if looks_like_question(question):
            candidates.append(question)
    for line in text.splitlines():
        stripped = line.strip()
        if looks_like_question(stripped):
            candidates.append(stripped)
    return dedupe(candidates, limit)


def looks_like_question(text: str) -> bool:
    return 8 <= len(text) <= 300 and bool(
        re.search(r"\?|？|下列|简述|说明|证明|计算|分析|设计|解释|比较|为什么|如何|求|写出|判断|选择", text, re.I)
    )


def extract_formulas(text: str, limit: int) -> list[str]:
    formulas = []
    for line in text.splitlines():
        stripped = line.strip()
        if 4 <= len(stripped) <= 120 and re.search(r"[=∑∫√≈≤≥±∞]|\\frac|\\sum|P\(|E\(|Var\(", stripped):
            cleaned = clean_formula_text(stripped)
            if cleaned:
                formulas.append(cleaned)
    return dedupe(formulas, limit)


def extract_definitions(lines: list[str], limit: int) -> list[str]:
    definitions = [
        line
        for line in lines
        if 8 <= len(line) <= 180 and re.search(r"定义|是指|称为|means|defined as|refers to", line, re.I)
    ]
    return dedupe(definitions, limit)


def extract_frequent_terms(text: str, limit: int) -> list[str]:
    tokens = re.findall(r"[\u4e00-\u9fff]{2,8}|[A-Za-z][A-Za-z0-9_-]{2,}", text)
    stop = {"the", "and", "for", "with", "that", "this", "chapter", "lecture", "page", "考试", "复习", "材料"}
    counts = Counter(
        token
        for token in tokens
        if token.lower() not in stop and clean_topic_name(token) and not looks_like_formula_fragment(token)
    )
    return clean_topic_list([term for term, _ in counts.most_common(limit * 2)], limit)


def extract_repeated_phrases(text: str) -> list[str]:
    phrases = re.findall(r"[\u4e00-\u9fffA-Za-z0-9]{4,18}", text)
    counts = Counter(phrases)
    return [phrase for phrase, count in counts.most_common(20) if count >= 2]


def cluster_question_candidates(questions: list[str]) -> list[dict]:
    clusters: dict[str, list[str]] = {}
    for question in questions:
        key = infer_question_action(question)
        clusters.setdefault(key, []).append(question)
    return [
        {"cluster": key, "examples": values[:5], "count": len(values)}
        for key, values in clusters.items()
    ]


def infer_question_action(question: str) -> str:
    for name, pattern in [
        ("计算/推导类", r"计算|求|推导|证明"),
        ("分析/解释类", r"分析|解释|为什么|说明"),
        ("设计/应用类", r"设计|应用|案例|实验"),
        ("概念辨析类", r"定义|比较|区别|判断|下列"),
    ]:
        if re.search(pattern, question):
            return name
    return "综合问答类"


def select_fragments(lines: list[str], limit: int) -> list[str]:
    scored = sorted(lines, key=lambda line: score_exam_words(line) + min(len(line), 120) // 20, reverse=True)
    return dedupe([line for line in scored if len(line) >= 6], limit)


def make_local_summary(text: str, terms: list[str], questions: list[str]) -> str:
    title = "、".join(terms[:5]) or "未识别明确主题"
    exam_hint = f"发现 {len(questions)} 个题目候选" if questions else "未发现明确题干"
    return f"本块可能围绕：{title}。{exam_hint}。"


def score_exam_words(text: str) -> int:
    return len(re.findall(r"重点|考点|题|答案|公式|定义|证明|计算|分析|exam|question|answer|important", text, re.I)) * 5


def dedupe(items: list[str], limit: int) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for item in items:
        cleaned = re.sub(r"\s+", " ", str(item)).strip()
        if not cleaned:
            continue
        key = cleaned.lower()
        if key in seen:
            continue
        seen.add(key)
        result.append(cleaned)
        if len(result) >= limit:
            break
    return result
