import re

from app.schemas.review import ReviewReport

MATERIAL_CHAR_LIMIT = 18000
CONTEXT_TOO_LONG_MESSAGE = "当前资料过长，系统已生成规则版报告。建议减少单次上传资料，或开启支持更长上下文的模型。"


def build_review_prompt(materials_text: str, rule_report: ReviewReport) -> str:
    compressed_materials = compress_materials_for_llm(materials_text)
    return f"""
请基于“上传材料节选”和“规则版报告”生成一个更自然、更准确的中文期末复习报告。

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

上传材料节选：
{compressed_materials}

规则版报告 JSON：
{rule_report.model_dump_json(ensure_ascii=False)}
""".strip()


def compress_materials_for_llm(text: str, limit: int = MATERIAL_CHAR_LIMIT) -> str:
    if len(text) <= limit:
        return text

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    scored: list[tuple[int, int, str]] = []
    for index, line in enumerate(lines):
        score = score_line(line)
        if score > 0:
            scored.append((score, index, line))

    selected: list[str] = []
    used_indexes: set[int] = set()
    for _, index, line in sorted(scored, key=lambda item: (-item[0], item[1])):
        if index in used_indexes:
            continue
        candidate = "\n".join([*selected, line])
        if len(candidate) > int(limit * 0.75):
            break
        selected.append(line)
        used_indexes.add(index)

    # 再按原文顺序补足开头和各段摘要，避免只保留孤立关键词。
    for index, line in enumerate(lines):
        if index in used_indexes:
            continue
        candidate = "\n".join([*selected, line])
        if len(candidate) > limit:
            break
        selected.append(line)
        used_indexes.add(index)

    selected.sort(key=lambda item: lines.index(item) if item in lines else 0)
    result = "\n".join(selected)
    if len(result) > limit:
        result = result[:limit]
    return result + "\n\n[系统提示：原始资料较长，以上为按章节、题干和关键词压缩后的节选。]"


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

