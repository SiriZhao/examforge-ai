from app.schemas.review import ReviewReport
from app.services.review_planner import sanitize_report


def generate_markdown_review(report: ReviewReport) -> str:
    report = sanitize_report(report)
    lines = [
        f"# {report.title}",
        "",
        f"生成时间：{report.generated_at}",
        "",
        "## 总览",
        report.summary,
        "",
        "## 章节优先级",
        "",
        "| 章节 | 重要度 | 材料命中 | 往年题命中 | 题型 | 关键词 |",
        "| --- | ---: | ---: | ---: | --- | --- |",
    ]

    for chapter in report.chapters:
        lines.append(
            "| {chapter} | {importance} | {material} | {exam} | {types} | {keywords} |".format(
                chapter=escape_table_cell(chapter.chapter),
                importance=chapter.importance,
                material=chapter.material_frequency,
                exam=chapter.past_exam_frequency,
                types=escape_table_cell("、".join(str(item) for item in chapter.question_types) or "暂无"),
                keywords=escape_table_cell("、".join(chapter.keywords) or "暂无"),
            )
        )

    append_past_exam_analysis(lines, report)
    append_review_order(lines, report)
    append_sprint_plans(lines, report)
    append_mock_exam(lines, report)
    append_anki_preview(lines, report)

    lines.extend(["", "## 章节复习建议"])
    for chapter in report.chapters:
        lines.extend(
            [
                "",
                f"### {chapter.chapter}",
                "",
                f"- 重要度：{chapter.importance}/100",
                f"- 材料命中：{chapter.material_frequency}",
                f"- 往年题命中：{chapter.past_exam_frequency}",
                f"- 关键词：{'、'.join(chapter.keywords) if chapter.keywords else '暂无'}",
                f"- 题型：{'、'.join(str(item) for item in chapter.question_types) if chapter.question_types else '暂无'}",
                f"- 复习建议：{chapter.review_advice}",
                "",
                "#### 公式",
            ]
        )
        if chapter.formulas:
            lines.extend([f"- `{formula}`" for formula in chapter.formulas])
        else:
            lines.append("- 暂无")

        lines.extend(["", "#### 示例题"])
        for example in chapter.examples:
            lines.append(f"- {example}")

    append_list(lines, "高频考点", report.high_frequency_points)
    append_list(lines, "考前冲刺清单", report.sprint_checklist)
    append_list(lines, "低优先级内容", report.low_priority)
    append_list(lines, "材料不足提示", report.insufficient_materials or ["暂无"])

    return "\n".join(lines)


def append_past_exam_analysis(lines: list[str], report: ReviewReport) -> None:
    lines.extend(["", "## 往年题高频考点分析", ""])
    lines.append(report.past_exam_analysis.summary or "暂无往年题分析。")
    if report.past_exam_analysis.detected_files:
        lines.extend(["", "| 文件 | 置信度 | 题目数 | 题型 | 章节 |", "| --- | ---: | ---: | --- | --- |"])
        for item in report.past_exam_analysis.detected_files:
            lines.append(
                "| {file} | {confidence} | {count} | {types} | {chapters} |".format(
                    file=escape_table_cell(item.filename),
                    confidence=item.confidence,
                    count=item.question_count,
                    types=escape_table_cell("、".join(item.question_types)),
                    chapters=escape_table_cell("、".join(item.matched_chapters)),
                )
            )
    if report.past_exam_analysis.high_frequency_topics:
        lines.extend(["", "| 考点 | 章节 | 频次 | 题型 |", "| --- | --- | ---: | --- |"])
        for topic in report.past_exam_analysis.high_frequency_topics:
            lines.append(
                "| {topic} | {chapter} | {frequency} | {types} |".format(
                    topic=escape_table_cell(topic.topic),
                    chapter=escape_table_cell(topic.chapter),
                    frequency=topic.frequency,
                    types=escape_table_cell("、".join(topic.question_types)),
                )
            )


def append_review_order(lines: list[str], report: ReviewReport) -> None:
    lines.extend(["", "## 推荐复习顺序", ""])
    for index, item in enumerate(report.review_order, start=1):
        lines.append(f"{index}. **{item.chapter}** ({item.importance}/100): {item.reason}")


def append_sprint_plans(lines: list[str], report: ReviewReport) -> None:
    lines.extend(["", "## 考前冲刺计划"])
    for plan in report.sprint_plans:
        lines.extend(["", f"### {plan.title}"])
        for item in plan.schedule:
            lines.append(f"- {item}")


def append_mock_exam(lines: list[str], report: ReviewReport) -> None:
    lines.extend(["", "## 模拟卷", ""])
    for index, question in enumerate(report.mock_exam.questions, start=1):
        lines.extend(
            [
                f"### {index}. {question.question_type}",
                "",
                question.question,
                "",
                f"**参考答案：** {question.answer}",
                "",
                f"_章节：{question.chapter}；考点：{question.concept}_",
                "",
            ]
        )


def append_anki_preview(lines: list[str], report: ReviewReport) -> None:
    lines.extend(["", "## Anki 卡片预览", "", "| 正面 | 背面 | 标签 |", "| --- | --- | --- |"])
    for card in report.anki_cards[:12]:
        lines.append(
            f"| {escape_table_cell(card.front)} | {escape_table_cell(card.back)} | {escape_table_cell(card.tags)} |"
        )


def append_list(lines: list[str], heading: str, items: list[str]) -> None:
    lines.extend(["", f"## {heading}"])
    for item in items:
        lines.append(f"- {item}")


def escape_table_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", "<br>")
