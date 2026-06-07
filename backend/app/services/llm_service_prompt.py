import re
from dataclasses import dataclass

from app.schemas.review import ReviewReport

MAX_LLM_INPUT_CHARS = 30000
MAX_CHUNK_CHARS = 8000
MAX_CHUNKS = 8
CONTEXT_TOO_LONG_MESSAGE = "资料过长，大模型增强未完成。系统已保留规则版报告。建议减少单次上传资料，或分批上传课件、教材和往年题后分别生成。"


@dataclass
class PreparedLLMContext:
    text: str
    original_chars: int
    compressed_chars: int
    needs_chunking: bool
    chunk_count: int
    chunk_chars: list[int]


def prepare_llm_context(materials_text: str, rule_report: ReviewReport) -> PreparedLLMContext:
    original_chars = len(materials_text)
    if original_chars <= MAX_LLM_INPUT_CHARS:
        return PreparedLLMContext(
            text=materials_text,
            original_chars=original_chars,
            compressed_chars=original_chars,
            needs_chunking=False,
            chunk_count=0,
            chunk_chars=[],
        )

    compressed = build_structured_context(materials_text, rule_report, MAX_LLM_INPUT_CHARS)
    needs_chunking = len(compressed) > MAX_LLM_INPUT_CHARS or original_chars > MAX_LLM_INPUT_CHARS * 2
    chunks = split_material_chunks(materials_text) if needs_chunking else []
    return PreparedLLMContext(
        text=compressed[:MAX_LLM_INPUT_CHARS],
        original_chars=original_chars,
        compressed_chars=min(len(compressed), MAX_LLM_INPUT_CHARS),
        needs_chunking=needs_chunking,
        chunk_count=len(chunks),
        chunk_chars=[len(chunk) for chunk in chunks],
    )


def build_review_prompt(context_text: str, rule_report: ReviewReport) -> str:
    return f"""
请基于“材料上下文”和“规则版报告”生成一个更自然、更准确的中文期末复习报告。

必须遵守：
1. 只输出 JSON 对象，不要输出 Markdown 代码块，不要解释。
2. JSON 字段必须完整匹配 ReviewReport：
   title, summary, chapters, past_exam_analysis, review_order, sprint_plans,
   mock_exam, anki_cards, high_frequency_points, sprint_checklist,
   low_priority, insufficient_materials, generated_at。
3. chapters 中每项必须包含：
   chapter, importance, material_frequency, past_exam_frequency, weighted_score,
   keywords, formulas, question_types, examples, frequency, review_advice。
4. question_types 只能使用：选择题、填空题、判断题、计算题、简答题、论述题、未知。
5. 不要编造材料中不存在的章节、题目或答案。
6. 不确定内容写入 insufficient_materials，并使用“当前材料不足，无法可靠判断。”。
7. 请过滤明显 OCR 噪声，例如 ROR、RAR、GERD、WAR、FALSE、TRUE 等碎片。
8. 所有面向用户的内容使用简体中文。

材料上下文：
{context_text}

规则版报告 JSON：
{rule_report.model_dump_json(ensure_ascii=False)}
""".strip()


def build_chunk_summary_prompt(chunk: str, chunk_index: int, total_chunks: int) -> str:
    return f"""
请总结以下课程材料分块，用简体中文输出结构化要点。
只需要普通文本，不要 JSON，不要 Markdown 表格。

分块：{chunk_index}/{total_chunks}

请包含：
1. 章节/主题
2. 核心概念
3. 可能考点
4. 典型题型
5. 关键词
6. 需要背诵的内容

材料分块：
{chunk}
""".strip()


def build_context_from_chunk_summaries(
    summaries: list[str],
    rule_report: ReviewReport,
    limit: int = MAX_LLM_INPUT_CHARS,
) -> str:
    priority_lines = [
        f"- {item.chapter}：{item.importance}/100，{item.reason}"
        for item in rule_report.review_order[:12]
    ]
    topic_lines = [
        f"- {topic.chapter}｜{topic.topic}：出现 {topic.frequency} 次，题型：{'、'.join(topic.question_types) or '未知'}"
        for topic in rule_report.past_exam_analysis.high_frequency_topics[:20]
    ]
    parts = [
        "以下是系统对超长材料进行分块摘要后的合并上下文。",
        "",
        "章节优先级：",
        "\n".join(priority_lines) or "暂无明确章节优先级。",
        "",
        "往年题高频考点：",
        "\n".join(topic_lines) or "暂无明确往年题统计。",
        "",
        "分块摘要：",
    ]
    for index, summary in enumerate(summaries, start=1):
        parts.append(f"\n[分块摘要 {index}]\n{summary.strip()}")
    return "\n".join(parts)[:limit]


def split_material_chunks(text: str) -> list[str]:
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
    if not paragraphs:
        paragraphs = [text]

    chunks: list[str] = []
    current: list[str] = []
    current_len = 0
    for paragraph in paragraphs:
        if len(paragraph) > MAX_CHUNK_CHARS:
            if current:
                chunks.append("\n\n".join(current))
                current = []
                current_len = 0
            for start in range(0, len(paragraph), MAX_CHUNK_CHARS):
                chunks.append(paragraph[start : start + MAX_CHUNK_CHARS])
            continue

        next_len = current_len + len(paragraph) + 2
        if current and next_len > MAX_CHUNK_CHARS:
            chunks.append("\n\n".join(current))
            current = [paragraph]
            current_len = len(paragraph)
        else:
            current.append(paragraph)
            current_len = next_len

    if current:
        chunks.append("\n\n".join(current))

    scored = sorted(chunks, key=score_chunk, reverse=True)
    selected = scored[:MAX_CHUNKS]
    return selected


def build_structured_context(text: str, rule_report: ReviewReport, limit: int) -> str:
    lines = clean_lines(text)
    important = select_important_lines(lines, int(limit * 0.55))

    priority = [
        f"- {item.chapter}：{item.importance}/100，{item.reason}"
        for item in rule_report.review_order[:12]
    ]
    keywords = []
    for chapter in rule_report.chapters[:12]:
        if chapter.keywords:
            keywords.append(f"- {chapter.chapter}：{'、'.join(chapter.keywords[:12])}")
    topics = [
        f"- {topic.chapter}｜{topic.topic}：{topic.frequency} 次，题型：{'、'.join(topic.question_types) or '未知'}"
        for topic in rule_report.past_exam_analysis.high_frequency_topics[:20]
    ]

    sections = [
        "规则版章节优先级：",
        "\n".join(priority) or "暂无明确章节优先级。",
        "",
        "规则版高频关键词：",
        "\n".join(keywords) or "暂无明确关键词。",
        "",
        "往年题统计：",
        "\n".join(topics) or rule_report.past_exam_analysis.summary or "暂无明确往年题统计。",
        "",
        "代表性材料节选：",
        important,
    ]
    return "\n".join(sections)[:limit * 2]


def clean_lines(text: str) -> list[str]:
    seen: set[str] = set()
    lines: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if re.fullmatch(r"[-–—_ ]*\d+[-–—_ ]*", line):
            continue
        if re.search(r"^(page|第\s*\d+\s*页)\b", line, re.I):
            continue
        if looks_like_ocr_noise(line):
            continue
        key = re.sub(r"\s+", " ", line.lower())
        if key in seen:
            continue
        seen.add(key)
        lines.append(line)
    return lines


def select_important_lines(lines: list[str], limit: int) -> str:
    scored = [(score_line(line), index, line) for index, line in enumerate(lines)]
    selected_indexes = {
        index
        for score, index, _ in sorted(scored, key=lambda item: (-item[0], item[1]))
        if score > 0
    }
    output: list[str] = []
    total = 0
    for index, line in enumerate(lines):
        if index not in selected_indexes and total > limit * 0.75:
            continue
        next_total = total + len(line) + 1
        if next_total > limit:
            break
        output.append(line)
        total = next_total
    return "\n".join(output)


def score_chunk(chunk: str) -> int:
    return sum(score_line(line) for line in chunk.splitlines()) + min(len(chunk) // 500, 10)


def score_line(line: str) -> int:
    score = 0
    if re.search(r"^(第.+章|第.+节|Chapter\s+\d+|Unit\s+\d+|Lecture\s+\d+)", line, re.I):
        score += 20
    if re.search(r"(选择题|填空题|简答题|论述题|判断题|Multiple choice|Fill in|Essay|Short answer)", line, re.I):
        score += 18
    if re.search(r"(重点|考点|关键词|公式|定义|原理|Key points|formula|definition)", line, re.I):
        score += 12
    if re.search(r"^\d+[\.\、)]", line):
        score += 10
    if len(line) > 30:
        score += 2
    return score


def looks_like_ocr_noise(line: str) -> bool:
    if len(line) <= 2:
        return True
    letters = re.findall(r"[A-Za-z]", line)
    if len(letters) >= 8:
        uppercase_ratio = sum(1 for char in letters if char.isupper()) / max(len(letters), 1)
        if uppercase_ratio > 0.85 and not re.search(r"ATP|DNA|RNA|PDF|OCR", line):
            return True
    return False

