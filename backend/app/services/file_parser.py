from collections.abc import Callable
from pathlib import Path

from PIL import Image

from app.schemas.review import OCRConfig, ParsedFile, ParsedPage
from app.services.ocr_service import OCRError, run_ocr_on_image, run_ocr_on_path
from app.services.runtime_paths import find_poppler_path

SUPPORTED_PARSE_EXTENSIONS = {".pptx", ".pdf", ".docx", ".md", ".png", ".jpg", ".jpeg"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}
PDF_TEXT_MIN_CHARS = 20


class ParseError(RuntimeError):
    pass


ProgressCallback = Callable[[str, float | None], None]


def parse_file(
    path: Path,
    ocr_config: OCRConfig | None = None,
    progress_callback: ProgressCallback | None = None,
) -> ParsedFile:
    config = ocr_config or OCRConfig()
    suffix = path.suffix.lower()

    if suffix not in SUPPORTED_PARSE_EXTENSIONS:
        raise ParseError(f"不支持解析该文件类型：{suffix or '未知'}。")
    if not path.exists():
        raise ParseError(f"文件不存在：{path.name}。")

    try:
        if suffix == ".docx":
            pages = parse_docx(path)
        elif suffix == ".pptx":
            pages = parse_pptx(path)
        elif suffix == ".md":
            pages = parse_markdown(path)
        elif suffix == ".pdf":
            pages = parse_pdf(path, config, progress_callback)
        else:
            if progress_callback:
                progress_callback(f"正在识别图片：{path.name}", None)
            pages = parse_image(path, config)
    except (ParseError, OCRError):
        raise
    except Exception as exc:
        raise ParseError(f"解析 {path.name} 失败：{exc}") from exc

    raw_text = "\n\n".join(page.text for page in pages if page.text.strip())
    return ParsedFile(
        filename=path.name,
        file_type=suffix,
        path=str(path.resolve()),
        pages=pages,
        raw_text=raw_text,
    )


def parse_docx(path: Path) -> list[ParsedPage]:
    try:
        from docx import Document
    except ImportError as exc:
        raise ParseError("未安装 python-docx。") from exc

    document = Document(path)
    lines = [paragraph.text.strip() for paragraph in document.paragraphs]
    text = "\n".join(line for line in lines if line)
    return [ParsedPage(page_number=1, text=text, source="text_extract")]


def parse_pptx(path: Path) -> list[ParsedPage]:
    try:
        from pptx import Presentation
    except ImportError as exc:
        raise ParseError("未安装 python-pptx。") from exc

    presentation = Presentation(path)
    pages: list[ParsedPage] = []
    for index, slide in enumerate(presentation.slides, start=1):
        slide_text: list[str] = []
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                text = shape.text.strip()
                if text:
                    slide_text.append(text)
        pages.append(
            ParsedPage(
                page_number=index,
                text="\n".join(slide_text),
                source="text_extract",
            )
        )
    return pages


def parse_markdown(path: Path) -> list[ParsedPage]:
    text = path.read_text(encoding="utf-8")
    return [ParsedPage(page_number=1, text=text, source="text_extract")]


def parse_pdf(
    path: Path,
    ocr_config: OCRConfig,
    progress_callback: ProgressCallback | None = None,
) -> list[ParsedPage]:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise ParseError("未安装 pypdf。") from exc

    try:
        reader = PdfReader(str(path))
    except Exception as exc:
        raise ParseError(f"无法打开 PDF：{path.name}。") from exc

    pages: list[ParsedPage] = []
    total_pages = len(reader.pages)
    for index, page in enumerate(reader.pages, start=1):
        if progress_callback:
            progress_callback(f"正在解析 PDF 第 {index}/{total_pages} 页", index / max(total_pages, 1))
        text = (page.extract_text() or "").strip()
        if len(text) >= PDF_TEXT_MIN_CHARS:
            pages.append(
                ParsedPage(page_number=index, text=text, source="text_extract")
            )
            continue

        image = render_pdf_page_to_image(path, index)
        if progress_callback:
            progress_callback(
                f"正在对扫描页执行 OCR：第 {index}/{total_pages} 页。本地 OCR 可能占用较高 CPU，请耐心等待。",
                index / max(total_pages, 1),
            )
        ocr_text = run_ocr_on_image(image, ocr_config)
        pages.append(
            ParsedPage(page_number=index, text=ocr_text, source="ocr_fallback")
        )

    return pages


def parse_image(path: Path, ocr_config: OCRConfig) -> list[ParsedPage]:
    text = run_ocr_on_path(path, ocr_config)
    return [ParsedPage(page_number=1, text=text, source="ocr_fallback")]


def render_pdf_page_to_image(path: Path, page_number: int) -> Image.Image:
    try:
        from pdf2image import convert_from_path
    except ImportError as exc:
        raise ParseError("未安装 pdf2image。") from exc

    try:
        poppler_path = find_poppler_path()
        images = convert_from_path(
            str(path),
            first_page=page_number,
            last_page=page_number,
            dpi=200,
            poppler_path=str(poppler_path) if poppler_path else None,
        )
    except Exception as exc:
        raise ParseError("PDF 扫描页渲染失败。请运行 scripts/install-ocr.ps1 安装 Poppler。") from exc

    if not images:
        raise ParseError(f"PDF 第 {page_number} 页无法渲染。")

    return images[0]


def parse_file_to_text(path: Path, ocr_config: OCRConfig | None = None) -> str:
    return parse_file(path, ocr_config).raw_text
