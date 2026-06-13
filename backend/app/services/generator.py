from app.schemas.review import ReviewReport
from app.services.review_planner import sanitize_report


def generate_markdown_review(report: ReviewReport, *, prefer_existing: bool = True) -> str:
    if prefer_existing and report.markdown.strip():
        return report.markdown.strip()

    report = sanitize_report(report)
    lines = [
        f"# {report.title}",
        "",
        f"生成时间：{report.generated_at}",
        "",
        "## 复习导览",
        report.summary,
        "",
    ]

    if report.overview:
        for label, key in [
            ("考试策略", "exam_strategy"),
            ("材料概况", "material_summary"),
            ("优先级建议", "priority_advice"),
        ]:
            value = report.overview.get(key)
            if value:
                lines.extend([f"### {label}", str(value), ""])

    append_quality(lines, report)
    append_study_units(lines, report)
    append_question_types(lines, report)
    append_past_exam_analysis(lines, report)
    lines.extend(["", "## 章节优先级", ""])
    append_review_order(lines, report)
    append_sprint_plans(lines, report)
    append_mock_exam(lines, report)
    append_anki_preview(lines, report)
    append_list(lines, "高频考点", report.high_frequency_points)
    append_list(lines, "考前冲刺清单", report.sprint_checklist)
    append_list(lines, "可略看的内容", report.low_priority)
    append_list(lines, "材料不足提示", report.insufficient_materials or ["暂无"])

    return "\n".join(lines).strip() + "\n"


def append_study_units(lines: list[str], report: ReviewReport) -> None:
    lines.extend(["", "## 知识结构与复习单元", ""])
    if report.study_units:
        for unit in report.study_units:
            lines.extend(
                [
                    f"### {unit.name}",
                    f"- 重要度：{unit.priority}/100",
                    f"- 划分理由：{unit.reason or '根据材料结构、题干线索和关键词聚合得到。'}",
                    f"- 复习方法：{unit.how_to_review or '先理解核心概念，再用题目检查。'}",
                ]
            )
            append_inline_list(lines, "必须掌握", unit.must_know)
            append_inline_list(lines, "核心要点", unit.key_points)
            append_inline_list(lines, "公式/方法", unit.formulas_or_methods)
            append_inline_list(lines, "常见考法", unit.common_exam_angles)
            append_inline_list(lines, "易错点", unit.pitfalls)
            lines.append("")
        return

    lines.extend(["| 章节/专题 | 重要度 | 关键词 | 复习建议 |", "| --- | ---: | --- | --- |"])
    for chapter in report.chapters:
        lines.append(
            "| {chapter} | {importance} | {keywords} | {advice} |".format(
                chapter=escape_table_cell(chapter.chapter),
                importance=chapter.importance,
                keywords=escape_table_cell("、".join(chapter.keywords) or "暂无"),
                advice=escape_table_cell(chapter.review_advice),
            )
        )


def append_question_types(lines: list[str], report: ReviewReport) -> None:
    lines.extend(["", "## 考点与题型", ""])
    if report.question_types:
        for item in report.question_types:
            lines.extend(
                [
                    f"### {item.name}",
                    f"- 证据：{item.evidence or '根据材料题干和知识点线索归纳。'}",
                    f"- 答题方法：{item.answer_strategy or '先定位考点，再按题干要求组织答案。'}",
                ]
            )
            append_inline_list(lines, "题型特征", item.features)
            append_inline_list(lines, "相关考点", item.related_topics)
            append_inline_list(lines, "样例题", item.sample_questions)
            lines.append("")
    else:
        lines.append("暂未识别出稳定题型。")


def append_past_exam_analysis(lines: list[str], report: ReviewReport) -> None:
    lines.extend(["", "## 往年题高频考点分析", ""])
    lines.append(report.past_exam_analysis.summary or "暂无往年题分析。")
    if report.past_exam_analysis.detected_files:
        lines.extend(["", "| 文件 | 置信度 | 题目数 | 题型 | 章节/专题 |", "| --- | ---: | ---: | --- | --- |"])
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
        lines.extend(["", "| 考点 | 章节/专题 | 频次 | 题型 |", "| --- | --- | ---: | --- |"])
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
        lines.append(f"{index}. **{item.chapter}**（{item.importance}/100）：{item.reason}")


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
            ]
        )
        if question.explanation:
            lines.append(f"**解析：** {question.explanation}")
        if question.chapter or question.concept:
            lines.append(f"_专题：{question.chapter}；考点：{question.concept}_")
        lines.append("")


def append_anki_preview(lines: list[str], report: ReviewReport) -> None:
    lines.extend(["", "## Anki 卡片预览", "", "| Front | Back | Tags |", "| --- | --- | --- |"])
    for card in report.anki_cards[:20]:
        lines.append(
            f"| {escape_table_cell(card.front)} | {escape_table_cell(card.back)} | {escape_table_cell(card.tags)} |"
        )


def append_list(lines: list[str], heading: str, items: list[str]) -> None:
    lines.extend(["", f"## {heading}"])
    for item in items:
        lines.append(f"- {item}")


def append_inline_list(lines: list[str], label: str, items: list[str]) -> None:
    if not items:
        return
    lines.append(f"- {label}：")
    for item in items[:10]:
        lines.append(f"  - {item}")


def append_quality(lines: list[str], report: ReviewReport) -> None:
    if not report.quality:
        return
    quality = report.quality
    lines.extend(
        [
            "",
            "## 生成质量评分",
            f"- 总分：{quality.quality_score}/100",
            f"- 资料完整度：{quality.material_completeness_score}/100",
            f"- 考点覆盖度：{quality.topic_coverage_score}/100",
            f"- 模拟题质量：{quality.mock_exam_quality_score}/100",
            f"- Anki 可用性：{quality.anki_quality_score}/100",
            f"- 导出就绪度：{quality.export_readiness_score}/100",
            f"- 证据整合度：{quality.evidence_integration_score}/100",
        ]
    )
    append_inline_list(lines, "质量提示", quality.quality_warnings)
    append_inline_list(lines, "需要修复的问题", quality.quality_failures)


def escape_table_cell(value: str) -> str:
    return str(value).replace("|", "\\|").replace("\n", "<br>")
