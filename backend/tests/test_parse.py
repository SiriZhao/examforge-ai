from pathlib import Path

from fastapi.testclient import TestClient
from PIL import Image

from app.config import settings
from app.main import app
from app.schemas.review import OCRConfig, ParsedFile, ParsedPage
from app.services import file_parser


def test_parse_endpoint_returns_unified_structure(
    tmp_path: Path, monkeypatch
) -> None:
    settings.upload_dir = tmp_path
    uploaded = tmp_path / "lecture.docx"
    uploaded.write_bytes(b"mock docx")

    def fake_parse_file(path: Path, ocr_config: OCRConfig) -> ParsedFile:
        return ParsedFile(
            filename=path.name,
            file_type=path.suffix,
            path=str(path),
            pages=[
                ParsedPage(
                    page_number=1,
                    text="chapter one review notes",
                    source="text_extract",
                )
            ],
            raw_text="chapter one review notes",
        )

    monkeypatch.setattr("app.routers.parse.parse_file", fake_parse_file)
    client = TestClient(app)

    response = client.post("/parse", json={"files": [uploaded.name]})

    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "已成功解析 1 个文件。"
    assert body["files"][0]["filename"] == "lecture.docx"
    assert body["files"][0]["pages"][0]["source"] == "text_extract"
    assert body["files"][0]["raw_text"] == "chapter one review notes"


def test_parse_rejects_paths_outside_uploads(tmp_path: Path) -> None:
    settings.upload_dir = tmp_path / "uploads"
    settings.upload_dir.mkdir()
    outside_file = tmp_path / "outside.pdf"
    outside_file.write_bytes(b"outside")
    client = TestClient(app)

    response = client.post("/parse", json={"files": [str(outside_file)]})

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "只能解析上传目录中的文件。"
    )


def test_parse_rejects_unsupported_file_type(tmp_path: Path) -> None:
    settings.upload_dir = tmp_path
    uploaded = tmp_path / "notes.txt"
    uploaded.write_text("plain text", encoding="utf-8")
    client = TestClient(app)

    response = client.post("/parse", json={"files": [uploaded.name]})

    assert response.status_code == 400
    assert response.json()["detail"] == "不支持解析该文件类型：.txt。"


def test_markdown_parse_reads_text(tmp_path: Path) -> None:
    markdown_path = tmp_path / "demo_course_material.md"
    markdown_path.write_text("# Demo Course\n\nChapter 1 notes", encoding="utf-8")

    parsed = file_parser.parse_file(markdown_path)

    assert parsed.file_type == ".md"
    assert parsed.pages[0].source == "text_extract"
    assert "Chapter 1 notes" in parsed.raw_text


def test_image_parse_uses_ocr_provider(tmp_path: Path, monkeypatch) -> None:
    image_path = tmp_path / "scan.png"
    image_path.write_bytes(b"fake image bytes")

    def fake_ocr(path: Path, config: OCRConfig) -> str:
        assert path == image_path
        assert config.provider == "custom_api"
        assert config.api_key == "request-only-key"
        return "ocr text from image"

    monkeypatch.setattr(file_parser, "run_ocr_on_path", fake_ocr)

    parsed = file_parser.parse_file(
        image_path,
        OCRConfig(
            provider="custom_api",
            api_url="https://example.test/ocr",
            api_key="request-only-key",
        ),
    )

    assert parsed.pages[0].source == "ocr_fallback"
    assert parsed.raw_text == "ocr text from image"


def test_pdf_short_text_page_uses_ocr_fallback(tmp_path: Path, monkeypatch) -> None:
    pdf_path = tmp_path / "scan.pdf"
    pdf_path.write_bytes(b"%PDF mock")

    class FakePdfPage:
        def extract_text(self) -> str:
            return "too short"

    class FakePdfReader:
        def __init__(self, _: str) -> None:
            self.pages = [FakePdfPage()]

    monkeypatch.setattr("pypdf.PdfReader", FakePdfReader)
    monkeypatch.setattr(
        file_parser,
        "render_pdf_page_to_image",
        lambda path, page_number: Image.new("RGB", (10, 10), "white"),
    )
    monkeypatch.setattr(
        file_parser,
        "run_ocr_on_image",
        lambda image, config: "ocr text from scanned pdf",
    )

    parsed = file_parser.parse_file(pdf_path, OCRConfig(provider="local_tesseract"))

    assert parsed.pages[0].page_number == 1
    assert parsed.pages[0].source == "ocr_fallback"
    assert parsed.raw_text == "ocr text from scanned pdf"
