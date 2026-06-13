import os

from PIL import Image, ImageEnhance, ImageOps

from app.schemas.review import OCRConfig
from app.services.ocr_providers.base import BaseOCRProvider
from app.services.runtime_paths import find_tesseract_cmd, find_tessdata_dir
from app.services.subprocess_utils import hide_subprocess_windows


class LocalTesseractOCRProvider(BaseOCRProvider):
    name = "local_tesseract"

    def extract_text(self, image: Image.Image, config: OCRConfig) -> str:
        try:
            import pytesseract
        except ImportError as exc:
            raise RuntimeError("未安装 pytesseract。") from exc

        tesseract_cmd = find_tesseract_cmd()
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = str(tesseract_cmd)

        tessdata_dir = find_tessdata_dir()
        if tessdata_dir:
            os.environ["TESSDATA_PREFIX"] = str(tessdata_dir)

        processed = preprocess_image(image)
        try:
            with hide_subprocess_windows():
                return pytesseract.image_to_string(
                    processed,
                    lang=config.language,
                ).strip()
        except Exception as exc:
            raise RuntimeError(
                "本地 Tesseract OCR 失败。请运行 scripts/install-ocr.ps1 安装 Tesseract、Poppler 和中文语言数据。"
            ) from exc


def preprocess_image(image: Image.Image) -> Image.Image:
    grayscale = ImageOps.grayscale(image)
    enhanced = ImageEnhance.Contrast(grayscale).enhance(1.8)
    return enhanced.point(lambda value: 255 if value > 160 else 0)
