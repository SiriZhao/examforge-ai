import logging
from pathlib import Path

from PIL import Image

from app.schemas.review import OCRConfig
from app.services.ocr_providers import get_ocr_provider

logger = logging.getLogger(__name__)


class OCRError(RuntimeError):
    pass


def open_image(path: Path) -> Image.Image:
    try:
        return Image.open(path)
    except Exception as exc:
        raise OCRError(f"无法打开图片进行 OCR：{path.name}。") from exc


def run_ocr_on_path(path: Path, config: OCRConfig) -> str:
    logger.info("OCR started: provider=%s file=%s", config.provider, path.name)
    with open_image(path) as image:
        text = run_ocr_on_image(image, config)
    logger.info("OCR completed: provider=%s file=%s", config.provider, path.name)
    return text


def run_ocr_on_image(image: Image.Image, config: OCRConfig) -> str:
    try:
        return get_ocr_provider(config.provider).extract_text(image, config)
    except RuntimeError as exc:
        raise OCRError(str(exc)) from exc


def ocr_image(file_path: str, provider: str = "local_tesseract", config: dict | None = None) -> str:
    raw_config = config or {}
    ocr_config = OCRConfig(provider=provider, **raw_config)
    return run_ocr_on_path(Path(file_path), ocr_config)
