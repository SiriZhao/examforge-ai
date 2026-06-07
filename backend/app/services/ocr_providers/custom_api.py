from PIL import Image

from app.schemas.review import OCRConfig
from app.services.ocr_providers.base import BaseOCRProvider
from app.services.ocr_providers.utils import image_to_base64


class CustomAPIOCRProvider(BaseOCRProvider):
    name = "custom_api"

    def extract_text(self, image: Image.Image, config: OCRConfig) -> str:
        import httpx

        if not config.api_url:
            raise RuntimeError("自定义 OCR 需要填写 api_url。")

        headers: dict[str, str] = {}
        if config.api_key:
            headers["Authorization"] = f"Bearer {config.api_key}"

        payload = {
            "image_base64": image_to_base64(image),
            "language": config.language,
            "model": config.model,
        }
        try:
            response = httpx.post(
                config.api_url,
                json=payload,
                headers=headers,
                timeout=60,
            )
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPError as exc:
            raise RuntimeError("自定义 OCR 请求失败。") from exc
        except ValueError as exc:
            raise RuntimeError("自定义 OCR 返回了无效 JSON。") from exc

        text = data.get("text") or data.get("raw_text")
        if not isinstance(text, str):
            raise RuntimeError("自定义 OCR 响应必须包含 text 或 raw_text。")
        return text.strip()
