from PIL import Image

from app.schemas.review import OCRConfig
from app.services.ocr_providers.base import BaseOCRProvider
from app.services.ocr_providers.utils import image_to_base64


class OpenAIVisionOCRProvider(BaseOCRProvider):
    name = "openai_vision"

    def extract_text(self, image: Image.Image, config: OCRConfig) -> str:
        import httpx

        if not config.api_key:
            raise RuntimeError("OpenAI 视觉识别需要 api_key。")

        image_url = f"data:image/png;base64,{image_to_base64(image)}"
        payload = {
            "model": config.model or "gpt-4.1-mini",
            "input": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": "请提取图片中所有可读文字，只返回识别出的文字。",
                        },
                        {"type": "input_image", "image_url": image_url},
                    ],
                }
            ],
        }
        try:
            response = httpx.post(
                "https://api.openai.com/v1/responses",
                json=payload,
                headers={"Authorization": f"Bearer {config.api_key}"},
                timeout=90,
            )
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPError as exc:
            raise RuntimeError("OpenAI 视觉识别请求失败。") from exc
        except ValueError as exc:
            raise RuntimeError("OpenAI 视觉识别返回了无效 JSON。") from exc

        text = data.get("output_text")
        if not isinstance(text, str):
            raise RuntimeError("OpenAI 视觉识别响应中没有 output_text。")
        return text.strip()
