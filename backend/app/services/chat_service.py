from app.schemas.review import ReviewReport


def answer_review_question(message: str, report: ReviewReport | None) -> str:
    if report is None:
        return "请先生成复习资料，我才能基于报告回答追问。"

    normalized = message.strip()
    if not normalized:
        return "请输入你想追问的问题。"

    if contains_any(normalized, ["背诵", "背诵版", "速记"]):
        return build_memorization_version(report)
    if contains_any(normalized, ["模拟题", "出题", "练习"]):
        return "可以点击“模拟题”快捷按钮生成题目；当前建议优先覆盖：" + join_items(report.high_frequency_points[:5])
    if contains_any(normalized, ["高频", "考点", "重点"]):
        return "高频考点如下：\n" + bullet_list(report.high_frequency_points)
    if contains_any(normalized, ["优先", "先复习", "章节"]):
        chapters = sorted(report.chapters, key=lambda item: item.importance, reverse=True)
        return "建议优先复习：\n" + bullet_list(
            [f"{item.chapter}（重要度 {item.importance}，高频度 {item.frequency}）" for item in chapters[:5]]
        )
    if contains_any(normalized, ["低优先级", "可以少看"]):
        return "低优先级内容：\n" + bullet_list(report.low_priority)

    return (
        "基于当前报告，建议按“高频考点 -> 高重要度章节 -> 公式与例题 -> 冲刺清单”的顺序复习。\n\n"
        "你也可以问我：生成背诵版、模拟题、高频考点、优先复习章节。"
    )


def build_memorization_version(report: ReviewReport) -> str:
    lines = ["背诵版复习提纲："]
    for chapter in sorted(report.chapters, key=lambda item: item.importance, reverse=True)[:6]:
        keywords = "、".join(chapter.keywords[:6]) if chapter.keywords else "暂无关键词"
        formulas = "；".join(chapter.formulas[:3]) if chapter.formulas else "暂无公式"
        lines.append(f"- {chapter.chapter}：关键词 {keywords}；公式 {formulas}")
    lines.append("最后按冲刺清单逐项自测：")
    lines.extend(f"- {item}" for item in report.sprint_checklist[:5])
    return "\n".join(lines)


def contains_any(text: str, words: list[str]) -> bool:
    return any(word in text for word in words)


def bullet_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in (items or ["当前材料不足，无法可靠判断"]))


def join_items(items: list[str]) -> str:
    return "、".join(items) if items else "当前材料不足，无法可靠判断"
