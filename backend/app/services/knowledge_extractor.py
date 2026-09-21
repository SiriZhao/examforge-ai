from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field

from app.schemas.review import ParsedFile


@dataclass
class KnowledgeExtraction:
    topics: list[dict] = field(default_factory=list)
    definitions: list[dict] = field(default_factory=list)
    formulas: list[dict] = field(default_factory=list)
    tables: list[dict] = field(default_factory=list)
    images: list[dict] = field(default_factory=list)
    unresolved: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


def extract_knowledge(parsed_files: list[ParsedFile]) -> KnowledgeExtraction:
    result = KnowledgeExtraction()
    for parsed in parsed_files:
        structure = parsed.document_structure
        if structure:
            for section in structure.sections:
                result.topics.append(
                    {
                        "title": section.title,
                        "level": section.level,
                        "source_anchor": section.source_anchor,
                        "pages": [section.page_start, section.page_end],
                    }
                )
            for block in structure.blocks:
                if block.type == "formula":
                    result.formulas.append({"text": block.text, "source_anchor": block.source_anchor, "confidence": block.confidence})
                elif block.type == "table":
                    result.tables.append({"rows": block.rows, "source_anchor": block.source_anchor, "confidence": block.confidence})
                elif block.type == "image":
                    result.images.append({"metadata": block.metadata, "source_anchor": block.source_anchor, "confidence": block.confidence})
        for page in parsed.pages:
            anchor = page.source_anchor or f"{parsed.filename}, p. {page.page_number}"
            for line in page.text.splitlines():
                stripped = line.strip()
                if re.search(r"定义|是指|称为|defined as|refers to", stripped, re.I) and 6 <= len(stripped) <= 260:
                    result.definitions.append({"text": stripped, "source_anchor": anchor, "confidence": page.confidence})
            if page.status != "processed":
                result.unresolved.append({"source_anchor": anchor, "status": page.status, "reason": page.warning or "识别结果需要复核"})
    result.topics = _dedupe_dicts(result.topics, "title")
    result.definitions = _dedupe_dicts(result.definitions, "text")
    result.formulas = _dedupe_dicts(result.formulas, "text")
    return result


def build_generation_material(parsed_files: list[ParsedFile]) -> tuple[str, list[tuple[str, str]], KnowledgeExtraction]:
    extraction = extract_knowledge(parsed_files)
    file_texts: list[tuple[str, str]] = []
    documents: list[str] = []
    for parsed in parsed_files:
        page_parts = []
        for page in parsed.pages:
            anchor = page.source_anchor or f"{parsed.filename}, p. {page.page_number}"
            section = f"｜{page.title}" if page.title else ""
            status = f"｜状态：{page.status}" if page.status != "processed" else ""
            page_parts.append(f"[{anchor}{section}{status}]\n{page.text}".strip())
        anchored = "\n\n".join(page_parts)
        file_texts.append((parsed.filename, anchored))
        documents.append(anchored)
    header = "[Document Structure / Knowledge Extractor]\n" + _compact_knowledge(extraction)
    return "\n\n".join([header, *documents]), file_texts, extraction


def _compact_knowledge(extraction: KnowledgeExtraction) -> str:
    topics = "；".join(f"{item['title']}（{item['source_anchor']}）" for item in extraction.topics[:40])
    formulas = "；".join(f"{item['text']}（{item['source_anchor']}）" for item in extraction.formulas[:30])
    unresolved = "；".join(f"{item['source_anchor']}：{item['reason']}" for item in extraction.unresolved[:20])
    return "\n".join(
        [
            f"章节树：{topics or '未识别明确章节'}",
            f"公式索引：{formulas or '未识别明确公式'}",
            f"待复核单元：{unresolved or '无'}",
        ]
    )


def _dedupe_dicts(items: list[dict], key: str) -> list[dict]:
    output: list[dict] = []
    seen: set[str] = set()
    for item in items:
        marker = str(item.get(key, "")).strip().casefold()
        if marker and marker not in seen:
            seen.add(marker)
            output.append(item)
    return output
