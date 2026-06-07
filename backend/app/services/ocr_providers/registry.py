from app.services.ocr_providers.base import BaseOCRProvider
from app.services.ocr_providers.baidu_ocr import BaiduOCROCRProvider
from app.services.ocr_providers.custom_api import CustomAPIOCRProvider
from app.services.ocr_providers.local_tesseract import LocalTesseractOCRProvider
from app.services.ocr_providers.openai_vision import OpenAIVisionOCRProvider
from app.services.ocr_providers.rapidocr_provider import RapidOCROCRProvider

_PROVIDERS: dict[str, BaseOCRProvider] = {
    RapidOCROCRProvider.name: RapidOCROCRProvider(),
    LocalTesseractOCRProvider.name: LocalTesseractOCRProvider(),
    CustomAPIOCRProvider.name: CustomAPIOCRProvider(),
    OpenAIVisionOCRProvider.name: OpenAIVisionOCRProvider(),
    BaiduOCROCRProvider.name: BaiduOCROCRProvider(),
}


def get_ocr_provider(name: str) -> BaseOCRProvider:
    try:
        return _PROVIDERS[name]
    except KeyError as exc:
        raise RuntimeError(f"不支持的 OCR 服务：{name}。") from exc
