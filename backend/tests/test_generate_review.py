from pathlib import Path
from urllib.parse import unquote

from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.schemas.review import ParsedFile, ParsedPage


PARSED_TEXT = """
Chapter 1 Photosynthesis
Key points: chloroplast, light reaction, Calvin cycle, ATP, NADPH.
1. Multiple choice: Which stage produces ATP and NADPH? A. Light reaction B. Germination C. Pollination D. Dormancy
2. Short answer: Explain why the Calvin cycle depends on light reactions.

Chapter 2 Plant Transport
Key points: xylem, phloem, stomata, guard cells, transpiration.
1. Fill in the blank: The tissue that transports sugar is ____.
2. Essay: Discuss the trade-off between gas exchange and water loss in leaves.
"""


def parsed_file(path: Path) -> ParsedFile:
    return ParsedFile(
        filename=path.name,
        file_type=path.suffix,
        path=str(path),
        pages=[ParsedPage(page_number=1, text=PARSED_TEXT, source="text_extract")],
        raw_text=PARSED_TEXT,
    )


def test_generate_review_exports_markdown_and_anki(
    tmp_path: Path, monkeypatch
) -> None:
    settings.upload_dir = tmp_path / "uploads"
    settings.output_dir = tmp_path / "outputs"
    settings.upload_dir.mkdir()
    uploaded = settings.upload_dir / "demo_past_exam.md"
    uploaded.write_text(PARSED_TEXT, encoding="utf-8")

    monkeypatch.setattr(
        "app.routers.generate_review.parse_file",
        lambda path, ocr_config: parsed_file(path),
    )

    client = TestClient(app)
    response = client.post(
        "/generate-review",
        json={
            "files": [uploaded.name],
            "export_format": "md",
            "title": "Plant Biology Final Sprint",
            "course_name": "植物学下",
            "llm_config": {
                "enabled": True,
                "provider": "openai",
                "api_key": "secret-key-should-not-leak",
            },
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["review_report"]["title"] == "植物学下"
    assert "章节优先级" in body["markdown"]
    assert "往年题高频考点分析" in body["markdown"]
    assert "推荐复习顺序" in body["markdown"]
    assert "模拟卷" in body["markdown"]
    assert body["download_path"].startswith("/download/")
    assert body["download_path"].endswith(".md")
    assert body["download_links"]["md"].endswith(".md")
    assert body["anki_csv_download_path"].startswith("/download/")
    assert body["download_links"]["md"].endswith(".md")
    assert unquote(body["download_links"]["md"]).endswith("植物学下_复习资料包.md")
    assert unquote(body["anki_csv_download_path"]).endswith("植物学下_Anki卡片.csv")
    assert body["review_report"]["past_exam_analysis"]["detected_files"]
    assert body["review_report"]["mock_exam"]["questions"]
    assert body["review_report"]["anki_cards"]
    assert body["review_report"]["quality"]["quality_score"] >= 0
    assert body["generation_summary"]["files_processed"] == 1
    assert body["generation_summary"]["pages_text_extracted"] == 1
    assert any(settings.output_dir.glob("*.md"))
    assert any(settings.output_dir.glob("*_Anki卡片.csv"))
    assert "secret-key-should-not-leak" not in response.text


def test_reoptimize_keeps_existing_report_without_ocr(tmp_path: Path, monkeypatch) -> None:
    settings.output_dir = tmp_path / "outputs"
    settings.output_dir.mkdir()
    from app.services.review_planner import generate_review_report

    review_report = generate_review_report(PARSED_TEXT, study_goal="balanced", exam_type="closed_book")

    def fail_parse(*args, **kwargs):
        raise AssertionError("reoptimize must not parse files or OCR")

    monkeypatch.setattr("app.routers.generate_review.parse_file", fail_parse)
    client = TestClient(app)
    response = client.post(
        "/api/review/reoptimize",
        json={
            "current_report": review_report.model_dump(mode="json"),
            "evidence_text": PARSED_TEXT,
            "optimization_goal": "memorization",
            "original_study_goal": "memorization",
            "original_exam_type": "closed_book",
            "llm_config": {"enabled": False},
        },
    )

    assert response.status_code == 200
    assert response.json()["optimized"] is True


def test_generate_review_exports_docx(
    tmp_path: Path, monkeypatch
) -> None:
    settings.upload_dir = tmp_path / "uploads"
    settings.output_dir = tmp_path / "outputs"
    settings.upload_dir.mkdir()
    uploaded = settings.upload_dir / "lecture.docx"
    uploaded.write_bytes(b"docx")

    monkeypatch.setattr(
        "app.routers.generate_review.parse_file",
        lambda path, ocr_config: parsed_file(path),
    )

    client = TestClient(app)
    response = client.post(
        "/generate-review",
        json={"files": [uploaded.name], "export_format": "docx"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["download_path"].startswith("/download/")
    assert body["download_path"].endswith(".docx")
    assert any(settings.output_dir.glob("*.docx"))


def test_generate_review_exports_pdf(
    tmp_path: Path, monkeypatch
) -> None:
    settings.upload_dir = tmp_path / "uploads"
    settings.output_dir = tmp_path / "outputs"
    settings.upload_dir.mkdir()
    uploaded = settings.upload_dir / "lecture.pdf"
    uploaded.write_bytes(b"pdf")

    monkeypatch.setattr(
        "app.routers.generate_review.parse_file",
        lambda path, ocr_config: parsed_file(path),
    )

    client = TestClient(app)
    response = client.post(
        "/generate-review",
        json={"files": [uploaded.name], "export_format": "pdf"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["download_path"].startswith("/download/")
    assert body["download_path"].endswith(".pdf")
    assert any(settings.output_dir.glob("*.pdf"))


def test_generate_review_can_export_all_formats(
    tmp_path: Path, monkeypatch
) -> None:
    settings.upload_dir = tmp_path / "uploads"
    settings.output_dir = tmp_path / "outputs"
    settings.upload_dir.mkdir()
    uploaded = settings.upload_dir / "lecture.pdf"
    uploaded.write_bytes(b"pdf")

    monkeypatch.setattr(
        "app.routers.generate_review.parse_file",
        lambda path, ocr_config: parsed_file(path),
    )

    client = TestClient(app)
    response = client.post(
        "/generate-review",
        json={"files": [uploaded.name], "export_formats": ["md", "docx", "pdf"]},
    )

    assert response.status_code == 200
    links = response.json()["download_links"]
    assert set(links) == {"md", "docx", "pdf"}
    assert all(link.startswith("/download/") for link in links.values())


def test_generate_review_rejects_empty_file_list() -> None:
    client = TestClient(app)
    response = client.post("/generate-review", json={"files": []})

    assert response.status_code == 400
    assert response.json()["detail"] == "请至少上传一个文件后再生成复习资料。"


def test_generate_review_rejects_path_outside_uploads(tmp_path: Path) -> None:
    settings.upload_dir = tmp_path / "uploads"
    settings.output_dir = tmp_path / "outputs"
    settings.upload_dir.mkdir()
    outside = tmp_path / "outside.pdf"
    outside.write_bytes(b"pdf")

    client = TestClient(app)
    response = client.post(
        "/generate-review",
        json={"files": [str(outside)], "export_format": "md"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "只能解析上传目录中的文件。"
    )
