from pathlib import Path

from app.schemas.review import ReviewReport, StudyUnit
from app.services import file_parser
from app.services.chunking import split_semantic_chunks
from app.services.knowledge_extractor import build_generation_material, extract_knowledge
from app.services.llm_service_prompt import build_review_prompt, compact_chunk_insights
from app.services.quality_checker import check_output_quality
from app.services.review_planner import generate_review_report
from app.templates import get_prompt_template


def test_parser_generates_document_structure_json_with_anchors_and_tables(tmp_path: Path) -> None:
    material = tmp_path / "probability.md"
    material.write_text(
        "# 概率论\n\n## 第一章 随机事件\n定义：样本空间是所有可能结果的集合。\n\n"
        "| 事件 | 含义 |\n| A | 目标事件 |\n\n## 第二章 条件概率\nP(A|B)=P(AB)/P(B)",
        encoding="utf-8",
    )

    parsed = file_parser.parse_file(material)
    structure = parsed.document_structure

    assert structure is not None
    assert structure.schema_version == "3.2"
    assert structure.title == "概率论"
    assert structure.page_count == 1
    assert any(section.title == "第一章 随机事件" for section in structure.sections)
    assert any(block.type == "table" and block.rows[0] == ["事件", "含义"] for block in structure.blocks)
    assert any(block.type == "formula" and "P(A|B)" in block.text for block in structure.blocks)
    assert all(block.source_anchor == "probability.md, p. 1" for block in structure.blocks)
    assert parsed.pages[0].status == "processed"


def test_structure_aware_chunks_preserve_sections_and_mark_overlap() -> None:
    text = "\n\n".join(
        [
            "# 第一章 基础\n" + "基础定义与条件。" * 35,
            "# 第二章 方法\n" + "推导步骤与例题。" * 35,
            "# 第三章 应用\n" + "应用边界与易错点。" * 35,
        ]
    )

    chunks = split_semantic_chunks(text, max_chars=220, overlap_chars=45)
    joined = "\n".join(chunk.text for chunk in chunks)

    assert len(chunks) >= 3
    assert all(len(chunk.text) <= 220 for chunk in chunks)
    assert all(title in joined for title in ("第一章 基础", "第二章 方法", "第三章 应用"))
    assert any(chunk.overlap_from_previous for chunk in chunks[1:])
    assert any("承接上文" in chunk.text for chunk in chunks[1:])


def test_knowledge_extractor_keeps_sources_and_unresolved_pages(tmp_path: Path) -> None:
    material = tmp_path / "memory.md"
    material.write_text("# 记忆系统\n定义：工作记忆用于短时加工。\nE=mc^2", encoding="utf-8")
    parsed = file_parser.parse_file(material)
    parsed.pages[0].warning = "图示需要人工复核"
    parsed.pages[0].status = "processed_with_warning"

    extraction = extract_knowledge([parsed])
    combined, file_texts, _ = build_generation_material([parsed])

    assert extraction.topics
    assert extraction.definitions[0]["source_anchor"] == "memory.md, p. 1"
    assert extraction.formulas
    assert extraction.unresolved[0]["status"] == "processed_with_warning"
    assert "[memory.md, p. 1" in combined
    assert file_texts[0][0] == "memory.md"


def test_prompt_template_registry_routes_four_learning_modes() -> None:
    assert get_prompt_template("one_day_sprint", "teaching_assistant")[0] == "exam"
    assert get_prompt_template("balanced", "teaching_assistant")[0] == "understanding"
    assert get_prompt_template("memorization", "teaching_assistant")[0] == "memory"
    assert get_prompt_template("practice_heavy", "teaching_assistant")[0] == "practice"

    report = generate_review_report("第一章 概率\n定义：概率描述事件发生的可能性。")
    prompt = build_review_prompt(
        {"course_name": "概率论", "files": [], "global_signals": {}, "chunks": []},
        report,
        [],
        study_goal="practice_heavy",
    )
    assert "v3.2 Prompt 模式：practice" in prompt
    assert "题目、答案、解析和来源依据" in prompt


def test_balanced_chunk_compaction_keeps_every_chunk_and_removes_repeat() -> None:
    compact = compact_chunk_insights(
        [
            "共同定义\n第一章独有考点",
            "共同定义\n第二章独有考点",
            "共同定义\n第三章独有考点",
        ],
        1000,
    )

    assert compact.count("共同定义") == 1
    assert all(f"[chunk_insight {index}]" in compact for index in range(1, 4))
    assert all(f"第{name}章独有考点" in compact for name in ("一", "二", "三"))


def test_quality_checker_reports_coverage_duplicates_and_empty_output() -> None:
    report = ReviewReport(
        title="概率论复习",
        summary="围绕随机事件进行复习。",
        study_units=[
            StudyUnit(name="随机事件", key_points=["样本空间"]),
            StudyUnit(name="随机事件", key_points=["事件关系"]),
        ],
    )
    checked = check_output_quality(report, ["随机事件", "条件概率", "随机变量"])
    empty = check_output_quality(ReviewReport(title="", summary=""), ["第一章"])

    assert checked.coverage_ratio < 0.8
    assert checked.missing_sections == ["条件概率", "随机变量"]
    assert checked.duplicate_sections == ["随机事件"]
    assert checked.warnings
    assert empty.is_empty is True
    assert "生成内容为空或过短。" in empty.failures
