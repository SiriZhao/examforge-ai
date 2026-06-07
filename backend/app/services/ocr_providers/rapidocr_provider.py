from PIL import Image

from app.schemas.review import OCRConfig
from app.services.ocr_providers.base import BaseOCRProvider
from app.services.ocr_providers.utils import image_to_bytes


class RapidOCROCRProvider(BaseOCRProvider):
    name = "rapidocr"

    def extract_text(self, image: Image.Image, config: OCRConfig) -> str:
        try:
            from rapidocr_onnxruntime import RapidOCR
        except ImportError as exc:
            raise RuntimeError(
                "RapidOCR 未安装。请运行 pip install -r backend/requirements.txt。"
            ) from exc

        engine = RapidOCR()
        result, _ = engine(image_to_bytes(image))
        if not result:
            return ""

        lines = [item[1].strip() for item in result if len(item) >= 2 and item[1].strip()]
        return "\n".join(lines)
