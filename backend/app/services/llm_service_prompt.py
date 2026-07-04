import json
import re
from dataclasses import dataclass

from app.schemas.review import DetailLevel, ExamType, OutputStyle, ReviewReport, StudyGoal

MAX_LLM_INPUT_CHARS = 42000
MAX_CHUNK_CHARS = 12000
MAX_CHUNKS = 12
CONTEXT_TOO_LONG_MESSAGE = "资料过长，大模型深度整理未完成。系统已保留本地安全底稿。建议分批上传课件、教材和往年题后分别生成。"


@dataclass
class PreparedLLMContext:
    text: str
    original_chars: int
    compressed_chars: int
    needs_chunking: bool
    chunk_count: int
    chunk_chars: list[int]


def prepare_llm_context(materials_text: str, safe_draft: ReviewReport) -> PreparedLLMContext:
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

    compressed = build_structured_context(materials_text, safe_draft, MAX_LLM_INPUT_CHARS)
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


def build_review_prompt(
    evidence_pack: dict,
    safe_draft: ReviewReport,
    chunk_insights: list[str],
    *,
    study_goal: StudyGoal = "balanced",
    exam_type: ExamType = "unknown",
    detail_level: DetailLevel = "detailed",
    output_style: OutputStyle = "teaching_assistant",
) -> str:
    evidence_limit = 18000 if chunk_insights else 24000
    evidence_json = json.dumps(evidence_pack, ensure_ascii=False)[:evidence_limit]
    insights = "\n\n".join(f"[chunk_insight {index + 1}]\n{item}" for index, item in enumerate(chunk_insights))
    goal_instruction = build_study_goal_instruction(study_goal)
    exam_instruction = build_exam_type_instruction(exam_type)
    detail_instruction = build_detail_level_instruction(detail_level)
    style_instruction = build_output_style_instruction(output_style)
    return f"""
用户复习目标：{study_goal}
目标策略：{goal_instruction}
考试类型：{exam_type}
考试策略：{exam_instruction}
生成详细度：{detail_level}
详细度策略：{detail_instruction}
输出风格：{output_style}
风格策略：{style_instruction}

v0.4.0 输出要求：
- 报告必须体现复习目标和考试类型差异。
- question_types 需要包含 name、confidence、evidence、evidence_sources、features、related_topics、answer_strategy、sample_questions、practice_suggestions、is_from_past_exam。
- mock_exam.questions 每题需要 question_type/type、difficulty、question、options、answer、explanation、related_topic、source_hint、source_basis。
- anki_cards 需要 front、back、tags、card_type、priority、source_hint，Front 不要过长，Back 必须能独立理解。
- 如果 study_goal 是 anki_focused，请增加高质量 Anki；如果是 practice_heavy，请增加题目和解析；如果 exam_type 是 programming，请包含代码阅读、输出判断、函数补全、Debug 或编程实现；如果 exam_type 是 essay_based，请包含论述框架。
- 质量优先于节省 token。必须优先保留往年题题干、题型线索、高频考点上下文、公式/定义/代码片段、OCR 证据、chunk_insights 和 local_safe_draft。

你是资深课程助教和期末复习教练，不是普通摘要助手或模板填空器。

任务：
根据 Evidence Pack、chunk_insights 和本地安全底稿，重新组织一份真正可复习、可导出的期末复习资料包。
你的目标是把杂乱资料整理成学生能直接背诵、刷题、冲刺和导出的资料包，而不是机械总结文档。

你可以自由完成：
- 判断课程主题；
- 合并和重命名章节/专题/知识模块；
- 根据真实题干和材料自动总结题型；
- 根据往年题题型、难度、问法和考点分布设计模拟题结构；
- 生成 Anki 卡片；
- 设计 1 天、3 天、7 天冲刺计划；
- 重排复习优先级。

必须遵守：
1. 不要固定套用“第 X 章”“主题 1”这类机械标题，除非材料本身清楚使用这些标题。
2. 不要把题型强行归入固定题型库。题型名称要根据材料和题干自然命名，例如“概念辨析题”“公式套用计算题”“实验设计题”等。
3. 可以使用基础学科常识补足解释、答题步骤和易错点，但必须优先依据用户上传材料，避免捏造材料中不存在的具体事实；如果是根据材料生成的练习题型，请明确其为“根据材料生成的练习题型”。
4. OCR 可能有错字和噪声，请结合上下文修正，不要机械照抄乱码。
5. 报告必须具体、可复习、可导出，不能只有空泛摘要。
6. 如果有往年题或练习题，模拟卷必须优先参考真实题干结构和题型线索；如果材料不足，宁可生成较少的保守练习题，也不要用万能模板凑数量。每题必须有答案、解析、相关考点和来源依据。
7. Anki 卡片必须字段干净，适合 CSV 导出。
8. 不承诺押题必中，不承诺提分。
9. 优先只输出一个合法 JSON 对象，不要输出 Markdown 代码块或解释文字。
10. 如果你判断当前模型无法稳定输出 JSON，可以输出完整 Markdown 报告；Markdown 必须包含复习导览、知识结构、高频考点、题型分析、模拟题与答案、Anki 卡片、考前冲刺计划。

禁止输出：
- 半截 JSON；
- 注释 JSON；
- 带尾随逗号的 JSON；
- 空泛摘要；
- “请自行整理”；
- 只有建议没有具体考点；
- 只有摘要没有题目和卡片。

JSON 需要兼容以下字段：
{{
  "title": "...",
  "summary": "...",
  "overview": {{
    "exam_strategy": "...",
    "material_summary": "...",
    "priority_advice": "..."
  }},
  "study_units": [
    {{
      "name": "LLM 自主命名的专题",
      "reason": "为什么这样划分",
      "priority": 0,
      "must_know": [],
      "key_points": [],
      "formulas_or_methods": [],
      "common_exam_angles": [],
      "pitfalls": [],
      "how_to_review": ""
    }}
  ],
  "question_types": [
    {{
      "name": "根据材料总结的题型",
      "evidence": "来自哪些材料或题干",
      "features": [],
      "related_topics": [],
      "answer_strategy": "",
      "sample_questions": []
    }}
  ],
  "chapters": [],
  "past_exam_analysis": {{"detected_files": [], "high_frequency_topics": [], "summary": ""}},
  "review_order": [],
  "sprint_plans": [],
  "mock_exam": {{"title": "模拟卷", "questions": []}},
  "anki_cards": [],
  "high_frequency_points": [],
  "sprint_checklist": [],
  "low_priority": [],
  "insufficient_materials": [],
  "markdown": "完整可读 Markdown",
  "generated_at": "..."
}}

兼容要求：
- chapters 可以由 study_units 映射生成，但章节名必须自然可复习。
- mock_exam.questions 每项包含 question_type、type、question、options、answer、explanation、chapter、concept、difficulty、related_topic、source_hint、source_basis。
- anki_cards 每项包含 front、back、tags；tags 可以是字符串。
- markdown 必须是最终可导出的完整正文，不要包含 evidence_pack 或 chunk_insights 原文。

Evidence Pack：
{evidence_json}

chunk_insights：
{insights or "短材料未进入分块理解。"}

本地安全底稿 JSON：
{safe_draft.model_dump_json(ensure_ascii=False)}
""".strip()


def build_chunk_summary_prompt(chunk: str, chunk_index: int, total_chunks: int) -> str:
    return f"""
请把下面的材料分块理解为 chunk_insight，不要只写摘要。

分块：{chunk_index}/{total_chunks}

输出普通文本，必须包含：
1. 本块主题；
2. 关键概念；
3. 重要定义；
4. 公式/方法；
5. 例题/题目候选；
6. 可考点；
7. 可能题型，题型名称由材料决定；
8. 可转 Anki 的问答；
9. 原文证据片段。

请避免照抄 OCR 乱码，遇到疑似错字请根据上下文修正。

材料分块：
{chunk}
""".strip()


def build_outline_naming_prompt(evidence_pack: dict, bad_titles: list[str]) -> str:
    compact_pack = {
        "course_name": evidence_pack.get("course_name"),
        "files": [
            {
                "filename": item.get("filename"),
                "file_type_guess": item.get("file_type_guess"),
                "possible_titles": item.get("possible_titles", [])[:8],
                "possible_questions": item.get("possible_questions", [])[:8],
                "possible_keywords": item.get("possible_keywords", [])[:12],
            }
            for item in evidence_pack.get("files", [])[:6]
        ],
        "global_signals": {
            "frequent_terms": evidence_pack.get("global_signals", {}).get("frequent_terms", [])[:30],
            "possible_exam_topics": evidence_pack.get("global_signals", {}).get("possible_exam_topics", [])[:24],
            "possible_question_clusters": evidence_pack.get("global_signals", {}).get("possible_question_clusters", [])[:12],
            "detected_exam_materials": evidence_pack.get("global_signals", {}).get("detected_exam_materials", [])[:8],
        },
        "bad_titles": bad_titles[:20],
    }
    return f"""
你是期末复习资料整理专家。完整 AI 深度整理暂时失败，现在只需要你做一次轻量专题命名。

请根据材料证据输出 5-12 个自然、可复习的专题名称。不要使用公式碎片、题干碎片、OCR 噪声或“未识别章节”。

只输出 JSON：
{{
  "study_units": [
    {{"name": "专题名称", "reason": "一句划分理由", "priority": 80, "key_points": ["关键词"], "how_to_review": "复习建议"}}
  ]
}}

材料证据：
{json.dumps(compact_pack, ensure_ascii=False)}
""".strip()


def build_question_type_inference_prompt(evidence_pack: dict, course_name: str | None = None) -> str:
    signals = evidence_pack.get("global_signals", {}) if isinstance(evidence_pack, dict) else {}
    question_candidates: list[dict] = []
    for file_item in evidence_pack.get("files", [])[:8]:
        for question in file_item.get("possible_questions", [])[:10]:
            question_candidates.append(
                {
                    "source_file": file_item.get("filename"),
                    "file_type_guess": file_item.get("file_type_guess"),
                    "question": question,
                }
            )
    compact_pack = {
        "course_name": course_name or evidence_pack.get("course_name"),
        "frequent_terms": signals.get("frequent_terms", [])[:30],
        "possible_exam_topics": signals.get("possible_exam_topics", [])[:24],
        "possible_question_clusters": signals.get("possible_question_clusters", [])[:16],
        "detected_exam_materials": signals.get("detected_exam_materials", [])[:8],
        "question_candidates": question_candidates[:50],
    }
    return f"""
你是大学期末复习题型分析专家。请根据真实题干、OCR 上下文、文件类型和课程高频考点，自动归纳题型。
不要把题型强行限制为选择题、填空题、判断题、简答题、计算题、论述题；这些只能作为普通参考。
不同课程可以出现代码阅读题、函数补全题、图示识别题、分类归纳题、实验观察分析题、条件概率建模题、文献解读题等自然题型。

只输出合法 JSON：
{{
  "question_types": [
    {{
      "name": "根据材料归纳出的题型名称",
      "evidence": "来自哪些材料或题干",
      "features": [],
      "related_topics": [],
      "answer_strategy": "",
      "sample_questions": [],
      "review_advice": ""
    }}
  ]
}}

如果没有真实往年题，请明确标注为“根据材料生成的练习题型”，不要伪装成真实往年题。
材料证据：{json.dumps(compact_pack, ensure_ascii=False)}
""".strip()


def build_study_goal_instruction(study_goal: StudyGoal) -> str:
    return {
        "one_day_sprint": "强调必背内容、高频考点、最可能出题方向、少量高价值题和最短路径复习，减少低频背景。",
        "three_day_sprint": "按 Day 1 打基础、Day 2 刷题型、Day 3 查漏补缺和模拟组织。",
        "seven_day_plan": "强调完整知识结构、每天任务、题目训练、Anki 复习和最后一日模拟。",
        "memorization": "强调名词解释、定义、公式、对比表、Anki 和易混概念。",
        "practice_heavy": "强调题型归纳、典型题、变式题、答题步骤、参考答案和解析。",
        "anki_focused": "强调卡片数量与质量，覆盖定义、公式、对比、易错点、题型套路，严格去重。",
        "past_exam_focused": "强调往年题考点加权、重复题型、命题偏好和高频题型，但不能承诺押题。",
        "balanced": "兼顾章节结构、高频考点、模拟卷、Anki 和冲刺计划。",
    }.get(study_goal, "兼顾章节结构、高频考点、模拟卷、Anki 和冲刺计划。")


def build_exam_type_instruction(exam_type: ExamType) -> str:
    return {
        "closed_book": "强调记忆、定义公式、易混点和快速答题。",
        "open_book": "强调材料定位、答题框架、综合分析、案例题和论述结构。",
        "computer_based": "强调机考速度、题型识别、步骤稳定和易错项检查。",
        "programming": "强调代码阅读、输出判断、函数补全、Debug、编程实现和边界条件。",
        "lab_exam": "强调实验原理、步骤、现象解释、数据处理和误差分析。",
        "essay_based": "强调概念框架、比较分析、论述提纲、论据组织和典型论述题。",
        "oral_presentation": "强调口头表达结构、关键概念解释、展示逻辑和追问准备。",
        "coursework_report": "强调报告结构、证据组织、论证链条和引用/材料支撑。",
        "unknown": "系统可根据材料自动判断可能考试形态，模拟卷保持多样。",
    }.get(exam_type, "系统可根据材料自动判断可能考试形态，模拟卷保持多样。")


def build_detail_level_instruction(detail_level: DetailLevel) -> str:
    return {
        "concise": "保持简洁，但不得删除往年题题干、关键公式、题型线索、答案解析和 Anki 必要内容。",
        "standard": "输出标准长度，覆盖核心专题、题型、模拟题、Anki 和冲刺计划。",
        "detailed": "默认采用详细讲义式输出，解释考点原因、答题步骤、易错点和复习优先级。",
        "exhaustive": "尽量全面保留证据和解释，增加例题、变式、易错点、Anki 卡片和多日计划。",
    }.get(detail_level, "默认采用详细讲义式输出，解释考点原因、答题步骤、易错点和复习优先级。")


def build_output_style_instruction(output_style: OutputStyle) -> str:
    return {
        "sprint": "像考前冲刺清单一样组织，突出最短路径、必背必练、最后 1/3/7 天安排。",
        "top_student_notes": "像高分学生笔记一样组织，突出结构化知识框架、对比、口诀和易混点。",
        "teaching_assistant": "像助教讲义一样组织，解释清楚概念、题型、答题步骤和材料证据。",
        "practice_training": "像刷题训练册一样组织，增加题型套路、典型题、变式题、答案和解析。",
        "anki_cards": "像制卡工作流一样组织，增加具体、去重、可直接导出的 Anki 卡片。",
    }.get(output_style, "像助教讲义一样组织，解释清楚概念、题型、答题步骤和材料证据。")


def build_context_from_chunk_summaries(
    summaries: list[str],
    safe_draft: ReviewReport,
    limit: int = MAX_LLM_INPUT_CHARS,
) -> str:
    priority_lines = [
        f"- {item.chapter}：{item.importance}/100，{item.reason}"
        for item in safe_draft.review_order[:12]
    ]
    topic_lines = [
        f"- {topic.chapter}｜{topic.topic}：出现 {topic.frequency} 次，题型：{'、'.join(topic.question_types) or '未知'}"
        for topic in safe_draft.past_exam_analysis.high_frequency_topics[:20]
    ]
    parts = [
        "以下是系统对长材料进行逐块理解后的 chunk_insights，不是最终报告。",
        "",
        "安全底稿中的复习顺序候选：",
        "\n".join(priority_lines) or "暂无明确复习顺序候选。",
        "",
        "安全底稿中的往年题高频线索：",
        "\n".join(topic_lines) or "暂无明确往年题统计。",
        "",
        "chunk_insights：",
    ]
    for index, summary in enumerate(summaries, start=1):
        parts.append(f"\n[chunk_insight {index}]\n{summary.strip()}")
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

    return sorted(chunks, key=score_chunk, reverse=True)[:MAX_CHUNKS]


def build_structured_context(text: str, safe_draft: ReviewReport, limit: int) -> str:
    lines = clean_lines(text)
    important = select_important_lines(lines, int(limit * 0.62))
    priority = [
        f"- {item.chapter}：{item.importance}/100，{item.reason}"
        for item in safe_draft.review_order[:12]
    ]
    keywords = [
        f"- {chapter.chapter}：{'、'.join(chapter.keywords[:12])}"
        for chapter in safe_draft.chapters[:12]
        if chapter.keywords
    ]
    topics = [
        f"- {topic.chapter}｜{topic.topic}：{topic.frequency} 次，题型：{'、'.join(topic.question_types) or '未知'}"
        for topic in safe_draft.past_exam_analysis.high_frequency_topics[:20]
    ]
    sections = [
        "本地安全底稿中的复习顺序候选：",
        "\n".join(priority) or "暂无明确复习顺序候选。",
        "",
        "本地安全底稿中的关键词候选：",
        "\n".join(keywords) or "暂无明确关键词。",
        "",
        "往年题/题干线索：",
        "\n".join(topics) or safe_draft.past_exam_analysis.summary or "暂无明确往年题统计。",
        "",
        "代表性材料证据：",
        important,
    ]
    return "\n".join(sections)[: limit * 2]


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
    if re.search(r"(题|答案|证明|计算|分析|设计|Multiple choice|Fill in|Essay|Short answer)", line, re.I):
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
    if len(re.findall(r"[�□■]", line)) > 0:
        return True
    letters = re.findall(r"[A-Za-z]", line)
    if len(letters) >= 8:
        uppercase_ratio = sum(1 for char in letters if char.isupper()) / max(len(letters), 1)
        if uppercase_ratio > 0.85 and not re.search(r"ATP|DNA|RNA|PDF|OCR", line):
            return True
    return False

